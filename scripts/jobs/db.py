"""SQLite storage for discovered jobs and scan runs."""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config
from .models import DB_COLUMNS, Job, Status, can_transition, utc_now

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_job_id TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL,
    canonical_url TEXT NOT NULL UNIQUE,
    company TEXT NOT NULL DEFAULT '',
    company_norm TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL DEFAULT '',
    title_norm TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    location_norm TEXT NOT NULL DEFAULT '',
    remote_type TEXT NOT NULL DEFAULT 'unknown',
    language TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    posted_at TEXT NOT NULL DEFAULT '',
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    deadline TEXT NOT NULL DEFAULT '',
    employment_type TEXT NOT NULL DEFAULT '',
    salary_min REAL,
    salary_max REAL,
    currency TEXT NOT NULL DEFAULT '',
    score REAL,
    score_reasons TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'discovered',
    feedback TEXT NOT NULL DEFAULT '',
    blocked_reason TEXT NOT NULL DEFAULT '',
    dedup_key TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_dedup ON jobs(dedup_key);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_last_seen ON jobs(last_seen);

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    fetched INTEGER NOT NULL DEFAULT 0,
    new_count INTEGER NOT NULL DEFAULT 0,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    filtered_count INTEGER NOT NULL DEFAULT 0,
    scored_count INTEGER NOT NULL DEFAULT 0,
    shortlisted_count INTEGER NOT NULL DEFAULT 0,
    llm_calls INTEGER NOT NULL DEFAULT 0,
    errors TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS source_health (
    source TEXT PRIMARY KEY,
    last_success TEXT,
    last_error TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    degraded INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    target = Path(path) if path else config.db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def backup(conn: sqlite3.Connection) -> Path | None:
    row = conn.execute("PRAGMA database_list").fetchone()
    if row is None:
        return None
    source = Path(row["file"])
    if not source.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = source.with_name(f"{source.name}.bak-{stamp}")
    shutil.copy2(source, target)
    return target


def init_db(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executescript(SCHEMA)
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def migrate(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        init_db(conn)
        return
    if version > SCHEMA_VERSION:
        raise RuntimeError(
            f"database schema {version} is newer than supported {SCHEMA_VERSION}"
        )
    if version < SCHEMA_VERSION:
        backup(conn)
        init_db(conn)


def schema_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def _row_for(conn: sqlite3.Connection, job: Job) -> sqlite3.Row | None:
    row = conn.execute(
        "SELECT * FROM jobs WHERE canonical_url = ?", (job.canonical_url,)
    ).fetchone()
    if row is not None:
        return row
    return conn.execute(
        "SELECT * FROM jobs WHERE dedup_key = ?", (job.dedup_key,)
    ).fetchone()


def upsert_job(conn: sqlite3.Connection, job: Job) -> tuple[int, bool]:
    job.prepare()
    existing = _row_for(conn, job)
    if existing is not None:
        merged = Job.from_row(existing)
        merged.last_seen = utc_now()
        if job.description and not merged.description:
            merged.description = job.description
        if job.posted_at and not merged.posted_at:
            merged.posted_at = job.posted_at
        if job.deadline and not merged.deadline:
            merged.deadline = job.deadline
        if job.remote_type != "unknown" and merged.remote_type == "unknown":
            merged.remote_type = job.remote_type
        if job.language and not merged.language:
            merged.language = job.language
        with conn:
            conn.execute(
                "UPDATE jobs SET last_seen=?, description=?, posted_at=?, "
                "deadline=?, remote_type=?, language=? WHERE id=?",
                (
                    merged.last_seen,
                    merged.description,
                    merged.posted_at,
                    merged.deadline,
                    merged.remote_type,
                    merged.language,
                    merged.id,
                ),
            )
        return int(merged.id), False

    job.id = None
    placeholders = ", ".join("?" for _ in DB_COLUMNS)
    columns = ", ".join(DB_COLUMNS)
    values = tuple(getattr(job, name) for name in DB_COLUMNS)
    with conn:
        cursor = conn.execute(
            f"INSERT INTO jobs ({columns}) VALUES ({placeholders})", values
        )
    return int(cursor.lastrowid), True


def get_job(conn: sqlite3.Connection, job_id: int) -> Job | None:
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return Job.from_row(row) if row else None


def get_by_url(conn: sqlite3.Connection, url: str) -> Job | None:
    row = conn.execute("SELECT * FROM jobs WHERE canonical_url = ?", (url,)).fetchone()
    return Job.from_row(row) if row else None


def list_jobs(
    conn: sqlite3.Connection,
    status: str | None = None,
    limit: int | None = None,
) -> list[Job]:
    sql = "SELECT * FROM jobs"
    params: list = []
    if status:
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY first_seen DESC, id DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(limit)
    return [Job.from_row(row) for row in conn.execute(sql, params).fetchall()]


def counts_by_status(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT status, COUNT(*) AS total FROM jobs GROUP BY status"
    ).fetchall()
    return {row["status"]: int(row["total"]) for row in rows}


def set_status(
    conn: sqlite3.Connection,
    job_id: int,
    target: str,
    approval_token: str | None = None,
) -> Job:
    job = get_job(conn, job_id)
    if job is None:
        raise KeyError(f"job {job_id} not found")
    if not can_transition(job.status, target, approval_token):
        raise ValueError(f"illegal transition {job.status} -> {target}")
    with conn:
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (target, job_id))
    job.status = target
    return job


def set_feedback(conn: sqlite3.Connection, job_id: int, feedback: str) -> None:
    with conn:
        conn.execute("UPDATE jobs SET feedback = ? WHERE id = ?", (feedback, job_id))


def purge_older_than(
    conn: sqlite3.Connection,
    days: int,
    now: datetime | None = None,
) -> int:
    reference = now or datetime.now(timezone.utc)
    cutoff = (reference - timedelta(days=days)).replace(microsecond=0).isoformat()
    with conn:
        cursor = conn.execute(
            "DELETE FROM jobs WHERE last_seen < ? AND status != ?",
            (cutoff, Status.SUBMITTED.value),
        )
    return int(cursor.rowcount)


def record_scan_start(conn: sqlite3.Connection) -> int:
    with conn:
        cursor = conn.execute(
            "INSERT INTO scans (started_at, status) VALUES (?, 'running')",
            (utc_now(),),
        )
    return int(cursor.lastrowid)


def record_scan_finish(
    conn: sqlite3.Connection,
    scan_id: int,
    status: str = "ok",
    counts: dict[str, int] | None = None,
    errors: str = "",
) -> None:
    counts = counts or {}
    with conn:
        conn.execute(
            "UPDATE scans SET finished_at=?, status=?, fetched=?, new_count=?, "
            "duplicate_count=?, filtered_count=?, scored_count=?, "
            "shortlisted_count=?, llm_calls=?, errors=? WHERE id=?",
            (
                utc_now(),
                status,
                counts.get("fetched", 0),
                counts.get("new", 0),
                counts.get("duplicate", 0),
                counts.get("filtered", 0),
                counts.get("scored", 0),
                counts.get("shortlisted", 0),
                counts.get("llm_calls", 0),
                errors,
                scan_id,
            ),
        )


def set_source_health(
    conn: sqlite3.Connection,
    source: str,
    ok: bool,
    error: str = "",
) -> None:
    row = conn.execute(
        "SELECT consecutive_failures FROM source_health WHERE source = ?", (source,)
    ).fetchone()
    if ok:
        failures = 0
    elif row is not None:
        failures = int(row["consecutive_failures"]) + 1
    else:
        failures = 1
    degraded = 0 if ok else int(failures >= 3)
    with conn:
        conn.execute(
            "INSERT INTO source_health (source, last_success, last_error, "
            "consecutive_failures, degraded) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(source) DO UPDATE SET last_success=excluded.last_success, "
            "last_error=excluded.last_error, "
            "consecutive_failures=excluded.consecutive_failures, "
            "degraded=excluded.degraded",
            (
                source,
                utc_now() if ok else None,
                "" if ok else error,
                failures,
                degraded,
            ),
        )


def source_health(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM source_health ORDER BY source").fetchall()
    return [dict(row) for row in rows]

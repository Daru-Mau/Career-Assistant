"""Command line entry point for the jobs pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from . import config, db, filters, report
from .models import Status

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_DISABLED = 3
EXIT_LOCKED = 4

LOCK_STALE_SECONDS = 6 * 60 * 60
SOURCES: list = []


class Locked(RuntimeError):
    pass


@contextmanager
def acquire_lock(path: Path | None = None):
    target = path or config.lock_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    _clear_stale(target)
    try:
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise Locked(f"another run holds {target}") from exc
    try:
        os.write(fd, f"{os.getpid()} {time.time()}".encode())
        yield target
    finally:
        os.close(fd)
        try:
            target.unlink()
        except FileNotFoundError:
            pass


def _clear_stale(target: Path) -> None:
    if not target.exists():
        return
    try:
        content = target.read_text(encoding="utf-8").strip().split()
        started = float(content[1]) if len(content) > 1 else target.stat().st_mtime
    except (OSError, ValueError):
        started = target.stat().st_mtime
    if time.time() - started > LOCK_STALE_SECONDS:
        try:
            target.unlink()
        except FileNotFoundError:
            pass


def _guard() -> int | None:
    if config.is_disabled():
        print(
            "jobs pipeline disabled: unset JOBS_DISABLED or remove the STOP file",
            file=sys.stderr,
        )
        return EXIT_DISABLED
    return None


def _open_db(path: str | None):
    conn = db.connect(path)
    db.migrate(conn)
    return conn


def cmd_status(args: argparse.Namespace) -> int:
    conn = _open_db(args.db)
    try:
        counts = db.counts_by_status(conn)
        payload = {
            "repo": str(config.REPO_ROOT),
            "db_path": str(Path(args.db).expanduser() if args.db else config.db_path()),
            "schema_version": db.schema_version(conn),
            "disabled": config.is_disabled(),
            "stop_file": str(config.stop_file()),
            "lock_file": str(config.lock_file()),
            "discoveries_dir": str(config.discoveries_dir()),
            "sources_registered": [source.name for source in SOURCES],
            "counts": counts,
            "total": sum(counts.values()),
        }
    finally:
        conn.close()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return EXIT_OK


def cmd_scan(args: argparse.Namespace) -> int:
    guard = _guard()
    if guard is not None:
        return guard

    try:
        with acquire_lock() as lock_path:
            conn = _open_db(args.db)
            try:
                if args.dry_run:
                    print(
                        json.dumps(
                            {
                                "dry_run": True,
                                "lock": str(lock_path),
                                "sources_registered": [s.name for s in SOURCES],
                                "note": "Phase 0 has no source adapters",
                            },
                            indent=2,
                            sort_keys=True,
                        )
                    )
                    return EXIT_OK

                scan_id = db.record_scan_start(conn)
                counts = {
                    "fetched": 0,
                    "new": 0,
                    "duplicate": 0,
                    "filtered": 0,
                    "scored": 0,
                    "shortlisted": 0,
                    "llm_calls": 0,
                }
                db.record_scan_finish(conn, scan_id, status="ok", counts=counts)
                path = report.write_daily_report(
                    jobs=db.list_jobs(conn, status=Status.SHORTLISTED.value),
                    source_health=db.source_health(conn),
                    counts=counts,
                )
                report.JsonlLogger().log(
                    "scan_complete",
                    scan_id=scan_id,
                    sources=len(SOURCES),
                    counts=counts,
                    report=str(path),
                )
            finally:
                conn.close()
    except Locked as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_LOCKED

    print(json.dumps({"scan_id": scan_id, "report": str(path), "counts": counts}))
    return EXIT_OK


def cmd_purge(args: argparse.Namespace) -> int:
    guard = _guard()
    if guard is not None:
        return guard
    conn = _open_db(args.db)
    try:
        removed = db.purge_older_than(conn, args.days)
    finally:
        conn.close()
    report.JsonlLogger().log("purge", removed=removed, days=args.days)
    print(json.dumps({"removed": removed, "days": args.days}))
    return EXIT_OK


def cmd_report(args: argparse.Namespace) -> int:
    guard = _guard()
    if guard is not None:
        return guard
    conn = _open_db(args.db)
    try:
        jobs = db.list_jobs(conn, status=Status.SHORTLISTED.value)
        path = report.write_daily_report(
            jobs=jobs,
            source_health=db.source_health(conn),
            counts=db.counts_by_status(conn),
        )
    finally:
        conn.close()
    print(json.dumps({"report": str(path), "shortlisted": len(jobs)}))
    return EXIT_OK


def cmd_filters(args: argparse.Namespace) -> int:
    cfg = filters.FilterConfig(
        locations=tuple(args.location),
        remote_ok=not args.no_remote,
        languages=tuple(args.language),
        exclude_seniority=not args.allow_senior,
        max_age_days=args.max_age_days,
        blocklist=tuple(args.blocklist),
    )
    print(
        json.dumps(
            {
                "locations": list(cfg.locations),
                "remote_ok": cfg.remote_ok,
                "languages": list(cfg.languages),
                "exclude_seniority": cfg.exclude_seniority,
                "max_age_days": cfg.max_age_days,
                "blocklist": list(cfg.blocklist),
            },
            indent=2,
        )
    )
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobs")
    parser.add_argument("--db", help="override the SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show database and kill-switch state")
    status.set_defaults(func=cmd_status)

    scan = sub.add_parser("scan", help="run one discovery pass")
    scan.add_argument("--dry-run", action="store_true", help="check guards without writing")
    scan.set_defaults(func=cmd_scan)

    purge = sub.add_parser("purge", help="delete stale discovery records")
    purge.add_argument("--days", type=int, default=config.caps().retention_days)
    purge.set_defaults(func=cmd_purge)

    report_cmd = sub.add_parser("report", help="write the daily markdown report")
    report_cmd.set_defaults(func=cmd_report)

    filters_cmd = sub.add_parser("filters", help="print the active filter config")
    filters_cmd.add_argument("--location", action="append", default=[])
    filters_cmd.add_argument("--language", action="append", default=[])
    filters_cmd.add_argument("--blocklist", action="append", default=[])
    filters_cmd.add_argument("--no-remote", action="store_true")
    filters_cmd.add_argument("--allow-senior", action="store_true")
    filters_cmd.add_argument(
        "--max-age-days", type=int, default=config.caps().max_posting_age_days
    )
    filters_cmd.set_defaults(func=cmd_filters)

    return parser


def main(argv: list[str] | None = None) -> int:
    config.ensure_runtime_dirs()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())

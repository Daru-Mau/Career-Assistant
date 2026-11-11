"""Structured logs, redaction, and the daily discovery report."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from . import config
from .models import Job, utc_now

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\w)(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,5}\d{2,4}(?!\w)")
TOKEN_RE = re.compile(r"\b[A-Za-z0-9_-]{32,}\b")


def redact(text: str) -> str:
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    text = TOKEN_RE.sub("[token]", text)
    return text


class JsonlLogger:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _log_path()

    def log(self, event: str, **fields) -> None:
        record = {"ts": utc_now(), "event": event}
        record.update(fields)
        line = redact(json.dumps(record, ensure_ascii=False, sort_keys=True))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def _log_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return config.discoveries_dir() / f"run-{stamp}.jsonl"


def daily_report_path(day: date | None = None) -> Path:
    target = day or datetime.now(timezone.utc).date()
    return config.discoveries_dir() / f"{target.isoformat()}.md"


def write_daily_report(
    jobs: list[Job],
    source_health: list[dict] | None = None,
    flags: list[str] | None = None,
    counts: dict[str, int] | None = None,
    path: Path | None = None,
) -> Path:
    target = path or daily_report_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    counts = counts or {}
    source_health = source_health or []
    flags = flags or []

    lines = [f"# Job discovery report: {target.stem}", ""]
    lines.append("## Run summary")
    lines.append("")
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.append("")

    lines.append("## Shortlist")
    lines.append("")
    if not jobs:
        lines.append("No jobs shortlisted.")
    else:
        for job in jobs:
            reasons = job.score_reasons or "no reasons recorded"
            lines.append(f"### {job.title} at {job.company}")
            lines.append("")
            lines.append(f"- Score: {job.score if job.score is not None else 'n/a'}")
            lines.append(f"- Location: {job.location or 'unknown'}")
            lines.append(f"- Remote: {job.remote_type}")
            lines.append(f"- Language: {job.language or 'unknown'}")
            lines.append(f"- Deadline: {job.deadline or 'none'}")
            lines.append(f"- Source: {job.source}")
            lines.append(f"- Link: {job.url}")
            lines.append(f"- Reasons: {reasons}")
            lines.append("")

    lines.append("## Source health")
    lines.append("")
    if not source_health:
        lines.append("No sources configured yet.")
    else:
        lines.append("| Source | Last success | Failures | Degraded | Error |")
        lines.append("|---|---|---|---|---|")
        for row in source_health:
            lines.append(
                "| {source} | {last_success} | {consecutive_failures} | "
                "{degraded} | {last_error} |".format(
                    source=row.get("source", ""),
                    last_success=row.get("last_success") or "",
                    consecutive_failures=row.get("consecutive_failures", 0),
                    degraded=row.get("degraded", 0),
                    last_error=(row.get("last_error") or "").replace("|", "/"),
                )
            )
    lines.append("")

    lines.append("## Flags")
    lines.append("")
    if not flags:
        lines.append("None.")
    else:
        for flag in flags:
            lines.append(f"- {flag}")
    lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")
    return target

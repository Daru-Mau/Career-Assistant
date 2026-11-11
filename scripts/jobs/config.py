"""Runtime configuration, paths, caps, and the kill switch."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


def db_path() -> Path:
    return _env_path(
        "CAREER_JOBS_DB",
        Path.home() / ".local" / "share" / "career-assistant" / "jobs.db",
    )


def discoveries_dir() -> Path:
    return _env_path("CAREER_DISCOVERIES_DIR", REPO_ROOT / "discoveries")


def stop_file() -> Path:
    return _env_path("CAREER_STOP_FILE", REPO_ROOT / "STOP")


def lock_file() -> Path:
    return _env_path("CAREER_JOBS_LOCK", db_path().parent / "jobs.lock")


def sources_file() -> Path:
    return _env_path(
        "CAREER_JOB_SOURCES",
        REPO_ROOT / "scripts" / "jobs" / "job_sources.json",
    )


def secrets_dir() -> Path:
    return _env_path(
        "CAREER_SECRETS_DIR",
        Path.home() / ".config" / "career-assistant",
    )


def is_disabled() -> bool:
    if os.environ.get("JOBS_DISABLED", "").strip() not in ("", "0", "false", "False"):
        return True
    return stop_file().exists()


@dataclass(frozen=True)
class Caps:
    llm_reviews_per_day: int = 15
    prepare_per_day: int = 5
    submissions_per_day: int = 5
    retention_days: int = 90
    max_posting_age_days: int = 45
    max_application_age_days_per_company: int = 30


def caps() -> Caps:
    return Caps(
        llm_reviews_per_day=int(os.environ.get("JOBS_LLM_CAP", "15")),
        prepare_per_day=int(os.environ.get("JOBS_PREPARE_CAP", "5")),
        submissions_per_day=int(os.environ.get("JOBS_SUBMIT_CAP", "5")),
        retention_days=int(os.environ.get("JOBS_RETENTION_DAYS", "90")),
        max_posting_age_days=int(os.environ.get("JOBS_MAX_AGE_DAYS", "45")),
        max_application_age_days_per_company=int(
            os.environ.get("JOBS_COMPANY_COOLDOWN_DAYS", "30")
        ),
    )


def ensure_runtime_dirs() -> None:
    db_path().parent.mkdir(parents=True, exist_ok=True)
    discoveries_dir().mkdir(parents=True, exist_ok=True)
    secrets_dir().mkdir(parents=True, exist_ok=True)
    try:
        secrets_dir().chmod(0o700)
    except OSError:
        pass

"""Canonical job record and the enforced status machine."""

from __future__ import annotations

import enum
from dataclasses import dataclass, fields
from datetime import datetime, timezone

from . import normalize


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Status(str, enum.Enum):
    DISCOVERED = "discovered"
    FILTERED_OUT = "filtered_out"
    SCORED = "scored"
    SHORTLISTED = "shortlisted"
    REJECTED_BY_ME = "rejected_by_me"
    PREPARED = "prepared"
    AWAITING_APPROVAL = "awaiting_approval"
    AWAITING_MANUAL = "awaiting_manual"
    SUBMITTED = "submitted"
    FAILED = "failed"
    EXPIRED = "expired"


TRANSITIONS: dict[str, frozenset[str]] = {
    Status.DISCOVERED.value: frozenset(
        {
            Status.FILTERED_OUT.value,
            Status.SCORED.value,
            Status.EXPIRED.value,
            Status.FAILED.value,
        }
    ),
    Status.SCORED.value: frozenset(
        {
            Status.SHORTLISTED.value,
            Status.FILTERED_OUT.value,
            Status.REJECTED_BY_ME.value,
            Status.EXPIRED.value,
            Status.FAILED.value,
        }
    ),
    Status.SHORTLISTED.value: frozenset(
        {
            Status.REJECTED_BY_ME.value,
            Status.PREPARED.value,
            Status.AWAITING_MANUAL.value,
            Status.EXPIRED.value,
            Status.FAILED.value,
        }
    ),
    Status.PREPARED.value: frozenset(
        {
            Status.AWAITING_APPROVAL.value,
            Status.AWAITING_MANUAL.value,
            Status.REJECTED_BY_ME.value,
            Status.FAILED.value,
            Status.EXPIRED.value,
        }
    ),
    Status.AWAITING_APPROVAL.value: frozenset(
        {
            Status.SUBMITTED.value,
            Status.AWAITING_MANUAL.value,
            Status.REJECTED_BY_ME.value,
            Status.FAILED.value,
            Status.EXPIRED.value,
        }
    ),
    Status.AWAITING_MANUAL.value: frozenset(
        {
            Status.PREPARED.value,
            Status.AWAITING_APPROVAL.value,
            Status.SUBMITTED.value,
            Status.REJECTED_BY_ME.value,
            Status.FAILED.value,
            Status.EXPIRED.value,
        }
    ),
    Status.FAILED.value: frozenset(
        {
            Status.SCORED.value,
            Status.SHORTLISTED.value,
            Status.PREPARED.value,
            Status.AWAITING_MANUAL.value,
            Status.EXPIRED.value,
        }
    ),
    Status.SUBMITTED.value: frozenset(),
    Status.FILTERED_OUT.value: frozenset(),
    Status.REJECTED_BY_ME.value: frozenset(),
    Status.EXPIRED.value: frozenset(),
}


class IllegalTransition(ValueError):
    pass


def can_transition(current: str, target: str, approval_token: str | None = None) -> bool:
    if target not in TRANSITIONS.get(current, frozenset()):
        return False
    if target == Status.SUBMITTED.value and not approval_token:
        return False
    return True


def transition(job: "Job", target: str, approval_token: str | None = None) -> None:
    if not can_transition(job.status, target, approval_token):
        raise IllegalTransition(f"{job.status} -> {target} is not allowed")
    job.status = target


DB_COLUMNS = (
    "id",
    "source",
    "source_job_id",
    "url",
    "canonical_url",
    "company",
    "company_norm",
    "title",
    "title_norm",
    "location",
    "location_norm",
    "remote_type",
    "language",
    "description",
    "posted_at",
    "first_seen",
    "last_seen",
    "deadline",
    "employment_type",
    "salary_min",
    "salary_max",
    "currency",
    "score",
    "score_reasons",
    "status",
    "feedback",
    "blocked_reason",
    "dedup_key",
)


@dataclass
class Job:
    id: int | None = None
    source: str = ""
    source_job_id: str = ""
    url: str = ""
    canonical_url: str = ""
    company: str = ""
    company_norm: str = ""
    title: str = ""
    title_norm: str = ""
    location: str = ""
    location_norm: str = ""
    remote_type: str = "unknown"
    language: str = ""
    description: str = ""
    posted_at: str = ""
    first_seen: str = ""
    last_seen: str = ""
    deadline: str = ""
    employment_type: str = ""
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str = ""
    score: float | None = None
    score_reasons: str = ""
    status: str = Status.DISCOVERED.value
    feedback: str = ""
    blocked_reason: str = ""
    dedup_key: str = ""

    def prepare(self) -> "Job":
        if not self.company_norm:
            self.company_norm = normalize.normalize_company(self.company)
        if not self.title_norm:
            self.title_norm = normalize.normalize_title(self.title)
        if not self.location_norm:
            self.location_norm = normalize.normalize_location(self.location)
        if not self.canonical_url and self.url:
            self.canonical_url = normalize.canonical_url(self.url)
        if not self.dedup_key:
            self.dedup_key = normalize.dedup_key(
                self.company_norm, self.title_norm, self.location_norm
            )
        now = utc_now()
        if not self.first_seen:
            self.first_seen = now
        if not self.last_seen:
            self.last_seen = now
        return self

    def to_row(self) -> dict:
        self.prepare()
        return {name: getattr(self, name) for name in DB_COLUMNS}

    @classmethod
    def from_row(cls, row) -> "Job":
        values = {name: row[name] for name in DB_COLUMNS if name in row.keys()}
        return cls(**values)


def assert_known_status(value: str) -> str:
    if value not in {member.value for member in Status}:
        raise ValueError(f"unknown status: {value}")
    return value


ALL_STATUSES = tuple(member.value for member in Status)
JOB_FIELDS = tuple(field.name for field in fields(Job))

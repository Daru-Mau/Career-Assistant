"""Deterministic hard filters applied before any scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from . import normalize
from .models import Job

GRADUATE_PATTERNS = (
    "junior",
    "graduate",
    "entry level",
    "entry-level",
    "trainee",
    "intern",
    "internship",
    "werkstudent",
    "working student",
    "stage",
    "stagiaire",
    "tirocinio",
    "tirocinante",
    "berufseinsteiger",
    "apprentice",
    "apprenticeship",
    "0-2 years",
    "0 2 years",
    "no experience required",
)

SENIOR_PATTERNS = (
    "senior",
    "sr.",
    "sr ",
    "lead",
    "principal",
    "staff",
    "head of",
    "director",
    "manager",
    "expert",
    "architect",
    "10+ years",
    "8+ years",
    "7+ years",
    "6+ years",
    "5+ years",
)

SCAM_PATTERNS = (
    "pay a fee",
    "registration fee",
    "processing fee",
    "send money",
    "western union",
    "bitcoin",
    "crypto payment",
    "no experience needed high salary",
    "earn 5000",
    "earn 10000",
    "guaranteed income",
    "work from home and earn",
)

FREE_MAIL_DOMAINS = (
    "@gmail.com",
    "@yahoo.",
    "@hotmail.",
    "@outlook.",
    "@proton.me",
    "@protonmail.",
    "@wp.pl",
    "@o2.pl",
    "@libero.it",
    "@virgilio.it",
)

REMOTE_VALUES = {"remote", "fully remote", "telework", "telecommute", "zdalna"}


@dataclass(frozen=True)
class FilterConfig:
    locations: tuple[str, ...] = ()
    remote_ok: bool = True
    languages: tuple[str, ...] = ()
    exclude_seniority: bool = True
    accept_graduate: bool = True
    max_age_days: int = 45
    blocklist: tuple[str, ...] = ()
    scam_filter: bool = True


@dataclass
class FilterResult:
    allowed: bool
    reason: str = ""
    flags: list[str] = field(default_factory=list)


def parse_posted_at(value: str) -> date | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    for candidate in (text, text[:10]):
        try:
            return datetime.fromisoformat(candidate).date()
        except ValueError:
            continue
    return None


def is_graduate_title(title: str) -> bool:
    normalized = normalize.normalize_title(title)
    return any(pattern in normalized for pattern in GRADUATE_PATTERNS)


def is_senior_title(title: str) -> bool:
    normalized = normalize.normalize_title(title)
    return any(pattern in normalized for pattern in SENIOR_PATTERNS)


def detect_scam(job: Job) -> str:
    text = f"{job.title} {job.description}".lower()
    for pattern in SCAM_PATTERNS:
        if pattern in text:
            return f"scam_phrase:{pattern}"
    company = job.company_norm or normalize.normalize_company(job.company)
    if not company:
        return "missing_company"
    for domain in FREE_MAIL_DOMAINS:
        if domain in text:
            return f"free_mail_contact:{domain}"
    return ""


def _location_matches(job: Job, locations: tuple[str, ...]) -> bool:
    haystack = f"{job.location_norm} {normalize.normalize_location(job.description[:400])}"
    return any(location in haystack for location in locations)


def apply_hard_filters(
    job: Job,
    config: FilterConfig | None = None,
    now: date | None = None,
) -> FilterResult:
    config = config or FilterConfig()
    job.prepare()
    flags: list[str] = []

    if config.blocklist:
        company = job.company_norm
        for blocked in config.blocklist:
            if normalize.normalize_company(blocked) in company:
                return FilterResult(False, "company_blocklist", flags)

    if config.scam_filter:
        scam = detect_scam(job)
        if scam:
            return FilterResult(False, scam, flags)

    posted = parse_posted_at(job.posted_at)
    if posted is not None:
        reference = now or datetime.now(timezone.utc).date()
        if (reference - posted).days > config.max_age_days:
            return FilterResult(False, "stale", flags)

    if config.locations:
        remote = job.remote_type.lower() in REMOTE_VALUES
        if not _location_matches(job, config.locations):
            if not (config.remote_ok and remote):
                return FilterResult(False, "location", flags)

    if config.languages and job.language:
        if job.language.lower() not in {lang.lower() for lang in config.languages}:
            return FilterResult(False, "language", flags)

    if config.exclude_seniority and is_senior_title(job.title):
        if not (config.accept_graduate and is_graduate_title(job.title)):
            return FilterResult(False, "seniority", flags)

    if job.deadline:
        deadline = parse_posted_at(job.deadline)
        reference = now or datetime.now(timezone.utc).date()
        if deadline is not None and deadline < reference:
            return FilterResult(False, "deadline_passed", flags)

    return FilterResult(True, "", flags)

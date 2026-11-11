"""Submission interface. Implementations arrive in a later phase."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


class SubmissionError(RuntimeError):
    pass


class ApprovalRequired(SubmissionError):
    pass


class AwaitingManual(SubmissionError):
    pass


@dataclass
class Draft:
    job_id: int
    channel: str
    recipient: str = ""
    subject: str = ""
    body: str = ""
    attachments: list[Path] = field(default_factory=list)
    fields: dict = field(default_factory=dict)


@dataclass
class ScreenshotReport:
    path: Path | None
    notes: str = ""
    blocked_fields: list[str] = field(default_factory=list)


@dataclass
class Receipt:
    job_id: int
    channel: str
    submitted_at: str
    confirmation_id: str = ""
    document_hashes: dict[str, str] = field(default_factory=dict)
    audit_path: Path | None = None


class Submitter(ABC):
    channel: str = "base"

    @abstractmethod
    def can_handle(self, job) -> bool:
        raise NotImplementedError

    @abstractmethod
    def prepare(self, job) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def dry_run(self, draft: Draft) -> ScreenshotReport:
        raise NotImplementedError

    @abstractmethod
    def submit(self, draft: Draft, approval_token: str) -> Receipt:
        raise NotImplementedError

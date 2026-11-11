"""Source adapter contract for job discovery."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable

from ..models import Job


class SourceError(RuntimeError):
    pass


@dataclass
class SourceQuery:
    keywords: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    remote: bool = False
    limit: int = 100


@dataclass
class RawJob:
    source: str
    url: str
    company: str
    title: str
    source_job_id: str = ""
    location: str = ""
    description: str = ""
    posted_at: str = ""
    deadline: str = ""
    employment_type: str = ""
    remote_type: str = "unknown"
    language: str = ""
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str = ""
    extra: dict = field(default_factory=dict)

    def to_job(self) -> Job:
        return Job(
            source=self.source,
            source_job_id=self.source_job_id,
            url=self.url,
            company=self.company,
            title=self.title,
            location=self.location,
            description=self.description,
            posted_at=self.posted_at,
            deadline=self.deadline,
            employment_type=self.employment_type,
            remote_type=self.remote_type,
            language=self.language,
            salary_min=self.salary_min,
            salary_max=self.salary_max,
            currency=self.currency,
        ).prepare()


class SourceAdapter(ABC):
    name: str = "base"
    official: bool = False
    requests_per_second: float = 1.0

    @abstractmethod
    def fetch(self, query: SourceQuery) -> Iterable[RawJob]:
        raise NotImplementedError

    def normalize(self, raw: RawJob) -> Job:
        return raw.to_job()

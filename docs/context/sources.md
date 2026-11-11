# Job Sources

Approved discovery sources for `scripts/jobs/`. Every adapter must have an entry
here before it is enabled. Record terms, attribution, and the date they were
last checked. When a term is unclear, default to the conservative reading and
flag it.

| Source | Focus | Access | Official | Auth | Phase | Status |
|---|---|---|---|---|---|---|
| Greenhouse | Company ATS | Public board API | Yes | None | 1a | Approved, adapter pending |
| Lever | Company ATS | Public postings API | Yes | None | 1a | Approved, adapter pending |
| EURES | EU-wide (IT/DE/PL/remote) | Job Vacancy API | Yes | Registration may be required | 1a | Approved, terms/endpoint to verify |
| Adzuna | IT/DE/PL + remote | Official API, free tier | Yes | API key | 1b | Approved, key and attribution required |
| Arbeitsagentur | Germany | Public JSON | Community | `X-API-Key: jobboerse-jobsuche` | 1b | Approved, undocumented endpoint |
| JustJoin.it | Poland/CEE tech | Public JSON | Community | None observed | 1b | Approved, undocumented endpoint |
| NoFluffJobs | Poland/CEE tech | Public JSON search | Community | None observed | 1b | Approved, undocumented endpoint |
| Arbeitnow | Remote-native | Public API | Yes | None | 1b | Approved, adapter pending |
| Remotive | Remote-native | Public API | Yes | None | 1b | Approved, adapter pending |
| RemoteOK | Remote-native | Public API | Yes | None | 1c | Approved, adapter pending |
| Himalayas | Remote-native | Public API | Yes | None | 1c | Approved, adapter pending |
| Welcome to the Jungle / Otta | EU tech/startups | TBD | TBD | TBD | 1c | Verify API and terms before adding |
| Ashby | Company ATS | Public feed | Yes | None | 2/3 | Approved, Phase 2/3 |
| Workable | Company ATS | Public feed | Yes | None | 2/3 | Approved, Phase 2/3 |
| SmartRecruiters | Company ATS | Public API | Yes | None | 2/3 | Approved, Phase 2/3 |
| Personio | Company ATS | Public feed | Yes | None | 2/3 | Approved, Phase 2/3 |
| Recruitee | Company ATS | Public API | Yes | None | 2/3 | Approved, Phase 2/3 |
| EURAXESS | PhD/academia | Feed/API | Mixed | TBD | 3 | Approved, Phase 3 |
| University RSS and group pages | PhD/academia | RSS/HTML | Mixed | None | 3 | Approved, robots.txt respected |
| LinkedIn | IT/DE/PL/remote | Email alerts only | No public job API | Mailbox | 4 | Approved, no direct scraping |
| Indeed | IT/DE/PL/remote | Email alerts only | No public job search API | Mailbox | 4 | Approved, no direct scraping |
| Glassdoor | IT/DE/PL/remote | Email alerts only | No public job API | Mailbox | 4 | Approved, no direct scraping |

## Excluded

| Source | Reason |
|---|---|
| InfoJobs Italia | Closed permanently at the end of 2025 |
| Pracuj.pl, StepStone, Subito, Bakeca, Jobrapido | HTML scraping only; deferred by decision |

## Per-source checklist

- Access method and base endpoint
- Official or community status
- Authentication and secret location
- Rate limit and backoff policy
- Attribution or redistribution requirement
- robots.txt status for scraping
- Language of returned data
- Last verified date

## Notes

- Community endpoints (Arbeitsagentur, JustJoin.it, NoFluffJobs) are
  undocumented and may change without notice. They are marked `community`,
  rate-limited conservatively, and covered by source health alerts.
- LinkedIn, Indeed, and Glassdoor are consumed only through saved-search email
  alerts parsed over IMAP. No logged-in scraping and no Easy Apply automation.
- Every new source requires explicit approval before an adapter is enabled.

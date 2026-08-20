# Known Errors

Gotchas inferred from the repo. They are observations, not confirmed bugs.

## Tracker file states (resolved)

- CSV is the source of truth. JobTracker.xlsx is a manual export, JobTracker_backup.xlsx is a fallback, and JobTracker.xlsm is outdated from a previous iteration, not part of the current flow.
- AGENTS.md used to reference tracking/JobTracker.xlsm but now points to tracking/JobTracker.csv, matching tracking/README.md and .opencode/commands/mark-applied.md.

## Status enum (resolved)

- application.yaml uses `preparation | applied | interview | offer | rejected | withdrawn` (template, lowercase). The tracker Status column uses its own set: `Applied | Rejected | Interview Scheduled | Withdrawn | No Response`. The two are different enums by design (yaml = lifecycle stage, tracker = outcome). prepare-application.md sets `status: preparation`, mark-applied.md sets `status: applied`; AGENTS.md, the template, and both commands now agree on the lowercase yaml enum. Post-submission outcomes are mirrored into both files by /update-status (AGENTS.md Stage 4).

## The 6-file invariant and generated outputs

- Applications contain 6 authored artifacts (analysis.md, fit_assessment.md, cv_changes.md, cover_letter.md, interview_topics.md, application.yaml) plus 4 build outputs produced by scripts/build_cv.py (<cv_stem>.html, <cv_stem>.pdf, <cl_stem>.html, <cl_stem>.pdf). The build outputs are generated, never hand-edited.
- Occasionally extra hand-written files appear (e.g. a stray `*.docx` export next to the PDFs). The convention allows 6 authored artifacts; extra files are tolerated but undocumented.

## Language rule sharp edges

- AGENTS.md mandates writing in the job description's language. Mixed-language sources (a posting in one language, a profile in another) can produce language inconsistencies if not checked in the review phase.
- Tracker titles may be non-English alongside English; column values are not language-normalized.

## CV quirks (watch for these in new profiles)

- Keep the "About me" a real summary; it can read like internal decision text if copied from planning notes.
- Keep skill separators consistent; repeat skill tokens (e.g. Unity, C#) across project and group lists.
- Use one project date format across entries.

## Profile files risks

- A grades/transcript file can be saved with a non-UTF-8 encoding (e.g. UTF-16) and be read as binary by tools expecting UTF-8; convert it to UTF-8.
- LinkedIn direct scraping can return HTTP 999; profile facts must come from web-search caches or user-pasted exports.

## Documentation drift (mostly resolved)

- application_workflow.md Phase 2 and README.md playbook examples aligned to actual playbooks/ filenames.
- AGENTS.md references .opencode/commands/prepare-application.md for cv_changes.md instructions, which exists; but AGENTS.md also says cover letter "max three paragraphs" while templates/cover_letter.md defines 3 paragraph placeholders, consistent.

## Pending

- (none)

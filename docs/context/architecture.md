# Architecture

## What this is

A markdown knowledge base for job applications. No code runtime, no tests, no build. The "engine" is opencode itself, driven by markdown instructions and commands.

## Stack

- Markdown (.md) as the storage format everywhere
- YAML metadata (application.yaml per application)
- CSV as tracker source of truth, XLSX as formatted export
- opencode: AGENTS.md (global instructions) + .opencode/commands/*.md (custom commands)
- Node only inside .opencode/node_modules (plugin dependency for @opencode-ai/plugin), not part of the data model

## Folder map

| Folder | Purpose |
|---|---|
| `profile/` | Single source of truth: master CV, thesis, grades, profile index, certs to-do, LinkedIn plan |
| `playbooks/` | Role-specific tailoring guidance (robotics, phd, hci, data_science, software_engineer, hospitality, retail, entry_level) |
| `templates/` | Fill-in skeletons for every generated artifact |
| `job_offers/<company-role>/` | Original job descriptions, one folder per application |
| `applications/<group>/<created>-<company-role>/` | Generated materials (analysis, fit, cv_changes, cover letter, interview topics, yaml); physically sorted by status group + generation date |
| `tracking/` | Historical application database: JobTracker.csv (source of truth), .xlsx (export), backup |
| `comparisons/` | Request-only side-by-side offer comparisons, one file per comparison; never edits tracker or application folders |
| `docs/context/` | This context pack |
| `.opencode/commands/` | review-job, prepare-application, mark-applied, update-status, discard-application |

## Data flow

1. User pastes job description
2. `/review-job` analyzes fit WITHOUT creating files
3. User approves
4. `/prepare-application` creates `job_offers/<company-role>/job_description.md` and `applications/01-preparing/<created>-<company-role>/` with 6 artifacts, then runs `scripts/build_cv.py` to generate `<cv_stem>.pdf` and `<cl_stem>.pdf`
5. User confirms submission
6. `/mark-applied` updates `application.yaml` (status: applied), inserts a row at the top of `JobTracker.csv` (newest-first), and moves the folder from `01-preparing/` to `02-applied/`
7. User reports an outcome; `/update-status` mirrors it in `application.yaml` (status) + `JobTracker.csv` (Status) together, and moves the folder to `03-closed/` when the outcome is rejected or withdrawn
8. `/discard-application` (optional) removes unsubmitted folders from `01-preparing/`, or marks a submitted row as Withdrawn (moving it to `03-closed/`) when the user decides not to pursue the role

## What does NOT exist

- No CI/CD, no automated tests, no linting, no package manager runtime (script dependencies are Python standard library + pymupdf)
- No automation beyond opencode commands (except scripts/build_cv.py, which renders HTML and PDFs via Edge headless)
- No database, no API, no frontend
- Optional git repository; if published, .gitignore keeps profile/, applications/, job_offers/, tracking/, comparisons/, career_preferences.md and config.json private
- No cover letter template for some roles; templates/cover_letter_template.html serves every application and templates/cover_letter.md is always authored and rendered

## Tracker files

- `JobTracker.csv` — source of truth, the only file edited programmatically
- `JobTracker.xlsx` — formatted export, refreshed manually (target name; not currently present — see tracking/README.md)
- `JobTracker_backup.xlsx` — fallback export, the only Excel artifact present today
- `JobTracker.xlsm` — outdated, created in a previous iteration, not used

## Pending

- [RESOLVED: .opencode/.gitignore contents] inspected 31/07/2026: ignores node_modules, package.json, package-lock.json, bun.lock, .gitignore. A @opencode-ai/plugin dependency exists in package.json but no plugin is configured in opencode.json; currently inert.

# Career Assistant

A structured, opencode-driven knowledge base for managing your professional profile and generating tailored job applications.

The repo is published as a **reusable template**: it ships with the workflow, templates, playbooks, and PDF build tooling, but no personal data. Each person clones it, drops in their own profile, and the same commands produce their applications.

## Philosophy

Every application is generated from the same factual source of truth. Nothing is invented. Role-specific emphasis changes; facts stay consistent.

## How it works

The repository is a markdown knowledge base. There is no runtime or build server; the "engine" is opencode itself, driven by the commands in `.opencode/commands/` and the instructions in `AGENTS.md` plus `docs/context/`.

```
profile/        Your facts (base CV, thesis, grades, preferences) - PRIVATE, gitignored
playbooks/      Role-specific tailoring guidance (software_engineer, robotics, ...)
templates/      Fill-in skeletons for every generated artifact
scripts/        build_cv.py - renders CV + cover letter HTML and converts to PDF via Edge
job_offers/     Original job descriptions, one folder per application - PRIVATE
applications/   Generated materials for each application - PRIVATE
tracking/       Application history (JobTracker.csv) - PRIVATE
comparisons/    Side-by-side offer comparisons - PRIVATE
docs/context/   This pack of instructions opencode loads every session
.opencode/      Commands that drive the workflow
```

Anything under `profile/`, `job_offers/`, `applications/`, `tracking/`, and `comparisons/` is **gitignored**. Your personal data and application history are never published or shared.

## Setup (first time)

1. **Copy the config:**
   ```bash
   cp config.example.json config.json
   ```
   Then edit `config.json` with your values and save it. `config.json` is gitignored, so it stays private. Fields:
   - `name` - your full name (used as the fallback header and cover-letter signoff)
   - `base_cv_file` - the filename of your base CV inside `profile/` (e.g. `your_name_cv.md`)
   - `cv_stem` / `cl_stem` - output names for your CV and cover letter (e.g. `YourName_cv`, `YourName_cl`)
   - `work_email` / `phd_email` - the `+work` / `+phd` mailbox aliases used per-application

2. **Add your profile files** in `profile/`:
   - your base CV (see `templates/base_cv.example.md` for the required section layout)
   - your thesis document (if relevant to your target roles)
   - your academic grades / transcript
   - `profile_index.md` describing which files to consult
   - `career_preferences.md` with your goals, geography, and preferences
   Copy any you want from your own machine; the structure is: `profile/<base_cv_file>` is the single source of truth that `build_cv.py` reads.

3. **Install the build dependencies:**
   - Microsoft Edge (default for the PDF conversion)
   - `pymupdf` on the Python you use to build: `python -m pip install pymupdf`

4. **Set your identity everywhere from one place:** all person-specific values (name, base CV file, PDF stems, email aliases) are read from `config.json`. The markdown instructions and build script reference `config.json`, so editing that one file is all you need after setup.

## Workflow

The flow is driven by opencode commands, run inside the repo:

| Command | What it does |
|---|---|
| `/review-job` | Analyzes a job description against your profile, creates nothing |
| `/prepare-application` | Creates `job_offers/<company-role>/` and `applications/<company-role>/`, writes 6 artifacts, builds the PDFs |
| `/mark-applied` | Updates `application.yaml` and adds a row to `tracking/JobTracker.csv` after you confirm submission |
| `/update-status` | Mirrors an outcome (rejected, interview, offer, withdrawn) into `application.yaml` and the tracker |
| `/discard-application` | Removes unsubmitted application folders, or marks a submitted row as Withdrawn |

The three gates are strict: review creates nothing, preparation does not touch the tracker, and the tracker is only updated on explicit submission confirmation.

Steps for a typical application:

1. Paste a job description and run `/review-job`.
2. Decide to proceed, then run `/prepare-application` to generate analysis, fit assessment, CV changes, cover letter, interview topics, and the YAML metadata, running `python scripts/build_cv.py <company-role>` to produce your CV + cover letter PDFs.
3. Confirm you submitted, then run `/mark-applied`.
4. Report outcomes as they happen and run `/update-status`.

## Design principles

- Single source of truth (the `profile/` base CV; `tracking/JobTracker.csv` for history)
- Separates facts from application-specific material
- Template-driven, consistent output
- Honest representation: never invent roles, dates, grades, or metrics
- Version-controlled, reusable, private-by-default

## Privacy note

Because `.gitignore` excludes them by default, the shared repo contains no personal information. When you publish, double-check with `git status` that only the template files, commands, playbooks, templates, scripts, config example, and docs are tracked, and that `config.json`, `profile/`, `applications/`, `job_offers/`, `tracking/`, and `comparisons/` are not.

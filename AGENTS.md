# Language

Detect the language of the job description. All generated files, modifications, and communications must be written in the same language as the job description. Set the `language` field in `application.yaml` accordingly (e.g. `Italian`, `English`, `German`). If the job description is in Italian, write everything in Italian.

---

# Writing Guidelines

Application materials must sound human, not generated. AI-rejection is rarely about AI itself; it is about content that looks and sounds like AI. Avoid anything that gives the writing away as generic.

## Prohibited Words

Never use these vague phrases in CVs, cover letters, or any application material:

- Results-driven
- Strategic thinker
- Proven track record
- Team player
- Responsible for
- Worked on
- Assisted with

They sound good but say nothing.

## Prohibited Formatting

- No long dashes (like this — or this –) scattered across documents
- No random bold words mid-sentence
- No overly "perfect" spacing or structure
- No sentences that are too polished and too long

## Required Style

- Write experience first (messy is fine); refine afterwards
- Keep formatting simple and consistent
- Bold only section headers, never random words
- Use normal punctuation, no fancy dashes
- Prefer specific, concrete statements over vague ones
- Write skill tokens in Title Case (e.g. Real-Time Systems, not real-time systems); lowercase tokens trigger a build warning and a rebuild cycle

## Specific Over Vague

Replace vague phrasing with quantified results:

- Instead of: "Responsible for project delivery"
  Say: "Led 3 cross-functional projects, reducing delivery time by 20%"
- Instead of: "Worked on clinical studies"
  Say: "Managed Phase II study across 5 sites, improving patient recruitment by 30%"

Every claim must be real. Never invent metrics, roles, dates, or results.

---

# Application Lifecycle

Job opportunities follow three different stages:

## Stage 1 — Review

Triggered when the user shares a job description without explicitly requesting an application.

Purpose:

Evaluate whether the opportunity is worth pursuing.

Actions:

- Analyze the job description.
- Compare against the profile.
- Identify strengths.
- Identify gaps.
- Extract ATS keywords.
- Estimate fit.

Do NOT:

- create application folders
- save the job description
- modify the tracker
- generate final application materials

Output:

Provide a review and recommendation.

---

## Interest & Fit Assessment

Before marking an application as prepared or applied, ask the user to rate their interest level from:

- **Top Choice** — high priority, actively pursuing
- **Consider** — open to it, not prioritizing
- **Low Interest** — backup / low commitment

After the user responds, also assign a **Fit Score** (your objective assessment of how well the profile matches the role, X/10).

Record these values in the tracker:
- `Priority Level` column stores the user's interest level
- `Fit Score (x/10)` column stores your assessment (e.g. 4)
- `Salary` and `Currency` columns store the compensation if known

---

## Stage 2 — Prepare Application

Triggered only when the user explicitly requests preparation.

Examples:

- "Prepare this application"
- "Create the application"
- "Proceed with this role"

Actions:

Create:

job_offers/<company-role>/
applications/<group>/<created>-<company-role>/

Save:

job_offers/<company-role>/job_description.md

Generate:

applications/<group>/<created>-<company-role>/

The application folder lives inside a status group:

- `01-preparing/` for status `preparation`
- `02-applied/` for `applied | interview | offer`
- `03-closed/` for `rejected | withdrawn`

`<created>` is the generation date from `application.yaml` (YYYY-MM-DD). It keeps the folder stable; only the group changes as the status moves. Within a group, folders sort by the YYYY-MM-DD name prefix (chronological, newest-first when sorted by name descending in a file explorer).

### analysis.md

Job summary table, responsibilities, required vs preferred skills table, ATS keywords, company observations.

### fit_assessment.md

Overall match score X/10, strengths table, partial matches table, genuine gaps table with severity + mitigation, recommendation.

### cv_changes.md

Instructions in .opencode/commands/prepare-application.md

Before authoring cv_changes.md, read .opencode/commands/cv-format-reference.md. Do not read build_cv.py or cv_template.html.

### cover_letter.md

Professional tone, max three paragraphs, avoids repeating CV. Role-specific, not generic.

### interview_topics.md

Technical topics, behavioral questions, relevant projects to reference, concepts to review (checklist), questions for interviewers.

### application.yaml

Metadata:

company:
role:
location:
status: preparation
match_score:
language:
playbooks:
  - {{ PLAYBOOK_1 }}  # e.g. software_engineer.md, robotics.md, phd.md, hci.md, data_science.md, hospitality.md, retail.md, entry_level.md
created: {{ YYYY-MM-DD }}  # must match the date prefix used in the folder name
last_updated:

### <cv_stem>.pdf + <cl_stem>.pdf

After the six application files above are written, run the build script to generate the printable PDFs:

python.exe scripts/build_cv.py "<group>/<created>-<company-role>"

The stems and the base CV filename come from `config.json` (`cv_stem`, `cl_stem`, `base_cv_file`). The script reads profile/<base_cv_file> (facts) and applications/<group>/<created>-<company-role>/cv_changes.md (tailoring), renders <cv_stem>.html and <cl_stem>.html, converts both to PDF with Edge headless, and verifies them with PyMuPDF (page count soft limit, no leftover placeholders).

Do NOT update the application tracker yet.

The application is considered:

Status: Preparation

---

## Stage 3 — Mark Applied

Triggered only when the user explicitly confirms submission.

Examples:

- "I applied"
- "Mark this as submitted"
- "Update my tracker"

Actions:

1. Update:

tracking/JobTracker.csv

Insert the new row at the top of the data rows (below the header), keeping the tracker sorted newest-first by Date Applied.

2. Update:

applications/<group>/<created>-<company-role>/application.yaml

with:

status: applied
date_applied: YYYY-MM-DD  # canonical format in application.yaml; M/D/YYYY is used only in JobTracker.csv

3. Relocate the folder to the group matching the new status (from `01-preparing/` to `02-applied/`):

applications/02-applied/<created>-<company-role>/

Never assume an application was submitted.

---

## Stage 4 — Post-Submission Status Changes

Triggered when the user reports an outcome for a submitted application: rejected, interview, offer, or withdrawal.

Examples:

- "They rejected me"
- "I got an interview"
- "I received an offer"
- "I'm withdrawing this one"

Both files must always mirror the same outcome. Never update one without the other:

1. Update:

applications/<group>/<created>-<company-role>/application.yaml

set status (lowercase enum) and bump last_updated:

- rejected
- interview
- offer
- withdrawn

2. Update:

tracking/JobTracker.csv

set the Status column of that row, reusing existing dropdown values (Rejected, Interview Scheduled, Withdrawn; keep the row in place, do not reorder or delete it):

- rejected -> Rejected
- interview -> Interview Scheduled
- offer -> keep Applied until accepted, then record manually
- withdrawn -> Withdrawn

3. Relocate the folder to the group matching the new status:

- rejected, withdrawn -> `applications/03-closed/<created>-<company-role>/`
- interview, offer -> stays in `applications/02-applied/`

Only update status after the user explicitly states the outcome. Never guess from silence.

---

# Application Commands

Supported commands:

## /review-job

Analyze a job offer without creating files.

## /prepare-application

Create application materials after the user decides to proceed.

## /mark-applied

Update tracking after the user confirms submission.

## /update-status

Mirror a reported outcome (rejected, interview, offer, withdrawn) into both application.yaml and the tracker.

## /discard-application

Cleanly discard a job review or prepared application after the user decides not to apply (or could not apply). Deletes unsubmitted application folders; refuses to delete submitted applications and treats those as withdrawals.

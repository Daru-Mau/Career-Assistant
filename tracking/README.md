# Application Tracking

## Purpose

This folder contains the user's job application tracking system.

The application tracker is used to maintain historical information about:

- submitted applications
- application status
- interview progress
- outcomes
- company history
- role targeting patterns

The tracker complements the `applications/` directory:

- `applications/` contains generated analysis and application materials.
- `tracking/` contains the historical database of applications.

---

## Files

| File | Role | Updated by |
|---|---|---|
| `JobTracker.csv` | **Source of truth** — machine-writable, programmatic updates | opencode |
| `JobTracker.xlsx` | **Formatted export** — human-readable with colors and table formatting | User (manual refresh from CSV) |
| `JobTracker_backup.xlsx` | Fallback if the XLSX export needs to be rebuilt | Generated automatically |

Note on current state: only `JobTracker.csv` and `JobTracker_backup.xlsx` exist right now. `JobTracker.xlsx` is the intended manual-export name and will appear once the export is refreshed; the backup doubles as the only current Excel artifact until then.

### CSV (source of truth)

`JobTracker.csv` is the primary file that opencode modifies when marking applications as submitted. It is safe to edit programmatically because CSV is a simple text format with no binary layout, macros, or formatting to corrupt.

### XLSX (formatted export)

`JobTracker.xlsx` is the formatted version with:

- table structure
- conditional formatting (status colors)
- column widths and alignment
- dropdown reference rows (choices section)

To refresh the XLSX after opencode updates the CSV:

1. Open `JobTracker.csv` in Excel.
2. Select the data range (columns A–K).
3. Apply the same table style and conditional formatting as before.
4. Save as `JobTracker.xlsx`.

---

## Column Structure

Both CSV and XLSX use the same 11 columns in the Job Details section:

| # | Column | Description |
|---|---|---|
| A | Company Name | Employer name |
| B | Position | Role title |
| C | Role | Employment type (Full-Time, Part-Time, Internship) |
| D | Modality | On-Site, Remote, Hybrid |
| E | Priority Level | Top Choice, Consider, Low interest |
| F | Salary | Compensation (optional) |
| G | Location | City, Country |
| H | Job Listing | URL or source (optional) |
| I | Date Applied | Date in M/D/YYYY format |
| J | Application Method | LinkedIn, Email, Indeed, etc. |
| K | Status | Applied, Rejected, Interview Scheduled, Withdrawn, No Response |

The top section (rows 1–10) contains reference data with dropdown choices.

---

## Tracker Update Rules

The tracker only contains applications that have actually been submitted.

Do not add:

- reviewed jobs
- rejected opportunities
- saved opportunities
- draft applications

A job enters the tracker only after the user confirms submission.

## Row Ordering

Data rows are sorted newest-first by Date Applied (most recent application at the top, directly below the header). New rows are inserted at the top, not appended at the bottom. When dates are equal, the relative order of existing rows is preserved.

---

## Workflow Integration

This tracker integrates with the command-based workflow defined in AGENTS.md and .opencode/commands/:

- **review-job** — evaluates fit, does not touch the tracker
- **prepare-application** — creates workspace and materials, does not touch the tracker
- **mark-applied** — updates application.yaml + adds a row to JobTracker.csv
- **discard-application** — deletes unsubmitted application folders, or sets an applied row's Status to Withdrawn (never deletes tracked applications)

A job enters the tracker only after the user explicitly confirms submission (mark-applied).

---

## Relationship Between Files

tracking/
├── JobTracker.csv          (source of truth — updated by opencode)
├── JobTracker.xlsx         (formatted export — refresh from CSV)
└── JobTracker_backup.xlsx  (fallback)

job_offers/
└── <company-role>/
    └── job_description.md

applications/
└── <company-role>/
    ├── analysis.md
    ├── fit_assessment.md
    ├── cv_changes.md
    ├── cover_letter.md
    ├── interview_topics.md
    ├── application.yaml
    ├── <cv_stem>.html
    ├── <cv_stem>.pdf
    ├── <cl_stem>.html
    └── <cl_stem>.pdf

The tracker provides the overview.
The application folder contains the details.

> Note: the data files in this folder (JobTracker.csv, JobTracker_*.xlsx) are
> gitignored — they hold private application history. This README is kept in
> version control as documentation of the tracker format.

---
description: Mark an application as submitted and update tracking
---

The user has explicitly confirmed that they submitted an application.

Update the application status according to AGENTS.md.

Before updating, consult:

- **tracking/README.md** — column structure, CSV as source of truth, update rules
- **templates/application.yaml** — fields to update (status, date_applied, fit_score, salary, currency)
- **career_preferences.md** — salary benchmarks to populate tracker columns

Actions:

1. Locate the correct application folder:

applications/<group>/<created>-<company-role>/

It should currently live in `01-preparing/`. To find it, derive the `<company-role>` leaf (lowercase-hyphenated company + role, e.g. "NTT DATA Junior Cybersecurity System Engineer" becomes ntt-data-junior-cybersecurity-system-engineer) and glob for `applications/*/*-<company-role>` (any group, any `<created>` prefix).

2. Update:

application.yaml

Set:

status: applied

Add:

date_applied: YYYY-MM-DD  # canonical format in application.yaml (M/D/YYYY is only used in JobTracker.csv)

3. Update tracking source of truth (CSV, not XLSX):

tracking/JobTracker.csv

Insert a new row at the TOP of the data rows (directly below the header, row 3), matching the column order in the header (row 2). Rows are kept sorted newest-first by Date Applied, so new applications always go first. If the spreadsheet is found unsorted, re-sort all data rows by Date Applied descending before adding the new one.

- Company Name
- Position
- Role (Full-Time / Part-Time / Internship)
- Modality (On-Site / Remote / Hybrid)
- Priority Level (Top Choice / Consider / Low interest)
- Fit Score (x/10) — from application.yaml fit_score
- Salary — from application.yaml salary
- Currency — from application.yaml currency
- Location (City, Country)
- Job Listing (URL if known)
- Date Applied (today in M/D/YYYY)
- Application Method (LinkedIn / Email / Indeed / etc.)
- Status (Applied)

4. Relocate the folder to the group matching the new status (from `01-preparing/` to `02-applied/`):

applications/02-applied/<created>-<company-role>/

Rules:

- Only update the tracker after explicit user confirmation.
- Never assume that preparation means submission.
- CSV is the source of truth — update JobTracker.csv, not JobTracker.xlsx.
- Preserve CSV header row and column order.
- Reuse existing dropdown values and categories.
- For later outcome changes (rejected, interview, withdrawal), use /update-status so application.yaml and the tracker stay in sync.

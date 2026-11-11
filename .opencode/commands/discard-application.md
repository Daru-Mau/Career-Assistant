---
description: Cleanly discard a job review or prepared application the user decided not to pursue
---

The user has decided not to pursue an application (or could not apply) and wants it removed cleanly.

Locate the application by the folder name the user provides (applications/<group>/<created>-<company-role>/). If the user only gave the company and role, derive the `<company-role>` leaf using the lowercase-hyphenated convention (e.g. "Atlante AI Engineer Intern" becomes atlante-ai-engineer-intern), then glob for `applications/*/*-<company-role>` (any group, any `<created>` prefix).

Before acting, consult:

- **tracking/README.md** — tracker rules, Status dropdown values, CSV as source of truth
- **templates/application.yaml** — status field values
- **tracking/JobTracker.csv** — whether the application already has a row

Determine the stage and act accordingly:

## 1. Review stage (no folders exist for this role)

- review-job creates nothing, so there is nothing to delete.
- Confirm to the user that the opportunity is simply dropped and that no files or tracker rows exist.
- Do not create, modify, or delete anything.

## 2. Preparation stage (applications/01-preparing/<created>-<company-role>/ exists and application.yaml has status: preparation)

- This application was never submitted, so it has no tracker row.
- Confirm the deletion with the user before proceeding.
- Delete job_offers/<company-role>/ and applications/01-preparing/<created>-<company-role>/ (whichever exist).
- Do NOT touch tracking/JobTracker.csv.

## 3. Applied stage (a row exists in tracking/JobTracker.csv, or application.yaml has status: applied or later)

- Never delete a submitted application.
- Explain to the user that this is a withdrawal, not a discard.
- If the user confirms they want to withdraw:
  - Update tracking/JobTracker.csv — set the Status column of that row to Withdrawn (reuse the existing dropdown value; keep the row in place).
  - Update applications/<group>/<created>-<company-role>/application.yaml — set status: withdrawn.
  - Relocate the folder to `applications/03-closed/<created>-<company-role>/`.
- Do not delete any files.

Rules:

- Require explicit user confirmation before deleting or updating anything.
- Never delete an application that has a row in the tracker.
- CSV is the source of truth — only edit tracking/JobTracker.csv, never the XLSX.
- Reuse existing dropdown values (Status: Withdrawn).

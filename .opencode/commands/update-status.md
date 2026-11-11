---
description: Mirror a reported application outcome (rejected, interview, offer, withdrawn) into both application.yaml and the tracker
---

The user has reported an outcome for a submitted application (rejected, interview, offer, or withdrawal).

You must only act when the user explicitly states the outcome. Never guess from silence or from relying solely on date patterns.

Before updating, consult:

- **tracking/README.md** — Status dropdown values, CSV as source of truth, row ordering
- **templates/application.yaml** — lowercase status enum (`preparation | applied | interview | offer | rejected | withdrawn`)
- **tracking/JobTracker.csv** — the row for this application

Locate the application folder:

applications/<group>/<created>-<company-role>/

If the user gave only the company and role, derive the `<company-role>` leaf with the lowercase-hyphenated convention (e.g. "NTT DATA Junior Cybersecurity System Engineer" becomes ntt-data-junior-cybersecurity-system-engineer), then glob for `applications/*/*-<company-role>` (any group, any `<created>` prefix). If no folder matches, tell the user and stop.

Check for `application.yaml`:

- If it is missing (e.g. the user submitted but never ran /mark-applied), do NOT invent or write one. Explain that this application has no metadata file, so the tracker cannot be safely updated in sync. Offer two choices:
  - Run /mark-applied first to create the tracking row and application.yaml, then rerun /update-status.
  - Update only the tracker row manually if one already exists, clearly flagging that application.yaml is absent and that its status will remain unknown.
  Do not write a minimal yaml stub silently; confirm the user's intent first.

Once both files exist, mirror the outcome in both:

1. Update:

applications/<group>/<created>-<company-role>/application.yaml

set status to the lowercase enum value matching the reported outcome and bump last_updated:

- rejected
- interview
- offer
- withdrawn

2. Update:

tracking/JobTracker.csv

set the Status column of that row reusing existing dropdown values (keep the row in place; do not reorder, add, or delete rows):

- rejected -> Rejected
- interview -> Interview Scheduled
- offer -> keep Applied until the user reports the offer was accepted, then record manually
- withdrawn -> Withdrawn

Mappings summary:

| Reported outcome | application.yaml `status` | JobTracker.csv Status |
|---|---|---|
| rejection | rejected | Rejected |
| interview | interview | Interview Scheduled |
| offer | offer | Applied (until accepted) |
| withdrawal | withdrawn | Withdrawn |

3. Relocate the folder to the group matching the new status:

- rejected, withdrawn -> move to `applications/03-closed/<created>-<company-role>/`
- interview, offer -> stays in `applications/02-applied/` (no move)

Rules:

- Both files must reflect the same outcome. Never update one without the other.
- Reuse existing dropdown values only.
- Never assume an outcome from silence or from application age.
- CSV is the source of truth — edit tracking/JobTracker.csv, never the XLSX.
- Do not reorder or delete tracker rows while updating status.
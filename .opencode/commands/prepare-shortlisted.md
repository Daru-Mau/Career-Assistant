---
description: Prepare applications for shortlisted jobs after explicit approval
---

Prepare applications for shortlisted jobs. This command is gated on Phase 5 and
must not be used before scoring has been calibrated for at least one week.

For each job the user explicitly approves:

1. Confirm the job status is `shortlisted` in the discovery database.
2. Run `/prepare-application` for that job, reusing the existing templates,
   playbooks, and `scripts/build_cv.py`.
3. Verify the PDFs exist and are non-empty.

Rules:

- Cap: 5 prepared applications per day.
- Never update `tracking/JobTracker.csv`.
- Never mark an application as applied or submitted.
- Do not invent facts. Every claim must come from `profile/`.
- If a required field, visa answer, salary expectation, or demographic answer is
  missing, set the job to `awaiting_manual` and stop.
- Do not send email or submit any form.

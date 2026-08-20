# Workflow

## Standard flow (the commands)

1. User shares a job description
2. `/review-job`
   - Read career_preferences.md, profile/profile_index.md, application_workflow.md
   - Output: Job Summary, Strong Matches, Partial Matches, Genuine Gaps, ATS Keywords, Fit Assessment, Recommendation
   - Creates nothing, touches no tracker
3. User decides to proceed
4. `/prepare-application`
   - Read application_workflow.md, career_preferences.md, profile_index.md, relevant playbooks, templates
   - Create job_offers/<company-role>/job_description.md and applications/<company-role>/ with 6 artifacts
   - Run scripts/build_cv.py to generate <cv_stem>.pdf + <cl_stem>.pdf
   - Set application.yaml status: preparation
   - Do NOT touch the tracker
5. User confirms submission
6. `/mark-applied`
   - Update application.yaml (status: applied, date_applied: YYYY-MM-DD)
   - Insert new row at the top of tracking/JobTracker.csv data rows (CSV, not XLSX or XLSM); dates in M/D/YYYY
   - Only after explicit confirmation

## Post-submission flow

1. User reports an outcome for a submitted application (rejected, interview, offer, withdrawal)
2. `/update-status`
   - Update application.yaml status (lowercase enum) + bump last_updated
   - Update tracking/JobTracker.csv Status column of that row (Rejected / Interview Scheduled / Withdrawn)
   - Keep the row in place; never update one file without the other

## Discard flow

1. User decides not to apply, or something prevents applying
2. `/discard-application`
   - Review stage: nothing was created, nothing to delete
   - Preparation stage: delete `job_offers/<company-role>/` and `applications/<company-role>/` after explicit confirmation; do NOT touch the tracker
   - Applied stage: refuses deletion; on request marks the row as Withdrawn in JobTracker.csv and sets application.yaml status: withdrawn

## "Done" checklist before calling an application ready

- [ ] No invented claims
- [ ] Correct technologies, dates, grades
- [ ] ATS-compatible keywords present
- [ ] Appropriate language (matches job description)
- [ ] CV changes seeded from base CV, not a previous application
- [ ] Page limit respected when possible (1 page job, 2 pages PhD; soft target)
- [ ] All {{ PLACEHOLDER }} fields filled
- [ ] Application.yaml metadata complete (status: preparation)
- [ ] Build script ran: <cv_stem>.pdf and <cl_stem>.pdf exist, no unresolved-placeholder warnings

## Tracker update checklist (mark-applied)

- [ ] CSV row order matches header (columns A-K, M/D/YYYY dates)
- [ ] Data rows sorted newest-first by Date Applied; new row inserted at the top
- [ ] Existing dropdown values reused
- [ ] Fit Score, Priority Level, Salary, Currency populated when known
- [ ] application.yaml status updated to applied

## Deploy

Not applicable. No deployment. "Shipping" = the files written to job_offers/ and applications/ plus tracker rows.

## Pending

- [RESOLVED: Phase 6 (post-application) outcome tracking] now implemented by /update-status command (18/08/2026). Interview notes, recruiter communication, and offer acceptance still have no dedicated command or file.
- [PENDING: role-to-playbook mapping] only examples exist (Robotics Research Engineer -> robotics.md + phd.md); no exhaustive table.
- [PENDING: XLSX refresh process] tracking/README.md describes a manual copy of formatting; not automated.

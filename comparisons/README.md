# Comparisons

This folder stores side-by-side comparisons of job offers or applications when asked.

Comparisons are made per request, in an offer-vs-offer space.

## Naming

`<company_a>-<role_a>_vs_<company_b>-<role_b>.md`

Lowercase-hyphenated, matching the `job_offers/<company-role>/` convention.
Example: `google-customer-engineer-ai-natives_vs_bending-spoons-security-engineer.md`.

## Lifecycle

- Comparisons are only created on request. They never update the tracker and never
  create or modify application folders or job offer descriptions.
- They are decision-support documents: recommendation and reasoning, not facts you
  have not witnessed.
- The perks and details live in the individual files (`job_offers/<company-role>/`
  and `applications/<company-role>/`); the comparison references them and does not
  duplicate or edit them.
- Public-opinion material (Glassdoor, Blind, company-issued docs, press) is folded in
  when useful, always labelled as crowd-sourced and third-party, with a date, never as
  verified employee records.

## Contents

1. Snapshot table: base, bonus, equity, location, modality, ranking (from `application.yaml`).
2. Net salary estimate (single) when relevant, applying the relevant local tax rules for the job's country.
3. Domain/career-trajectory comparison.
4. Risk - Gap analysis, cross-referencing the fit_assessment of each side.
5. Public reviews: working environment, policies, growth potential (when requested).
6. Recommendation with open questions for the user.
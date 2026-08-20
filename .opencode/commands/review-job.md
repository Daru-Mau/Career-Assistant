---
description: Analyze a job offer without creating application files or updating tracking
---

Review the provided job description according to the workflow defined in AGENTS.md.

Your goal is to determine whether this opportunity is worth pursuing before creating any permanent files.

Before analyzing, consult:

- **career_preferences.md** — career goals, interests, geographic preferences, philosophy
- **profile/profile_index.md** — identifies which profile files to use as source
- **application_workflow.md** — Phase 2 (Role Classification) to frame the role in context of relevant playbooks

Analyze:

- company
- role title
- location
- seniority
- industry
- required skills
- preferred skills
- soft skills
- ATS keywords
- posting language
- company style

Compare the role against the profile sources (filenames and which exist per the user's profile/ folder; the base CV name comes from config.json):

1. profile/<base_cv_file> (base CV)
2. the thesis document in profile/ when relevant
3. the academic grades / transcript file in profile/ when academic information is needed

Provide:

# Job Summary

# Strong Matches

# Partial Matches

# Genuine Gaps

# ATS Keywords

# Fit Assessment

# Recommendation

Rules:

- Do not create job_offers folders.
- Do not create applications folders.
- Do not modify the Excel tracker.
- Do not assume the user will apply.
- Be honest about missing requirements.

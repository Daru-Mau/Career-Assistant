# Application Workflow

This document describes the standard workflow for creating and managing job applications.

The Career Assistant should follow this process whenever a new job opportunity is provided.

---

# Phase 1 — Job Offer Intake

Input:

- pasted job description
- uploaded document
- URL content copied by the user

Analyze (do NOT create folders yet):

- company
- role title
- location
- seniority
- employment type
- industry
- required skills
- preferred skills
- soft skills
- ATS keywords
- application language

The job description itself is saved only later, during Phase 4 preparation:

```
job_offers/<company-role>/job_description.md
```

---

# Phase 2 — Role Classification

Determine the most relevant playbook(s):

Examples:

- software_engineer.md
- robotics.md
- hci.md
- data_science.md
- phd.md
- hospitality.md
- retail.md
- entry_level.md

Multiple playbooks can be combined when appropriate.

Example:

Robotics Research Engineer:

- robotics.md
- phd.md

---

# Phase 3 — Profile Matching

Consult:

```
profile/
```

Primary sources:

1. Master CV
2. Thesis document
3. Academic grades

Identify:

## Strong matches

Experience directly aligned with the role.

## Partial matches

Transferable skills or adjacent experience.

## Gaps

Missing requirements.

Gaps must be honest and never hidden.

---

# Phase 4 — Application Generation

Create:

```
applications/<group>/<created>-<company-role>/
```

Generate:

## analysis.md

Job analysis and keyword extraction.

## fit_assessment.md

Compatibility evaluation.

## cv_changes.md

Tailoring instructions consumed by scripts/build_cv.py to produce the per-application CV.

Include:

- a replacement professional summary
- work experience bullets
- a **descriptive title per selected project** (a meaningful phrase stating what the project is, e.g. "Gamified Exploration Mobile App (Mapuka)", adapted from the base CV title with the job's ATS keywords)
- full rewritten bullets for every selected project, seeded with ATS keywords
- regrouped skills
- the most relevant certifications from the base CV that match the job offer, or note none apply
- project ordering
- skills emphasis

## cover_letter.md

Professional tone, max three paragraphs, avoids repeating the CV. Role-specific, not generic.

Keep:

- specific
- professional
- concise

## interview_topics.md

Prepare:

- technical topics
- behavioral examples
- project discussion points
- interviewer questions

## application.yaml

Metadata.

## Generated PDFs

After the artifacts above are written, run:

```
python.exe scripts/build_cv.py "<group>/<created>-<company-role>"
```

to produce `<cv_stem>.pdf` and `<cl_stem>.pdf` from the base CV + cv_changes.md + cover_letter.md (stems and the base CV filename come from `config.json`).

---

# Phase 5 — Review

Before submission:

Check:

- no invented claims
- correct technologies
- correct dates
- correct grades
- ATS compatibility
- appropriate language
- build script ran: `<cv_stem>.pdf` and `<cl_stem>.pdf` exist, no unresolved-placeholder warnings

---

# Phase 6 — Post Application

Update:

- application status
- interview notes
- recruiter communication
- outcomes

Applications should become a historical knowledge base.

The generated `<cv_stem>.html`, `<cv_stem>.pdf`, `<cl_stem>.html`, and `<cl_stem>.pdf` stay in the folder as the submitted record.

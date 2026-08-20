---
description: Create application workspace and materials after user approval
---

Prepare the application according to AGENTS.md.

This command is only used after the user has reviewed the opportunity and decided to proceed.

Before generating, consult:

- **application_workflow.md** — phases 1-6 process (classification, review checklist, post-application)
- **career_preferences.md** — rules on summaries, cover letters, thesis prioritization, salary benchmarks
- **profile/profile_index.md** — identifies which profile files to use as source
- **playbooks/*** — select the most relevant playbook(s) for the role; applies CV length (1pg jobs, 2pg PhD), keyword emphasis, and project priorities. Reference them by filename with .md extension (e.g. software_engineer.md, robotics.md).
- **templates/*** — follow the exact section structure and placeholder format for each generated file

Create:

job_offers/<company-role>/

applications/<company-role>/

Save the original job description:

job_offers/<company-role>/job_description.md

Generate inside:

applications/<company-role>/

## analysis.md

Follow template at templates/analysis.md — fill all {{ PLACEHOLDER }} fields.

## fit_assessment.md

Follow template at templates/fit_assessment.md — fill all {{ PLACEHOLDER }} fields.

## cv_changes.md

**Always start from the base CV at profile/<base_cv_file> (see config.json) — never increment from a previous application.**

Before authoring cv_changes.md, read .opencode/commands/cv-format-reference.md. Do not read build_cv.py or cv_template.html.

Follow template at templates/cv_changes.md for section structure.

Additional rules:

- **Page limits:** 1 page for job applications, 2 pages for PhD applications (from playbooks).
- **If content overflows the page limit:** trim to fit by omitting the lowest-relevance projects and tightening bullets first; do not shrink fonts or margins to force content in.
- **Select only most relevant projects** — omit low-relevance entries to fit page limit.
- **Every selected project gets a descriptive title** — a short meaningful phrase stating what the project is (e.g. "Gamified Exploration Mobile App"), optionally with the project name in parentheses. Start from the base CV's project title and adapt it with the job's ATS keywords. This descriptive title, not the bare project name, goes on the CV.
- **Every selected project gets full rewritten bullet points**, seeded with ATS keywords from the job offer.
- **Skills** — Skill group names are FIXED (Strict): you may only use exactly these 8 canonical English headers, in any order — Programming Languages, Embedded & Systems, Backend & Cloud, Frontend, Mobile & XR, Tools & Practices, Research Methods, Soft Skills. Never rename, translate, or add groups; i18n happens automatically at render time via SKILL_GROUPS_I18N, so always write the English group names regardless of the job description's language. Each skill token must be in Title Case (e.g. Real-Time Systems, not real-time systems); lowercase tokens trigger a build warning and a rebuild cycle. Only reorder the groups and change the comma-separated values within each group. To remove a whole group from the rendered CV, write `**<Group>:** OMIT` (e.g. `**Mobile & XR:** OMIT`); unmentioned groups fall back to their base-CV values. No prose lines inside the Skills section. Compact, comma-separated groups.
- **Work Experience** — the heading is the role title shown on the CV (e.g. "Freelance AI Data Curator"), derived from the actual work and adapted to the role; never use a contracting person's/company's name as the heading. Rewrite bullets if relevant; omit if not. No long dashes (— –).
- **Certifications** — list the most relevant certifications from the base CV that match the job offer's domain and skills (with issuer and date). Omit the section or state "none apply" when no certification matches.
- **Explicit ordering recommendation** — table with position, entry, rationale, and why others were omitted.

## cover_letter.md

Follow template at templates/cover_letter.md.

Requirements from career_preferences.md:

- maximum three paragraphs
- professional tone
- address genuine motivation
- address significant gaps honestly
- avoid repeating the CV

## interview_topics.md

Follow template at templates/interview_topics.md.

## application.yaml

Follow template at templates/application.yaml.

Set:

status: preparation

Rules:

- Do not update tracking/JobTracker.csv.
- Do not mark the application as submitted.
- The user must explicitly confirm submission later.

## Generate PDFs (<cv_stem>.pdf + <cl_stem>.pdf)

After all six files above exist, generate the printable PDFs by running the build script:

```bash
python.exe scripts/build_cv.py <company-role>
```

The script (stems and base CV filename come from config.json):

1. Reads `profile/<base_cv_file>` (facts) + `applications/<company-role>/cv_changes.md` (tailoring).
2. Renders `applications/<company-role>/<cv_stem>.html` and converts it to `<cv_stem>.pdf` with Edge headless.
3. Reads `applications/<company-role>/cover_letter.md`, renders `<cl_stem>.html`, and converts it to `<cl_stem>.pdf`.
4. Verifies both PDFs with PyMuPDF: page count (soft limit, from application.yaml playbooks), no leftover `{{ }}` placeholders.

Prerequisites:

- `pymupdf` installed on the Windows Python (`python.exe -m pip install pymupdf`).
- Microsoft Edge present (default for the script).

Check the build output:

- [ ] `<cv_stem>.pdf` and `<cl_stem>.pdf` were written to the application folder.
- [ ] No "WARNING: unresolved placeholders" lines.
- [ ] No "WARNING: project override ... not matched" lines.
- [ ] Page count respected when possible (1 page jobs, 2 pages PhD; flexible).

Rules:

- Run PDF generation only after the six application files are written.
- Do not edit <cv_stem>.html, <cv_stem>.pdf, <cl_stem>.html, or <cl_stem>.pdf by hand.
- The generated PDFs are final for submission; the user may still tweak copy in the source markdown and rebuild.

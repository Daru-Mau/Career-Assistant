# Conventions

## File naming

- Application folders: `job_offers/<company-role>/` and `applications/<company-role>/` (lowercase-hyphenated company + role, e.g. `acme-software-engineer`)
- Generated artifacts always named: analysis.md, fit_assessment.md, cv_changes.md, cover_letter.md, interview_topics.md, application.yaml
- Playbooks: lowercase_snake (robotics.md, data_science.md)

## Structure per application

Every application folder contains exactly 6 generated markdown/YAML files: analysis.md, fit_assessment.md, cv_changes.md, cover_letter.md, interview_topics.md, application.yaml.

After prepare-application runs the build script (scripts/build_cv.py), the folder also contains 4 build outputs: `<cv_stem>.html`, `<cv_stem>.pdf`, `<cl_stem>.html`, `<cl_stem>.pdf` (filenames from config.json). They are generated artifacts, never edited by hand.

## Writing rules

Follow the Writing Guidelines in AGENTS.md (authoritative, auto-loaded every session). Summary: match the job description's language, never invent facts, avoid the prohibited vague phrases, no long dashes or random bold, prefer specific quantified statements.

## Template usage

- All generated markdown files follow templates/ with {{ PLACEHOLDER }} fields
- `<cv_stem>.html` and `<cl_stem>.html` use templates/cv_template.html and templates/cover_letter_template.html as fixed layout skeletons (no placeholders)
- cv_changes.md: always start from the base CV (profile/<base_cv_file>, see config.json), never increment from a previous application
- Select only the most relevant projects; omit low-relevance entries
- Rewrite every selected project's bullets with ATS keywords seeded from the job offer

## Page limits

- 1 page for job applications, 2 pages for PhD applications (from playbooks)
- Treated as a soft target: keep to the limit when possible; the build script warns rather than fails when a CV exceeds it

## Tracking rules

- CSV is the source of truth; never edit XLSX or XLSM programmatically (XLSM is outdated from a previous iteration)
- Tracker only gets rows after explicit user confirmation of submission
- Never assume preparation = submission
- Dates in M/D/YYYY format
- Reuse existing dropdown values (Priority Level, Status, Modality, Role)

## CV structure conventions

- Summary, Work Experience, Projects, Key Skills, Skills groups, Languages, Education, Certifications, Honors, Digital Skills
- Skills grouped: Programming Languages, Embedded & Systems, Backend & Cloud, Frontend, Mobile & XR, Tools & Practices, Research Methods, Soft Skills
- Projects carry dates in [ DD/MM/YYYY ] format and a "Key Skills:" line

## Tests and commits

- No tests exist. Optionally version-controlled if you initialize a git repository; see .gitignore for what stays private.

## Pending

- (none)

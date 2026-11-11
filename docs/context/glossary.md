# Glossary

## Domain terms

| Term | Meaning |
|---|---|
| **ATS** | Applicant Tracking System; parses CVs for keywords. CVs must stay ATS-compatible |
| **Fit Score** | Objective assessment (X/10) of how well the profile matches a role; recorded in tracker + application.yaml |
| **Priority Level** | User's interest: Top Choice / Consider / Low interest |
| **Playbook** | Role-specific guidance file (e.g. robotics.md) that shapes emphasis and CV length |
| **Master CV** | profile/<base_cv_file>, the factual base every application is built from (filename from config.json) |
| **Source of truth** | The file/place from which facts are taken without invention (profile/; JobTracker.csv for tracking) |
| **Modality** | On-Site / Remote / Hybrid (tracker column) |
| **Status** | Applied / Rejected / Interview Scheduled / Withdrawn / No Response (tracker) |

## Entities

- **Application folder**: applications/<group>/<created>-<company-role>/ containing 6 markdown/YAML artifacts, plus generated <cv_stem>.html/<cv_stem>.pdf and <cl_stem>.html/<cl_stem>.pdf after the build script
- **Job offer folder**: job_offers/<company-role>/ holding job_description.md
- **application.yaml**: per-application metadata (company, role, status, match_score, fit_score, salary, currency, language, playbooks, dates)
- **Playbooks set**: software_engineer, robotics, hci, data_science, phd, hospitality, retail, entry_level
- **Tracker files**: JobTracker.csv (source of truth), JobTracker.xlsx (export), JobTracker_backup.xlsx (fallback). JobTracker.xlsm is outdated from a previous iteration and not used.

## Internal acronyms / shorthand

| Term | Meaning |
|---|---|
| JD | Job Description |
| CV | Curriculum Vitae |
| SWE | Software Engineering |
| HCI | Human-Computer Interaction |
| XR | Extended Reality |
| PhD | Doctorate position |
| ESP32 | Microcontroller (thesis hardware) |
| FABRIK IK | Inverse kinematics solver used in thesis VR |

## Person

- Candidate / user: the person whose profile lives in `profile/`. Referenced as "the user" or "the candidate" throughout docs. Their `config.json` drives the build naming (`name`, `base_cv_file`, `cv_stem`, `cl_stem`, emails).

## Pending

- [PENDING: meanings of tracker reference rows 1-10 dropdown choices] header exists ("Job Details / Application Status") but the choices list is not documented in tracking/README.md.
- [RESOLVED: application statuses in application.yaml] unified to lowercase `preparation | applied | interview | offer | rejected | withdrawn` across template, commands, and AGENTS.md on 31/07/2026. Distinct from tracker Status enum (Applied/Rejected/...) by design.

# Decisions

Inferred from the repo structure and documents. Not all have written rationale; where the why is explicit it is noted, otherwise marked pending.

## Single source of truth in profile/

- **What:** profile/ holds the master CV, thesis, grades, index; generated applications never invent facts
- **Why:** README: "Every application should be generated from the same factual source of truth. Nothing should be invented."
- **Discarded:** storing tailored CVs per application; keeping facts scattered across applications

## Separation of job offers from generated material

- **What:** job_offers/<company-role>/job_description.md is saved separately from applications/<group>/<created>-<company-role>/
- **Why:** applications become a historical knowledge base; the original posting stays immutable and reusable for analysis
- **Discarded:** embedding the JD inside each generated doc

## Filesystem-level application sorting

- **What:** applications/ are physically organized as `applications/<group>/<created>-<company-role>/` with three status groups (01-preparing, 02-applied, 03-closed) and a YYYY-MM-DD name prefix from application.yaml `created`
- **Why:** the previous flat alphabetical layout hid newly generated applications; folders now sort by status group first and by generation date within a group in any file explorer, without relying on an index or the tracker
- **Discarded:** an index README + listing script (added to a flat layout) that described the order instead of providing it at the filesystem level

## Playbooks as role-specific guidance

- **What:** playbooks/*.md tailor emphasis (robotics, phd, hci, etc.), set CV length (1 or 2 pages) and keyword priorities
- **Why:** one profile, many role framings; playbooks encode "what to emphasize" without rewriting facts
- **Discarded:** a separate CV per playbook

## Template-driven generation

- **What:** templates/ define section structure and {{ PLACEHOLDER }} fields for every artifact
- **Why:** guarantees consistent output shape across applications
- **Discarded:** free-form generation

## CSV as tracker source of truth (not XLSX/XLSM)

- **What:** JobTracker.csv is machine-writable; JobTracker.xlsx is a formatted export refreshed manually
- **Why:** XLSX/XLSM are binary with macros/formatting that programmatic edits can corrupt; CSV is simple text
- **Discarded:** editing XLSX/XLSM programmatically
- **Note:** JobTracker.xlsm is outdated, created in a previous iteration, and no longer part of the flow

## Explicit user confirmation gates

- **What:** three strict stages: review (no files), prepare (files, no tracker), applied (tracker, only on confirmation)
- **Why:** "Never assume preparation means submission"; prevents phantom applications
- **Discarded:** marking applications applied automatically

## Commands as the only workflow entry points

- **What:** .opencode/commands/{review-job,prepare-application,mark-applied,update-status,discard-application}.md define the workflow operations
- **Why:** repeatable, documented, inspectable triggers for each lifecycle step
- **Discarded:** ad-hoc file creation

## Curated certifications

- **What:** CERTIFICATIONS on the master CV lists only high-relevance credentials; profile_index says to discard beginner/soft-skill courses
- **Why:** avoids diluting the CV; ATS value per line
- **Discarded:** mirroring all LinkedIn certs

## Pending

- [PENDING: role classification mapping] application_workflow.md gives example role-to-playbook combos but no full mapping table exists. Tracked in workflow.md.

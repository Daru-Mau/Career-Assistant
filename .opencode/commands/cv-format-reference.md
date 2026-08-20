# CV Format Reference

## What to read instead of the source
This file replaces reading build_cv.py, cv_template.html, or any other application's cv_changes.md.
Refer to templates/cv_changes.md for the canonical section structure and placeholder format.

## Section order (template)
Summary → Projects → Experience → Skills → Education → Certifications → Languages

## cv_changes.md authoring rules

### Descriptive title syntax
**Descriptive title for X:**
Full Descriptive Title Here

### Replace bullets syntax
**Replace bullets for X:**
- Bullet one
- Bullet two

### Skill groups - 8 canonical headers, always English, Title Case tokens
**Programming Languages:** ...
**Embedded & Systems:** ...
**Backend & Cloud:** ...
**Frontend:** ...
**Mobile & XR:** ...
**Tools & Practices:** ...
**Research Methods:** ...
**Soft Skills:** ...

Rules:
- Exactly these 8 headers, no renames, no additions
- Token Title Case - "Real-Time Systems" not "real-time systems"
- No prose lines inside Skills (Note:, Avoid:, etc. will leak into PDF)
- i18n is automatic at render - always write English group names

### Omit a group entirely (frees page space)
To drop a whole group from the rendered CV:
**Mobile & XR:** OMIT
Any canonical group not mentioned reverts to its base-CV values; omit only the groups irrelevant to the role.

## Accepted date formats
- yaml: YYYY-MM-DD
- CSV: M/D/YYYY

## Page limits
- Default roles: 1 page (trim by omitting low-relevance projects, never shrink fonts)
- PhD/research: 2 pages

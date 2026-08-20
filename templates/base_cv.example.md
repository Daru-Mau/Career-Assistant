# {{ YOUR_FULL_NAME }}

Copy this file into `profile/` as your base CV, name it to match `base_cv_file` in your `config.json`, and replace the `{{ }}` placeholders with your real facts. This is the single source of truth that `scripts/build_cv.py` reads and every application is built from. Never invent facts here.

## Contact Information

- **Nationality:** {{ NATIONALITY }}
- **Place of birth:** {{ PLACE_OF_BIRTH }}
- **Phone number:** {{ PHONE }}
- **Email address:** {{ EMAIL }}
- **LinkedIn:** {{ LINKEDIN_URL }}
- **GitHub:** {{ GITHUB_URL }}
- **Address:** {{ STREET }} {{ CITY }} {{ POSTAL_CODE }} ({{ COUNTRY }})

## About Me

{{ PROFESSIONAL_SUMMARY_PARAGRAPH_1 }}

{{ PROFESSIONAL_SUMMARY_PARAGRAPH_2 }}

## Work Experience

### {{ ROLE_TITLE }}

**Location:** {{ CITY }}, {{ COUNTRY }}
**Period:** [ {{ DD/MM/YYYY }} - {{ DD/MM/YYYY }} ]

- {{ SPECIFIC_RESULT_1 }}
- {{ SPECIFIC_RESULT_2 }}

## Projects

Keep each project entry below, ordered by relevance. Use a descriptive title with the project's name in parentheses, a single-line date in `[ DD/MM/YYYY - DD/MM/YYYY ]`, specific result bullets, and a `**Key Skills:**` line of Title Case tokens separated by `|`.

### {{ DESCRIPTIVE_TITLE }} ({{ PROJECT_NAME }})

[ {{ DD/MM/YYYY }} - {{ DD/MM/YYYY }} ]

- {{ SPECIFIC_RESULT_1 }}
- {{ SPECIFIC_RESULT_2 }}
- {{ SPECIFIC_RESULT_3 }}

**Key Skills:** {{ SKILL_1 }} | {{ SKILL_2 }} | {{ SKILL_3 }}

### {{ DESCRIPTIVE_TITLE }} ({{ PROJECT_NAME }})

[ {{ DD/MM/YYYY }} - {{ DD/MM/YYYY }} ]

- {{ SPECIFIC_RESULT_1 }}
- {{ SPECIFIC_RESULT_2 }}

**Key Skills:** {{ SKILL_1 }} | {{ SKILL_2 }} | {{ SKILL_3 }}

## Skills

Comma-separated groups. Use exactly these canonical group names (translation happens at render time). Each token in Title Case. No group is a subset of another, no duplicates across groups.

**Programming Languages:** {{ PYTHON }}, {{ JAVASCRIPT }}, ...

**Embedded & Systems:** {{ C }}, {{ C++ }}, ...

**Backend & Cloud:** {{ FRAMEWORK }}, {{ DATABASE }}, ...

**Frontend:** {{ REACT }}, {{ VUE }}, ...

**Mobile & XR:** {{ REACT_NATIVE }}, {{ UNITY }}, ...

**Tools & Practices:** {{ GIT }}, {{ CI/CD }}, ...

**Research Methods:** {{ USER_STUDIES }}, {{ EXPERIMENT_DESIGN }}, ...

**Soft Skills:** {{ ANALYTICAL_THINKING }}, {{ PROBLEM_SOLVING }}, ...

## Language Skills

**Mother tongue(s):** {{ MOTHER_TONGUE }} (native)

**Other language(s):** {{ LANGUAGE_A }} ({{ LEVEL }}) | {{ LANGUAGE_B }} ({{ LEVEL }})

## Education and Training

### {{ DEGREE }} — {{ INSTITUTION }}

- Graduated: {{ DD/MM/YYYY }}
- City: {{ CITY }} | Country: {{ COUNTRY }} | Website: {{ URL }} | Field(s) of study: {{ FIELD }}

### {{ DEGREE }} — {{ INSTITUTION }}

- City: {{ CITY }} | Country: {{ COUNTRY }} | Website: {{ URL }} | Field(s) of study: {{ FIELD }}

## Certifications

Only high-relevance credentials. List each as a bullet with name, issuer, and date.

- **{{ CERTIFICATION_NAME }}** | {{ ISSUER }} | Issued {{ MONTH YYYY }}
- **{{ CERTIFICATION_NAME }}** | {{ ISSUER }} | Issued {{ MONTH YYYY }}

## Honours and Awards

- **{{ AWARD }}** | {{ INSTITUTION }}

## Hobbies and Interests

- {{ HOBBY_1 }}
- {{ HOBBY_2 }}

#!/usr/bin/env python3
"""Build and verify a per-application PDF CV.

Usage:
    python build_cv.py "<group>/<created>-<company-role>"

where <group> is one of 01-preparing / 02-applied / 03-closed (the arg is
joined onto applications/, so it can be a nested relative path).

Reads:
    profile/<base_cv_file>              (base CV, source of truth -- filename from config.json)
    applications/<group>/<created>-<company-role>/cv_changes.md (tailored overrides)
    applications/<group>/<created>-<company-role>/application.yaml (metadata)
    templates/cv_template.html          (canonical layout)

Writes (stems <cv_stem>/<cl_stem> come from config.json):
    applications/<group>/<created>-<company-role>/<cv_stem>.html
    applications/<group>/<created>-<company-role>/<cv_stem>.pdf
    applications/<group>/<created>-<company-role>/<cl_stem>.html
    applications/<group>/<created>-<company-role>/<cl_stem>.pdf

Verifies with PyMuPDF: page count, no placeholder leftovers, presence of
ATS keywords. Facts that cannot be confidently overridden fall back to the
base CV so nothing is invented.
"""

import collections
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "templates", "cv_template.html")
CL_TEMPLATE = os.path.join(REPO, "templates", "cover_letter_template.html")


def load_config():
    """Load person-specific values from config.json (local, gitignored),
    falling back to the tracked config.example.json so a fresh clone works
    out of the box. Returns {} if neither is present."""
    for p in ("config.json", "config.example.json"):
        path = os.path.join(REPO, p)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError):
                break
    return {}


CONFIG = load_config()


def cfg(key, default=""):
    return CONFIG.get(key, default)


PROFILE_CV = os.path.join(REPO, "profile", cfg("base_cv_file", "your_name_cv.md"))
CV_STEM = cfg("cv_stem", "YourName_cv")
CL_STEM = cfg("cl_stem", "YourName_cl")
NAME = cfg("name", "Your Full Name")
WORK_EMAIL = cfg("work_email", "")
PHD_EMAIL = cfg("phd_email", "")

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print(f"WARNING: {msg}", file=sys.stderr)


def expected_pages(yaml_path):
    """phd.md playbook -> 2 pages, else 1 page."""
    if not os.path.exists(yaml_path):
        return 1
    try:
        txt = open(yaml_path, encoding="utf-8").read()
    except OSError:
        return 1
    if re.search(r"phd\.md", txt):
        return 2
    return 1


def contact_email(yaml_path, base_email):
    """Use the +work or +phd alias email depending on the playbook, so
    recruiters can be filtered by mailbox easily. Values come from config.json
    (work_email / phd_email); fall back to the base CV email when unset."""
    if not os.path.exists(yaml_path):
        return base_email
    try:
        txt = open(yaml_path, encoding="utf-8").read()
    except OSError:
        return base_email
    if re.search(r"phd\.md", txt):
        return PHD_EMAIL or base_email
    return WORK_EMAIL or base_email


LANG_ALIASES = {"english": "en", "italian": "it", "german": "de",
                "french": "fr", "spanish": "es"}

SECTION_HEADERS = {
    "en": {"summary": "Professional Summary", "projects": "Projects",
           "work": "Experience", "skills": "Key Skills",
           "education": "Education", "certifications": "Certifications",
           "languages": "Languages"},
    "it": {"summary": "Riepilogo Professionale", "projects": "Progetti",
           "work": "Esperienza Lavorativa", "skills": "Competenze Chiave",
           "education": "Istruzione", "certifications": "Certificazioni",
           "languages": "Lingue"},
}

SKILL_GROUPS_I18N = {
    "it": {
        "Programming Languages": "Linguaggi di Programmazione",
        "Embedded & Systems": "Embedded e Sistemi",
        "Backend & Cloud": "Backend e Cloud",
        "Frontend": "Frontend",
        "Mobile & XR": "Mobile e XR",
        "Tools & Practices": "Strumenti e Pratiche",
        "Research Methods": "Metodi di Ricerca",
        "Soft Skills": "Soft Skills",
    },
}

MISC_I18N = {
    "it": {
        "Key Skills:": "Competenze Chiave:",
        "Project": "Progetto",
        "Relevant Coursework": "Corsi Pertinenti",
        "Relevant coursework:": "Corsi pertinenti:",
    },
}


def lang_from_yaml(yaml_path):
    """Return a 2-letter language code from application.yaml (default 'en').
    All section headers, skill group names and inline labels follow this
    language; anything untranslated falls back to the English key."""
    if os.path.exists(yaml_path):
        try:
            txt = open(yaml_path, encoding="utf-8").read()
        except OSError:
            return "en"
        m = re.search(r"(?m)^\s*language:\s*([A-Za-z]+)", txt)
        if m:
            return LANG_ALIASES.get(m.group(1).strip().lower(), "en")
    return "en"


def i18n(lang, key, table):
    """Translate 'key' through 'table' for 'lang', falling back to the key."""
    return table.get(lang, {}).get(key, key)


# --------------------------------------------------------------------------
# Markdown -> structured helpers
# --------------------------------------------------------------------------

def split_sections(text, markers):
    """Split a markdown doc by its main section headings. Yields (name, body)."""
    sections = []
    lines = text.splitlines()
    cur_name, cur_body = None, []
    for line in lines:
        m = re.match(r"^##\s+(.*)$", line.strip())
        if m:
            if cur_name is not None:
                sections.append((cur_name, "\n".join(cur_body)))
            cur_name = m.group(1).strip()
            cur_body = []
        elif cur_name is not None:
            cur_body.append(line)
    if cur_name is not None:
        sections.append((cur_name, "\n".join(cur_body)))
    return sections


def split_h3(body):
    """Split a section body at its '### ' sub-headings."""
    sections = []
    cur = None
    for line in body.splitlines():
        m = re.match(r"^###\s+(.*)$", line.strip())
        if m:
            if cur is not None:
                sections.append((cur[0], "\n".join(cur[1])))
            cur = [m.group(1).strip(), []]
        elif cur is not None:
            cur[1].append(line)
    if cur is not None:
        sections.append((cur[0], "\n".join(cur[1])))
    return sections


def find_section(text, *needles):
    low = text.lower()
    for name, body in split_sections(text, []):
        for needle in needles:
            if needle in name.lower() and len(body.strip()) > 0:
                return body.strip()
    return None


def bullet_lines(lines):
    """Return lines that look like bullets, stripped of leader."""
    out = []
    for l in lines:
        s = l.strip()
        m = re.match(r"^[•*\-]\s+(.+)$", s)
        m2 = re.match(r"^\|\s*(.+?)\s*\|$", s)
        if m:
            out.append(m.group(1).strip())
        elif m2 and m2.group(1).strip():
            out.append(m2.group(1).strip())
    return out


def split_fences_outside(text):
    """Split text into ('code', block) and ('text', paragraph) segments."""
    parts = re.split(r"(```(?:[a-zA-Z]*)\n.*?```)", text, re.S)
    out = []
    for p in parts:
        if not p.strip():
            continue
        if p.startswith("```"):
            inner = re.sub(r"^```[a-zA-Z]*\n|```$", "", p, flags=re.S)
            out.append(("code", inner))
        else:
            out.append(("text", p))
    return out


# --------------------------------------------------------------------------
# Base CV parsing
# --------------------------------------------------------------------------

def parse_base_cv(text):
    data = {}
    data["name"] = ""
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        data["name"] = m.group(1).strip()

    contact = {}
    contact_body = find_section(text, "contact information", "informazioni di contatto")
    if contact_body:
        for key in ("Phone number", "Email address", "LinkedIn", "GitHub", "Address"):
            # handles both **Key:** value  and  **Key**: value
            cm = re.search(r"^\s*-\s*\*\*" + re.escape(key) + r"(?:\*\*:?|:\*\*)\s*(.+)$",
                           contact_body, re.M)
            if cm:
                contact[key] = cm.group(1).strip()
        addr = contact.get("Address", "")
        m = re.search(r"([A-Za-zÀ-ÿ]+)\s*\([^)]*\)\s*$", addr)
        if m:
            contact["City"] = m.group(1).strip()
    data["contact"] = contact

    about = find_section(text, "about me", "profilo", "summary")
    data["about"] = "\n".join(
        l for l in (about or "").splitlines() if l.strip()) if about else ""

    projects = []
    proj_marker = find_section(text, "projects", "progetti")
    if proj_marker:
        for name, body in split_h3(proj_marker):
            if not name.strip():
                continue
            pr = {"title": name.strip()}
            pr["key_skills"] = ""
            ks = re.search(r"\*\*Key Skills?:\*\*\s*(.+)$", body, re.M)
            if ks:
                pr["key_skills"] = ks.group(1).strip()
            pr["bullets"] = bullet_lines([l for l in body.splitlines()
                                          if not l.strip().startswith("**") and
                                          l.strip() and not re.match(r"^\[", l.strip())])
            pr["date"] = ""
            dm = re.search(r"^\s*\[(.+?)\]\s*$", body, re.M)
            if dm:
                pr["date"] = dm.group(1).strip()
            pr["raw"] = body
            projects.append(pr)
    data["projects"] = projects

    skills = {}
    skills_body = find_section(text, "skills", "competenze", "key skills")
    if skills_body:
        for line in skills_body.splitlines():
            gm = re.match(r"^\*\*(.+?):\*\*\s*(.+)$", line.strip())
            if gm and gm.group(2).strip():
                skills[gm.group(1).strip()] = gm.group(2).strip()
    data["skills"] = skills

    langs = []
    lang_body = find_section(text, "language skills", "lingue", "language")
    if lang_body:
        for line in lang_body.splitlines():
            if "**" in line:
                lm = re.match(r"^\*\*(.+?):\*\*\s*(.+)$", line.strip())
                if lm:
                    langs.append(f"{lm.group(1).strip()}: {lm.group(2).strip()}")
    data["languages"] = langs

    edu = []
    edu_body = find_section(text, "education and training", "education", "istruzione")
    if edu_body:
        for name, body in split_h3(edu_body):
            if name.strip():
                edu.append({"title": name.strip(), "body": body.strip()})
    data["education"] = edu

    certs = []
    cert_body = find_section(text, "certifications", "certificazioni")
    if cert_body:
        certs = bullet_lines(cert_body.splitlines())
    data["certifications"] = certs

    honors = []
    hon_body = find_section(text, "honours and awards", "honors", "premi")
    if hon_body:
        honors = bullet_lines(hon_body.splitlines())
    data["honors"] = honors
    return data


# --------------------------------------------------------------------------
# cv_changes.md parsing (tolerant; falls back silently where uncertain)
# --------------------------------------------------------------------------

def parse_summary(changelog):
    s = None
    parts = split_sections(changelog, [])
    for name, body in parts:
        low = name.lower()
        if any(k in low for k in ("professional summary", "riepilogo professionale",
                                  "about me", "profilo", "summary", "riepilogo")):
            s = body
            break
    if s is None:
        return None
    fences = re.findall(r"```[a-zA-Z]*\n(.*?)```", s, re.S)
    if fences:
        return fences[0].strip()
    # bold "Replacement:"/"Sostituisci" paragraph fallback
    m = re.search(r"\*\*(?:Replace|Replacement|Sostituisci|Sostituzione)"
                  r"[^:]*:\*\*\s*\n?\s*([^\n]+)", s, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"\*\*.*(?:replace|sostituisci).*?:\*\*\s*\n?\s*([^\n]+)", s, re.S)
    if m:
        return m.group(1).strip()
    return None


_WORK_OMIT = object()  # sentinel: section exists but is explicitly omitted

def parse_work(changelog, base):
    out = []
    parts = split_sections(changelog, [])
    for name, body in parts:
        low = name.lower()
        if any(k in low for k in ("work experience", "esperienza lavorativa")):
            # explicit omit instruction
            if re.search(r"\b(omit|remove|skip|exclude|ometti|rimuovi)\b",
                         body, re.I):
                return _WORK_OMIT
            hm = re.search(r"^###\s+(.+)$", body, re.M)
            entry_title = hm.group(1).strip() if hm else "Freelance AI Data Curator"
            bullets = None
            for seg_type, seg in split_fences_outside(body):
                if seg_type == "code":
                    bullets = bullet_lines(seg.splitlines())
                    break
            if bullets is None:
                lst = [l.strip() for l in body.splitlines()
                       if re.match(r"^[•\-*]\s+", l.strip())]
                if lst:
                    bullets = bullet_lines(lst)
            if bullets:
                out.append({"title": entry_title, "bullets": bullets})
    return out


def collect_block(lines, start, labels=()):
    """Collect content lines starting at `start`, stopping at blank-line
    boundaries UNLESS inside a fenced block, and stopping on the next
    label/heading line. Returns list of original lines."""
    block = []
    in_fence = False
    i = start
    label_re = [re.compile(l) for l in labels]
    while i < len(lines):
        raw = lines[i]
        l = raw.strip()
        if not in_fence and any(r.match(l) for r in label_re):
            break
        if l.startswith("```"):
            in_fence = not in_fence
            block.append(raw)
            i += 1
            continue
        if not in_fence and not l:
            # only break here if we already have content and next non-empty
            # line is a label/heading (avoids stopping at inner blank lines)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or any(r.match(lines[j].strip())
                                      for r in label_re):
                break
            block.append(raw)
        else:
            block.append(raw)
        i += 1
    return block


def parse_project_overrides(changelog):
    """Return {project key: {"title": str, "bullets": [..]}}."""
    overrides = collections.OrderedDict()
    cur_key = None
    cur_waiting_title = None
    sections = split_sections(changelog, [])
    proj_body = None
    for name, body in sections:
        low = name.lower()
        if any(k in low for k in ("projects", "progetti")):
            proj_body = body
            break
    if proj_body is None:
        return overrides

    lines = proj_body.splitlines()
    i = 0
    pending_title = None
    while i < len(lines):
        line = lines[i].strip()
        # descriptive title: **Descriptive title for X:** or IT equivalent
        m = re.match(r"^\*\*(?:Descriptive title|Titolo descrittivo|Title)"
                     r"(?: for| per)?(?: the)?\s*(.*?):\*\*\s*$", line)
        if m:
            key = m.group(1).strip()
            i += 1
            title_lines = []
            while i < len(lines) and lines[i].strip():
                title_lines.append(lines[i].strip())
                i += 1
            pending_title = (key, "\n".join(title_lines))
            continue
        # replace bullets labels
        m = re.match(r"^(?:#+\s*)?\*\*(?:Replace bullets|Sostituisci i bullet)"
                     r"(?: for| per)?\s*(.*?):\*\*\s*$", line)
        if not m:
            m = re.match(r"^###\s*(?:Replace bullets|Sostituisci i|Replace)\s+"
                         r"(?:for\s+|per\s+)?(.*)$", line)
        if m:
            key = m.group(1).strip().rstrip(":. ").strip()
            i += 1
            block = collect_block(lines, i, labels=(
                r"^\*\*(?:Replace bullets|Sostituisci i bullet)"
                r"(?: for| per)?\s*.*?:\*\*\s*$",
                r"^\*\*(?:Descriptive title|Titolo descrittivo|Title)"
                r"(?: for| per)?(?: the)?\s*.*?:\*\*\s*$",
                r"^\*\*[A-Za-zÀ-ÿ ]+:\*\*\s*$",
                r"^###\s*(?:Replace bullets|Sostituisci i|Replace)" +
                r"(?: for| per)?\s",
                r"^##?\s",
            ))
            # code fence handling
            bl = [l for l in block if l.strip()]
            joined = "\n".join(bl)
            fences = re.findall(r"```[a-zA-Z]*\n(.*?)```", joined, re.S)
            if fences:
                bullets = bullet_lines(fences[0].splitlines())
            else:
                bullets = bullet_lines(bl)
            if pending_title and not key:
                key = pending_title[0]
            if not key:
                key = cur_key or "Project"
            if pending_title and pending_title[0] == key:
                title = pending_title[1].strip()
            else:
                # bare key reference — title will be resolved to base CV full
                # title at render time; store None so render_projects can detect
                title = None
            overrides[key] = {"title": title, "bullets": bullets, "_key": key}
            cur_key = key
            pending_title = None
            continue
        i += 1

    # Reorder numbered list -> base project mapping
    reorder = []
    for line in proj_body.splitlines():
        rm = re.match(r"^\s*\d+\.\s+(.+)$", line.strip())
        if rm and not re.search(r"remove|omit|skip|lowest|low relevance|omessi",
                                rm.group(1), re.I):
            reorder.append(rm.group(1).strip())
    return overrides, reorder


def _norm_group_name(s):
    """Lowercase and strip punctuation/& to compare group names."""
    s = (s or "").lower().replace("&", "").replace("and", "")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def _skill_tokens(s):
    return {t.strip().lower() for t in (s or "").split(",") if t.strip()}


def _resolve_canonical(gname, gval, canonical):
    """Map an agent group to a canonical base group: exact name match,
    else best token overlap with a canonical group's value (tie-break by
    canonical order). Returns the canonical group name or None."""
    gn = _norm_group_name(gname)
    order = list(canonical)
    for c in order:
        if gn == _norm_group_name(c):
            return c
    gset = _skill_tokens(gval)
    best, best_n = None, 0
    for c in order:
        n = len(gset & _skill_tokens(canonical[c]))
        if n > best_n:
            best, best_n = c, n
    if best_n > 0:
        return best
    return None


def _merge_values(*values):
    """Join multiple comma lists into one, preserving first-seen order."""
    seen, out = set(), []
    for v in values:
        for t in (v or "").split(","):
            t = t.strip()
            key = t.lower()
            if t and key not in seen:
                seen.add(key)
                out.append(t)
    return ", ".join(out)


def parse_skills(changelog, base):
    found = False
    agent = {}
    for name, body in split_sections(changelog, []):
        low = name.lower()
        if any(k in low for k in ("skills", "competenze", "key skills")):
            found = True
            lines = body.splitlines()
            for idx, line in enumerate(lines):
                gm = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line.strip())
                if not gm:
                    continue
                gname = gm.group(1).strip()
                gval = gm.group(2).strip()
                if not gval:
                    # value on the following line(s) of the same block
                    j = idx + 1
                    while j < len(lines) and lines[j].strip().startswith("**"):
                        j += 1
                    nxt = []
                    while j < len(lines) and lines[j].strip():
                        nxt.append(lines[j].strip())
                        j += 1
                    gval = " ".join(nxt)
                skip = gname.lower().startswith(("excluded", "nota",
                                                 "not " "consider", "consider",
                                                 "page", "position", "ordering",
                                                 "note"))
                skip = skip or any(w in gname.lower() for w in
                                   ("excluded", "note", "notes", "rationale",
                                    "omessi", "checklist", "tabella"))
                # reject agent prose lines that are not real skill groups
                if re.search(r"\b(do not|don't|avoid|make sure)\b",
                             gval, re.I):
                    skip = True
                if not skip and gval:
                    agent[gname] = gval
            break
    if not found:
        # no skills section in changelog at all — fall back to base CV
        return dict(base.get("skills", {}))
    # Warn on tokens written all-lowercase in the source (soft-skill style
    # words like 'communication, adaptability' instead of Title Case).
    known = set()
    for v in base.get("skills", {}).values():
        known |= _skill_tokens(v)
    for gname, gval in agent.items():
        bad = []
        for raw in (gval or "").split(","):
            tok = raw.strip().lower()
            if (raw.strip() == raw.strip().lower() and raw.strip().isalpha()
                    and len(tok) >= 3 and tok not in known):
                bad.append(raw.strip())
        if bad:
            warn(f"skill group '{gname}' has all-lowercase values "
                 f"({', '.join(bad[:4])}); use Title Case like the base CV")
    # Enforce the canonical base taxonomy: every agent group is mapped onto
    # a canonical group name; unknown groups are dropped with a warning.
    canonical = dict(base.get("skills", {}))
    if not canonical:
        return agent
    replaced = {}
    omit = set()
    for gname, gval in agent.items():
        target = _resolve_canonical(gname, gval, canonical)
        if target is None:
            warn(f"skill group '{gname}' does not map to any canonical group; dropping")
            continue
        if (gval or "").strip().upper() == "OMIT":
            omit.add(target)
            continue
        if target in replaced:
            replaced[target] = _merge_values(replaced[target], gval)
        else:
            replaced[target] = gval
    # start from canonical groups so the standard taxonomy is always present,
    # skipping any group the agent explicitly asked to omit (value "OMIT")
    skills = {}
    for c in canonical:
        if c in omit:
            continue
        if c in replaced:
            skills[c] = replaced[c]
        else:
            skills[c] = canonical[c]
    _dedup_skills(skills)
    return skills


def _dedup_skills(skills):
    """Drop a group when its values are fully covered by another group, and
    warn on duplicated skill tokens across groups."""
    def tokens(s):
        return {t.strip().lower() for t in s.split(",") if t.strip()}
    items = list(skills.items())
    removed = []
    for i, (g1, v1) in enumerate(items):
        if g1 in removed:
            continue
        t1 = tokens(v1)
        for g2, v2 in items:
            if g2 == g1 or g2 in removed:
                continue
            t2 = tokens(v2)
            if t1 and t1 <= t2:
                warn(f"skill group '{g1}' is a subset of '{g2}'; dropping")
                removed.append(g1)
                break
    for g in removed:
        skills.pop(g, None)
    seen = {}
    for gname, gval in skills.items():
        for t in tokens(gval):
            if t in seen and seen[t] != gname:
                warn(f"skill '{t}' appears in both '{seen[t]}' and '{gname}'")
            seen[t] = gname


def parse_certifications(changelog, base):
    certs = list(base.get("certifications", []))
    for name, body in split_sections(changelog, []):
        low = name.lower()
        if any(k in low for k in ("certifications", "certificazioni")):
            bullets = bullet_lines(body.splitlines())
            if bullets:
                # keep only lines that look like cert entries (contain issuer/date)
                filtered = [b for b in bullets if re.search(r"\d{4}", b) or
                            "|" in b or "Coursera" in b or "Platzi" in b]
                if filtered:
                    certs = filtered
                break
    return certs


def parse_languages(changelog, base):
    langs = list(base.get("languages", []))
    for name, body in split_sections(changelog, []):
        low = name.lower()
        if "languages" in low or "lingue" in low:
            b = [l for l in bullet_lines(body.splitlines()) if ":" in l]
            if b:
                return b
    return langs


def parse_education(changelog, base):
    edu = list(base.get("education", []))
    for name, body in split_sections(changelog, []):
        low = name.lower()
        if "education" in low or "istruzione" in low:
            bullets = bullet_lines(body.splitlines())
            extra = []
            for b in bullets:
                if "no changes" in b.lower() or "nessuna modific" in b.lower() or \
                   "mantieni" in b.lower():
                    continue
                if "corsi pertinenti" in b.lower() or "relevant coursework" in b.lower() or \
                   "selected coursework" in b.lower():
                    extra.append("Relevant coursework: " + b.split(":", 1)[1].strip())
            if extra:
                edu = edu + [{"title": "Relevant Coursework", "body": "", "line": extra[0]}]
            return edu
    return edu


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _clean_dash(s):
    """Replace long em/en dashes with a plain hyphen (AGENTS guideline)."""
    if not s:
        return s or ""
    return re.sub(r"[—–]", "-", s)


def _norm(s):
    s = (s or "").lower()
    s = re.sub(r"[—–\-/–/:,()&'\"*#|]", " ", s)
    return " ".join(s.split())


STOPWORDS = {"the", "to", "with", "master", "for", "and", "in", "of",
             "application", "platform", "system", "project", "real", "time",
             "data", "app", "mobile", "web", "full", "stack", "based", "using",
             "authentication", "services", "control", "software"}


def _tokens(s):
    return {w for w in _norm(s).split()
            if len(w) >= 4 and w not in STOPWORDS}


def _paren_name(s):
    """Extract the distinctive project name from '(Name)' parentheses."""
    m = re.findall(r"\(([^()]+)\)", s or "")
    if not m:
        return ""
    names = [p.strip() for p in m if p.strip()]
    for n in names:
        if n.lower() not in {"master's thesis", "master's", "thesis"} and \
           not re.search(r"(^|\s)(master|thesis|advisor|prof)($|\s)", n, re.I):
            return n
    return names[-1] if names else ""


def _score(a, b):
    """Return 2 on a confident match (parenthetical name or key present),
    1 on a partial token match, 0 otherwise."""
    a, b = a or "", b or ""
    if not a or not b:
        return 0
    # direct substring of key in title
    key = a.strip()
    if key and len(key) >= 3 and (key.lower() in b.lower() or b.lower() in key.lower()):
        return 2
    # parenthetical project names agree
    pa, pb = _paren_name(a).lower(), _paren_name(b).lower()
    if pa and pb and (pa in pb or pb in pa or pa == pb):
        return 2
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0
    if ta <= tb or tb <= ta:
        return 2
    inter = ta & tb
    return 1 if len(inter) >= 2 else 0


def _best_match(target, candidates, key_fn=None):
    """Return the candidate with the best score vs target (and its score)."""
    best_c, best_s = None, 0
    for c in candidates:
        cval = key_fn(c) if key_fn else c
        s = _score(target, cval)
        if s > best_s:
            best_c, best_s = c, s
    return best_c, best_s


def _strip_md(s):
    if not s:
        return s or ""
    s = re.sub(r"\*\*", "", s)
    return _clean_dash(s).strip()


def render_projects(base_projects, overrides, reorder, base, lang="en"):
    html = []
    if reorder:
        for item in reorder:
            item = item.strip()
            base_hit = None
            if base_projects:
                base_hit, bsc = _best_match(item, base_projects,
                                            key_fn=lambda p: p["title"])
                if bsc < 1:
                    base_hit = None
            best_ov = None
            if overrides:
                best_ov, osc = _best_match(
                    item, overrides.values(),
                    key_fn=lambda o: (o.get("title") or o.get("_key") or ""))
                if osc < 1:
                    best_ov = None
            # display title: override descriptive title if it differs from its
            # key, else the reorder item, else base title
            if best_ov and best_ov.get("title"):
                title = _strip_md(best_ov["title"])
            elif base_hit:
                title = base_hit["title"].strip()
            elif item:
                title = _strip_md(item)
            else:
                title = i18n(lang, "Project", MISC_I18N)
            if best_ov and best_ov["bullets"]:
                bullets = best_ov["bullets"]
            else:
                bullets = (base_hit["bullets"] if base_hit else [])
            date = base_hit["date"] if base_hit else ""
            html.append('<div class="entry">')
            html.append(f'<div class="entry-head"><span class="title">{esc(title)}</span></div>')
            if bullets:
                html.append("<ul>")
                for b in bullets:
                    html.append(f"<li>{esc(b)}</li>")
                html.append("</ul>")
            if base_hit and base_hit.get("key_skills") and not best_ov:
                html.append(f'<div class="key-skills"><b>{esc(i18n(lang, "Key Skills:", MISC_I18N))}</b> '
                            f'{esc(base_hit["key_skills"])}</div>')
            html.append("</div>")
            if best_ov:
                best_ov["_used"] = True
    else:
        for p in base_projects:
            if overrides:
                ov, ovs = _best_match(
                    p["title"], overrides.values(),
                    key_fn=lambda o: (o.get("title") or o.get("_key") or ""))
                if ovs < 1:
                    ov = None
            else:
                ov = None
            if ov:
                ov["_used"] = True
                title = _strip_md(ov["title"]) if ov.get("title") else p["title"].strip()
                bullets = ov["bullets"] or p["bullets"]
            else:
                title, bullets = p["title"].strip(), p["bullets"]
            html.append('<div class="entry">')
            html.append(f'<div class="entry-head"><span class="title">{esc(title)}</span></div>')
            if bullets:
                html.append("<ul><li>" + "</li><li>".join(esc(b) for b in bullets) +
                            "</li></ul>")
            if not ov and p.get("key_skills"):
                html.append(f'<div class="key-skills"><b>{esc(i18n(lang, "Key Skills:", MISC_I18N))}</b> '
                            f'{esc(p["key_skills"])}</div>')
            html.append("</div>")
    # any overrides not consumed
    for key, ov in overrides.items():
        if not ov.get("_used") and ov.get("title") and ov.get("bullets"):
            warn(f"project override '{key}' not matched to a base project; using as-is")
            html.append('<div class="entry">')
            html.append(f'<div class="entry-head"><span class="title">{esc(_strip_md(ov["title"]))}</span></div>')
            html.append("<ul><li>" + "</li><li>".join(esc(b) for b in ov["bullets"]) +
                        "</li></ul></div>")
    return "\n".join(html)


def render_skills(skills, lang="en"):
    if not skills:
        return ""
    groups = []
    for gname, gval in skills.items():
        label = i18n(lang, gname, SKILL_GROUPS_I18N)
        groups.append(f'<div class="skill-group">'
                      f'<b>{esc(label)}:</b> {esc(gval)}</div>')
    return "\n".join(groups)


def render_work(entries, base, lang="en"):
    if not entries:
        return ""
    html = [f'<section class="experience"><h2>{i18n(lang, "work", SECTION_HEADERS)}</h2>']
    for e in entries:
        html.append('<div class="entry"><div class="entry-head">'
                    f'<span class="title">{esc(_clean_dash(e["title"]))}</span></div><ul>')
        for b in e["bullets"]:
            html.append(f"<li>{esc(_strip_md(b))}</li>")
        html.append("</ul></div>")
    html.append("</section>")
    return "\n".join(html)


def _edu_meta(body):
    """City and country, e.g. 'Milano, Italy'. No graduation year."""
    cm = re.search(r"City[:：]\s*([^|]+)", body)
    city = cm.group(1).strip() if cm else ""
    co = re.search(r"Country[:：]\s*([^|]+)", body)
    country = co.group(1).strip() if co else ""
    return ", ".join(x for x in [city, country] if x)


def render_education(edu, base, lang="en"):
    if not edu:
        return ""
    items = list(edu)
    items.sort(key=lambda e: _edu_year(e), reverse=True)
    html = [f'<section class="education"><h2>{i18n(lang, "education", SECTION_HEADERS)}</h2>']
    for e in items:
        title = _clean_dash((e.get("title", "") or "").strip().split(" — ")[0])
        if title == "Relevant Coursework":
            title = i18n(lang, "Relevant Coursework", MISC_I18N)
        html.append(f'<div class="entry"><div class="entry-head">'
                    f'<span class="title">{esc(title)}</span>')
        body = e.get("body", "") or ""
        meta = _edu_meta(body)
        if meta:
            html.append(f'<span class="date">{esc(meta)}</span>')
        html.append("</div>")
        line = e.get("line")
        if line:
            if line.startswith("Relevant coursework:"):
                line = i18n(lang, "Relevant coursework:", MISC_I18N) + line.split(":", 1)[1]
            html.append(f'<div class="summary">{esc(line)}</div>')
        html.append("</div>")
    html.append("</section>")
    return "\n".join(html)


def _edu_year(e):
    m = re.search(r"\b(20\d\d)\b", e.get("body", "") or "")
    return int(m.group(1)) if m else 0


def render_certifications(certs, lang="en"):
    if not certs:
        return ""
    html = [f'<section class="certifications"><h2>{i18n(lang, "certifications", SECTION_HEADERS)}</h2>'
            '<ul class="certs">']
    for c in certs:
        html.append(f"<li>{esc(_strip_md(c))}</li>")
    html.append("</ul></section>")
    return "\n".join(html)


def render_languages(langs, lang="en"):
    if not langs:
        return ""
    html = [f'<section class="languages"><h2>{i18n(lang, "languages", SECTION_HEADERS)}</h2>'
            '<ul class="lang">']
    for l in langs:
        html.append(f"<li>{esc(l)}</li>")
    html.append("</ul></section>")
    return "\n".join(html)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def _md_paragraphs(md):
    """Split a simple cover-letter markdown file into (text, html) blocks."""
    blocks = re.split(r"\n\s*\n", md.strip())
    out = []
    for b in blocks:
        lines = [_strip_md(l.rstrip()) for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        joined = " ".join(lines)
        out.append(("text", joined))
    return out


def build_cover_letter(app_dir, app_name, base, lang="en"):
    cl_path = os.path.join(app_dir, "cover_letter.md")
    if not os.path.exists(cl_path):
        warn(f"no cover_letter.md for {app_name}; skipping cover letter PDF")
        return
    text = open(cl_path, encoding="utf-8").read()
    blocks = _md_paragraphs(text)

    html_parts = []
    for kind, content in blocks:
        if kind == "text":
            low = content.lower()
            cls = ""
            if re.match(r"^(dear|gentile|egregio|e.g\.)", low) or \
               content.rstrip().endswith(",") and "regards" not in low and \
               "sincerely" not in low and "cordialm" not in low and len(content) < 200:
                cls = ' class="salutation"'
            elif re.search(r"\bregards\b|\bsincere\b|\bcordealmente\b|\bcordiali saluti\b|"
                           r"\bcordiali\b|\bsaluti\b", low) or low.startswith("best "):
                cls = ' class="signoff"'
            html_parts.append(f"<p{cls}>{esc(content)}</p>")
        else:
            html_parts.append(f"<div>{esc(content)}</div>")

    template = open(CL_TEMPLATE, encoding="utf-8").read()
    placeholders = {
        "NAME": esc(base.get("name", NAME)),
        "CONTENT": "\n".join(html_parts),
        "LANG": lang,
    }
    for key, val in placeholders.items():
        template = template.replace("{{ " + key + " }}", val)
    leftover = re.findall(r"\{\{\s*\w+\s*\}\}", template)
    if leftover:
        warn(f"cover letter unresolved placeholders: {sorted(set(leftover))}")

    html_path = os.path.join(app_dir, CL_STEM + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"wrote {html_path}")

    pdf_path = os.path.join(app_dir, CL_STEM + ".pdf")
    render_pdf(html_path, pdf_path, app_dir)
    verify_pdf(pdf_path, expected_pages={1, 2})


def main():
    if len(sys.argv) < 2:
        print('Usage: python build_cv.py "<group>/<created>-<company-role>"', file=sys.stderr)
        sys.exit(2)
    app = sys.argv[1]
    app_dir = os.path.join(REPO, "applications", app)
    changelog_path = os.path.join(app_dir, "cv_changes.md")
    yaml_path = os.path.join(app_dir, "application.yaml")
    if not os.path.exists(changelog_path):
        print(f"error: missing {changelog_path}", file=sys.stderr)
        sys.exit(1)

    base = parse_base_cv(open(PROFILE_CV, encoding="utf-8-sig").read())
    changelog = open(changelog_path, encoding="utf-8-sig").read()
    lang = lang_from_yaml(yaml_path)

    summary = parse_summary(changelog) or base.get("about")
    work = parse_work(changelog, base)
    if work is _WORK_OMIT:
        work = []  # explicitly omitted — render nothing
    elif not work:
        # no work section in changelog at all — fall back to base CV
        work_body = find_section(open(PROFILE_CV, encoding="utf-8-sig").read(),
                                 "work experience", "esperienza lavorativa")
        if work_body:
            hm = re.search(r"^###\s+(.+)$", work_body, re.M)
            t = hm.group(1).strip() if hm else "Freelance AI Data Curator"
            work = [{"title": t, "bullets": bullet_lines(work_body.splitlines())}]
    overrides, reorder = parse_project_overrides(changelog)
    skills = parse_skills(changelog, base)
    certs = parse_certifications(changelog, base)
    langs = parse_languages(changelog, base)
    edu = parse_education(changelog, base)

    template = open(TEMPLATE, encoding="utf-8").read()

    placeholders = {
        "NAME": esc(base.get("name", NAME)),
        "EMAIL": esc(contact_email(yaml_path, base.get("contact", {}).get("Email address", ""))),
        "PHONE": esc(base.get("contact", {}).get("Phone number", "")),
        "LOCATION": esc(base.get("contact", {}).get("City", "")),
        "LINKEDIN": esc(base.get("contact", {}).get("LinkedIn", "")),
        "GITHUB": esc(base.get("contact", {}).get("GitHub", "")),
        "SUMMARY": esc(summary),
        "SUMMARY_HEADER": i18n(lang, "summary", SECTION_HEADERS),
        "PROJECTS_HEADER": i18n(lang, "projects", SECTION_HEADERS),
        "SKILLS_HEADER": i18n(lang, "skills", SECTION_HEADERS),
        "WORK_EXPERIENCE": render_work(work, base, lang),
        "PROJECTS": render_projects(base["projects"], overrides, reorder, base, lang),
        "SKILLS": render_skills(skills, lang),
        "EDUCATION": render_education(edu, base, lang),
        "CERTIFICATIONS": render_certifications(certs, lang),
        "EXTRAS": render_languages(langs, lang),
        "LANG": lang,
    }

    for key, val in placeholders.items():
        template = template.replace("{{ " + key + " }}", val)

    leftover = re.findall(r"\{\{\s*\w+\s*\}\}", template)
    if leftover:
        warn(f"unresolved placeholders: {sorted(set(leftover))}")

    html_path = os.path.join(app_dir, CV_STEM + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"wrote {html_path}")

    pdf_path = os.path.join(app_dir, CV_STEM + ".pdf")
    n_exp = expected_pages(yaml_path)
    render_pdf(html_path, pdf_path, app_dir)
    verify_pdf(pdf_path, expected_pages=n_exp)

    build_cover_letter(app_dir, app, base, lang)

    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s) emitted:", file=sys.stderr)
        for w in WARNINGS:
            print(f"  - {w}", file=sys.stderr)


def render_pdf(html_path, pdf_path, app_dir):
    edge = next((p for p in EDGE_CANDIDATES if os.path.exists(p)), None)
    if not edge:
        print("error: Edge not found. Install msedge or set EDGE_CANDIDATES.", file=sys.stderr)
        sys.exit(1)
    html_url = "file:///" + html_path.replace("\\", "/")
    # write PDF into app dir via Windows absolute path
    cmd = [edge, "--headless", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}",
           html_url]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(pdf_path):
        print("error: Edge failed to produce PDF.", file=sys.stderr)
        print("stdout:", res.stdout[-2000:], file=sys.stderr)
        print("stderr:", res.stderr[-2000:], file=sys.stderr)
        sys.exit(1)
    print(f"wrote {pdf_path}")


def verify_pdf(pdf_path, expected_pages=None):
    import pymupdf
    doc = pymupdf.open(pdf_path)
    n = doc.page_count
    text = ""
    for page in doc:
        text += page.get_text()
    lowered = text.lower()
    issues = []
    print(f"[verify] pages={n}, chars={len(text.strip())}")
    if expected_pages is not None:
        allowed = expected_pages if isinstance(expected_pages, (list, tuple, set)) else {expected_pages}
        if n > max(allowed):
            warn(f"page count {n} exceeds the suggested {sorted(allowed)} for this role "
                 "(limit is flexible; consider tightening content or font size)")
    if "{{" in text:
        issues.append("placeholder leftovers found in PDF text")
    if issues:
        for i in issues:
            print(f"[verify] FAIL: {i}")
        sys.exit(1)
    print("[verify] OK")


if __name__ == "__main__":
    main()
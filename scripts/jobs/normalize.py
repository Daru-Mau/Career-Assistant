"""Canonical forms for URLs, companies, titles, and untrusted text."""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {
    "gh_src",
    "ref",
    "referrer",
    "source",
    "src",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "trk",
    "trackingid",
    "lever-source",
    "lever-origin",
    "campaign",
}

LEGAL_SUFFIXES = (
    "gmbh",
    "gmbh & co kg",
    "gmbh and co kg",
    "ag",
    "inc",
    "incorporated",
    "ltd",
    "limited",
    "llc",
    "plc",
    "s.p.a",
    "s p a",
    "spa",
    "s.r.l",
    "s r l",
    "srl",
    "s.a.s",
    "s a s",
    "sas",
    "s.a",
    "s a",
    "sa",
    "b.v",
    "b v",
    "bv",
    "n.v",
    "n v",
    "nv",
    "oy",
    "oyj",
    "ab",
    "as",
    "aps",
    "kft",
    "sp. z o.o",
    "sp z o o",
    "z o o",
)

ZERO_WIDTH = dict.fromkeys(
    map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"), None
)

HIDDEN_BLOCK_RE = re.compile(
    r"<(script|style|noscript)\b[^>]*>.*?</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
HIDDEN_ATTR_RE = re.compile(
    r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*"
    r"(?:hidden|display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0)"
    r"[^>]*>.*?</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
PUNCT_RE = re.compile(r"[^a-z0-9 ]+")

INJECTION_PATTERNS = (
    "ignore previous",
    "ignore all previous",
    "disregard previous",
    "disregard all previous",
    "new instructions",
    "system prompt",
    "as an ai",
    "you are now",
    "run the following",
    "execute the following",
    "send your cv to",
    "send your resume to",
    "email your cv to",
    "email your resume to",
    "reveal your",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _is_tracking(key: str) -> bool:
    lowered = key.strip().lower()
    return lowered in TRACKING_KEYS or any(
        lowered.startswith(prefix) for prefix in TRACKING_PREFIXES
    )


def canonical_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = (parsed.scheme or "https").lower()
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"not an absolute URL: {url!r}")

    port = parsed.port
    netloc = host
    if port and not (
        (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    ):
        netloc = f"{host}:{port}"

    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not _is_tracking(key)
    ]
    query = urlencode(sorted(pairs))
    return urlunsplit((scheme, netloc, path, query, ""))


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode("ascii")


def normalize_company(name: str) -> str:
    text = _fold(name).lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    changed = True
    while changed:
        changed = False
        for suffix in LEGAL_SUFFIXES:
            pattern = rf"(?:^|\s){re.escape(suffix)}$"
            if re.search(pattern, text):
                text = re.sub(pattern, "", text).strip()
                changed = True
    return text


def normalize_title(title: str) -> str:
    text = _fold(title).lower()
    text = re.sub(r"\((?:m|f|d|w|x|k|\s|/)+\)", " ", text)
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_location(location: str) -> str:
    text = _fold(location).lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def dedup_key(company_norm: str, title_norm: str, location_norm: str) -> str:
    payload = "|".join((company_norm, title_norm, location_norm))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def strip_hidden_text(raw_html: str) -> str:
    text = HIDDEN_BLOCK_RE.sub(" ", raw_html)
    text = COMMENT_RE.sub(" ", text)
    text = HIDDEN_ATTR_RE.sub(" ", text)
    text = text.translate(ZERO_WIDTH)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return WHITESPACE_RE.sub(" ", text).strip()


def detect_injection_phrases(text: str) -> list[str]:
    lowered = _fold(text).lower()
    return [phrase for phrase in INJECTION_PATTERNS if phrase in lowered]


def extract_email_addresses(text: str) -> list[str]:
    seen: list[str] = []
    for match in EMAIL_RE.findall(text):
        lowered = match.lower()
        if lowered not in seen:
            seen.append(lowered)
    return seen

"""TinyFish wrapper: Search + Fetch, with allowlist filtering and error mapping.

Endpoints and parameters here come from the official TinyFish docs
(https://docs.tinyfish.ai). Re-check the docs before adding new parameters.
"""
import hashlib
from urllib.parse import urlparse

import httpx

from app.config import settings

SEARCH_URL = "https://api.search.tinyfish.ai"
FETCH_URL = "https://api.fetch.tinyfish.ai"

SEARCH_TIMEOUT_SECONDS = 30
FETCH_TIMEOUT_SECONDS = 150  # docs: client timeout 150 s
MAX_SOURCES = 3  # keep quota use and demo time small

# Official-domain allowlist per destination (nationality: India, student visa)
OFFICIAL_DOMAINS = {
    "Germany": ["diplo.de"],
    "United Kingdom": ["gov.uk"],
    "Canada": ["canada.ca"],
}

# One search query per corridor; site: restricts results to the official domain
SEARCH_QUERIES = {
    "Germany": "site:india.diplo.de national visa student documents required",
    "United Kingdom": "site:gov.uk student visa documents you must provide",
    "Canada": "site:canada.ca study permit apply documents India",
}

# Optional extra filter: if a corridor is listed here, the URL path must start
# with one of these prefixes. Keeps the UK on Student visa pages only
# (not Graduate visa or Short-term study visa pages).
REQUIRED_PATH_PREFIXES = {
    "United Kingdom": ["/student-visa"],
}

# TinyFish error codes that mean "blocked"; every other failure becomes "error".
# Both end up as "could not verify" in the UI.
BLOCKED_CODES = {"bot_blocked", "login_required"}


class TinyFishError(Exception):
    """Raised when a TinyFish call fails as a whole (e.g. search is down)."""


def _headers() -> dict:
    return {"X-API-Key": settings.TINYFISH_API_KEY}


def is_official(url: str, destination: str) -> bool:
    """True only if the URL's host is an allowlisted domain or a subdomain of one."""
    host = (urlparse(url).hostname or "").lower()
    for domain in OFFICIAL_DOMAINS.get(destination, []):
        if host == domain or host.endswith("." + domain):
            return True
    return False


def _path_ok(url: str, destination: str) -> bool:
    """True if the corridor has no path rule, or the URL path matches one."""
    prefixes = REQUIRED_PATH_PREFIXES.get(destination)
    if not prefixes:
        return True
    path = urlparse(url).path.lower()
    return any(path.startswith(p) for p in prefixes)


def content_hash(text: str) -> str:
    """SHA-256 fingerprint of page text. Same text -> same hash."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def search(query: str) -> list[dict]:
    """Raw TinyFish Search. Returns the list of results (position, title, url...)."""
    try:
        resp = httpx.get(
            SEARCH_URL,
            headers=_headers(),
            params={"query": query, "location": "IN", "language": "en"},
            timeout=SEARCH_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise TinyFishError(f"Search request failed: {exc}") from exc

    if resp.status_code != 200:
        raise TinyFishError(f"Search returned HTTP {resp.status_code}")
    return resp.json().get("results", [])


def search_official(destination: str) -> list[dict]:
    """Search for the corridor's official pages and keep only allowlisted URLs.

    Returns a ranked list: [{"url": ..., "rank": 1, "title": ...}, ...]
    An empty list means "no official source found" (never guess a checklist).
    """
    query = SEARCH_QUERIES.get(destination)
    if query is None:
        return []

    kept, seen = [], set()
    for result in search(query):
        url = result.get("url", "")
        if (not url or url in seen
                or not is_official(url, destination)
                or not _path_ok(url, destination)):
            continue
        seen.add(url)
        kept.append({"url": url, "rank": len(kept) + 1, "title": result.get("title", "")})
        if len(kept) == MAX_SOURCES:
            break
    return kept


def fetch(urls: list[str]) -> list[dict]:
    """Fetch pages as markdown. Returns exactly one dict per requested URL:

    {"url", "final_url", "status": "ok"|"blocked"|"error",
     "text", "error_code", "raw_error"}
    """
    if not urls:
        return []
    if len(urls) > 10:
        raise ValueError("TinyFish Fetch accepts at most 10 URLs per call")

    def failed(url: str, code: str, raw=None) -> dict:
        status = "blocked" if code in BLOCKED_CODES else "error"
        return {"url": url, "final_url": url, "status": status,
                "text": "", "error_code": code, "raw_error": raw}

    try:
        resp = httpx.post(
            FETCH_URL,
            headers=_headers(),
            json={"urls": urls, "format": "markdown"},
            timeout=FETCH_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException:
        return [failed(u, "timeout") for u in urls]
    except httpx.HTTPError as exc:
        return [failed(u, "request_failed", str(exc)) for u in urls]

    if resp.status_code != 200:
        return [failed(u, f"http_{resp.status_code}") for u in urls]

    body = resp.json()
    pages: dict[str, dict] = {}

    for r in body.get("results", []):
        url = r.get("url", "")
        text = (r.get("text") or "").strip()
        if not text:
            pages[url] = failed(url, "empty_content")
            continue
        pages[url] = {"url": url, "final_url": r.get("final_url", url),
                      "status": "ok", "text": text,
                      "error_code": None, "raw_error": None}

    for e in body.get("errors", []):
        url = e.get("url", "")
        # Verified from a real response: the field is "error" (older guess: "code")
        code = e.get("error") or e.get("code") or "unknown_error"
        pages[url] = failed(url, code, e)

    # One entry per requested URL, in order. Anything TinyFish did not report
    # is treated as an error, never as success.
    return [pages.get(u) or failed(u, "no_response") for u in urls]
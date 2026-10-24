from datetime import datetime, timezone

import requests

from app.config import TINYFISH_API_KEY

SEARCH_URL = "https://api.search.tinyfish.ai"
FETCH_URL = "https://api.fetch.tinyfish.ai"


def _headers():
    return {"X-API-Key": TINYFISH_API_KEY}


def search(query: str) -> dict:
    """TinyFish Search. Returns {ok, results, error}."""
    if not TINYFISH_API_KEY:
        return {"ok": False, "results": [], "error": "TINYFISH_API_KEY missing in .env"}
    try:
        r = requests.get(
            SEARCH_URL, headers=_headers(), params={"query": query}, timeout=30
        )
    except requests.RequestException as e:
        return {"ok": False, "results": [], "error": f"Network error: {e}"}

    if r.status_code != 200:
        return {
            "ok": False,
            "results": [],
            "error": f"Search failed with status {r.status_code}",
        }

    data = r.json()
    results = [
        {
            "position": item.get("position"),
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "url": item.get("url"),
        }
        for item in data.get("results", [])
    ]
    return {"ok": True, "results": results, "error": None}


def fetch_page(url: str) -> dict:
    """TinyFish Fetch for ONE url. If it fails, ok is False => 'could not verify'."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    failed = {
        "ok": False,
        "url": url,
        "title": None,
        "text": "",
        "fetched_at": fetched_at,
        "error": "could not verify",
    }
    if not TINYFISH_API_KEY:
        failed["error"] = "could not verify: TINYFISH_API_KEY missing"
        return failed
    try:
        r = requests.post(
            FETCH_URL,
            headers=_headers(),
            json={"urls": [url], "format": "markdown"},
            timeout=60,
        )
    except requests.RequestException as e:
        failed["error"] = f"could not verify: network error ({e})"
        return failed

    if r.status_code != 200:
        failed["error"] = f"could not verify: status {r.status_code}"
        return failed

    data = r.json()
    pages = data.get("results") or []
    if not pages:
        errors = data.get("errors") or []
        reason = errors[0].get("error") if errors else "no content returned"
        failed["error"] = f"could not verify: {reason}"
        return failed

    page = pages[0]
    text = page.get("text")
    if not isinstance(text, str) or not text.strip():
        failed["error"] = "could not verify: empty page text"
        return failed

    return {
        "ok": True,
        "url": page.get("final_url") or url,
        "title": page.get("title"),
        "text": text,
        "fetched_at": fetched_at,
        "error": None,
    }


if __name__ == "__main__":
    # Quick self-test: python -m app.services.tinyfish
    s = search("Germany student visa requirements")
    print("SEARCH ok:", s["ok"], "| error:", s["error"], "| results:", len(s["results"]))
    for item in s["results"][:3]:
        print(" -", item["title"], "->", item["url"])

    if s["ok"] and s["results"]:
        p = fetch_page(s["results"][0]["url"])
        print("FETCH ok:", p["ok"], "| error:", p["error"])
        print("Text length:", len(p["text"]))
        print(p["text"][:300])
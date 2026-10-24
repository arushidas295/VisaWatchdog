import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
HEADERS = {"X-API-Key": os.getenv("TINYFISH_API_KEY")}

CORRIDORS = {
    "India -> Germany (student)": "National visa study requirements site:india.diplo.de",
    "India -> UK (student)": "Student visa how to apply documents site:gov.uk",
    "India -> Canada (study permit)": "Study permit documents required India site:canada.ca",
}

for label, query in CORRIDORS.items():
    print("\n==========", label)
    s = httpx.get(
        "https://api.search.tinyfish.ai",
        params={"query": query, "location": "IN", "language": "en"},
        headers=HEADERS,
        timeout=30,
    )
    results = s.json().get("results", []) if s.status_code == 200 else []
    print("Search status:", s.status_code, "| results:", len(results))
    if not results:
        print("COULD NOT FIND OFFICIAL SOURCE")
        continue
    url = results[0]["url"]
    print("Top result:", url)
    f = httpx.post(
        "https://api.fetch.tinyfish.ai",
        json={"urls": [url], "format": "markdown"},
        headers=HEADERS,
        timeout=150,
    )
    data = f.json()
    for page in data.get("results", []):
        print("Fetched OK | text length:", len(page.get("text") or ""))
    for err in data.get("errors", []):
        print("COULD NOT VERIFY ->", err.get("error"))

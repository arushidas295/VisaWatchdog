import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
KEY = os.getenv("TINYFISH_API_KEY")
HEADERS = {"X-API-Key": KEY}

if not KEY:
    raise SystemExit("TINYFISH_API_KEY is empty in backend/.env")

# 1) SEARCH
print("=== SEARCH ===")
r = httpx.get(
    "https://api.search.tinyfish.ai",
    params={"query": "Germany student visa requirements India embassy", "location": "IN", "language": "en"},
    headers=HEADERS,
    timeout=30,
)
print("Status:", r.status_code)
if r.status_code != 200:
    raise SystemExit(r.text)

results = r.json().get("results", [])
for item in results:
    print(item["position"], item["site_name"], "->", item["url"])

if not results:
    raise SystemExit("No search results")

# 2) FETCH the first result
url = results[0]["url"]
print("\n=== FETCH ===")
print("Fetching:", url)
r = httpx.post(
    "https://api.fetch.tinyfish.ai",
    json={"urls": [url], "format": "markdown"},
    headers=HEADERS,
    timeout=150,
)
print("Status:", r.status_code)
data = r.json()

for page in data.get("results", []):
    text = page.get("text") or ""
    print("Title:", page.get("title"))
    print("Text length:", len(text))
    print("First 300 characters:\n", text[:300])

for err in data.get("errors", []):
    print("COULD NOT VERIFY:", err.get("url"), "->", err.get("error"))

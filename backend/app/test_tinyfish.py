import os

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("TINYFISH_API_KEY", "")

if not KEY:
    print("TINYFISH_API_KEY nahi mili. .env check karo.")
    raise SystemExit

headers = {"X-API-Key": KEY}

print("=== SEARCH ===")
r = requests.get(
    "https://api.search.tinyfish.ai",
    headers=headers,
    params={"query": "Germany student visa requirements"},
    timeout=30,
)
print("Status:", r.status_code)
print(r.text[:1500])

print()
print("=== FETCH ===")
r = requests.post(
    "https://api.fetch.tinyfish.ai",
    headers=headers,
    json={"urls": ["https://example.com"], "format": "markdown"},
    timeout=60,
)
print("Status:", r.status_code)
print(r.text[:1500])
# backend/app/services/extractor.py
import json
import httpx
from app.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a visa requirements extractor.
Extract all document and eligibility requirements from the given text.

RULES (strictly follow these):
1. Every item MUST include a "passage" field: an exact verbatim quote copied word-for-word from the source text.
2. If you cannot find a direct quote for a requirement, do NOT include that item.
3. Return ONLY valid JSON — no explanation, no markdown, no code fences.
4. "required" is true if mandatory, false if optional.

Return this exact format:
{
  "items": [
    {
      "name": "short name of requirement",
      "required": true,
      "details": "any extra detail",
      "passage": "exact verbatim quote from the source text"
    }
  ]
}"""

MAX_CHARS = 12000


def _validate_items(items: list, source_text: str) -> list:
    valid = []
    for item in items:
        passage = item.get("passage", "").strip()
        if not passage:
            continue
        if passage in source_text:
            valid.append(item)
        else:
            print(f"[extractor] Dropping '{item.get('name')}': passage not found")
    return valid


async def extract_requirements(raw_text: str) -> list[dict]:
    if not settings.LLM_API_KEY:
        print("[extractor] No LLM_API_KEY set")
        return []

    truncated = raw_text[:MAX_CHARS]

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract visa requirements from this text:\n\n{truncated}"}
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(GROQ_URL, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"[extractor] Groq error {response.status_code}: {response.text[:500]}")
                return []

        data = response.json()
        raw_output = data["choices"][0]["message"]["content"].strip()

        if raw_output.startswith("```"):
            parts = raw_output.split("```")
            raw_output = parts[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]

        parsed = json.loads(raw_output)
        items = parsed.get("items", [])
        valid_items = _validate_items(items, raw_text)
        print(f"[extractor] {len(valid_items)} valid items (dropped {len(items)-len(valid_items)})")
        return valid_items

    except Exception as e:
        print(f"[extractor] Failed: {e}")
        return []
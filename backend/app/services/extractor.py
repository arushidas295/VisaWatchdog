# backend/app/services/extractor.py
import json
import httpx
from app.config import settings

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-1.5-flash:generateContent?key={{api_key}}"
)

PROMPT_TEMPLATE = """You are a visa requirements extractor.

Given the text below from an official visa information page, extract all document
and eligibility requirements as a JSON object.

RULES (strictly follow these):
1. Every item MUST include a "passage" field: an exact verbatim quote copied
   word-for-word from the source text below.
2. If you cannot find a direct quote for a requirement, do NOT include that item.
3. Return ONLY valid JSON — no explanation, no markdown, no code fences.
4. "required" is true if the item is mandatory, false if optional.

Return this exact format:
{{
  "items": [
    {{
      "name": "short name of requirement",
      "required": true,
      "details": "any extra detail",
      "passage": "exact verbatim quote from the source text"
    }}
  ]
}}

Source text:
{source_text}
"""

MAX_CHARS = 12000  # Gemini 1.5 Flash handles this easily


def _build_prompt(text: str) -> str:
    # Truncate very long pages to avoid token limits
    truncated = text[:MAX_CHARS]
    return PROMPT_TEMPLATE.format(source_text=truncated)


def _validate_items(items: list, source_text: str) -> list:
    """Drop any item whose passage does not appear in the source text."""
    valid = []
    for item in items:
        passage = item.get("passage", "").strip()
        if not passage:
            continue  # No passage = drop
        if passage in source_text:
            valid.append(item)
        else:
            print(f"[extractor] Dropping item '{item.get('name')}': passage not found in source")
    return valid


async def extract_requirements(raw_text: str) -> list[dict]:
    """
    Send raw page text to Gemini and return validated checklist items.
    Returns an empty list if extraction fails.
    """
    if not settings.LLM_API_KEY:
        print("[extractor] No LLM_API_KEY set, skipping extraction")
        return []

    prompt = _build_prompt(raw_text)
    url = GEMINI_URL.format(api_key=settings.LLM_API_KEY)

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()

        # Pull the text out of Gemini's response structure
        raw_output = (
            data["candidates"][0]["content"]["parts"][0]["text"]
        )

        # Clean up in case Gemini wraps in markdown code fences
        raw_output = raw_output.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]

        parsed = json.loads(raw_output)
        items = parsed.get("items", [])

        # Validate: passage must exist in source text
        valid_items = _validate_items(items, raw_text)
        print(f"[extractor] {len(valid_items)} valid items (dropped {len(items) - len(valid_items)})")
        return valid_items

    except Exception as e:
        print(f"[extractor] Extraction failed: {e}")
        return []
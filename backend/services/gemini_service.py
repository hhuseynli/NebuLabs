from __future__ import annotations

import json
import os

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency during local bootstrap
    genai = None


def _configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and genai is not None


async def generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    if not _configured():
        return ""

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = await client.aio.models.generate_content(model=model, contents=prompt)

    text = getattr(response, "text", None)
    if text:
        return text.strip()

    # Some SDK responses expose content in candidates/parts rather than .text
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        candidate = candidates[0]
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if parts and len(parts) > 0:
            part_text = getattr(parts[0], "text", "")
            return (part_text or "").strip()

    return ""


async def generate_json(prompt: str, fallback: dict, model: str = "gemini-2.0-flash") -> dict:
    text = await generate_text(prompt, model=model)
    if not text:
        return fallback

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return fallback

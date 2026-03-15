from __future__ import annotations

import asyncio
import json
import os

try:
    from groq import AsyncGroq
except Exception:  # pragma: no cover - optional dependency during local bootstrap
    AsyncGroq = None


MODEL = "llama-3.3-70b-versatile"

MOCK_RESPONSES = {
    "faq": '{"answer": "To get started, install the SDK and run the quickstart guide. Several members have shared setup tutorials in this community.", "source_excerpt": "Here is how I set this up in 10 minutes...", "confidence": 0.88}',
    "sentiment": '{"score": 72, "label": "healthy", "summary": "Community is broadly positive and active. Some friction around beginner questions.", "trending_topics": ["Flutter", "Firebase", "state management"], "friction_signals": ["Beginner questions receiving dismissive responses"], "churn_risk_members": ["u/silent_dev_99"]}',
    "fundraiser_detect": '{"detected": true, "need": "venue for monthly meetup", "confidence": 0.88, "trigger_post_id": null}',
    "fundraiser_post": '{"title": "Community Goal: Meetup Venue Fund", "body": "Hey everyone! We noticed many of you have been asking about a proper venue for our next meetup. Let\'s make it happen together!", "goal_amount": 300, "deadline_days": 14}',
}


def _configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY")) and AsyncGroq is not None


def parse_json(raw: str) -> dict:
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


async def generate_text(prompt: str, model: str = MODEL, mock_key: str | None = None) -> str:
    if os.getenv("USE_MOCK", "false").lower() == "true" and mock_key:
        return MOCK_RESPONSES.get(mock_key, '{"mock": true}')

    if not _configured():
        return MOCK_RESPONSES.get(mock_key, "") if mock_key else ""

    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            if "429" in str(exc) and attempt < 2:
                await asyncio.sleep(2 ** (attempt + 1))
                continue
            return MOCK_RESPONSES.get(mock_key, "") if mock_key else ""

    return MOCK_RESPONSES.get(mock_key, "") if mock_key else ""


async def generate_json(
    prompt: str,
    fallback: dict,
    model: str = MODEL,
    mock_key: str | None = None,
) -> dict:
    text = await generate_text(prompt, model=model, mock_key=mock_key)
    if not text:
        return fallback

    try:
        return parse_json(text)
    except Exception:
        return fallback

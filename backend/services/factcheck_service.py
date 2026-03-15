from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from models.community import Post
from services import gemini_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_FACTCHECK_CACHE: dict[str, dict] = {}

KEYWORDS_SUPPORTED = ["official", "documented", "recommended", "supported"]
KEYWORDS_CONTRADICTED = ["always", "never", "100%", "guaranteed", "all", "none"]


def _read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _fallback_verdicts(post: Post) -> list[dict]:
    text = f"{post.title}. {post.body}".strip()
    claim = text[:220] if text else "No clear claim found"
    lower = text.lower()

    if any(word in lower for word in KEYWORDS_CONTRADICTED):
        verdict = "contradicted"
        explanation = "This uses absolute language and is likely too broad for a reliable technical claim."
        confidence = 0.78
    elif any(word in lower for word in KEYWORDS_SUPPORTED):
        verdict = "supported"
        explanation = "This aligns with generally accepted developer guidance."
        confidence = 0.71
    else:
        verdict = "unverified"
        explanation = "There is not enough concrete evidence in the post to verify this confidently."
        confidence = 0.64

    return [
        {
            "claim": claim,
            "verdict": verdict,
            "explanation": explanation,
            "confidence": confidence,
        }
    ]


def _overall_from_verdicts(verdicts: list[dict]) -> str:
    verdict_values = [item.get("verdict") for item in verdicts]
    if verdict_values and all(value == "supported" for value in verdict_values):
        return "all_supported"
    if "contradicted" in verdict_values:
        return "contains_errors"
    return "mostly_unverified"


def get_cached_result(post_id: str) -> dict | None:
    return _FACTCHECK_CACHE.get(post_id)


async def analyze_post(post: Post) -> dict:
    fallback_verdicts = _fallback_verdicts(post)
    fallback = {"verdicts": fallback_verdicts}

    prompt = _read_prompt("factcheck_analyze.txt").format(
        title=post.title,
        body=post.body,
    )
    payload = await gemini_service.generate_json(prompt, fallback=fallback)

    verdicts = payload.get("verdicts") if isinstance(payload, dict) else None
    if not isinstance(verdicts, list) or not verdicts:
        verdicts = fallback_verdicts

    normalized: list[dict] = []
    for raw in verdicts:
        if not isinstance(raw, dict):
            continue
        verdict = raw.get("verdict")
        if verdict not in {"supported", "unverified", "contradicted"}:
            verdict = "unverified"
        normalized.append(
            {
                "claim": str(raw.get("claim") or post.title),
                "verdict": verdict,
                "explanation": str(raw.get("explanation") or "No explanation provided."),
                "confidence": float(raw.get("confidence") or 0.5),
            }
        )

    if not normalized:
        normalized = fallback_verdicts

    result = {
        "post_id": post.id,
        "verdicts": normalized,
        "overall": _overall_from_verdicts(normalized),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    _FACTCHECK_CACHE[post.id] = result
    return result

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from db import queries
from services import gemini_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
POSITIVE = {"thanks", "great", "helpful", "love", "awesome", "nice", "works"}
NEGATIVE = {"stuck", "broken", "hate", "bad", "confusing", "issue", "problem"}


def _read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _label(score: int) -> str:
    if score >= 70:
        return "healthy"
    if score >= 40:
        return "neutral"
    return "at risk"


def _heuristic_score(texts: list[str]) -> int:
    pos = 0
    neg = 0
    for text in texts:
        lower = text.lower()
        pos += sum(1 for token in POSITIVE if token in lower)
        neg += sum(1 for token in NEGATIVE if token in lower)
    base = 55 + (pos * 4) - (neg * 5)
    return max(0, min(100, base))


async def build_report(community_id: str) -> dict:
    cached = queries.get_cached_sentiment(community_id=community_id, max_age_minutes=5)
    if cached:
        return {
            **cached,
            "cached": True,
        }

    posts = queries.list_community_posts(community_id=community_id, limit=100, offset=0)
    post_texts = [f"{p.title}. {p.body}" for p in posts]
    comments = []
    for post in posts[:50]:
        comments.extend(queries.list_post_comments(post.id)[:4])
    comment_texts = [c.body for c in comments]

    score = _heuristic_score(post_texts + comment_texts)
    default_topics = []
    if posts:
        default_topics = [p.title.split(" ")[0] for p in posts[:4] if p.title]
    fallback = {
        "summary": "Community discussion is moving, with pockets of helpful collaboration and a few unresolved friction points.",
        "trending_topics": default_topics or ["onboarding", "tooling", "debugging"],
        "friction_signals": [
            "Some questions are unresolved for too long",
            "Repeated beginner questions indicate missing onboarding references",
        ],
        "churn_risk_members": [],
    }

    context = "\n".join((post_texts + comment_texts)[:220])
    payload = fallback
    if context:
        prompt = _read_prompt("sentiment_report.txt").format(context=context)
        payload = await gemini_service.generate_json(prompt, fallback=fallback)

    report = {
        "score": score,
        "label": _label(score),
        "summary": str(payload.get("summary") or fallback["summary"]),
        "trending_topics": payload.get("trending_topics") or fallback["trending_topics"],
        "friction_signals": payload.get("friction_signals") or fallback["friction_signals"],
        "churn_risk_members": payload.get("churn_risk_members") or fallback["churn_risk_members"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cached": False,
    }
    queries.cache_sentiment(community_id=community_id, report=report)
    return report

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

from db import queries
from services import groq_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
FAQ_CACHE_TTL_SECONDS = 300
_FAQ_CACHE: dict[tuple[str, str], tuple[dict, datetime]] = {}


def _read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _find_source_post_id(posts: list, question: str) -> str | None:
    tokens = {token for token in question.lower().split() if len(token) > 3}
    for post in posts:
        text = f"{post.title} {post.body}".lower()
        if any(token in text for token in tokens):
            return post.id
    return posts[0].id if posts else None


async def answer_question(community_id: str, question: str) -> dict:
    cache_key = (community_id, question.strip().lower())
    now = datetime.now(timezone.utc)
    cached = _FAQ_CACHE.get(cache_key)
    if cached:
        payload, ts = cached
        if now - ts <= timedelta(seconds=FAQ_CACHE_TTL_SECONDS):
            return payload

    posts = queries.list_community_posts(community_id=community_id, limit=200, offset=0)
    snippets: list[str] = []
    for post in posts[:80]:
        snippets.append(f"POST[{post.id}] {post.title}: {post.body}")
        for comment in queries.list_post_comments(post.id)[:4]:
            snippets.append(f"COMMENT[{comment.id}] {comment.body}")

    context = "\n".join(snippets[:300])
    source_post_id = _find_source_post_id(posts, question)
    source_excerpt = None
    if source_post_id:
        source_post = next((post for post in posts if post.id == source_post_id), None)
        if source_post:
            source_excerpt = (source_post.body or source_post.title or "")[:180] or None

    fallback_answer = {
        "answer": "I couldn't find a confident answer in the community yet. Try asking in the Posts tab!",
        "source_post_id": None,
        "source_excerpt": None,
        "confidence": 0.24,
    }

    if not snippets:
        return fallback_answer

    prompt = _read_prompt("faq_answer.txt").format(question=question, context=context)
    payload = await groq_service.generate_json(prompt, fallback=fallback_answer, mock_key="faq")

    answer = str(payload.get("answer") or fallback_answer["answer"])
    confidence = float(payload.get("confidence") or fallback_answer["confidence"])
    response_source = payload.get("source_post_id") or source_post_id
    response_excerpt = payload.get("source_excerpt") or source_excerpt

    bounded_confidence = max(0.0, min(1.0, confidence))
    if bounded_confidence < 0.4:
        return fallback_answer

    response = {
        "answer": answer,
        "source_post_id": response_source,
        "source_excerpt": response_excerpt,
        "confidence": bounded_confidence,
    }
    _FAQ_CACHE[cache_key] = (response, now)
    return response

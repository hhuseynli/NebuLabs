from __future__ import annotations

from pathlib import Path

from db import queries
from services import gemini_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


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
    posts = queries.list_community_posts(community_id=community_id, limit=200, offset=0)
    snippets: list[str] = []
    for post in posts[:80]:
        snippets.append(f"POST[{post.id}] {post.title}: {post.body}")
        for comment in queries.list_post_comments(post.id)[:4]:
            snippets.append(f"COMMENT[{comment.id}] {comment.body}")

    context = "\n".join(snippets[:300])
    source_post_id = _find_source_post_id(posts, question)

    fallback_answer = {
        "answer": "I could not find a confident answer from community content yet. Try asking in the Posts tab.",
        "source_post_id": source_post_id,
        "confidence": 0.24,
    }

    if not snippets:
        return fallback_answer

    prompt = _read_prompt("faq_answer.txt").format(question=question, context=context)
    payload = await gemini_service.generate_json(prompt, fallback=fallback_answer)

    answer = str(payload.get("answer") or fallback_answer["answer"])
    confidence = float(payload.get("confidence") or fallback_answer["confidence"])
    response_source = payload.get("source_post_id") or source_post_id

    return {
        "answer": answer,
        "source_post_id": response_source,
        "confidence": max(0.0, min(1.0, confidence)),
    }

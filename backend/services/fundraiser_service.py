from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from db import queries
from services import groq_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _community_name(community_id: str) -> str:
    community = queries.get_community_by_id(community_id)
    return community.name if community else "this community"


async def scan_and_create(community_id: str) -> dict:
    recent = queries.get_recent_fundraiser_post(community_id=community_id, hours=48)
    if recent:
        return {
            "detected": False,
            "confidence": 0.0,
            "message": "A fundraiser was created recently; skipping",
        }

    content = queries.get_community_content(community_id=community_id, limit=50)
    if not content:
        return {
            "detected": False,
            "confidence": 0.0,
            "message": "No community activity available for fundraiser scan",
        }

    detect_prompt = _read_prompt("fundraiser_detect.txt").format(content=content)
    detection_fallback = {
        "detected": False,
        "need": "",
        "confidence": 0.0,
        "trigger_post_id": None,
    }
    detected = await groq_service.generate_json(
        detect_prompt,
        fallback=detection_fallback,
        mock_key="fundraiser_detect",
    )

    confidence = float(detected.get("confidence") or 0.0)
    need = str(detected.get("need") or "").strip()
    if not detected.get("detected") or confidence < 0.75 or not need:
        return {
            "detected": False,
            "confidence": confidence,
            "message": "No funding need detected with sufficient confidence",
        }

    post_prompt = _read_prompt("fundraiser_post.txt").format(
        community_name=_community_name(community_id),
        need=need,
    )
    post_fallback = {
        "title": f"Community Goal: {need}",
        "body": f"We identified a shared need: {need}. Pledge support below to help this community goal.",
        "goal_amount": 200,
        "deadline_days": 14,
    }
    generated = await groq_service.generate_json(
        post_prompt,
        fallback=post_fallback,
        mock_key="fundraiser_post",
    )

    goal_amount = int(generated.get("goal_amount") or post_fallback["goal_amount"])
    deadline_days = int(generated.get("deadline_days") or post_fallback["deadline_days"])
    deadline = datetime.now(timezone.utc) + timedelta(days=max(1, min(90, deadline_days)))

    fundraiser_meta = {
        "goal_amount": max(1, goal_amount),
        "currency": "AZN",
        "deadline": deadline.isoformat(),
        "status": "active",
        "trigger_post_id": detected.get("trigger_post_id"),
        "pledge_count": 0,
        "total_pledged": 0,
    }

    post = queries.insert_post(
        community_id=community_id,
        title=str(generated.get("title") or post_fallback["title"]),
        body=str(generated.get("body") or post_fallback["body"]),
        flair="🎯 Community Goal",
        is_human=False,
        author_id=None,
        agent_id=None,
        opendata_citation=None,
        agent_type="fundraiser",
        fundraiser_meta=fundraiser_meta,
    )

    return {
        "detected": True,
        "need": need,
        "confidence": confidence,
        "post_id": post.id,
        "message": "Fundraiser post created successfully",
    }

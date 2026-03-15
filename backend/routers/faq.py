from fastapi import APIRouter, HTTPException, Query

from db import queries
from services import faq_service

router = APIRouter(tags=["faq"])


@router.get("/communities/{slug}/faq/ask")
async def ask_faq(slug: str, q: str = Query(min_length=3, max_length=500)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    return await faq_service.answer_question(community.id, q)

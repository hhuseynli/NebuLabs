from fastapi import APIRouter, HTTPException, Query, Request

from db import queries
from limiter import limiter
from services import faq_service

router = APIRouter(tags=["faq"])


@router.get("/communities/{slug}/faq/ask")
@limiter.limit("10/minute")
async def ask_faq(request: Request, slug: str, q: str = Query(min_length=3, max_length=500, strip_whitespace=True)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    return await faq_service.answer_question(community.id, q)

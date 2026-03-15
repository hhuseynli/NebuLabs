from fastapi import APIRouter, Depends, HTTPException

from db import queries
from routers.deps import get_current_user_id
from services import sentiment_service

router = APIRouter(tags=["sentiment"])


@router.get("/communities/{slug}/sentiment")
async def get_sentiment(slug: str, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    if community.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the community organizer can access sentiment")

    return await sentiment_service.build_report(community.id)

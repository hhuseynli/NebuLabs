from fastapi import APIRouter, Depends, HTTPException

from db import queries
from models.community import DemoSeedRequest
from routers.deps import get_current_user_id
from services import demo_seed_service

router = APIRouter(tags=["demo"])


@router.post("/communities/{slug}/demo-seed")
async def seed_demo_data(slug: str, payload: DemoSeedRequest, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    if community.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only the community organizer can run demo seeding")

    try:
        return demo_seed_service.seed_community_scenario(community_id=community.id, scenario=payload.scenario)
    except ValueError as exc:
        code = str(exc)
        if code == "INVALID_SCENARIO":
            raise HTTPException(status_code=400, detail="Invalid demo scenario")
        if code == "COMMUNITY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Community not found")
        raise

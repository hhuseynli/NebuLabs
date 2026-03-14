from fastapi import APIRouter, Depends, HTTPException

from db import queries
from models.community import CommunityAdvancePhase
from routers.deps import get_current_user_id
from services import feed_service, revival_service

router = APIRouter(prefix="/communities/{slug}/revival", tags=["revival"])


@router.get("")
async def get_revival(slug: str):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    return revival_service.get_status(community.id)


@router.post("/advance")
async def advance_revival(slug: str, payload: CommunityAdvancePhase, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    if community.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only community creator can advance phase")

    before = community.revival_phase
    try:
        phase = revival_service.advance_phase(community.id, payload.to_phase)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid phase transition")

    await feed_service.publish(
        community.id,
        "phase_change",
        {"from": before, "to": phase, "human_activity_ratio": community.human_activity_ratio},
    )

    return {"phase": phase, "message": "Phase manually advanced"}

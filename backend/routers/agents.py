from fastapi import APIRouter, Depends, HTTPException

from db import queries
from routers.deps import get_current_user_id

router = APIRouter(prefix="/communities/{slug}/agents", tags=["agents"])


@router.get("")
async def get_agents(slug: str):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    return {"agents": [agent.model_dump() for agent in queries.get_community_agents(community.id)]}


@router.patch("/{agent_id}")
async def update_agent_status(slug: str, agent_id: str, payload: dict, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    if community.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only community creator can manage agents")

    status_value = payload.get("status")
    if status_value not in {"active", "retiring", "retired"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        agent = queries.set_agent_status(community_id=community.id, agent_id=agent_id, status=status_value)
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
    except ValueError:
        raise HTTPException(status_code=403, detail="Cross-community access blocked")

    return {"id": agent.id, "status": agent.status}

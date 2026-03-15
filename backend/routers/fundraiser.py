from fastapi import APIRouter, Depends, HTTPException, status

from db import queries
from models.community import PledgeCreate
from routers.deps import get_current_user_id
from services import fundraiser_service

router = APIRouter(tags=["fundraiser"])


@router.post("/communities/{slug}/fundraiser/scan")
async def scan_fundraiser(slug: str, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail={"code": "COMMUNITY_NOT_FOUND", "message": "No community with that slug"})
    if community.created_by != user_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only organizer can run fundraiser scan"})
    return await fundraiser_service.scan_and_create(community.id)


@router.get("/posts/{post_id}/pledges")
async def get_pledges(post_id: str, user_id: str = Depends(get_current_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail={"code": "POST_NOT_FOUND", "message": "Post not found"})
    if not queries.is_community_member(community_id=post.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member"})
    if post.agent_type != "fundraiser":
        raise HTTPException(status_code=400, detail={"code": "NOT_A_FUNDRAISER", "message": "Pledges are supported only for fundraiser posts"})

    summary = queries.get_pledge_summary(post_id)
    goal_amount = (post.fundraiser_meta or {}).get("goal_amount") if post.fundraiser_meta else None
    return {
        **summary,
        "goal_amount": goal_amount,
    }


@router.post("/posts/{post_id}/pledge", status_code=status.HTTP_201_CREATED)
async def create_pledge(post_id: str, payload: PledgeCreate, user_id: str = Depends(get_current_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail={"code": "POST_NOT_FOUND", "message": "Post not found"})
    if not queries.is_community_member(community_id=post.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member"})
    if post.agent_type != "fundraiser":
        raise HTTPException(status_code=400, detail={"code": "NOT_A_FUNDRAISER", "message": "Pledges are supported only for fundraiser posts"})

    try:
        pledge = queries.add_pledge(
            post_id=post_id,
            community_id=post.community_id,
            user_id=user_id,
            amount_suggested=payload.amount_suggested,
            message=payload.message,
        )
    except ValueError as exc:
        if str(exc) == "ALREADY_PLEDGED":
            raise HTTPException(status_code=400, detail={"code": "ALREADY_PLEDGED", "message": "You already pledged for this fundraiser"})
        raise

    return {
        "id": pledge["id"],
        "amount_suggested": pledge["amount_suggested"],
        "message": pledge["message"],
        "created_at": pledge["created_at"],
    }


@router.delete("/posts/{post_id}/pledge")
async def retract_pledge(post_id: str, user_id: str = Depends(get_current_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail={"code": "POST_NOT_FOUND", "message": "Post not found"})
    if not queries.is_community_member(community_id=post.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a member"})
    if post.agent_type != "fundraiser":
        raise HTTPException(status_code=400, detail={"code": "NOT_A_FUNDRAISER", "message": "Pledges are supported only for fundraiser posts"})

    removed = queries.remove_pledge(post_id=post_id, user_id=user_id)
    if not removed:
        raise HTTPException(status_code=404, detail={"code": "PLEDGE_NOT_FOUND", "message": "No pledge to retract"})
    return {"message": "Pledge retracted"}

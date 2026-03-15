from fastapi import APIRouter, Depends, HTTPException, Query, status

from db import queries
from models.community import CommunityCreate
from routers.deps import get_current_user_id, get_optional_user_id
from services import agent_service

router = APIRouter(prefix="/communities", tags=["communities"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_community(payload: CommunityCreate, user_id: str = Depends(get_current_user_id)):
    rules = await agent_service.generate_rules(
        description=payload.description,
        ideal_member_description=payload.ideal_member_description,
    )

    try:
        community = queries.create_community(
            name=payload.name,
            description=payload.description,
            rules=rules,
            created_by=user_id,
        )
    except ValueError as exc:
        if str(exc) == "DUPLICATE_SLUG":
            raise HTTPException(status_code=409, detail="Community slug already taken")
        raise

    return queries.to_community_response(community, [])


@router.get("/{slug}")
async def get_community(slug: str):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    agents = queries.get_community_agents(community.id)
    return queries.to_community_response(community, agents)


@router.get("/{slug}/posts")
async def get_community_posts(
    slug: str,
    sort: str = Query(default="hot", pattern="^(hot|new|top)$"),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Depends(get_optional_user_id),
):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    posts = queries.list_community_posts(community_id=community.id, limit=limit, offset=offset)

    if sort == "top":
        posts = sorted(posts, key=lambda p: p.upvotes - p.downvotes, reverse=True)
    elif sort == "new":
        posts = sorted(posts, key=lambda p: p.created_at, reverse=True)

    return {
        "posts": [queries.serialize_post(post=post, user_id=user_id, include_body=True) for post in posts],
        "total": queries.count_community_posts(community.id),
    }


@router.post("/{slug}/join")
async def join_community(slug: str, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    member_count = queries.join_community(community_id=community.id, user_id=user_id)
    return {"member_count": member_count}


@router.post("/{slug}/leave")
async def leave_community(slug: str, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    member_count = queries.leave_community(community_id=community.id, user_id=user_id)
    return {"member_count": member_count}

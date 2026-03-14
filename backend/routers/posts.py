from fastapi import APIRouter, Depends, HTTPException

from db import queries
from models.community import CommentCreate, PostCreate, VotePayload
from routers.deps import get_current_user_id, get_optional_user_id
from services import factcheck_service, feed_service, revival_service

router = APIRouter(tags=["posts"])


@router.post("/communities/{slug}/posts", status_code=201)
async def create_post(slug: str, payload: PostCreate, user_id: str = Depends(get_current_user_id)):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    if not queries.is_community_member(community_id=community.id, user_id=user_id):
        raise HTTPException(status_code=403, detail="Not a member")

    post = queries.insert_post(
        community_id=community.id,
        title=payload.title,
        body=payload.body,
        flair=payload.flair,
        is_human=True,
        author_id=user_id,
        agent_id=None,
        opendata_citation=None,
    )

    transition = revival_service.check_transition(community.id)
    await feed_service.publish(
        community.id,
        "new_post",
        queries.serialize_post(post=post, user_id=user_id),
    )

    factcheck = await factcheck_service.maybe_create_factcheck(community.id, post.id)
    if factcheck:
        await feed_service.publish(
            community.id,
            "factcheck_fired",
            {
                "post_id": post.id,
                "agent_name": factcheck["agent_name"],
                "preview": factcheck["comment"]["body"][:120],
            },
        )

    if transition:
        await feed_service.publish(
            community.id,
            "phase_change",
            {"from": transition[0], "to": transition[1], "human_activity_ratio": community.human_activity_ratio},
        )

    return {"id": post.id, "title": post.title, "created_at": post.created_at}


@router.get("/posts/{post_id}")
async def get_post(post_id: str, user_id: str | None = Depends(get_optional_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = queries.build_comment_tree(post_id=post_id, user_id=user_id)
    payload = queries.serialize_post(post=post, user_id=user_id)
    payload["comments"] = comments
    return payload


@router.post("/posts/{post_id}/vote")
async def vote_post(post_id: str, payload: VotePayload, user_id: str = Depends(get_current_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not queries.is_community_member(community_id=post.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="Not a member")

    return queries.vote_post(post_id=post_id, user_id=user_id, value=payload.value)


@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: str, user_id: str | None = Depends(get_optional_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"comments": queries.build_comment_tree(post_id=post_id, user_id=user_id)}


@router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: str, payload: CommentCreate, user_id: str = Depends(get_current_user_id)):
    post = queries.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not queries.is_community_member(community_id=post.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="Not a member")

    comment = queries.insert_comment(
        post_id=post_id,
        community_id=post.community_id,
        body=payload.body,
        parent_comment_id=payload.parent_comment_id,
        is_human=True,
        author_id=user_id,
        agent_id=None,
        is_factcheck=False,
    )

    await feed_service.publish(
        post.community_id,
        "new_comment",
        queries.serialize_comment(comment=comment, user_id=user_id),
    )

    return {"id": comment.id, "body": comment.body, "created_at": comment.created_at}


@router.post("/comments/{comment_id}/vote")
async def vote_comment(comment_id: str, payload: VotePayload, user_id: str = Depends(get_current_user_id)):
    comment = queries.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not queries.is_community_member(community_id=comment.community_id, user_id=user_id):
        raise HTTPException(status_code=403, detail="Not a member")

    return queries.vote_comment(comment_id=comment_id, user_id=user_id, value=payload.value)

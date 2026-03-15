from fastapi import APIRouter, HTTPException

from db import queries

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}")
async def get_user_profile(username: str):
    user = queries.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recent_posts = queries.get_user_recent_posts(user.id)
    recent_comments = queries.get_user_recent_comments(user.id)
    post_count = len([p for p in queries.store.posts_by_id.values() if p.author_id == user.id])
    comment_count = len([c for c in queries.store.comments_by_id.values() if c.author_id == user.id])

    return {
        "id": user.id,
        "username": user.username,
        "bio": queries.store.user_bio.get(user.id, "Building things."),
        "karma": user.karma,
        "post_count": post_count,
        "comment_count": comment_count,
        "is_agent": False,
        "recent_posts": [queries.serialize_post(post=post, include_body=False) for post in recent_posts],
        "recent_comments": [queries.serialize_comment(comment=comment) for comment in recent_comments],
        "joined_at": user.created_at,
    }

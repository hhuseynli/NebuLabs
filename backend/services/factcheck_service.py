from __future__ import annotations

from db import queries
from models.community import Post
from services import open_data_service

HIGH_CONFIDENCE_PHRASES = [
    "globally",
    "always",
    "never",
    "100%",
    "guaranteed",
    "confirmed",
    "proven",
]


def should_factcheck(post: Post) -> bool:
    if not post.is_human:
        return False

    text = f"{post.title} {post.body}".lower()
    return any(marker in text for marker in HIGH_CONFIDENCE_PHRASES)


async def maybe_create_factcheck(community_id: str, post_id: str) -> dict | None:
    post = queries.get_post(post_id)
    if not post or post.community_id != community_id:
        return None
    if not should_factcheck(post):
        return None

    agents = [agent for agent in queries.get_community_agents(community_id) if agent.status == "active"]
    if not agents:
        return None

    chosen = agents[0]
    citation_name, citation_stat = await open_data_service.fetch_citation("ecology")
    body = (
        f"Worth clarifying: according to opendata.az ({citation_name}), {citation_stat}. "
        "This claim may be overstated based on the available data."
    )

    comment = queries.insert_comment(
        post_id=post_id,
        community_id=community_id,
        body=body,
        parent_comment_id=None,
        is_human=False,
        author_id=None,
        agent_id=chosen.id,
        is_factcheck=True,
    )

    return {
        "comment": queries.serialize_comment(comment=comment),
        "agent_name": chosen.name,
    }

from __future__ import annotations

from db import queries


PHASE_ORDER = ["spark", "pull", "handoff", "complete"]


def current_phase(community_id: str) -> str:
    community = queries.get_community_by_id(community_id)
    if not community:
        raise ValueError("COMMUNITY_NOT_FOUND")
    return community.revival_phase


def recompute_ratio(community_id: str) -> float:
    return queries.recompute_human_ratio(community_id=community_id)


def check_transition(community_id: str) -> tuple[str, str] | None:
    community = queries.get_community_by_id(community_id)
    if not community:
        return None

    before = community.revival_phase
    ratio = recompute_ratio(community_id)

    if before == "spark":
        posts = queries.list_community_posts(community_id=community_id, limit=50, offset=0)
        if any(post.is_human for post in posts):
            queries.set_phase(community_id=community_id, phase="pull")
    elif before == "pull" and ratio > 0.60:
        queries.set_phase(community_id=community_id, phase="handoff")
    elif before == "handoff":
        active_agents = [a for a in queries.get_community_agents(community_id) if a.status != "retired"]
        if not active_agents:
            queries.set_phase(community_id=community_id, phase="complete")

    after = queries.get_community_by_id(community_id).revival_phase
    if before != after:
        return before, after
    return None


def advance_phase(community_id: str, to_phase: str) -> str:
    if to_phase not in PHASE_ORDER:
        raise ValueError("INVALID_PHASE")

    queries.set_phase(community_id=community_id, phase=to_phase)
    return to_phase


def get_status(community_id: str) -> dict:
    community = queries.get_community_by_id(community_id)
    if not community:
        raise ValueError("COMMUNITY_NOT_FOUND")

    posts = queries.list_community_posts(community_id=community_id, limit=500, offset=0)
    human_posts = len([p for p in posts if p.is_human])
    agent_posts = len([p for p in posts if not p.is_human])
    agents = queries.get_community_agents(community_id)
    active = len([a for a in agents if a.status != "retired"])
    retired = len([a for a in agents if a.status == "retired"])

    return {
        "phase": community.revival_phase,
        "human_activity_ratio": community.human_activity_ratio,
        "total_posts": len(posts),
        "human_posts": human_posts,
        "agent_posts": agent_posts,
        "agents_active": active,
        "agents_retired": retired,
        "phase_history": queries.get_phase_history(community_id),
    }

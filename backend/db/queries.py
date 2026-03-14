from __future__ import annotations

import re
import hashlib
import hmac
import secrets
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from db.supabase_client import get_supabase_client, is_supabase_enabled
from models.agent import Agent
from models.community import Comment, Community, Post, Rule
from models.user import User


@dataclass
class InMemoryStore:
    users_by_id: dict[str, User]
    users_by_email: dict[str, User]
    passwords: dict[str, str]
    tokens: dict[str, str]
    communities_by_id: dict[str, Community]
    communities_by_slug: dict[str, Community]
    community_members: dict[str, set[str]]
    agents_by_id: dict[str, Agent]
    agents_by_community: dict[str, list[str]]
    posts_by_id: dict[str, Post]
    posts_by_community: dict[str, list[str]]
    comments_by_id: dict[str, Comment]
    comments_by_post: dict[str, list[str]]
    post_votes: dict[str, dict[str, int]]
    comment_votes: dict[str, dict[str, int]]
    phase_history: dict[str, list[dict[str, Any]]]
    user_bio: dict[str, str]


store = InMemoryStore(
    users_by_id={},
    users_by_email={},
    passwords={},
    tokens={},
    communities_by_id={},
    communities_by_slug={},
    community_members={},
    agents_by_id={},
    agents_by_community={},
    posts_by_id={},
    posts_by_community={},
    comments_by_id={},
    comments_by_post={},
    post_votes=defaultdict(dict),
    comment_votes=defaultdict(dict),
    phase_history=defaultdict(list),
    user_bio={},
)


def _new_id() -> str:
    return str(uuid.uuid4())


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return f"{salt}${digest}"


def _verify_password(password: str, encoded: str) -> bool:
    if "$" not in encoded:
        return False
    salt, expected = encoded.split("$", 1)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return hmac.compare_digest(digest, expected)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug


def _sb_upsert(table: str, payload: dict[str, Any]) -> None:
    client = get_supabase_client()
    if not client:
        return
    try:
        client.table(table).upsert(payload).execute()
    except Exception:
        # Supabase sync should never break local in-memory flow.
        return


def _sb_insert(table: str, payload: dict[str, Any]) -> None:
    client = get_supabase_client()
    if not client:
        return
    try:
        client.table(table).insert(payload).execute()
    except Exception:
        return


def _community_to_payload(community: Community) -> dict[str, Any]:
    return {
        "id": community.id,
        "name": community.name,
        "slug": community.slug,
        "description": community.description,
        "rules": [rule.model_dump() for rule in community.rules],
        "member_count": community.member_count,
        "revival_phase": community.revival_phase,
        "human_activity_ratio": community.human_activity_ratio,
        "created_by": community.created_by,
        "created_at": community.created_at.isoformat(),
    }


def _user_to_payload(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "karma": user.karma,
        "created_at": user.created_at.isoformat(),
    }


def _agent_to_payload(agent: Agent) -> dict[str, Any]:
    return {
        "id": agent.id,
        "community_id": agent.community_id,
        "name": agent.name,
        "backstory": agent.backstory,
        "personality_traits": agent.personality_traits,
        "opinion_set": agent.opinion_set,
        "expertise_areas": agent.expertise_areas,
        "activity_level": agent.activity_level,
        "status": agent.status,
        "post_count": agent.post_count,
        "created_at": agent.created_at.isoformat(),
    }


def _post_to_payload(post: Post) -> dict[str, Any]:
    return {
        "id": post.id,
        "community_id": post.community_id,
        "title": post.title,
        "body": post.body,
        "flair": post.flair,
        "author_id": post.author_id,
        "agent_id": post.agent_id,
        "is_human": post.is_human,
        "opendata_citation": post.opendata_citation,
        "upvotes": post.upvotes,
        "downvotes": post.downvotes,
        "comment_count": post.comment_count,
        "has_factcheck": post.has_factcheck,
        "created_at": post.created_at.isoformat(),
    }


def _comment_to_payload(comment: Comment) -> dict[str, Any]:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "community_id": comment.community_id,
        "body": comment.body,
        "parent_comment_id": comment.parent_comment_id,
        "author_id": comment.author_id,
        "agent_id": comment.agent_id,
        "is_human": comment.is_human,
        "is_factcheck": comment.is_factcheck,
        "upvotes": comment.upvotes,
        "downvotes": comment.downvotes,
        "created_at": comment.created_at.isoformat(),
    }


def _row_to_user(row: dict[str, Any]) -> User:
    return User(
        id=row["id"],
        email=row.get("email", "placeholder@example.com"),
        username=row["username"],
        karma=row.get("karma", 0),
        created_at=row.get("created_at"),
    )


def _row_to_rule(rule_row: dict[str, Any]) -> Rule:
    return Rule(title=rule_row.get("title", "Rule"), body=rule_row.get("body", ""))


def _row_to_community(row: dict[str, Any]) -> Community:
    rules_data = row.get("rules") or []
    return Community(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        description=row.get("description", ""),
        rules=[_row_to_rule(r) for r in rules_data],
        member_count=row.get("member_count", 1),
        revival_phase=row.get("revival_phase", "spark"),
        human_activity_ratio=row.get("human_activity_ratio", 0.0),
        created_by=row.get("created_by", ""),
        created_at=row.get("created_at"),
    )


def _row_to_agent(row: dict[str, Any]) -> Agent:
    return Agent(
        id=row["id"],
        community_id=row["community_id"],
        name=row["name"],
        backstory=row.get("backstory", ""),
        personality_traits=row.get("personality_traits") or [],
        opinion_set=row.get("opinion_set") or {},
        expertise_areas=row.get("expertise_areas") or [],
        activity_level=row.get("activity_level", "medium"),
        status=row.get("status", "active"),
        post_count=row.get("post_count", 0),
        created_at=row.get("created_at"),
    )


def _row_to_post(row: dict[str, Any]) -> Post:
    return Post(
        id=row["id"],
        community_id=row["community_id"],
        title=row["title"],
        body=row.get("body", ""),
        flair=row.get("flair"),
        agent_id=row.get("agent_id"),
        author_id=row.get("author_id"),
        is_human=row.get("is_human", True),
        opendata_citation=row.get("opendata_citation"),
        upvotes=row.get("upvotes", 0),
        downvotes=row.get("downvotes", 0),
        comment_count=row.get("comment_count", 0),
        has_factcheck=row.get("has_factcheck", False),
        created_at=row.get("created_at"),
    )


def _row_to_comment(row: dict[str, Any]) -> Comment:
    return Comment(
        id=row["id"],
        post_id=row["post_id"],
        community_id=row["community_id"],
        body=row.get("body", ""),
        parent_comment_id=row.get("parent_comment_id"),
        author_id=row.get("author_id"),
        agent_id=row.get("agent_id"),
        is_human=row.get("is_human", True),
        is_factcheck=row.get("is_factcheck", False),
        upvotes=row.get("upvotes", 0),
        downvotes=row.get("downvotes", 0),
        created_at=row.get("created_at"),
    )


# Auth

def create_user(email: str, password: str, username: str, user_id: str | None = None) -> User:
    if email in store.users_by_email:
        raise ValueError("EMAIL_TAKEN")

    for u in store.users_by_id.values():
        if u.username.lower() == username.lower():
            raise ValueError("USERNAME_TAKEN")

    user = User(id=user_id or _new_id(), email=email, username=username)
    store.users_by_id[user.id] = user
    store.users_by_email[email] = user
    store.passwords[user.id] = _hash_password(password)
    _sb_upsert("users", _user_to_payload(user))
    return user


def authenticate(email: str, password: str) -> User | None:
    user = store.users_by_email.get(email)
    if not user:
        return None
    encoded = store.passwords.get(user.id)
    if not encoded:
        return None
    return user if _verify_password(password, encoded) else None


def issue_token(user_id: str) -> str:
    token = _new_id()
    store.tokens[token] = user_id
    return token


def get_user_by_token(token: str) -> User | None:
    user_id = store.tokens.get(token)
    if not user_id:
        return None
    return store.users_by_id.get(user_id)


def get_user_by_email(email: str) -> User | None:
    client = get_supabase_client()
    if client:
        try:
            rows = client.table("users").select("*").eq("email", email).limit(1).execute().data
            if rows:
                return _row_to_user(rows[0])
        except Exception:
            pass
    return store.users_by_email.get(email)


# Communities

def create_community(
    name: str,
    description: str,
    rules: list[Rule],
    created_by: str,
) -> Community:
    slug = slugify(name)
    if slug in store.communities_by_slug:
        raise ValueError("DUPLICATE_SLUG")

    community = Community(
        id=_new_id(),
        name=name,
        slug=slug,
        description=description,
        rules=rules,
        created_by=created_by,
        member_count=1,
    )
    store.communities_by_id[community.id] = community
    store.communities_by_slug[slug] = community
    store.community_members[community.id] = {created_by}
    store.posts_by_community[community.id] = []
    store.agents_by_community[community.id] = []
    _sb_upsert("communities", _community_to_payload(community))
    _sb_upsert(
        "community_members",
        {"user_id": created_by, "community_id": community.id, "role": "owner"},
    )
    return community


def get_community_by_slug(slug: str) -> Community | None:
    client = get_supabase_client()
    if client:
        try:
            row = client.table("communities").select("*").eq("slug", slug).limit(1).execute().data
            if row:
                return _row_to_community(row[0])
        except Exception:
            pass
    return store.communities_by_slug.get(slug)


def get_community_by_id(community_id: str) -> Community | None:
    client = get_supabase_client()
    if client:
        try:
            row = client.table("communities").select("*").eq("id", community_id).limit(1).execute().data
            if row:
                return _row_to_community(row[0])
        except Exception:
            pass
    return store.communities_by_id.get(community_id)


def is_community_member(*, community_id: str, user_id: str) -> bool:
    client = get_supabase_client()
    if client:
        try:
            rows = (
                client.table("community_members")
                .select("user_id")
                .eq("community_id", community_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
                .data
            )
            return len(rows) > 0
        except Exception:
            pass
    return user_id in store.community_members.get(community_id, set())


def join_community(*, community_id: str, user_id: str) -> int:
    members = store.community_members.get(community_id, set())
    before = len(members)
    members.add(user_id)
    store.community_members[community_id] = members
    if len(members) != before:
        community = store.communities_by_id[community_id]
        community.member_count += 1
        _sb_upsert(
            "community_members",
            {"user_id": user_id, "community_id": community_id, "role": "member"},
        )
        _sb_upsert("communities", _community_to_payload(community))
    return store.communities_by_id[community_id].member_count


def leave_community(*, community_id: str, user_id: str) -> int:
    members = store.community_members.get(community_id, set())
    if user_id in members and len(members) > 1:
        members.remove(user_id)
        store.communities_by_id[community_id].member_count -= 1
        client = get_supabase_client()
        if client:
            try:
                client.table("community_members").delete().eq("community_id", community_id).eq("user_id", user_id).execute()
            except Exception:
                pass
        _sb_upsert("communities", _community_to_payload(store.communities_by_id[community_id]))
    return store.communities_by_id[community_id].member_count


def list_community_posts(community_id: str, limit: int = 20, offset: int = 0) -> list[Post]:
    client = get_supabase_client()
    if client:
        try:
            end = offset + limit - 1
            rows = (
                client.table("posts")
                .select("*")
                .eq("community_id", community_id)
                .order("created_at", desc=True)
                .range(offset, end)
                .execute()
                .data
            )
            return [_row_to_post(row) for row in rows]
        except Exception:
            pass
    post_ids = store.posts_by_community.get(community_id, [])
    selected = post_ids[offset : offset + limit]
    return [store.posts_by_id[p_id] for p_id in selected]


def count_community_posts(community_id: str) -> int:
    client = get_supabase_client()
    if client:
        try:
            result = client.table("posts").select("id", count="exact").eq("community_id", community_id).limit(1).execute()
            if result.count is not None:
                return int(result.count)
        except Exception:
            pass
    return len(store.posts_by_community.get(community_id, []))


def insert_post(
    *,
    community_id: str,
    title: str,
    body: str,
    flair: str | None,
    is_human: bool,
    author_id: str | None,
    agent_id: str | None,
    opendata_citation: str | None,
) -> Post:
    post = Post(
        id=_new_id(),
        community_id=community_id,
        title=title,
        body=body,
        flair=flair,
        is_human=is_human,
        author_id=author_id,
        agent_id=agent_id,
        opendata_citation=opendata_citation,
    )
    store.posts_by_id[post.id] = post
    if community_id not in store.posts_by_community:
        store.posts_by_community[community_id] = []
    store.posts_by_community[community_id].insert(0, post.id)
    recompute_human_ratio(community_id=community_id)
    _sb_upsert("posts", _post_to_payload(post))
    return post


def get_post(post_id: str) -> Post | None:
    client = get_supabase_client()
    if client:
        try:
            rows = client.table("posts").select("*").eq("id", post_id).limit(1).execute().data
            if rows:
                return _row_to_post(rows[0])
        except Exception:
            pass
    return store.posts_by_id.get(post_id)


def get_post_community_id(post_id: str) -> str | None:
    post = get_post(post_id)
    if not post:
        return None
    return post.community_id


def insert_comment(
    *,
    post_id: str,
    community_id: str,
    body: str,
    parent_comment_id: str | None,
    is_human: bool,
    author_id: str | None,
    agent_id: str | None,
    is_factcheck: bool,
) -> Comment:
    comment = Comment(
        id=_new_id(),
        post_id=post_id,
        community_id=community_id,
        body=body,
        parent_comment_id=parent_comment_id,
        is_human=is_human,
        author_id=author_id,
        agent_id=agent_id,
        is_factcheck=is_factcheck,
    )
    store.comments_by_id[comment.id] = comment
    if post_id not in store.comments_by_post:
        store.comments_by_post[post_id] = []
    store.comments_by_post[post_id].append(comment.id)
    post = store.posts_by_id[post_id]
    post.comment_count += 1
    if is_factcheck:
        post.has_factcheck = True
        _sb_upsert("posts", _post_to_payload(post))
    _sb_upsert("comments", _comment_to_payload(comment))
    return comment


def list_post_comments(post_id: str) -> list[Comment]:
    client = get_supabase_client()
    if client:
        try:
            rows = (
                client.table("comments")
                .select("*")
                .eq("post_id", post_id)
                .order("created_at", desc=False)
                .execute()
                .data
            )
            return [_row_to_comment(row) for row in rows]
        except Exception:
            pass
    ids = store.comments_by_post.get(post_id, [])
    return [store.comments_by_id[c_id] for c_id in ids]


def get_comment(comment_id: str) -> Comment | None:
    client = get_supabase_client()
    if client:
        try:
            rows = client.table("comments").select("*").eq("id", comment_id).limit(1).execute().data
            if rows:
                return _row_to_comment(rows[0])
        except Exception:
            pass
    return store.comments_by_id.get(comment_id)


def vote_post(*, post_id: str, user_id: str, value: int) -> dict[str, int | None]:
    post = store.posts_by_id[post_id]
    old = store.post_votes[post_id].get(user_id, 0)

    if old == 1:
        post.upvotes = max(0, post.upvotes - 1)
    elif old == -1:
        post.downvotes = max(0, post.downvotes - 1)

    if value == old:
        value = 0

    if value == 1:
        post.upvotes += 1
        store.post_votes[post_id][user_id] = 1
    elif value == -1:
        post.downvotes += 1
        store.post_votes[post_id][user_id] = -1
    else:
        store.post_votes[post_id].pop(user_id, None)

    final_vote = store.post_votes[post_id].get(user_id)
    _sb_upsert("posts", _post_to_payload(post))
    if final_vote is not None:
        _sb_insert(
            "votes",
            {
                "user_id": user_id,
                "community_id": post.community_id,
                "post_id": post_id,
                "comment_id": None,
                "value": final_vote,
            },
        )
    return {"upvotes": post.upvotes, "downvotes": post.downvotes, "user_vote": final_vote}


def vote_comment(*, comment_id: str, user_id: str, value: int) -> dict[str, int | None]:
    comment = store.comments_by_id[comment_id]
    old = store.comment_votes[comment_id].get(user_id, 0)

    if old == 1:
        comment.upvotes = max(0, comment.upvotes - 1)
    elif old == -1:
        comment.downvotes = max(0, comment.downvotes - 1)

    if value == old:
        value = 0

    if value == 1:
        comment.upvotes += 1
        store.comment_votes[comment_id][user_id] = 1
    elif value == -1:
        comment.downvotes += 1
        store.comment_votes[comment_id][user_id] = -1
    else:
        store.comment_votes[comment_id].pop(user_id, None)

    final_vote = store.comment_votes[comment_id].get(user_id)
    _sb_upsert("comments", _comment_to_payload(comment))
    if final_vote is not None:
        _sb_insert(
            "votes",
            {
                "user_id": user_id,
                "community_id": comment.community_id,
                "post_id": None,
                "comment_id": comment_id,
                "value": final_vote,
            },
        )
    return {"upvotes": comment.upvotes, "downvotes": comment.downvotes, "user_vote": final_vote}


def insert_agent(agent: Agent) -> Agent:
    store.agents_by_id[agent.id] = agent
    if agent.community_id not in store.agents_by_community:
        store.agents_by_community[agent.community_id] = []
    store.agents_by_community[agent.community_id].append(agent.id)
    _sb_upsert("agents", _agent_to_payload(agent))
    return agent


def get_community_agents(community_id: str) -> list[Agent]:
    client = get_supabase_client()
    if client:
        try:
            rows = client.table("agents").select("*").eq("community_id", community_id).execute().data
            return [_row_to_agent(row) for row in rows]
        except Exception:
            pass
    agent_ids = store.agents_by_community.get(community_id, [])
    return [store.agents_by_id[a_id] for a_id in agent_ids]


def to_community_response(community: Community, agents: list[Agent]) -> dict[str, Any]:
    return {
        "id": community.id,
        "name": community.name,
        "slug": community.slug,
        "description": community.description,
        "rules": [rule.model_dump() for rule in community.rules],
        "member_count": community.member_count,
        "revival_phase": community.revival_phase,
        "human_activity_ratio": community.human_activity_ratio,
        "agents": [agent.model_dump() for agent in agents],
    }


def set_agent_status(*, community_id: str, agent_id: str, status: str) -> Agent:
    agent = store.agents_by_id[agent_id]
    if agent.community_id != community_id:
        raise ValueError("CROSS_TENANT")
    agent.status = status  # type: ignore[assignment]
    _sb_upsert("agents", _agent_to_payload(agent))
    return agent


def recompute_human_ratio(*, community_id: str, last_n: int = 50) -> float:
    posts = list_community_posts(community_id=community_id, limit=last_n, offset=0)
    if not posts:
        ratio = 0.0
    else:
        human_count = len([p for p in posts if p.is_human])
        ratio = human_count / len(posts)

    community = store.communities_by_id[community_id]
    community.human_activity_ratio = round(ratio, 2)
    _sb_upsert("communities", _community_to_payload(community))
    return community.human_activity_ratio


def set_phase(*, community_id: str, phase: str) -> None:
    community = store.communities_by_id[community_id]
    if community.revival_phase != phase:
        store.phase_history[community_id].append({"phase": community.revival_phase})
        _sb_insert("phase_history", {"community_id": community_id, "phase": community.revival_phase})
    community.revival_phase = phase  # type: ignore[assignment]
    _sb_upsert("communities", _community_to_payload(community))


def get_phase_history(community_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if client:
        try:
            rows = (
                client.table("phase_history")
                .select("phase,created_at")
                .eq("community_id", community_id)
                .order("created_at", desc=False)
                .execute()
                .data
            )
            return [{"phase": row.get("phase"), "created_at": row.get("created_at")} for row in rows]
        except Exception:
            pass
    return store.phase_history.get(community_id, [])


def to_post_author(*, post: Post) -> dict[str, Any]:
    if post.is_human and post.author_id:
        user = store.users_by_id.get(post.author_id)
        username = user.username if user else "unknown"
        if username == "unknown" and is_supabase_enabled():
            client = get_supabase_client()
            if client:
                try:
                    rows = client.table("users").select("username").eq("id", post.author_id).limit(1).execute().data
                    if rows:
                        username = rows[0].get("username", "unknown")
                except Exception:
                    pass
        return {"id": post.author_id, "username": username, "is_agent": False}
    if post.agent_id:
        agent = store.agents_by_id.get(post.agent_id)
        if agent:
            return {"id": agent.id, "username": agent.name, "is_agent": True}
        if is_supabase_enabled():
            client = get_supabase_client()
            if client:
                try:
                    rows = client.table("agents").select("id,name").eq("id", post.agent_id).limit(1).execute().data
                    if rows:
                        row = rows[0]
                        return {"id": row.get("id"), "username": row.get("name", "unknown"), "is_agent": True}
                except Exception:
                    pass
    return {"id": None, "username": "unknown", "is_agent": False}


def to_comment_author(*, comment: Comment) -> dict[str, Any]:
    if comment.is_human and comment.author_id:
        user = store.users_by_id.get(comment.author_id)
        username = user.username if user else "unknown"
        if username == "unknown" and is_supabase_enabled():
            client = get_supabase_client()
            if client:
                try:
                    rows = client.table("users").select("username").eq("id", comment.author_id).limit(1).execute().data
                    if rows:
                        username = rows[0].get("username", "unknown")
                except Exception:
                    pass
        return {"id": comment.author_id, "username": username, "is_agent": False}
    if comment.agent_id:
        agent = store.agents_by_id.get(comment.agent_id)
        if agent:
            return {"id": agent.id, "username": agent.name, "is_agent": True}
        if is_supabase_enabled():
            client = get_supabase_client()
            if client:
                try:
                    rows = client.table("agents").select("id,name").eq("id", comment.agent_id).limit(1).execute().data
                    if rows:
                        row = rows[0]
                        return {"id": row.get("id"), "username": row.get("name", "unknown"), "is_agent": True}
                except Exception:
                    pass
    return {"id": None, "username": "unknown", "is_agent": False}


def serialize_post(*, post: Post, user_id: str | None = None, include_body: bool = True) -> dict[str, Any]:
    user_vote = None
    if user_id:
        user_vote = store.post_votes[post.id].get(user_id)

    community = store.communities_by_id.get(post.community_id)

    payload = {
        "id": post.id,
        "community_id": post.community_id,
        "community_slug": community.slug if community else None,
        "title": post.title,
        "flair": post.flair,
        "opendata_citation": post.opendata_citation,
        "author": to_post_author(post=post),
        "upvotes": post.upvotes,
        "downvotes": post.downvotes,
        "comment_count": post.comment_count,
        "has_factcheck": post.has_factcheck,
        "user_vote": user_vote,
        "created_at": post.created_at,
    }
    if include_body:
        payload["body"] = post.body
    return payload


def serialize_comment(*, comment: Comment, user_id: str | None = None) -> dict[str, Any]:
    user_vote = None
    if user_id:
        user_vote = store.comment_votes[comment.id].get(user_id)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "community_id": comment.community_id,
        "body": comment.body,
        "author": to_comment_author(comment=comment),
        "upvotes": comment.upvotes,
        "downvotes": comment.downvotes,
        "is_factcheck": comment.is_factcheck,
        "parent_comment_id": comment.parent_comment_id,
        "user_vote": user_vote,
        "created_at": comment.created_at,
    }


def build_comment_tree(*, post_id: str, user_id: str | None = None) -> list[dict[str, Any]]:
    comments = list_post_comments(post_id)
    by_parent: dict[str | None, list[Comment]] = defaultdict(list)
    for c in comments:
        by_parent[c.parent_comment_id].append(c)

    def walk(parent_id: str | None) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for child in sorted(by_parent[parent_id], key=lambda item: item.created_at):
            node = serialize_comment(comment=child, user_id=user_id)
            node["replies"] = walk(child.id)
            out.append(node)
        return out

    return walk(None)


def get_user_by_username(username: str) -> User | None:
    client = get_supabase_client()
    if client:
        try:
            rows = client.table("users").select("*").ilike("username", username).limit(1).execute().data
            if rows:
                return _row_to_user(rows[0])
        except Exception:
            pass
    for user in store.users_by_id.values():
        if user.username.lower() == username.lower():
            return user
    return None


def get_user_recent_posts(user_id: str, limit: int = 10) -> list[Post]:
    client = get_supabase_client()
    if client:
        try:
            rows = (
                client.table("posts")
                .select("*")
                .eq("author_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
                .data
            )
            return [_row_to_post(row) for row in rows]
        except Exception:
            pass
    posts = [p for p in store.posts_by_id.values() if p.author_id == user_id]
    posts.sort(key=lambda item: item.created_at, reverse=True)
    return posts[:limit]


def get_user_recent_comments(user_id: str, limit: int = 10) -> list[Comment]:
    client = get_supabase_client()
    if client:
        try:
            rows = (
                client.table("comments")
                .select("*")
                .eq("author_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
                .data
            )
            return [_row_to_comment(row) for row in rows]
        except Exception:
            pass
    comments = [c for c in store.comments_by_id.values() if c.author_id == user_id]
    comments.sort(key=lambda item: item.created_at, reverse=True)
    return comments[:limit]

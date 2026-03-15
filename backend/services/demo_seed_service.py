from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import datetime

from db import queries

POSITIVE_WORDS = ["great", "helpful", "awesome", "clear", "valuable", "nice"]
NEUTRAL_WORDS = ["discussion", "update", "question", "note", "detail", "context"]
NEGATIVE_WORDS = ["stuck", "broken", "confusing", "issue", "bad", "blocked"]


@dataclass
class ScenarioConfig:
    post_min: int
    post_max: int
    comments_min: int
    comments_max: int
    votes_multiplier: int
    mood: str


SCENARIOS: dict[str, ScenarioConfig] = {
    "regular": ScenarioConfig(post_min=5, post_max=10, comments_min=4, comments_max=5, votes_multiplier=2, mood="regular"),
    "uptrend": ScenarioConfig(post_min=14, post_max=20, comments_min=12, comments_max=20, votes_multiplier=8, mood="uptrend"),
    "decline": ScenarioConfig(post_min=3, post_max=5, comments_min=0, comments_max=1, votes_multiplier=1, mood="decline"),
}


def _word_for_mood(mood: str, i: int) -> str:
    if mood == "uptrend":
        return POSITIVE_WORDS[i % len(POSITIVE_WORDS)]
    if mood == "decline":
        return NEGATIVE_WORDS[i % len(NEGATIVE_WORDS)]
    return (POSITIVE_WORDS + NEUTRAL_WORDS)[i % (len(POSITIVE_WORDS) + len(NEUTRAL_WORDS))]


def _vote_value(mood: str) -> int:
    if mood == "uptrend":
        return 1
    if mood == "decline":
        return -1 if random.random() < 0.65 else 1
    return 1 if random.random() < 0.75 else -1


def _create_member(index: int, scenario: str, tag: str) -> str:
    email = f"{scenario}_member_{index}_{tag}@cultifydemo.com"
    username = f"{scenario}_{index}_{tag}"[:30]
    password = "password123"
    try:
        user = queries.create_user(email=email, password=password, username=username)
    except ValueError:
        user = queries.get_user_by_email(email)
        if not user:
            user = queries.create_user(email=f"{uuid.uuid4().hex[:8]}_{email}", password=password, username=f"{username[:20]}_{uuid.uuid4().hex[:6]}")
    return user.id


def seed_community_scenario(*, community_id: str, scenario: str) -> dict:
    config = SCENARIOS.get(scenario)
    if not config:
        raise ValueError("INVALID_SCENARIO")

    community = queries.get_community_by_id(community_id)
    if not community:
        raise ValueError("COMMUNITY_NOT_FOUND")

    # Replace mode: clear existing activity so each run produces a clean scenario snapshot.
    queries.clear_community_content(community_id=community_id)

    random.seed(datetime.utcnow().timestamp())
    tag = datetime.utcnow().strftime("%m%d%H%M%S")

    member_count = 10 if scenario == "regular" else (18 if scenario == "uptrend" else 6)
    member_ids: list[str] = []
    for i in range(member_count):
        user_id = _create_member(i, scenario, tag)
        queries.join_community(community_id=community_id, user_id=user_id)
        member_ids.append(user_id)

    posts_created = 0
    comments_created = 0
    votes_submitted = 0

    total_posts = random.randint(config.post_min, config.post_max)
    for p in range(total_posts):
        author_id = random.choice(member_ids)
        word = _word_for_mood(config.mood, p)
        post = queries.insert_post(
            community_id=community_id,
            title=f"{community.name} demo thread {p + 1}: {word}",
            body=f"Community update: this week feels {word}. Sharing practical context and asking for input.",
            flair="Discussion" if p % 2 == 0 else "Question",
            is_human=True,
            author_id=author_id,
            agent_id=None,
            opendata_citation=None,
        )
        posts_created += 1

        comments_per_post = random.randint(config.comments_min, config.comments_max)
        for c in range(comments_per_post):
            commenter = random.choice(member_ids)
            comment_word = _word_for_mood(config.mood, p + c)
            queries.insert_comment(
                post_id=post.id,
                community_id=community_id,
                body=f"Comment {c + 1}: this topic is {comment_word}. Adding a concrete detail for the thread.",
                parent_comment_id=None,
                is_human=True,
                author_id=commenter,
                agent_id=None,
            )
            comments_created += 1

        votes_target = max(1, comments_per_post * config.votes_multiplier)
        for _ in range(votes_target):
            voter = random.choice(member_ids)
            queries.vote_post(post_id=post.id, user_id=voter, value=_vote_value(config.mood))
            votes_submitted += 1

    return {
        "scenario": scenario,
        "community_id": community_id,
        "reset_performed": True,
        "posts_created": posts_created,
        "comments_created": comments_created,
        "post_votes_submitted": votes_submitted,
        "member_count": member_count,
    }

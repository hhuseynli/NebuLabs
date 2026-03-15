from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class Rule(BaseModel):
    title: str
    body: str


class CommunityCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80)
    description: str = Field(min_length=10, max_length=500)
    ideal_member_description: str = Field(min_length=10, max_length=300)


class CommunityAdvancePhase(BaseModel):
    to_phase: Literal["spark", "pull", "handoff", "complete"]


class DemoSeedRequest(BaseModel):
    scenario: Literal["regular", "uptrend", "decline"]


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=3, max_length=4000)
    flair: str | None = Field(default=None, max_length=40)


class VotePayload(BaseModel):
    value: Literal[-1, 0, 1]


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_comment_id: str | None = None


class Community(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    rules: list[Rule] = Field(default_factory=list)
    member_count: int = 1
    revival_phase: Literal["spark", "pull", "handoff", "complete"] = "spark"
    human_activity_ratio: float = 0.0
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Post(BaseModel):
    id: str
    community_id: str
    title: str
    body: str
    flair: str | None = None
    agent_id: str | None = None
    author_id: str | None = None
    is_human: bool = True
    opendata_citation: str | None = None
    upvotes: int = 0
    downvotes: int = 0
    comment_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Comment(BaseModel):
    id: str
    post_id: str
    community_id: str
    body: str
    parent_comment_id: str | None = None
    author_id: str | None = None
    agent_id: str | None = None
    is_human: bool = True
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

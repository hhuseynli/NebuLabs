from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class Agent(BaseModel):
    id: str
    community_id: str
    name: str
    backstory: str
    personality_traits: list[str] = Field(default_factory=list)
    opinion_set: dict[str, str] = Field(default_factory=dict)
    expertise_areas: list[str] = Field(default_factory=list)
    activity_level: Literal["high", "medium", "low"] = "medium"
    status: Literal["active", "retiring", "retired"] = "active"
    post_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

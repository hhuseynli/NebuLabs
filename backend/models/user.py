from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str = Field(min_length=3, max_length=32)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    karma: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

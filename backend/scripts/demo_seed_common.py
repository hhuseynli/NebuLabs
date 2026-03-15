from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"
DEFAULT_PASSWORD = "password123"

POSITIVE_WORDS = ["thanks", "great", "helpful", "love", "awesome", "nice", "works"]
NEGATIVE_WORDS = ["stuck", "broken", "hate", "bad", "confusing", "issue", "problem"]


@dataclass
class ScenarioProfile:
    name: str
    post_count: int
    comments_per_post: int
    votes_per_post: int
    mood: str


class DemoSeeder:
    def __init__(self, api_base: str, timeout: float = 30.0):
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, *, token: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{self.api_base}{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urlrequest.Request(url=url, data=body, headers=headers, method=method)

        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            text = exc.read().decode("utf-8") if exc.fp else ""
            raise RuntimeError(f"{method} {path} -> {exc.code}: {text.strip()}") from exc
        except URLError as exc:
            raise RuntimeError(f"{method} {path} -> connection failed: {exc}") from exc

        if not raw:
            return {}
        return json.loads(raw)

    def signup_or_login(self, *, email: str, username: str, password: str = DEFAULT_PASSWORD) -> tuple[str, dict[str, Any]]:
        try:
            data = self._request(
                "POST",
                "/auth/signup",
                payload={"email": email, "password": password, "username": username},
            )
            return data["token"], data["user"]
        except RuntimeError:
            data = self._request(
                "POST",
                "/auth/login",
                payload={"email": email, "password": password},
            )
            return data["token"], data["user"]

    def ensure_community(self, *, slug: str, owner_token: str, owner_name: str) -> dict[str, Any]:
        try:
            return self._request("GET", f"/communities/{slug}")
        except RuntimeError:
            title = slug.replace("-", " ").title()
            return self._request(
                "POST",
                "/communities",
                token=owner_token,
                payload={
                    "name": title,
                    "description": f"{title} demo community for organizer {owner_name}.",
                    "ideal_member_description": "Developers who ask practical questions and help each other solve problems.",
                },
            )

    def join_community(self, *, slug: str, token: str) -> None:
        self._request("POST", f"/communities/{slug}/join", token=token)

    def create_post(self, *, slug: str, token: str, title: str, body: str, flair: str) -> str:
        data = self._request(
            "POST",
            f"/communities/{slug}/posts",
            token=token,
            payload={"title": title, "body": body, "flair": flair},
        )
        return data["id"]

    def create_comment(self, *, post_id: str, token: str, body: str) -> None:
        self._request(
            "POST",
            f"/posts/{post_id}/comments",
            token=token,
            payload={"body": body, "parent_comment_id": None},
        )

    def vote_post(self, *, post_id: str, token: str, value: int) -> None:
        self._request(
            "POST",
            f"/posts/{post_id}/vote",
            token=token,
            payload={"value": value},
        )


def parse_args(default_slug: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Backend API base URL")
    parser.add_argument("--slug", default=default_slug, help="Community slug")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def _word_for_mood(mood: str, i: int) -> str:
    if mood == "uptrend":
        return POSITIVE_WORDS[i % len(POSITIVE_WORDS)]
    if mood == "decline":
        return NEGATIVE_WORDS[i % len(NEGATIVE_WORDS)]
    return POSITIVE_WORDS[i % len(POSITIVE_WORDS)] if i % 3 else NEGATIVE_WORDS[i % len(NEGATIVE_WORDS)]


def _vote_for_mood(mood: str) -> int:
    if mood == "uptrend":
        return 1
    if mood == "decline":
        return -1 if random.random() < 0.65 else 1
    return 1 if random.random() < 0.75 else -1


def seed_scenario(profile: ScenarioProfile, *, api_base: str, slug: str, seed: int) -> None:
    random.seed(seed)
    now_tag = datetime.utcnow().strftime("%m%d%H%M")
    seeder = DemoSeeder(api_base)

    owner_email = f"owner_{profile.mood}_{now_tag}@cultifydemo.com"
    owner_username = f"owner_{profile.mood}_{now_tag}"[:28]
    owner_token, owner = seeder.signup_or_login(email=owner_email, username=owner_username)

    community = seeder.ensure_community(slug=slug, owner_token=owner_token, owner_name=owner["username"])
    actual_slug = community["slug"]

    members: list[tuple[str, str]] = []
    member_count = 8 if profile.mood == "regular" else (12 if profile.mood == "uptrend" else 5)
    for i in range(member_count):
        email = f"{profile.mood}_member_{i}_{now_tag}@cultifydemo.com"
        username = f"{profile.mood}_m{i}_{now_tag}"[:30]
        token, user = seeder.signup_or_login(email=email, username=username)
        seeder.join_community(slug=actual_slug, token=token)
        members.append((token, user["username"]))

    created_posts = 0
    created_comments = 0
    created_votes = 0

    for i in range(profile.post_count):
        author_token, author_name = random.choice(members)
        mood_word = _word_for_mood(profile.mood, i)
        title = f"{profile.name} Thread {i + 1}: {mood_word.title()} progress update"
        body = (
            f"Quick update from {author_name}. This week discussion is {mood_word}. "
            f"We are tracking what works, what is confusing, and what members need next."
        )
        flair = "Discussion" if i % 2 == 0 else "Question"

        post_id = seeder.create_post(slug=actual_slug, token=author_token, title=title, body=body, flair=flair)
        created_posts += 1

        for c in range(profile.comments_per_post):
            commenter_token, commenter_name = random.choice(members)
            comment_word = _word_for_mood(profile.mood, i + c)
            comment = (
                f"{commenter_name}: This thread is {comment_word}. "
                "Sharing a practical tip and asking follow-up questions."
            )
            seeder.create_comment(post_id=post_id, token=commenter_token, body=comment)
            created_comments += 1

        for _ in range(profile.votes_per_post):
            voter_token, _ = random.choice(members)
            vote_value = _vote_for_mood(profile.mood)
            seeder.vote_post(post_id=post_id, token=voter_token, value=vote_value)
            created_votes += 1

    print(f"Scenario: {profile.name}")
    print(f"Community slug: {actual_slug}")
    print(f"Posts created: {created_posts}")
    print(f"Comments created: {created_comments}")
    print(f"Post votes submitted: {created_votes}")

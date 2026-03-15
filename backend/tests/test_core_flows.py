import os

from fastapi.testclient import TestClient

from db import queries
from db.supabase_client import clear_supabase_client_cache
from main import app


os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_KEY", None)
os.environ.pop("APP_MODE", None)
clear_supabase_client_cache()


client = TestClient(app)


def reset_store() -> None:
    queries.store.users_by_id.clear()
    queries.store.users_by_email.clear()
    queries.store.passwords.clear()
    queries.store.tokens.clear()
    queries.store.communities_by_id.clear()
    queries.store.communities_by_slug.clear()
    queries.store.community_members.clear()
    queries.store.agents_by_id.clear()
    queries.store.agents_by_community.clear()
    queries.store.posts_by_id.clear()
    queries.store.posts_by_community.clear()
    queries.store.comments_by_id.clear()
    queries.store.comments_by_post.clear()
    queries.store.post_votes.clear()
    queries.store.comment_votes.clear()
    queries.store.phase_history.clear()
    queries.store.user_bio.clear()


def signup_user(email: str, username: str):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "username": username},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    return data["token"], data["user"]


def create_community(token: str, name: str = "UrbanBeekeeping"):
    resp = client.post(
        "/api/v1/communities",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "description": "For city beekeepers and rooftop pollination enthusiasts.",
            "ideal_member_description": "Hobbyist beekeepers aged 25-45 interested in sustainability",
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_signup_and_login_success():
    reset_store()

    token, user = signup_user("test1@example.com", "test_user_1")
    assert token
    assert user["username"] == "test_user_1"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test1@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    payload = login.json()
    assert payload["user"]["username"] == "test_user_1"
    assert payload["token"]


def test_community_creation_returns_rules_without_auto_agents():
    reset_store()

    token, _ = signup_user("test2@example.com", "test_user_2")
    community = create_community(token)

    assert community["slug"] == "urbanbeekeeping"
    assert len(community["rules"]) >= 3
    assert len(community["agents"]) == 0
    assert community["revival_phase"] == "spark"


def test_vote_toggle_behavior_for_posts():
    reset_store()

    token, _ = signup_user("test4@example.com", "test_user_4")
    community = create_community(token, name="UrbanBeekeepingY")

    post = client.post(
        f"/api/v1/communities/{community['slug']}/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "My hive update", "body": "Some body text", "flair": "Progress"},
    )
    post_id = post.json()["id"]

    upvote = client.post(
        f"/api/v1/posts/{post_id}/vote",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 1},
    )
    assert upvote.status_code == 200
    assert upvote.json()["upvotes"] == 1
    assert upvote.json()["user_vote"] == 1

    toggle_off = client.post(
        f"/api/v1/posts/{post_id}/vote",
        headers={"Authorization": f"Bearer {token}"},
        json={"value": 1},
    )
    assert toggle_off.status_code == 200
    assert toggle_off.json()["upvotes"] == 0
    assert toggle_off.json()["user_vote"] is None


def test_join_and_leave_community_updates_member_count():
    reset_store()

    owner_token, _ = signup_user("owner@example.com", "owner_user")
    member_token, _ = signup_user("member@example.com", "member_user")
    community = create_community(owner_token, name="UrbanBeekeepingZ")

    joined = client.post(
        f"/api/v1/communities/{community['slug']}/join",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert joined.status_code == 200
    assert joined.json()["member_count"] == 2

    left = client.post(
        f"/api/v1/communities/{community['slug']}/leave",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert left.status_code == 200
    assert left.json()["member_count"] == 1


def test_error_envelope_for_unauthorized_request():
    reset_store()

    response = client.post(
        "/api/v1/communities",
        json={
            "name": "UnauthorizedCommunity",
            "description": "This request should fail without auth token.",
            "ideal_member_description": "Anyone",
        },
    )

    assert response.status_code == 401
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "HTTP_ERROR"

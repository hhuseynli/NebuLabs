from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None  # type: ignore[assignment]


def _load_backend_env() -> None:
    # Ensure DB helpers and scripts load backend/.env even when not started via main.py.
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path, override=False)


_load_backend_env()


@lru_cache(maxsize=1)
def get_supabase_client() -> Any | None:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)


def is_supabase_enabled() -> bool:
    return get_supabase_client() is not None


def get_app_mode() -> str:
    mode = os.getenv("APP_MODE", "").strip().lower()
    if mode in {"local", "hybrid", "supabase"}:
        return mode
    return "hybrid" if is_supabase_enabled() else "local"


def clear_supabase_client_cache() -> None:
    get_supabase_client.cache_clear()


def get_user_id_from_jwt(token: str) -> str | None:
    client = get_supabase_client()
    if not client:
        return None
    try:
        result = client.auth.get_user(token)
        user = getattr(result, "user", None)
        if user is None:
            return None
        return getattr(user, "id", None)
    except Exception:
        return None


def supabase_sign_up(email: str, password: str) -> tuple[str | None, str | None, str | None]:
    client = get_supabase_client()
    if not client:
        return None, None, "Supabase client not configured"
    try:
        result = client.auth.sign_up({"email": email, "password": password})
        user = getattr(result, "user", None)
        session = getattr(result, "session", None)
        user_id = getattr(user, "id", None) if user else None
        access_token = getattr(session, "access_token", None) if session else None
        if not user_id:
            return None, None, "Supabase did not return a user"
        return user_id, access_token, None
    except Exception as exc:
        return None, None, str(exc)


def supabase_sign_in(email: str, password: str) -> tuple[str | None, str | None, str | None]:
    client = get_supabase_client()
    if not client:
        return None, None, "Supabase client not configured"
    try:
        result = client.auth.sign_in_with_password({"email": email, "password": password})
        user = getattr(result, "user", None)
        session = getattr(result, "session", None)
        user_id = getattr(user, "id", None) if user else None
        access_token = getattr(session, "access_token", None) if session else None
        if not user_id or not access_token:
            return None, None, "Supabase did not return a full session"
        return user_id, access_token, None
    except Exception as exc:
        return None, None, str(exc)

from fastapi import Header, HTTPException

from db.supabase_client import get_app_mode, get_user_id_from_jwt, is_supabase_enabled
from db import queries


def get_current_user_id(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    mode = get_app_mode()
    if mode == "supabase" and not is_supabase_enabled():
        raise HTTPException(status_code=503, detail="Supabase is required but not configured")

    token = authorization.split(" ", 1)[1].strip()
    if mode != "supabase":
        user = queries.get_user_by_token(token)
        if user:
            return user.id

    supabase_user_id = get_user_id_from_jwt(token)
    if supabase_user_id:
        return supabase_user_id

    raise HTTPException(status_code=401, detail="Invalid token")


def get_optional_user_id(authorization: str = Header(default="")) -> str | None:
    if not authorization.startswith("Bearer "):
        return None

    mode = get_app_mode()
    if mode == "supabase" and not is_supabase_enabled():
        return None

    token = authorization.split(" ", 1)[1].strip()
    if mode != "supabase":
        user = queries.get_user_by_token(token)
        if user:
            return user.id
    return get_user_id_from_jwt(token)

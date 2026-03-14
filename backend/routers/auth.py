from fastapi import APIRouter, HTTPException, status

from db import queries
from db.supabase_client import get_app_mode, is_supabase_enabled, supabase_sign_in, supabase_sign_up
from models.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate):
    mode = get_app_mode()
    supabase_enabled = is_supabase_enabled()

    if mode == "supabase" and not supabase_enabled:
        raise HTTPException(status_code=503, detail="Supabase is required but not configured")

    if mode != "local" and supabase_enabled:
        user_id, token, signup_error = supabase_sign_up(payload.email, payload.password)
        if not user_id:
            raise HTTPException(status_code=400, detail=f"Unable to sign up with Supabase: {signup_error or 'unknown error'}")

        # Ensure profile row exists in local app user table.
        try:
            user = queries.create_user(
                email=payload.email,
                password=payload.password,
                username=payload.username,
                user_id=user_id,
            )
        except ValueError:
            # Existing profile row is acceptable.
            existing = queries.get_user_by_email(payload.email)
            if not existing:
                raise HTTPException(status_code=409, detail="Email already exists")
            user = existing

        if not token:
            _, token, signin_error = supabase_sign_in(payload.email, payload.password)

        if not token:
            if mode == "supabase":
                raise HTTPException(status_code=503, detail=f"Unable to issue Supabase session token: {signin_error or 'unknown error'}")
            # In hybrid mode, local token fallback keeps local dev usable.
            token = queries.issue_token(user.id)

        return {
            "user": {"id": user.id, "username": user.username, "karma": user.karma},
            "token": token,
        }

    try:
        user = queries.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "EMAIL_TAKEN":
            raise HTTPException(status_code=409, detail="Email already exists")
        if code == "USERNAME_TAKEN":
            raise HTTPException(status_code=409, detail="Username already exists")
        raise

    token = queries.issue_token(user.id)
    return {
        "user": {"id": user.id, "username": user.username, "karma": user.karma},
        "token": token,
    }


@router.post("/login")
async def login(payload: UserLogin):
    mode = get_app_mode()
    supabase_enabled = is_supabase_enabled()

    if mode == "supabase" and not supabase_enabled:
        raise HTTPException(status_code=503, detail="Supabase is required but not configured")

    if mode != "local" and supabase_enabled:
        user_id, token, signin_error = supabase_sign_in(payload.email, payload.password)
        if (not user_id or not token) and mode == "supabase":
            raise HTTPException(status_code=401, detail=f"Invalid credentials: {signin_error or 'unknown error'}")
        if user_id and token:
            # Resolve profile by email from local cache/state fallback.
            user = queries.get_user_by_email(payload.email)
            if not user:
                username = payload.email.split("@")[0]
                try:
                    user = queries.create_user(payload.email, payload.password, username, user_id=user_id)
                except ValueError:
                    user = queries.get_user_by_email(payload.email)

            return {
                "user": {"id": user.id if user else user_id, "username": user.username if user else payload.email, "karma": user.karma if user else 0},
                "token": token,
            }

    user = queries.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = queries.issue_token(user.id)
    return {
        "user": {"id": user.id, "username": user.username, "karma": user.karma},
        "token": token,
    }

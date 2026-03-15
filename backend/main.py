import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers.agents import router as agents_router
from routers.auth import router as auth_router
from routers.communities import router as communities_router
from routers.feed import router as feed_router
from routers.posts import router as posts_router
from routers.revival import router as revival_router
from routers.users import router as users_router
from scheduler import start_scheduler

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_scheduler()
    yield


app = FastAPI(title="Kindling API", version="0.1.0", lifespan=lifespan)

def _normalize_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


def _load_allowed_origins() -> list[str]:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    configured = os.getenv("FRONTEND_URLS", "")
    single = os.getenv("FRONTEND_URL", "")
    if single:
        configured = f"{configured},{single}" if configured else single

    if configured:
        for raw in configured.split(","):
            origin = _normalize_origin(raw)
            if origin and origin not in origins:
                origins.append(origin)

    return origins


allowed_origins = _load_allowed_origins()
allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(communities_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(revival_router, prefix="/api/v1")
app.include_router(feed_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        payload = {"error": detail}
    else:
        code = "HTTP_ERROR"
        message = detail if isinstance(detail, str) else "Request failed"
        payload = {"error": {"code": code, "message": message}}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {}
    loc = first.get("loc") if isinstance(first, dict) else []
    field = ".".join(str(x) for x in loc[1:]) if isinstance(loc, (list, tuple)) and len(loc) > 1 else "field"
    message = first.get("msg") if isinstance(first, dict) and first.get("msg") else "Invalid request payload"
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": f"{field}: {message}"}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "Unexpected server error"}},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

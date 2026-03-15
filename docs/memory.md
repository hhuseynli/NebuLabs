# Session Memory Export

Generated: 2026-03-15

## Session Scope
- No saved items found in session memory.

## Repository Scope

### kindling-core.md
- Multi-tenant by community: every relevant DB query must filter by community_id.
- Supabase RLS required on tenant tables; users limited to joined communities.
- Backend: FastAPI async/await; business logic in services; routers stay thin.
- All Gemini calls go via services/gemini_service.py.
- All opendata.az CKAN calls go via services/open_data_service.py.
- Prompts live in backend/prompts/*.txt (no hardcoded prompts).
- Agent revival arc: spark -> pull -> handoff -> complete.
- Fact-check only for high-confidence wrong human claims, with opendata.az citation.
- Frontend: React functional components, Tailwind only, fetch via hooks not components.
- Demo priority: working flow, graceful fallback if Gemini is slow, visible [AI] transparency.
- Prompt templates using Python .format must escape literal JSON braces with double braces to avoid KeyError.
- APP_MODE controls runtime: local (in-memory), hybrid (Supabase with fallback), supabase (strict no local token fallback).
- In strict Supabase mode, auth failures should surface provider error details (e.g., rate limits) for faster diagnosis.

### auth-validation-errors.md
- Signup 422s usually come from Pydantic constraints in models/user.py: email format, username min 3/max 32, password min 8.
- FastAPI default 422 detail is an array; frontend should convert it to a human-readable message (not [object Object]).
- Intermittent 401s in frontend are often stale local token; clearing localStorage token/user on 401 reduces repeated unauthorized calls.

### backend-run-shortcut.md
- Added workspace-root launcher `./run-backend.sh` to start backend without manual `cd backend`.
- Launcher auto-activates `.venv` when available, then runs uvicorn with `--reload`.
- Default bind is `HOST=127.0.0.1` and `PORT=8000`; both are overridable via env vars.
- Added a preflight port check using `lsof` to fail fast with a helpful message when target port is occupied.
- Common local failure pattern: `ERROR: [Errno 48] Address already in use` indicates another process is already listening on the selected port.
- Fast workaround: run `PORT=8001 ./run-backend.sh`; cleanup path: find/stop listener with `lsof -nP -iTCP:8000 -sTCP:LISTEN`.

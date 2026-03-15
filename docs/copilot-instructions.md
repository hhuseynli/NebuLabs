# Copilot Instructions — Cultify

## What Cultify Is
Cultify is a Reddit-style community platform built for tech communities (GDGs, Stack Overflow groups, local dev meetups). It has all standard Reddit mechanics plus an AI layer that reduces organizer burden, surfaces community health signals, and keeps members engaged — making tech communities impossible to abandon.

## Stack
- **Frontend**: React (Vite), TailwindCSS, React Router v6 — Vercel
- **Backend**: Python (FastAPI) — Railway
- **Database**: Supabase (Postgres + Auth + RLS)
- **AI**: Google Gemini API (`gemini-2.0-flash` default, `gemini-2.0-pro` for quality-critical generation)
- **Scheduling**: APScheduler in-process with FastAPI (only needed if Revival Arc is active)

---

## Runtime Modes (APP_MODE)
| Mode | Behaviour |
|------|-----------|
| `local` | In-memory storage, no Supabase required |
| `hybrid` | Supabase with local token fallback |
| `supabase` | Strict — no local fallback; surfaces provider error details on auth failure |

Set via `APP_MODE=` in `.env`.

---

## Multi-Tenancy
Every community is a fully isolated tenant. **Every DB query must filter by `community_id`.** Supabase RLS policies enforce this at the database layer. The backend uses the service role key which bypasses RLS for internal AI writes — never expose the service key to the frontend.

---

## AI Feature Status

Only three features are active in the current build. All six are fully designed.

| Feature | Status | Router | Service |
|---------|--------|--------|---------|
| Community FAQ Tab | ✅ ACTIVE | `routers/faq.py` | `services/faq_service.py` |
| Per-Post Fact Checker | ✅ ACTIVE | `routers/factcheck.py` | `services/factcheck_service.py` |
| Sentiment Dashboard | ✅ ACTIVE | `routers/sentiment.py` | `services/sentiment_service.py` |
| Revival Arc Agents | 🔲 DESIGNED | `routers/agents.py` | `services/agent_service.py` |
| Event Suggester | 🔲 DESIGNED | `routers/events.py` | `services/event_service.py` |
| Weekly Digest | 🔲 DESIGNED | `routers/digest.py` | `services/digest_service.py` |

**To activate a designed feature**: uncomment its router in `main.py`, ensure service + prompt files exist, update this table.
**To deactivate an active feature**: comment out its router in `main.py`, leave service file in place.

---

## Active Feature Behaviour

### FAQ Tab
- Endpoint: `GET /communities/:slug/faq/ask?q=...`
- Fetches last 200 posts + comments for community, passes with question to Gemini
- Returns: `{ answer, source_post_id, confidence }`
- Never invents — Gemini instructed to only synthesise from provided content
- Prompt: `prompts/faq_answer.txt`

### Per-Post Fact Checker
- Endpoint: `POST /posts/:id/factcheck`
- Lazy — only runs when user opens the panel, not on post creation
- Gemini reads post body, identifies verifiable claims, returns verdict per claim
- Verdict shape: `{ claim, verdict: "supported"|"unverified"|"contradicted", explanation, confidence }`
- Prompt: `prompts/factcheck_analyze.txt`

### Sentiment Dashboard
- Endpoint: `GET /communities/:slug/sentiment`
- Organizer-only — enforced in route handler by checking community creator
- Reads last 100 posts + comments, returns health report
- Returns: `{ score, trending_topics[], friction_signals[], churn_risk_members[] }`
- Prompt: `prompts/sentiment_report.txt`

---

## Code Conventions

### Python (FastAPI)
- `async/await` throughout — use `httpx.AsyncClient` for all external HTTP
- Pydantic v2 models for all request/response schemas
- Thin routers — all business logic in `/services/`
- All Gemini calls through `services/gemini_service.py` only — no direct API calls elsewhere
- Prompts in `/prompts/*.txt` — never hardcode prompt strings inline
- **Escape literal JSON braces in `.format()` prompts with `{{` and `}}`** — bare `{}` causes `KeyError`
- Every query includes `community_id` filter — no exceptions
- `python-dotenv` for env vars — never hardcode keys

### React
- Functional components only — no class components
- Custom hooks in `/hooks/` for all async/stateful logic — never fetch directly in components
- Context API for: auth state, current community, feed state
- TailwindCSS only — no inline styles, no CSS modules
- **On any 401 response → clear `localStorage` token and user, redirect to `/login`** — stale tokens cause cascading errors
- FastAPI 422 returns `detail` as an array — convert to human-readable string before displaying; never show `[object Object]`

### Database
- All queries in `db/queries.py`
- RLS enabled on all tenant tables
- Timestamps always UTC

### General
- Mock fallback in every AI service — demo must survive slow Gemini
- `USE_MOCK=true` in `.env` forces mock mode globally
- Never expose raw Gemini responses to frontend — always parse and validate first
- Log AI actions to `agent_logs` table

---

## Known Issues & Fixes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `422` on signup | Pydantic constraints: username 3–32 chars, password ≥8 chars, valid email | Validate on frontend before submit |
| `[object Object]` in error UI | FastAPI 422 `detail` is array, not string | `detail.map(e => e.msg).join(', ')` |
| Intermittent `401` | Stale localStorage token | Clear token/user on every 401, redirect to login |
| `KeyError` in prompt | Literal `{}` in `.format()` string | Replace `{` with `{{` and `}` with `}}` |
| `Address already in use` | Port 8000 occupied | `PORT=8001 ./run-backend.sh` |

---

## File Reference

```
backend/
  main.py                    # register only ACTIVE routers here
  run-backend.sh             # workspace-root launcher — auto-activates .venv, port preflight
  scheduler.py               # only needed if Revival Arc active
  routers/
    auth.py
    communities.py
    posts.py
    comments.py
    faq.py                   # ✅
    factcheck.py             # ✅
    sentiment.py             # ✅
    agents.py                # 🔲
    revival.py               # 🔲
    feed.py                  # 🔲
    events.py                # 🔲
    digest.py                # 🔲
  services/
    gemini_service.py        # ALL Gemini calls go here
    faq_service.py           # ✅
    factcheck_service.py     # ✅
    sentiment_service.py     # ✅
    agent_service.py         # 🔲
    revival_service.py       # 🔲
    event_service.py         # 🔲
    digest_service.py        # 🔲
  models/
    community.py / post.py / comment.py / agent.py / user.py
  prompts/
    faq_answer.txt           # ✅
    factcheck_analyze.txt    # ✅
    sentiment_report.txt     # ✅
    generate_agents.txt      # 🔲
    spark_post.txt           # 🔲
    pull_reply.txt           # 🔲
    suggest_event.txt        # 🔲
    weekly_digest.txt        # 🔲
  db/
    supabase_client.py
    queries.py               # all DB queries — always filter by community_id

frontend/src/
  context/    AuthContext.jsx, CommunityContext.jsx, FeedContext.jsx
  hooks/      useAuth.js, usePosts.js, useComments.js,
              useFAQ.js, useFactCheck.js, useSentiment.js,
              useAgents.js (🔲), useRevival.js (🔲)
  pages/      Landing, Login, Signup, Home, Community,
              PostDetail, Profile, CreateCommunity, Dashboard
  components/
    layout/     Navbar.jsx, Sidebar.jsx
    posts/      PostCard.jsx, CreatePostForm.jsx
    comments/   CommentThread.jsx, CommentCard.jsx, CommentForm.jsx
    voting/     VoteButtons.jsx
    tabs/       FAQTab.jsx, FactCheckPanel.jsx, SentimentDashboard.jsx
    agents/     AgentBadge.jsx, AgentCard.jsx (🔲)
    revival/    RevivalArcBar.jsx, ActivityChart.jsx (🔲)
    community/  CommunityCard.jsx, CommunityHeader.jsx, RulesPanel.jsx
```

## Copilot Priorities
1. `community_id` filter on every relevant DB query — non-negotiable
2. Only wire ACTIVE feature routers in `main.py`
3. All three active features must be demoable end-to-end
4. Reddit mechanics must feel familiar — don't reinvent the UX
5. Mock fallbacks over broken UI when Gemini is slow
6. README.md is scored by AI judge — keep it updated

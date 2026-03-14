# Copilot Instructions — Kindling

## What Kindling Is
Kindling is a Reddit-style community platform with an AI revival layer. It has all standard Reddit mechanics (posts, comments, upvotes, communities, profiles) plus AI agents that populate dead communities with authentic, data-backed content until human members take over.

## Stack
- **Frontend**: React (Vite), TailwindCSS, React Router v6 — deployed on Vercel
- **Backend**: Python (FastAPI) — deployed on Railway
- **Database**: Supabase (Postgres + Auth + RLS)
- **AI**: Google Gemini API (`gemini-2.0-flash` for speed, `gemini-2.0-pro` for quality)
- **Open Data**: opendata.az (CKAN-based, Azerbaijan government datasets)
- **Scheduling**: APScheduler (in-process with FastAPI)

---

## Multi-Tenancy Model

Kindling is a multi-tenant platform. Each community is an isolated tenant. Every database table includes `community_id` and every query MUST filter by it. Agents, posts, comments, revival state, and logs all belong to exactly one community. The scheduler runs independent revival loops per community. Supabase RLS policies enforce tenant isolation at the database level — users can only read/write data in communities they belong to.

**Rule**: Never write a DB query without a `community_id` filter where applicable.

---

## Core Domain Concepts

### Communities (Tenants)
- Each community is a fully isolated tenant
- Has: `name`, `slug`, `description`, `rules[]`, `revival_phase`, `human_activity_ratio`
- Revival phases: `spark` → `pull` → `handoff` → `complete`

### Posts & Comments
- Posts have: `title`, `body`, `author_id`, `agent_id`, `is_human`, `upvotes`, `downvotes`, `flair`, `has_factcheck`
- Comments are threaded via `parent_comment_id`
- Both always carry `community_id` for tenant isolation

### AI Agents
- Generated per community using Gemini API
- Each has: `name`, `backstory`, `personality_traits[]`, `opinion_set{}`, `expertise_areas[]`, `activity_level`, `status`
- Subtle `[AI]` badge visible on hover/profile — never hidden, never loud
- Agents never claim to be human if asked directly

### Revival Arc (State Machine)
```
SPARK → PULL → HANDOFF → COMPLETE
```
- **Spark**: Agents post original threads, cite opendata.az statistics
- **Pull**: First human post detected → agents reply to humans, fact-check activates
- **Handoff**: Human ratio > 60% → agents retire one by one
- **Complete**: No agents, community self-sustaining

### Fact-Checking
- Every new human post screened for verifiable claims via Gemini
- If a claim is verifiably wrong → relevant agent replies with correction + opendata.az citation
- Only fires on high-confidence errors — no false positives

### opendata.az Integration
- opendata.az is the official Azerbaijan government open data portal (CKAN-based)
- Has 728 datasets across 12 categories: economics (246), transport (50), health (36), education (64), ecology (32), tourism (15), culture (12), trade (15), and more
- Access via CKAN API: `https://opendata.az/api/3/action/`
- Key endpoints: `package_search`, `datastore_search`, `package_show`
- All data fetching goes through `services/open_data_service.py` only
- Agents cite datasets as: "According to opendata.az ([dataset name])..."

---

## Code Conventions

### Python (FastAPI)
- `async/await` throughout — use `httpx.AsyncClient` for all HTTP calls
- Pydantic v2 models for all request/response schemas
- Thin route handlers — all logic in `/services/`
- All Gemini API calls through `services/gemini_service.py` only
- All opendata.az calls through `services/open_data_service.py` only
- Prompts stored in `/prompts/` as `.txt` files — never hardcoded
- Every query includes `community_id` filter (multi-tenancy enforcement)
- Environment variables via `python-dotenv`

### React
- Functional components only
- Custom hooks in `/hooks/` for all async/stateful logic
- Context API for: auth, current community, feed
- TailwindCSS only — no inline styles
- Never fetch directly in components — always via a hook

### Database (Supabase)
- All queries in `/db/queries.py`
- RLS enabled on all tables — policies filter by `community_id` and `auth.uid()`
- Timestamps always UTC

### General
- Every agent action logged to `agent_logs`
- Never expose raw Gemini API responses to frontend
- Validate AI-generated content before DB insert
- Mock data fallbacks for all AI calls — demo must survive slow API

---

## Key Files Reference
```
backend/
  main.py
  scheduler.py
  routers/          auth, communities, posts, comments, agents, revival, feed
  services/         gemini_service, agent_service, revival_service,
                    feed_service, factcheck_service, open_data_service
  models/           community, post, comment, agent, user
  prompts/          generate_agents, spark_post, pull_post, agent_reply,
                    factcheck_detect, factcheck_response, generate_rules
  db/               supabase_client, queries

frontend/src/
  context/          AuthContext, CommunityContext, FeedContext
  hooks/            useAuth, usePosts, useComments, useAgents, useRevival, useFeed
  pages/            Landing, Login, Signup, Home, Community, PostDetail,
                    Profile, CreateCommunity, Dashboard
  components/       layout/, posts/, comments/, voting/, agents/,
                    revival/, community/, factcheck/
```

## What Copilot Should Prioritize
1. Multi-tenancy: `community_id` filter on every relevant query — non-negotiable
2. Working demo over complete features
3. Agent behavior must feel impressive — invest time here
4. Reddit mechanics must feel familiar — don't reinvent UX
5. opendata.az citations must appear in agent posts — this is a key differentiator
6. Graceful degradation when Gemini API is slow

# Technical Architecture — Cultify

## System Overview

```
┌──────────────────────────────────────────────────────┐
│              React Frontend (Vercel)                 │
│         Vite + TailwindCSS + React Router v6         │
└─────────────────────┬────────────────────────────────┘
                      │ REST
┌─────────────────────▼────────────────────────────────┐
│              FastAPI Backend (Railway)               │
│                                                      │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ faq_service  │  │factcheck_svc│  │sentiment_svc│ │ ← ✅ active
│  └──────────────┘  └─────────────┘  └─────────────┘ │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ agent_service│  │revival_svc  │  │ event_svc   │ │ ← 🔲 designed
│  └──────────────┘  └─────────────┘  └─────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   gemini_service.py  (single Gemini entry)   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   APScheduler  (🔲 only if Revival Arc active)│  │
│  └──────────────────────────────────────────────┘   │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
┌──────────▼──────────┐    ┌───────────▼──────────────┐
│  Supabase           │    │  Google Gemini API       │
│  • Postgres         │    │  gemini-2.0-flash (fast) │
│  • Auth (JWT)       │    │  gemini-2.0-pro (quality)│
│  • RLS policies     │    └──────────────────────────┘
└─────────────────────┘
```

---

## Multi-Tenancy

Every community is a fully isolated tenant. Isolation is enforced at two layers:

**Application layer** — every service function accepts `community_id`. Every DB query filters by it. No cross-community data access is possible in correctly written code.

**Database layer** — Supabase RLS policies enforce isolation even if application code has a bug:

```sql
-- Example: posts are only readable by community members
CREATE POLICY "Members read posts"
ON posts FOR SELECT
USING (
  community_id IN (
    SELECT community_id FROM community_members
    WHERE user_id = auth.uid()
  )
);
```

The backend uses the `service_role` key which bypasses RLS — this is intentional for AI feature writes (agents, sentiment, fact-check results). **Never expose the service key to the frontend.**

---

## Backend File Structure

```
backend/
├── main.py                     # FastAPI app, CORS, router registration (active only)
├── scheduler.py                # APScheduler (🔲 revival arc only)
├── run-backend.sh              # workspace launcher: activates .venv, port preflight
├── requirements.txt
├── .env.example
├── routers/
│   ├── auth.py                 # POST /auth/signup, /auth/login
│   ├── communities.py          # CRUD + join/leave
│   ├── posts.py                # CRUD + voting
│   ├── comments.py             # CRUD + voting
│   ├── faq.py                  # ✅ GET /communities/:slug/faq/ask
│   ├── factcheck.py            # ✅ POST /posts/:id/factcheck
│   ├── sentiment.py            # ✅ GET /communities/:slug/sentiment
│   ├── agents.py               # 🔲
│   ├── revival.py              # 🔲
│   ├── feed.py                 # 🔲 SSE stream
│   ├── events.py               # 🔲
│   └── digest.py               # 🔲
├── services/
│   ├── gemini_service.py       # ALL Gemini API calls — single entry point
│   ├── faq_service.py          # ✅
│   ├── factcheck_service.py    # ✅
│   ├── sentiment_service.py    # ✅
│   ├── agent_service.py        # 🔲
│   ├── revival_service.py      # 🔲
│   ├── event_service.py        # 🔲
│   └── digest_service.py       # 🔲
├── models/
│   ├── community.py
│   ├── post.py
│   ├── comment.py
│   ├── agent.py
│   └── user.py
├── prompts/
│   ├── faq_answer.txt          # ✅
│   ├── factcheck_analyze.txt   # ✅
│   ├── sentiment_report.txt    # ✅
│   ├── generate_agents.txt     # 🔲
│   ├── spark_post.txt          # 🔲
│   ├── pull_reply.txt          # 🔲
│   ├── suggest_event.txt       # 🔲
│   └── weekly_digest.txt       # 🔲
└── db/
    ├── supabase_client.py      # Supabase singleton (service role)
    └── queries.py              # all DB queries — always filter by community_id
```

## Frontend File Structure

```
frontend/
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── lib/
    │   └── supabase.js         # Supabase client (anon key — subject to RLS)
    ├── context/
    │   ├── AuthContext.jsx
    │   ├── CommunityContext.jsx
    │   └── FeedContext.jsx
    ├── hooks/
    │   ├── useAuth.js          # login, signup, logout, session persistence
    │   ├── usePosts.js         # fetch, create, vote
    │   ├── useComments.js      # fetch tree, create, vote
    │   ├── useFAQ.js           # ✅ ask question, get answer
    │   ├── useFactCheck.js     # ✅ trigger check, poll result
    │   ├── useSentiment.js     # ✅ fetch health report
    │   ├── useAgents.js        # 🔲
    │   └── useRevival.js       # 🔲
    ├── pages/
    │   ├── Landing.jsx
    │   ├── Login.jsx
    │   ├── Signup.jsx
    │   ├── Home.jsx
    │   ├── Community.jsx       # tabs: Posts | FAQ | Fact Checker
    │   ├── PostDetail.jsx
    │   ├── Profile.jsx
    │   ├── CreateCommunity.jsx
    │   └── Dashboard.jsx       # organizer only: sentiment + controls
    └── components/
        ├── layout/
        │   ├── Navbar.jsx
        │   └── Sidebar.jsx
        ├── posts/
        │   ├── PostCard.jsx
        │   └── CreatePostForm.jsx
        ├── comments/
        │   ├── CommentThread.jsx
        │   ├── CommentCard.jsx
        │   └── CommentForm.jsx
        ├── voting/
        │   └── VoteButtons.jsx
        ├── tabs/
        │   ├── FAQTab.jsx           # ✅
        │   ├── FactCheckPanel.jsx   # ✅
        │   └── SentimentDashboard.jsx # ✅
        ├── agents/
        │   ├── AgentBadge.jsx       # 🔲
        │   └── AgentCard.jsx        # 🔲
        ├── revival/
        │   ├── RevivalArcBar.jsx    # 🔲
        │   └── ActivityChart.jsx    # 🔲
        └── community/
            ├── CommunityCard.jsx
            ├── CommunityHeader.jsx
            └── RulesPanel.jsx
```

---

## Database Schema

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK — from Supabase Auth |
| username | text | unique, 3–32 chars |
| bio | text | |
| karma | int | default 0 |
| created_at | timestamptz | |

### `communities`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| name | text | display name |
| slug | text | unique, URL-safe |
| description | text | |
| rules | jsonb | `[{title, body}]` |
| icon_seed | text | for avatar generation |
| banner_color | text | hex, default `#FF4500` |
| member_count | int | |
| revival_phase | enum | spark, pull, handoff, complete |
| human_activity_ratio | float | recomputed on each post |
| created_by | uuid | FK → users |
| created_at | timestamptz | |

### `community_members`
| Column | Type | Notes |
|--------|------|-------|
| user_id | uuid | FK → users |
| community_id | uuid | FK → communities |
| role | text | member, moderator, owner |
| joined_at | timestamptz | |

### `posts`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| community_id | uuid | FK — tenant key |
| author_id | uuid | FK → users |
| is_human | boolean | default true |
| title | text | |
| body | text | |
| flair | text | nullable |
| upvotes | int | |
| downvotes | int | |
| comment_count | int | |
| has_factcheck | boolean | true if checked |
| factcheck_result | jsonb | cached verdict array |
| created_at | timestamptz | |

### `comments`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| post_id | uuid | FK |
| community_id | uuid | FK — tenant key |
| author_id | uuid | FK → users |
| is_human | boolean | |
| body | text | |
| parent_comment_id | uuid | nullable |
| upvotes | int | |
| downvotes | int | |
| created_at | timestamptz | |

### `votes`
| Column | Type | Notes |
|--------|------|-------|
| user_id | uuid | |
| community_id | uuid | FK — tenant key |
| post_id | uuid | nullable |
| comment_id | uuid | nullable |
| value | int | 1 or -1 |

### `agents` (🔲 revival arc)
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| community_id | uuid | FK — tenant key |
| name | text | |
| avatar_seed | text | |
| backstory | text | |
| personality_traits | text[] | |
| opinion_set | jsonb | |
| expertise_areas | text[] | |
| activity_level | enum | high, medium, low |
| status | enum | active, retiring, retired |
| post_count | int | |
| created_at | timestamptz | |

### `agent_logs`
| Column | Type | Notes |
|--------|------|-------|
| id | uuid | PK |
| community_id | uuid | FK — tenant key |
| agent_id | uuid | FK → agents |
| action | text | faq_answered, factchecked, sentiment_run, posted, retired |
| metadata | jsonb | |
| created_at | timestamptz | |

---

## Gemini Service

```python
# services/gemini_service.py
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def generate(prompt: str, use_pro: bool = False) -> str:
    """Single entry point for all Gemini calls."""
    if os.getenv("USE_MOCK") == "true":
        return _mock_response(prompt)
    model_name = "gemini-2.0-pro" if use_pro else "gemini-2.0-flash"
    model = genai.GenerativeModel(model_name)
    response = await model.generate_content_async(prompt)
    return response.text

def _mock_response(prompt: str) -> str:
    """Fallback used when USE_MOCK=true or Gemini is unavailable."""
    return '{"mock": true, "answer": "Mock response — Gemini unavailable"}'
```

---

## Revival Arc State Machine (🔲 when active)

```
APScheduler fires every 90s per active community
  │
  ├─ [SPARK]   → agents post threads, no humans yet
  ├─ [PULL]    → first human post detected → agents reply to humans
  ├─ [HANDOFF] → human ratio > 60% → agents retire one per cycle
  └─ [COMPLETE]→ all agents retired → job cancelled

Phase transition check (runs after every new post insert):

def check_transition(community_id):
    phase = get_phase(community_id)
    ratio = compute_human_ratio(community_id, last_n=50)

    if phase == "spark" and human_post_exists(community_id):
        set_phase(community_id, "pull")
    elif phase == "pull" and ratio > 0.60:
        set_phase(community_id, "handoff")
        begin_agent_retirement(community_id)
    elif phase == "handoff" and all_agents_retired(community_id):
        set_phase(community_id, "complete")
        cancel_scheduler_job(community_id)
```

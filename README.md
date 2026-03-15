# Cultify

**Make tech communities impossible to abandon.**

Cultify is a Reddit-style community platform built for tech communities — Google Developer Groups, Stack Overflow communities, and local dev meetups. It ships with an AI layer that handles the repetitive work that burns organizers out: answering FAQs, fact-checking technical posts, and surfacing community health signals — so organizers can focus on what only humans can do.

> Built at the **Build with AI Hackathon** · Baku, Azerbaijan · March 2026

---

## Table of Contents

- [The Problem](#the-problem)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Pivot Guide](#pivot-guide)
- [Contributing](#contributing)

---

## The Problem

Tech communities are fragile. Most don't survive their first year.

| Failure Mode | What Happens |
|---|---|
| **Engagement Decay** | Initial excitement fades. Members attend once, then disappear. No mechanism to pull them back. |
| **Silent Members** | 80% of members lurk. No onboarding, no pathways to contribute. Talent goes untapped. |
| **Fragmented Tooling** | Discord, Meetup, Notion, LinkedIn — all disconnected. Organizers burn out managing chaos. |
| **No Signal on Health** | Organizers have no data. They can't tell if the community is growing, stagnating, or dying. |

These communities aren't optional infrastructure — they are the ecosystem. When a tech community dies, it takes its accumulated knowledge, trust, and talent with it.

---

## Features

### Reddit Core
- Email signup and login via Supabase Auth
- Create and join communities with rules and descriptions
- Posts with title, body, and flair tagging
- Upvote / downvote on posts and comments
- Threaded nested comments
- User profiles with karma and activity history
- Home feed aggregated from joined communities
- Community feed with Hot / New / Top sorting
- Full multi-tenant isolation — communities are fully independent

### AI Features

> **Three features are active in the current build.** All six are fully designed and ready to enable — see [Pivot Guide](#pivot-guide).

#### ✅ Community FAQ Tab
Every community gets a live FAQ tab. Members ask questions in plain language; the AI searches the entire community's post and comment history and returns an instant answer with a citation to the source thread. New members get answered in seconds. The organizer never has to answer the same question twice.

#### ✅ Per-Post Fact Checker
Every post has an inline AI analysis panel. On demand, the AI reads the post, identifies each verifiable technical claim, and returns a verdict: **Supported**, **Unverified**, or **Contradicted** — with a plain-language explanation. Built for dev communities where wrong advice about security, APIs, or configuration spreads fast.

#### ✅ Sentiment Dashboard *(organizer only)*
The organizer dashboard shows a live community health report: overall sentiment score (0–100), trending topics, friction signals, and members at churn risk. Gives organizers the signal on community health they've never had before.

#### 🔲 Revival Arc Agents *(designed)*
AI agents populate new communities during the cold start phase with authentic content. State machine: Spark → Pull → Handoff → Complete. Agents retire as human activity grows.

#### 🔲 Event Suggester *(designed)*
Detects engagement momentum peaks, suggests community events, and drafts the event post with format, time, and agenda.

#### 🔲 Weekly Digest *(designed)*
Personalized weekly summary per member — top missed discussions, questions matching their expertise, upcoming events. Zero organizer effort.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TailwindCSS + React Router v6 |
| Backend | Python 3.11 + FastAPI |
| Database | Supabase (Postgres + Auth + Row Level Security) |
| AI | Google Gemini API (`gemini-2.0-flash` / `gemini-2.0-pro`) |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) account (free tier)
- [Google AI Studio](https://aistudio.google.com) API key

### Clone

```bash
git clone https://github.com/your-org/cultify.git
cd cultify
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in your keys
```

Start the server (from workspace root):

```bash
./run-backend.sh
```

The launcher auto-activates `.venv` and checks for port conflicts. If port 8000 is occupied:

```bash
PORT=8001 ./run-backend.sh

# Find what's using the port:
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local       # fill in your keys
npm run dev                       # http://localhost:5173
```

---

## Environment Variables

### Backend — `backend/.env`

```env
GEMINI_API_KEY=           # from aistudio.google.com
SUPABASE_URL=             # from Supabase project settings
SUPABASE_SERVICE_KEY=     # service_role key — never expose to frontend
APP_MODE=local            # local | hybrid | supabase
ENVIRONMENT=development
USE_MOCK=false            # set true to force mock AI responses (demo fallback)
```

`APP_MODE` behaviour:

| Value | Behaviour |
|---|---|
| `local` | In-memory storage, no Supabase required |
| `hybrid` | Supabase with local token fallback |
| `supabase` | Strict Supabase — surfaces provider errors on auth failure |

### Frontend — `frontend/.env.local`

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=   # anon public key — safe to expose
```

---

## Database Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the schema below
3. Go to **Authentication → Providers → Email** and disable *Confirm email* for faster testing

<details>
<summary>Full SQL schema (click to expand)</summary>

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  username TEXT UNIQUE NOT NULL CHECK (char_length(username) BETWEEN 3 AND 32),
  bio TEXT,
  karma INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE revival_phase AS ENUM ('spark', 'pull', 'handoff', 'complete');

CREATE TABLE communities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  rules JSONB DEFAULT '[]',
  icon_seed TEXT,
  banner_color TEXT DEFAULT '#FF4500',
  member_count INT DEFAULT 0,
  revival_phase revival_phase DEFAULT 'spark',
  human_activity_ratio FLOAT DEFAULT 0.0,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE community_members (
  user_id UUID REFERENCES users(id),
  community_id UUID REFERENCES communities(id),
  role TEXT DEFAULT 'member',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, community_id)
);

CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  author_id UUID REFERENCES users(id),
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  title TEXT NOT NULL,
  body TEXT,
  flair TEXT,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  has_factcheck BOOLEAN DEFAULT FALSE,
  factcheck_result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  author_id UUID REFERENCES users(id),
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  body TEXT NOT NULL,
  parent_comment_id UUID REFERENCES comments(id),
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE votes (
  user_id UUID REFERENCES users(id),
  community_id UUID REFERENCES communities(id),
  post_id UUID REFERENCES posts(id),
  comment_id UUID REFERENCES comments(id),
  value INT CHECK (value IN (-1, 1))
);

-- Row Level Security
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Members read posts" ON posts FOR SELECT USING (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members create posts" ON posts FOR INSERT WITH CHECK (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members read comments" ON comments FOR SELECT USING (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
```

</details>

---

## Project Structure

```
cultify/
├── backend/
│   ├── main.py                    # FastAPI app — register only active routers
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/
│   │   ├── auth.py
│   │   ├── communities.py
│   │   ├── posts.py
│   │   ├── comments.py
│   │   ├── faq.py                 # ✅ active
│   │   ├── factcheck.py           # ✅ active
│   │   ├── sentiment.py           # ✅ active
│   │   ├── agents.py              # 🔲 revival arc
│   │   ├── revival.py             # 🔲 revival arc
│   │   ├── feed.py                # 🔲 revival arc SSE
│   │   ├── events.py              # 🔲 event suggester
│   │   └── digest.py              # 🔲 weekly digest
│   ├── services/
│   │   ├── gemini_service.py      # all Gemini calls — single entry point
│   │   ├── faq_service.py         # ✅
│   │   ├── factcheck_service.py   # ✅
│   │   ├── sentiment_service.py   # ✅
│   │   ├── agent_service.py       # 🔲
│   │   └── revival_service.py     # 🔲
│   ├── models/
│   ├── prompts/
│   │   ├── faq_answer.txt
│   │   ├── factcheck_analyze.txt
│   │   └── sentiment_report.txt
│   └── db/
│       ├── supabase_client.py
│       └── queries.py
├── frontend/
│   └── src/
│       ├── context/
│       ├── hooks/
│       ├── pages/
│       └── components/
├── run-backend.sh
├── .github/
│   └── copilot-instructions.md
└── README.md
```

---

## API Reference

| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/auth/signup` | Register user | Core |
| POST | `/auth/login` | Login | Core |
| POST | `/communities` | Create community | Core |
| GET | `/communities/:slug` | Get community | Core |
| POST | `/communities/:slug/join` | Join community | Core |
| GET | `/communities/:slug/posts` | List posts | Core |
| POST | `/communities/:slug/posts` | Create post | Core |
| POST | `/posts/:id/vote` | Vote on post | Core |
| GET | `/posts/:id/comments` | Get comment tree | Core |
| POST | `/posts/:id/comments` | Add comment | Core |
| GET | `/communities/:slug/faq/ask?q=` | Ask FAQ | ✅ AI |
| POST | `/posts/:id/factcheck` | Fact-check post | ✅ AI |
| GET | `/communities/:slug/sentiment` | Sentiment report | ✅ AI |

Full request/response contracts: [`docs/API.md`](docs/API.md)

---

## Known Issues

| Symptom | Cause | Fix |
|---|---|---|
| `422` on signup | Pydantic validation — username must be 3–32 chars, password ≥8, valid email | Validate on frontend before submit |
| `[object Object]` in error UI | FastAPI 422 `detail` is an array | `detail.map(e => e.msg).join(', ')` |
| Intermittent `401` | Stale localStorage token | Clear token/user on any 401, redirect to `/login` |
| `KeyError` in prompt | Literal `{}` in `.format()` string | Escape as `{{` and `}}` |
| `Address already in use` | Port 8000 occupied | `PORT=8001 ./run-backend.sh` |

---

## Pivot Guide

All six AI features are fully designed. To swap features mid-build:

**Deactivate a feature:**
```python
# backend/main.py
# app.include_router(faq.router)  ← comment out
```
Leave the service file in place.

**Activate a designed feature:**
```python
# backend/main.py
app.include_router(agents.router)  # uncomment or add
```
Ensure the service file, prompt file, and any required DB columns exist first.

**Estimated additional build time per swap:**

| Swap In | Extra Time |
|---|---|
| Revival Arc Agents | ~2 hours |
| Weekly Digest | ~1.5 hours |
| Event Suggester | ~1 hour |

**Force mock AI responses** (demo safety net):
```env
USE_MOCK=true
```

---

## Docs

| Document | Description |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | Product requirements, feature scope, success criteria |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System diagram, DB schema, service architecture |
| [`docs/API.md`](docs/API.md) | Full API contracts with request/response examples |
| [`docs/COMPONENTS.md`](docs/COMPONENTS.md) | React component specs and hook reference |
| [`docs/USER_FLOW.md`](docs/USER_FLOW.md) | Screen flows for member, organizer, and demo operator |
| [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) | Step-by-step demo script with recovery playbook |
| [`docs/HOSTING_AND_INFRA.md`](docs/HOSTING_AND_INFRA.md) | Railway, Supabase, Vercel setup guides |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot context — conventions, known issues, feature status |

---

## Contributing

This project was built during a single-day hackathon. If you want to extend it:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/weekly-digest`
3. Follow the conventions in `.github/copilot-instructions.md`
4. Every new AI feature needs: a router, a service, a prompt file, and a mock fallback
5. Open a PR

---

*"Make communities impossible to abandon."*

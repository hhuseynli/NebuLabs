# Cultify

**Make tech communities impossible to abandon.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres-dark)](https://supabase.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.0-orange)](https://aistudio.google.com)

Cultify is a Reddit-style community platform for tech communities — Google Developer Groups, Stack Overflow communities, local dev meetups. It combines standard community mechanics with an AI layer that handles the work that burns organizers out.

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
- [Known Issues](#known-issues)
- [Docs](#docs)

---

## The Problem

Tech communities are fragile. Most don't survive their first year.

| Failure Mode | What Happens |
|---|---|
| **Engagement Decay** | Initial excitement fades. Members attend once, then disappear. |
| **Silent Members** | 80% lurk. No onboarding, no pathways to contribute. |
| **Fragmented Tooling** | Discord, Meetup, Notion, LinkedIn — all disconnected. Organizers burn out. |
| **No Signal on Health** | Organizers can't tell if the community is growing, stagnating, or dying. |
| **No Funding** | Communities run on volunteer energy alone. When that runs out, they collapse. |

---

## Features

### Community Platform
- Email signup / login (Supabase Auth)
- Create and join communities with rules
- Posts with title, body, flair, upvote/downvote
- Threaded nested comments
- User profiles with karma
- Home feed + community feed (Hot / New / Top)
- Full multi-tenant isolation per community

### AI Features

#### ✅ Community FAQ Tab
Members ask questions in plain language. Gemini searches the community's entire post and comment history and returns an instant answer — with a citation to the source thread. New members get answered in seconds. Organizers stop repeating themselves.

#### ✅ Sentiment Analyser *(organizer only)*
Reads recent community activity and produces a health report: overall score (0–100), trending topics, friction signals, and members at churn risk. Cached for 5 minutes, refreshable on demand. Gives organizers the signal they've never had.

#### ✅ Fundraiser Agent
Scans community discussions every 10 minutes. When it detects an expressed need for funding or resources (venue, equipment, swag, speaker travel), it autonomously creates a fundraising post with a goal amount, deadline, and pledge tracker. Members pledge support. Organizer effort required: zero.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TailwindCSS + React Router v6 |
| Backend | Python 3.11 + FastAPI |
| Database | Supabase (Postgres + Auth + RLS) |
| AI | Google Gemini API (`gemini-2.0-flash`) |
| Scheduling | APScheduler (fundraiser agent loop) |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) account
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
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in keys
./run-backend.sh                # from workspace root
```

Port conflict:
```bash
PORT=8001 ./run-backend.sh
lsof -nP -iTCP:8000 -sTCP:LISTEN   # find what's using the port
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                         # http://localhost:5173
```

---

## Environment Variables

### Backend — `backend/.env`
```env
GEMINI_API_KEY=           # aistudio.google.com → Get API Key
SUPABASE_URL=             # Supabase project settings → Project URL
SUPABASE_SERVICE_KEY=     # service_role key — never expose to frontend
APP_MODE=local            # local | hybrid | supabase
ENVIRONMENT=development
USE_MOCK=false            # true = force mock AI responses (demo fallback)
```

### Frontend — `frontend/.env.local`
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=   # anon public key
```

---

## Database Setup

1. Create project at [supabase.com](https://supabase.com)
2. SQL Editor → run schema below
3. Authentication → Providers → Email → disable *Confirm email*

<details>
<summary>Full SQL schema</summary>

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
  sentiment_cache JSONB,
  sentiment_updated_at TIMESTAMPTZ,
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
  agent_type TEXT,
  title TEXT NOT NULL,
  body TEXT,
  flair TEXT,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  fundraiser_meta JSONB,
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

CREATE TABLE pledges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  amount_suggested INT,
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (post_id, user_id)
);

CREATE TABLE agent_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  action TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE pledges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Members read posts" ON posts FOR SELECT USING (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members create posts" ON posts FOR INSERT WITH CHECK (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members read comments" ON comments FOR SELECT USING (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members read pledges" ON pledges FOR SELECT USING (
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
CREATE POLICY "Members create pledges" ON pledges FOR INSERT WITH CHECK (
  auth.uid() IS NOT NULL AND
  community_id IN (SELECT community_id FROM community_members WHERE user_id = auth.uid())
);
```

</details>

---

## Project Structure

```
cultify/
├── backend/
│   ├── main.py
│   ├── scheduler.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth.py  communities.py  posts.py  comments.py
│   │   ├── faq.py          ✅
│   │   ├── sentiment.py    ✅
│   │   └── fundraiser.py   ✅
│   ├── services/
│   │   ├── gemini_service.py
│   │   ├── faq_service.py       ✅
│   │   ├── sentiment_service.py ✅
│   │   └── fundraiser_service.py ✅
│   ├── prompts/
│   │   ├── faq_answer.txt
│   │   ├── sentiment_report.txt
│   │   ├── fundraiser_detect.txt
│   │   └── fundraiser_post.txt
│   └── db/
│       ├── supabase_client.py
│       └── queries.py
├── frontend/src/
│   ├── context/   hooks/   pages/
│   └── components/
│       ├── tabs/        FAQTab.jsx  SentimentDashboard.jsx
│       └── posts/       PostCard.jsx  FundraiserPost.jsx
├── run-backend.sh
├── .github/copilot-instructions.md
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register |
| POST | `/auth/login` | Login |
| POST | `/communities` | Create community |
| GET | `/communities/:slug` | Get community |
| POST | `/communities/:slug/join` | Join |
| GET | `/communities/:slug/posts` | List posts |
| POST | `/communities/:slug/posts` | Create post |
| POST | `/posts/:id/vote` | Vote |
| GET | `/posts/:id/comments` | Comment tree |
| POST | `/posts/:id/comments` | Add comment |
| GET | `/communities/:slug/faq/ask?q=` | **FAQ** ✅ |
| GET | `/communities/:slug/sentiment` | **Sentiment** ✅ |
| POST | `/communities/:slug/fundraiser/scan` | **Trigger fundraiser** ✅ |
| GET | `/posts/:id/pledges` | Get pledges ✅ |
| POST | `/posts/:id/pledge` | Pledge ✅ |
| DELETE | `/posts/:id/pledge` | Retract pledge ✅ |

Full contracts with request/response examples: [`docs/API.md`](docs/API.md)

---

## Known Issues

| Symptom | Cause | Fix |
|---|---|---|
| `422` on signup | Username 3–32 chars, password ≥8, valid email | Validate frontend before submit |
| `[object Object]` error | FastAPI 422 `detail` is array | `detail.map(e => e.msg).join(', ')` |
| `401` intermittent | Stale localStorage token | Clear on every 401, redirect `/login` |
| `KeyError` in prompt | Literal `{}` in `.format()` | Escape as `{{` and `}}` |
| Port 8000 occupied | Another process listening | `PORT=8001 ./run-backend.sh` |
| Fundraiser fires repeatedly | Missing 48h cooldown check | `get_recent_fundraiser_post()` must be called first in `scan_and_create()` |

---

## Docs

| File | Contents |
|---|---|
| [`docs/API.md`](docs/API.md) | Full API contracts |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System diagram, DB schema, fundraiser flow |
| [`docs/COMPONENTS.md`](docs/COMPONENTS.md) | React component specs, hooks |
| [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) | Step-by-step demo + recovery playbook |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Copilot context — full feature implementation guide |

---

*"Make communities impossible to abandon."*

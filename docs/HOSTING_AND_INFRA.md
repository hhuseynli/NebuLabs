# Hosting & Infrastructure — Kindling

## Overview

| Layer | Platform | Why |
|-------|----------|-----|
| Frontend | Vercel | Zero-config React deploys, instant CDN, free tier |
| Backend | Railway | Best DX for FastAPI, git-push deploys, no sleep on paid, SSE support |
| Database + Auth | Supabase | Managed Postgres + JWT auth + RLS in one free tier |
| AI | Google Gemini API | Fast, capable, generous free tier |
| Open Data | opendata.az | No auth required, CKAN API, free |

---

## Why Railway for the Backend

Railway is the best choice for a FastAPI backend at hackathon scale:
- Git-push deploys in under 2 minutes
- Stays alive — no cold starts on the Hobby plan ($5/month, includes $5 credit)
- SSE (Server-Sent Events) works natively — no WebSocket workarounds needed
- APScheduler runs in-process without extra configuration
- Environment variables managed via dashboard
- Logs are easy to find and tail in real time

**Alternative considered: Render** — also good, but free tier spins down after inactivity (50-second cold starts), which would break the live demo. Railway stays awake.

---

## Railway Setup (Step by Step)

### 1. Create account and project
```
1. Go to railway.app → Sign up with GitHub
2. New Project → Deploy from GitHub repo
3. Select your repo → Railway auto-detects Python
```

### 2. Add environment variables
In Railway dashboard → your service → Variables tab:
```
GEMINI_API_KEY=your_key_here
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
ENVIRONMENT=production
```

### 3. Add a `Procfile` to your repo root
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Add `requirements.txt`
```
fastapi
uvicorn[standard]
supabase
google-generativeai
httpx
apscheduler
python-dotenv
pydantic
```

### 5. Deploy
```bash
git add .
git commit -m "initial deploy"
git push origin main
# Railway auto-deploys on push
```

### 6. Get your public URL
Railway dashboard → your service → Settings → Domain
Copy the auto-generated URL (e.g. `kindling-backend.railway.app`)
Set this as `VITE_API_URL` in your Vercel frontend environment variables.

### 7. Enable CORS in FastAPI
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Supabase Setup (Step by Step)

### 1. Create project
```
1. Go to supabase.com → New project
2. Choose a name: "kindling"
3. Set a strong database password (save it)
4. Region: closest to Railway's region (default: US East)
5. Wait ~2 minutes for provisioning
```

### 2. Get credentials
Go to Project Settings → API:
- `Project URL` → this is your `SUPABASE_URL`
- `anon public` key → used in frontend (`VITE_SUPABASE_ANON_KEY`)
- `service_role` key → used in backend (`SUPABASE_SERVICE_KEY`) — never expose this to frontend

### 3. Create tables
Go to SQL Editor → New query. Run this schema:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (extends Supabase Auth)
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  username TEXT UNIQUE NOT NULL,
  bio TEXT,
  karma INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Communities
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

-- Community members
CREATE TABLE community_members (
  user_id UUID REFERENCES users(id),
  community_id UUID REFERENCES communities(id),
  role TEXT DEFAULT 'member',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, community_id)
);

-- Agents
CREATE TYPE agent_status AS ENUM ('active', 'retiring', 'retired');
CREATE TYPE activity_level AS ENUM ('high', 'medium', 'low');

CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  avatar_seed TEXT,
  backstory TEXT,
  personality_traits TEXT[],
  opinion_set JSONB DEFAULT '{}',
  expertise_areas TEXT[],
  activity_level activity_level DEFAULT 'medium',
  status agent_status DEFAULT 'active',
  post_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  author_id UUID REFERENCES users(id),
  agent_id UUID REFERENCES agents(id),
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  title TEXT NOT NULL,
  body TEXT,
  flair TEXT,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  has_factcheck BOOLEAN DEFAULT FALSE,
  opendata_citation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  author_id UUID REFERENCES users(id),
  agent_id UUID REFERENCES agents(id),
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  body TEXT NOT NULL,
  parent_comment_id UUID REFERENCES comments(id),
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  is_factcheck BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Votes
CREATE TABLE votes (
  user_id UUID REFERENCES users(id),
  community_id UUID REFERENCES communities(id),
  post_id UUID REFERENCES posts(id),
  comment_id UUID REFERENCES comments(id),
  value INT CHECK (value IN (-1, 1)),
  PRIMARY KEY (user_id, COALESCE(post_id, uuid_nil()), COALESCE(comment_id, uuid_nil()))
);

-- Agent logs
CREATE TABLE agent_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id),
  action TEXT NOT NULL,
  phase revival_phase,
  target_post_id UUID,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Enable Row Level Security (RLS)

```sql
-- Enable RLS on all tables
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;

-- Posts: readable by community members
CREATE POLICY "Read posts as member"
ON posts FOR SELECT
USING (
  community_id IN (
    SELECT community_id FROM community_members WHERE user_id = auth.uid()
  )
);

-- Posts: writable by authenticated users who are members
CREATE POLICY "Create posts as member"
ON posts FOR INSERT
WITH CHECK (
  auth.uid() IS NOT NULL AND
  community_id IN (
    SELECT community_id FROM community_members WHERE user_id = auth.uid()
  )
);

-- Comments: same pattern as posts
CREATE POLICY "Read comments as member"
ON comments FOR SELECT
USING (
  community_id IN (
    SELECT community_id FROM community_members WHERE user_id = auth.uid()
  )
);

-- Agents: readable by community members
CREATE POLICY "Read agents as member"
ON agents FOR SELECT
USING (
  community_id IN (
    SELECT community_id FROM community_members WHERE user_id = auth.uid()
  )
);

-- NOTE: Backend uses service_role key which bypasses RLS
-- RLS only applies to frontend/anon requests
```

### 5. Set up Supabase Auth
```
Supabase Dashboard → Authentication → Providers
→ Email: Enable (default)
→ Disable email confirmation for hackathon speed:
  Authentication → Email Templates → toggle off "Confirm email"
```

### 6. Install Supabase client in backend
```bash
pip install supabase
```

```python
# db/supabase_client.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # service role — bypasses RLS for agent writes
)
```

### 7. Install Supabase client in frontend
```bash
npm install @supabase/supabase-js
```

```javascript
// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY  // anon key — subject to RLS
)
```

---

## Gemini API Setup

```
1. Go to aistudio.google.com
2. Get API Key → Create API key
3. Add to Railway env vars: GEMINI_API_KEY=your_key
```

```bash
pip install google-generativeai
```

```python
# services/gemini_service.py
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def generate(prompt: str, use_pro: bool = False) -> str:
    model_name = "gemini-2.0-pro" if use_pro else "gemini-2.0-flash"
    model = genai.GenerativeModel(model_name)
    response = await model.generate_content_async(prompt)
    return response.text
```

Gemini free tier: 1,500 requests/day on Flash, 50/day on Pro. More than enough for a hackathon.

---

## Vercel Frontend Setup

```
1. Push frontend to GitHub
2. Go to vercel.com → New Project → Import repo
3. Framework preset: Vite
4. Root directory: frontend/
5. Environment variables:
   VITE_API_URL=https://your-backend.railway.app
   VITE_SUPABASE_URL=https://xxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key
6. Deploy
```

---

## Local Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in keys
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.example .env.local  # fill in keys
npm run dev                  # runs on localhost:5173
```

`.env.example` (backend):
```
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
ENVIRONMENT=development
```

`.env.local` (frontend):
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

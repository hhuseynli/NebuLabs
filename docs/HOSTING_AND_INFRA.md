# Hosting & Infrastructure — Cultify

**Status**: Optional. This is for production deployment. For local development, see [README.md](../README.md).

---

## Stack Summary

| Layer | Platform | Why |
|-------|----------|-----|
| Frontend | Vercel | Zero-config Vite deploys, CDN, free tier |
| Backend | Railway | No sleep on Hobby plan, git-push deploys, native Python support |
| Database + Auth | Supabase | Postgres + JWT auth + RLS, free tier |
| AI | Groq API | Fast inference, generous free tier, no rate-limit surprises |

**Why Railway over Render**: Render's free tier spins down after inactivity — 50s cold start. Railway Hobby ($5/month, includes $5 credit) stays alive.

---

## Railway — Backend Setup

```bash
# 1. Go to railway.app → sign up with GitHub
# 2. New Project → Deploy from GitHub repo → select your repo
# 3. Railway auto-detects Python

# Add Procfile at repo root:
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

**Environment variables** (Railway dashboard → service → Variables):
```
GROQ_API_KEY=                          # from console.groq.com
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
APP_MODE=supabase
ENVIRONMENT=production
USE_MOCK=false
```

**CORS** — add to `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

After deploy: Railway dashboard → Settings → Domain → copy URL → set as `VITE_API_URL` in Vercel.

---

## Supabase — Database Setup

```
1. supabase.com → New project → name: "cultify"
2. Set DB password (save it)
3. Region: us-east-1 (matches Railway default)
4. Wait ~2 minutes
```

**Get credentials** → Project Settings → API:
- `Project URL` → `SUPABASE_URL`
- `anon public` key → `VITE_SUPABASE_ANON_KEY` (frontend)
- `service_role` key → `SUPABASE_SERVICE_KEY` (backend only — never expose)

**Run schema** → SQL Editor → paste full schema from `docs/ARCHITECTURE.md` → Run.

**Disable email confirmation** (speeds up hackathon testing):
```
Supabase → Authentication → Providers → Email → toggle off "Confirm email"
```

**Backend client** (uses service role — bypasses RLS for AI writes):
```bash
pip install supabase
```
```python
# db/supabase_client.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)
```

**Frontend client** (uses anon key — subject to RLS):
```bash
npm install @supabase/supabase-js
```
```javascript
// src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
```

---

## Groq API Setup

```
1. console.groq.com → Sign up (free) → Create API key
2. Add to Railway env vars: GROQ_API_KEY=your_key
```

```bash
pip install groq
```

Free tier: Excellent for development. Groq's free tier supports generous request rates without typical enterprise rate-limiting surprises. Model: `llama-3.3-70b-versatile` (active), `mixtral-8x7b` (alternative).

---

## Vercel — Frontend Setup

```
1. vercel.com → New Project → Import GitHub repo
2. Framework preset: Vite
3. Root directory: frontend/
4. Environment variables:
   VITE_API_URL=https://your-backend.railway.app
   VITE_SUPABASE_URL=https://xxxx.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key
5. Deploy
```

---

## Local Development

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in keys
./run-backend.sh                # from workspace root (includes port preflight)
```

`run-backend.sh`:
```bash
#!/bin/bash
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

# Port preflight
if lsof -nP -iTCP:$PORT -sTCP:LISTEN &>/dev/null; then
  echo "ERROR: Port $PORT already in use."
  echo "Run: PORT=8001 ./run-backend.sh"
  exit 1
fi

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

cd backend
uvicorn main:app --host $HOST --port $PORT --reload
```

```bash
# Frontend
cd frontend
npm install
cp .env.example .env.local      # fill in keys
npm run dev                     # localhost:5173
```

**`.env.example` (backend)**:
```
GROQ_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
APP_MODE=supabase
ENVIRONMENT=production
USE_MOCK=false
```

**`.env.example` (frontend)**:
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

---

## `requirements.txt`
```
fastapi
uvicorn[standard]
supabase
google-generativeai
httpx
apscheduler
python-dotenv
pydantic>=2.0
```

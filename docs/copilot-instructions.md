# Copilot Instructions — Cultify

## What This Is
Cultify is a Reddit-style community platform for tech communities (GDGs, Stack Overflow groups, dev meetups). Standard Reddit mechanics + three AI features:

1. **FAQ Tab** — answers member questions from community content
2. **Sentiment Analyser** — organizer-only health dashboard
3. **Fundraiser Agent** — autonomously detects funding needs and creates fundraising posts

## Stack
- **Frontend**: React (Vite) + TailwindCSS + React Router v6 → Vercel
- **Backend**: Python 3.11 + FastAPI → Railway
- **Database**: Supabase (Postgres + Auth + RLS)
- **AI**: Google Gemini API (`gemini-2.0-flash` default, `gemini-2.0-pro` for agent generation)
- **Scheduling**: APScheduler in-process (fundraiser agent loop)

---

## Runtime Modes
```
APP_MODE=local      # in-memory, no Supabase
APP_MODE=hybrid     # Supabase + local token fallback
APP_MODE=supabase   # strict, surfaces provider errors on auth failure
USE_MOCK=false      # set true to force mock AI responses globally
```

---

## Multi-Tenancy Rule
**Every DB query must filter by `community_id`.** No exceptions. Supabase RLS enforces this at DB level. Backend uses service role key (bypasses RLS for agent writes). Frontend uses anon key (subject to RLS).

---

## Known Issues (fix before they happen)
- `422` on signup → Pydantic: username 3–32 chars, password ≥8, valid email
- `[object Object]` in UI → FastAPI 422 `detail` is array → `detail.map(e => e.msg).join(', ')`
- Intermittent `401` → stale localStorage token → clear on every 401, redirect to `/login`
- `KeyError` in prompt → literal `{}` in `.format()` → escape as `{{` and `}}`
- Port conflict → `PORT=8001 ./run-backend.sh` → find process: `lsof -nP -iTCP:8000 -sTCP:LISTEN`

---

## Feature 1: FAQ Tab

**Endpoint**: `GET /communities/:slug/faq/ask?q=<question>`

**Service**: `services/faq_service.py`
```python
async def answer_question(community_slug: str, question: str) -> dict:
    # 1. Fetch last 200 posts + comments for community (queries.py)
    # 2. Build context string: "POST: {title}\n{body}\n\nCOMMENT: {body}\n..."
    # 3. Load prompt from prompts/faq_answer.txt
    # 4. Call gemini_service.generate(prompt.format(context=context, question=question))
    # 5. Parse JSON response: { answer, source_post_id, source_excerpt, confidence }
    # 6. If confidence < 0.4: return low-confidence fallback message
    # 7. Return result
```

**Prompt** (`prompts/faq_answer.txt`):
```
You are a helpful assistant for a tech community. Answer the question using ONLY the content provided below. Do not invent information. If you cannot find a confident answer, say so.

Community content:
{context}

Question: {question}

Respond ONLY with valid JSON (no markdown, no backticks):
{{"answer": "...", "source_excerpt": "...", "confidence": 0.0}}

confidence is a float 0.0-1.0. Set below 0.4 if you cannot find a good answer.
```

**Frontend**: `components/tabs/FAQTab.jsx`
- Search-style input + Ask button
- Loading state: "Searching community knowledge..."
- High confidence (≥0.7): show answer + green confidence bar + source link
- Low confidence (<0.4): "Couldn't find a confident answer — try asking in the community"
- Session history: last 5 Q&As stored in component state

---

## Feature 2: Sentiment Analyser

**Endpoint**: `GET /communities/:slug/sentiment`  
**Auth**: Returns `403` if caller is not `community.created_by`

**Service**: `services/sentiment_service.py`
```python
async def generate_report(community_slug: str) -> dict:
    # 1. Fetch last 100 posts + comments (queries.py, filter by community_id)
    # 2. Build flat text: "POST [{upvotes}↑]: {title} — {body}\nCOMMENT: {body}\n..."
    # 3. Load prompt from prompts/sentiment_report.txt
    # 4. Call gemini_service.generate(prompt.format(content=content), use_pro=False)
    # 5. Parse JSON response
    # 6. Return result + cache in community row (sentiment_cache column, updated_at)
```

**Prompt** (`prompts/sentiment_report.txt`):
```
You are analysing the health of a tech community. Read the posts and comments below and produce a health report.

Content:
{content}

Respond ONLY with valid JSON (no markdown, no backticks):
{{
  "score": 0,
  "label": "healthy",
  "summary": "...",
  "trending_topics": [],
  "friction_signals": [],
  "churn_risk_members": []
}}

score: integer 0-100. label: "healthy" if >=70, "neutral" if 40-69, "at risk" if <40.
friction_signals: list of plain-language observations about problems.
churn_risk_members: list of usernames who posted once or rarely and show disengagement signals.
```

**DB addition**: Add to `communities` table:
```sql
ALTER TABLE communities ADD COLUMN sentiment_cache JSONB;
ALTER TABLE communities ADD COLUMN sentiment_updated_at TIMESTAMPTZ;
```

**Frontend**: `components/tabs/SentimentDashboard.jsx` — organizer only, rendered in Dashboard page
- Large score number + label badge (green/yellow/red)
- Summary paragraph
- Trending topics as chips
- Friction signals as warning list (⚠ icon)
- Churn risk members as clickable username list
- [Refresh Report] button — disabled for 5 min after last run (show countdown)

---

## Feature 3: Fundraiser Agent

**This is the main event. Read carefully.**

The fundraiser agent runs on APScheduler every 10 minutes per community. It scans recent posts and comments for expressions of unmet needs that require funding or resources. When it detects one with sufficient confidence, it autonomously creates a fundraising post in the community feed with a goal, a reason, and a pledge tracker.

### How Detection Works
The agent reads the last 50 posts + comments and asks Gemini: "Does this community have an expressed need that could be addressed with funding or resources?" Examples it should catch:
- "We really need a venue for our next meetup"
- "Would be amazing to have swag/stickers for members"
- "We need a projector/equipment for the event"
- "Wish we could afford a speaker from abroad"

It should NOT fire on: general complaints, technical problems, feature requests unrelated to funding.

### Fundraiser Post Format
When the agent fires, it inserts a post with:
- `is_human: false`, `agent_type: "fundraiser"`
- `flair: "🎯 Community Goal"`
- Title: `"Community Goal: [goal name]"`
- Body: structured fundraiser content (see prompt)
- `fundraiser_meta` JSONB column: `{ goal_amount, currency, pledges: [], deadline, status: "active"|"funded"|"closed", trigger_post_id }`

### Pledge Mechanic
Members "pledge" by clicking a [Pledge Support] button on a fundraiser post. This is NOT real money — it's a show-of-interest mechanic. Each pledge stores `{ user_id, amount_suggested, message }` in `fundraiser_meta.pledges`. The post body updates to show current pledge count vs goal.

### DB additions:
```sql
-- Add to posts table
ALTER TABLE posts ADD COLUMN agent_type TEXT; -- "fundraiser" | null
ALTER TABLE posts ADD COLUMN fundraiser_meta JSONB;

-- Pledges table
CREATE TABLE pledges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  amount_suggested INT, -- in AZN, nullable
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Endpoints
```
POST /communities/:slug/fundraiser/scan     # manual trigger (demo use)
GET  /posts/:id/pledges                     # get pledges for fundraiser post
POST /posts/:id/pledge                      # submit a pledge
DELETE /posts/:id/pledge                    # retract pledge
```

### Scheduler Setup (`scheduler.py`)
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.fundraiser_service import scan_and_create

scheduler = AsyncIOScheduler()

def start_fundraiser_scheduler(community_id: str):
    scheduler.add_job(
        scan_and_create,
        'interval',
        minutes=10,
        args=[community_id],
        id=f"fundraiser_{community_id}",
        replace_existing=True
    )

def stop_fundraiser_scheduler(community_id: str):
    scheduler.remove_job(f"fundraiser_{community_id}")
```

Start scheduler in `main.py` `startup` event. Fire per community on creation.

### Service (`services/fundraiser_service.py`)
```python
async def scan_and_create(community_id: str):
    # 1. Check: has a fundraiser post been created in last 48h? If yes, skip.
    # 2. Fetch last 50 posts + comments for community
    # 3. Call gemini_service.detect_funding_need(content) → { detected, need, confidence, trigger_post_id }
    # 4. If confidence < 0.75: skip (avoid false positives)
    # 5. Call gemini_service.generate_fundraiser_post(need, community_name)
    # 6. Insert post with agent_type="fundraiser", fundraiser_meta, flair="🎯 Community Goal"
    # 7. Log to agent_logs
```

### Prompts

**`prompts/fundraiser_detect.txt`**:
```
You are analysing posts and comments in a tech community to detect expressed needs that could be addressed with funding or community resources.

Community content (last 50 posts and comments):
{content}

Does this community have a clear, expressed need for funding or resources? Examples: venue for meetup, equipment, swag, travel costs for speakers, hosting costs.

Respond ONLY with valid JSON (no markdown, no backticks):
{{"detected": false, "need": "", "confidence": 0.0, "trigger_post_id": null}}

Only set detected=true if confidence >= 0.75. Be conservative — false positives are worse than misses.
```

**`prompts/fundraiser_post.txt`**:
```
You are a community manager creating a fundraising post for a tech community called "{community_name}".

The need that was detected: {need}

Write an enthusiastic, honest fundraising post. Include:
- What the goal is
- Why it matters for the community
- A suggested goal amount in AZN (be realistic: venue ~200-500, equipment ~100-300, swag ~50-150)
- How members can help (pledge support below)

Respond ONLY with valid JSON (no markdown, no backticks):
{{"title": "Community Goal: ...", "body": "...", "goal_amount": 0, "deadline_days": 14}}
```

### Frontend: `components/posts/FundraiserPost.jsx`
Renders differently from a normal PostCard when `agent_type === "fundraiser"`:
```
🎯 Community Goal banner (teal/green accent)
Title
Body
Progress bar: [████░░░░░░] X pledges · AZN Y committed
[Pledge Support] button → opens modal: amount (optional) + message
List of recent pledges (username + message, amount optional)
"Posted by Cultify Fundraiser Agent" attribution
```

---

## Gemini Service (full implementation)

**`services/gemini_service.py`**:
```python
import google.generativeai as genai
import os, json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MOCK_RESPONSES = {
    "faq": '{"answer": "To get started, install the SDK and run the quickstart.", "source_excerpt": "I set this up last month...", "confidence": 0.85}',
    "sentiment": '{"score": 72, "label": "healthy", "summary": "Community is active. Some friction around beginner questions.", "trending_topics": ["Flutter", "Firebase"], "friction_signals": ["Beginner questions dismissed"], "churn_risk_members": ["u/silent_dev"]}',
    "fundraiser_detect": '{"detected": true, "need": "venue for monthly meetup", "confidence": 0.88, "trigger_post_id": null}',
    "fundraiser_post": '{"title": "Community Goal: Meetup Venue", "body": "We need a venue for our next meetup...", "goal_amount": 300, "deadline_days": 14}',
}

async def generate(prompt: str, use_pro: bool = False, mock_key: str = None) -> str:
    if os.getenv("USE_MOCK") == "true" and mock_key:
        return MOCK_RESPONSES.get(mock_key, '{"mock": true}')
    model_name = "gemini-2.0-pro" if use_pro else "gemini-2.0-flash"
    model = genai.GenerativeModel(model_name)
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        if mock_key:
            return MOCK_RESPONSES.get(mock_key, '{"error": true}')
        raise e

def parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)
```

---

## Router Registration (`main.py`)

```python
# ACTIVE — register these
app.include_router(auth.router, prefix="/api/v1")
app.include_router(communities.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(faq.router, prefix="/api/v1")           # ✅ FAQ
app.include_router(sentiment.router, prefix="/api/v1")     # ✅ Sentiment
app.include_router(fundraiser.router, prefix="/api/v1")    # ✅ Fundraiser

# DESIGNED — do not register yet
# app.include_router(agents.router, prefix="/api/v1")
# app.include_router(revival.router, prefix="/api/v1")
# app.include_router(events.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    scheduler.start()
    # Start fundraiser scheduler for all existing active communities
    communities = await queries.get_all_active_communities()
    for c in communities:
        start_fundraiser_scheduler(c["id"])
```

---

## File Checklist (what needs to exist)

```
backend/
  main.py                        ← register active routers + startup
  scheduler.py                   ← APScheduler setup
  run-backend.sh                 ← workspace launcher
  requirements.txt               ← include apscheduler
  routers/
    auth.py         communities.py    posts.py    comments.py
    faq.py          ✅               sentiment.py  ✅     fundraiser.py  ✅
  services/
    gemini_service.py              ← parse_json + mock responses + generate()
    faq_service.py                 ✅
    sentiment_service.py           ✅
    fundraiser_service.py          ✅ scan_and_create() + manual trigger
  prompts/
    faq_answer.txt
    sentiment_report.txt
    fundraiser_detect.txt
    fundraiser_post.txt
  db/
    supabase_client.py
    queries.py                     ← get_community_content(), get_all_active_communities()

frontend/src/
  hooks/
    useFAQ.js           useSentiment.js      useFundraiser.js
  pages/
    Community.jsx        ← tabs: Posts | FAQ
    Dashboard.jsx        ← SentimentDashboard (organizer only)
    PostDetail.jsx       ← renders FundraiserPost if agent_type === "fundraiser"
  components/
    tabs/
      FAQTab.jsx
      SentimentDashboard.jsx
    posts/
      PostCard.jsx
      FundraiserPost.jsx          ← pledge UI, progress bar
```

---

## Build Order (5 hours)

```
Hour 1 — Foundation check
  Verify existing Reddit mechanics work: auth, posts, comments, votes
  Add DB columns: sentiment_cache, agent_type, fundraiser_meta
  Create pledges table
  Wire scheduler in main.py startup

Hour 2 — FAQ Tab
  faq_service.py + prompts/faq_answer.txt
  faq.py router
  FAQTab.jsx + useFAQ.js
  Test: ask a question, get answer with citation

Hour 3 — Sentiment Analyser
  sentiment_service.py + prompts/sentiment_report.txt
  sentiment.py router (403 if not creator)
  SentimentDashboard.jsx + useSentiment.js
  Test: generate report, verify score + signals appear

Hour 4 — Fundraiser Agent
  fundraiser_service.py: scan_and_create() + detect logic
  fundraiser.py router: scan endpoint + pledge endpoints
  FundraiserPost.jsx: progress bar + pledge modal
  Test: manual trigger → fundraiser post appears → pledge works

Hour 5 — Polish + Demo prep
  Mock fallbacks working (USE_MOCK=true test)
  Pre-seed demo community with content
  Fundraiser manual trigger tested end-to-end
  README updated, deploy to Railway + Vercel
  Run full demo script once
```

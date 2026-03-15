# Architecture — Cultify

## System Diagram

```
┌────────────────────────────────────────────────┐
│           React Frontend (Vercel)              │
└──────────────────┬─────────────────────────────┘
                   │ REST
┌──────────────────▼─────────────────────────────┐
│         FastAPI Backend (Railway)              │
│                                                │
│  faq_service      sentiment_service            │
│  fundraiser_service    gemini_service          │
│                                                │
│  APScheduler ← fundraiser scan loop           │
│               (every 10 min per community)    │
└──────────┬──────────────────────┬─────────────┘
           │                      │
┌──────────▼──────────┐  ┌────────▼────────────┐
│  Supabase           │  │  Gemini API         │
│  Postgres + Auth    │  │  gemini-2.0-flash   │
│  RLS policies       │  └─────────────────────┘
└─────────────────────┘
```

---

## Backend File Structure

```
backend/
├── main.py
├── scheduler.py
├── run-backend.sh
├── requirements.txt
├── .env.example
├── routers/
│   ├── auth.py
│   ├── communities.py
│   ├── posts.py
│   ├── comments.py
│   ├── faq.py
│   ├── sentiment.py
│   └── fundraiser.py
├── services/
│   ├── gemini_service.py
│   ├── faq_service.py
│   ├── sentiment_service.py
│   └── fundraiser_service.py
├── models/
│   ├── community.py
│   ├── post.py
│   ├── comment.py
│   └── user.py
├── prompts/
│   ├── faq_answer.txt
│   ├── sentiment_report.txt
│   ├── fundraiser_detect.txt
│   └── fundraiser_post.txt
└── db/
    ├── supabase_client.py
    └── queries.py
```

## Frontend File Structure

```
frontend/src/
├── main.jsx
├── App.jsx
├── lib/
│   └── supabase.js
├── context/
│   ├── AuthContext.jsx
│   ├── CommunityContext.jsx
│   └── FeedContext.jsx
├── hooks/
│   ├── useAuth.js
│   ├── usePosts.js
│   ├── useComments.js
│   ├── useFAQ.js
│   ├── useSentiment.js
│   └── useFundraiser.js
├── pages/
│   ├── Landing.jsx
│   ├── Login.jsx
│   ├── Signup.jsx
│   ├── Home.jsx
│   ├── Community.jsx        ← tabs: Posts | FAQ
│   ├── PostDetail.jsx       ← renders FundraiserPost if agent_type=fundraiser
│   ├── Profile.jsx
│   ├── CreateCommunity.jsx
│   └── Dashboard.jsx        ← SentimentDashboard (organizer only)
└── components/
    ├── layout/
    │   ├── Navbar.jsx
    │   └── Sidebar.jsx
    ├── posts/
    │   ├── PostCard.jsx
    │   ├── FundraiserPost.jsx
    │   └── CreatePostForm.jsx
    ├── comments/
    │   ├── CommentThread.jsx
    │   ├── CommentCard.jsx
    │   └── CommentForm.jsx
    ├── voting/
    │   └── VoteButtons.jsx
    ├── tabs/
    │   ├── FAQTab.jsx
    │   └── SentimentDashboard.jsx
    └── community/
        ├── CommunityCard.jsx
        ├── CommunityHeader.jsx
        └── RulesPanel.jsx
```

---

## Database Schema (full — run in Supabase SQL Editor)

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  username TEXT UNIQUE NOT NULL CHECK (char_length(username) BETWEEN 3 AND 32),
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
  sentiment_cache JSONB,
  sentiment_updated_at TIMESTAMPTZ,
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

-- Posts
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  author_id UUID REFERENCES users(id),
  is_human BOOLEAN NOT NULL DEFAULT TRUE,
  agent_type TEXT,                    -- "fundraiser" | null
  title TEXT NOT NULL,
  body TEXT,
  flair TEXT,
  upvotes INT DEFAULT 0,
  downvotes INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  fundraiser_meta JSONB,              -- only for agent_type="fundraiser"
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments
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

-- Votes
CREATE TABLE votes (
  user_id UUID REFERENCES users(id),
  community_id UUID REFERENCES communities(id),
  post_id UUID REFERENCES posts(id),
  comment_id UUID REFERENCES comments(id),
  value INT CHECK (value IN (-1, 1))
);

-- Pledges (fundraiser)
CREATE TABLE pledges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  amount_suggested INT,
  message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (post_id, user_id)           -- one pledge per user per fundraiser
);

-- Agent logs
CREATE TABLE agent_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  community_id UUID REFERENCES communities(id) ON DELETE CASCADE,
  action TEXT NOT NULL,               -- "faq_answered" | "sentiment_run" | "fundraiser_created" | "fundraiser_skipped"
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
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

---

## Fundraiser Agent — Detailed Flow

```
APScheduler → scan_and_create(community_id) every 10 min
  │
  ├─ Check: fundraiser post created in last 48h? → skip if yes
  │
  ├─ Fetch last 50 posts + comments for community
  │
  ├─ gemini_service.generate(fundraiser_detect prompt, mock_key="fundraiser_detect")
  │   → parse JSON: { detected, need, confidence, trigger_post_id }
  │
  ├─ confidence < 0.75? → log "skipped", return
  │
  ├─ gemini_service.generate(fundraiser_post prompt, mock_key="fundraiser_post")
  │   → parse JSON: { title, body, goal_amount, deadline_days }
  │
  ├─ Insert post:
  │     community_id = community_id
  │     author_id = null (agent post)
  │     is_human = false
  │     agent_type = "fundraiser"
  │     flair = "🎯 Community Goal"
  │     title = generated title
  │     body = generated body
  │     fundraiser_meta = {
  │       goal_amount: goal_amount,
  │       currency: "AZN",
  │       deadline: now + deadline_days,
  │       status: "active",
  │       trigger_post_id: trigger_post_id,
  │       pledge_count: 0,
  │       total_pledged: 0
  │     }
  │
  └─ Log to agent_logs: action="fundraiser_created", metadata={need, confidence, post_id}
```

---

## Key `queries.py` Functions Needed

```python
# Community content for AI
async def get_community_content(community_id: str, limit: int = 200) -> str:
    # Fetch posts + comments, format as flat text for prompt injection
    # Format: "POST [{upvotes}↑]: {title}\n{body}\n\nCOMMENT: {body}\n..."

# Fundraiser checks
async def get_recent_fundraiser_post(community_id: str, hours: int = 48) -> dict | None:
    # Return most recent fundraiser post if within hours window, else None

# Scheduler startup
async def get_all_active_communities() -> list[dict]:
    # Return all communities (id, slug) — used to restart scheduler on app startup

# Pledge aggregation
async def get_pledge_summary(post_id: str) -> dict:
    # Return { pledge_count, total_pledged, pledges[] }

# Sentiment cache
async def get_cached_sentiment(community_id: str, max_age_minutes: int = 5) -> dict | None:
    # Return cached sentiment if within max_age window, else None

async def cache_sentiment(community_id: str, report: dict):
    # UPDATE communities SET sentiment_cache=report, sentiment_updated_at=now()
```

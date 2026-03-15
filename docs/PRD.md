# Product Requirements Document — Cultify
**Version**: 4.0 | Hackathon MVP | Build with AI Hackathon, Baku 2026

---

## Problem Statement

Tech communities are fragile. Most don't survive their first year — not because people stop caring, but because the infrastructure to sustain them doesn't exist.

The four failure modes (per hackathon organizers):

| Failure Mode | Root Cause |
|-------------|-----------|
| **Engagement Decay** | Initial excitement fades; no mechanism to re-engage members who go quiet |
| **Silent Members** | 80% of members lurk; no onboarding or pathways to contribute |
| **Fragmented Tooling** | Discord, Meetup, Notion, LinkedIn all disconnected; organizers burn out managing chaos |
| **No Signal on Health** | Organizers have no data to know if community is growing, stagnating, or dying |

These communities — Google Developer Groups, Stack Overflow communities, local dev meetups — run on volunteer energy. When the one or two people holding it together burn out, the community collapses and takes its accumulated knowledge with it.

---

## Solution

Cultify is a Reddit-style platform with an AI layer purpose-built for tech communities. It consolidates community activity into one place and uses AI to handle the repetitive work that burns organizers out — answering FAQs, checking factual accuracy of posts, surfacing health signals — so organizers can focus on what only humans can do: building relationships and driving momentum.

---

## Target Users

**Primary — Community Organizer**: Manages a GDG, Stack Overflow tag community, or local dev meetup. Spends hours a week answering the same questions, moderating, and wondering if their effort is working. Has no funding, no dedicated tooling, no health data.

**Secondary — Community Member**: Developer who joined a community but lurks. Hasn't found a low-friction way to contribute. Gets no value out of passive membership and eventually stops showing up.

---

## Feature Scope

### Reddit Core (Foundation)
- [ ] Email signup / login via Supabase Auth
- [ ] Create and join communities (multi-tenant, fully isolated)
- [ ] Posts: title, body, flair, upvote/downvote
- [ ] Threaded comments with nested replies
- [ ] User profiles: karma, post history, comment history
- [ ] Community rules sidebar
- [ ] Home feed: aggregated from joined communities
- [ ] Community feed: Hot / New / Top sorting
- [ ] Post detail with full comment thread
- [ ] Join / leave community

### AI Feature Suite

> **Hackathon build: three active features.** All six are fully designed and activatable — see Pivot Guide in README.

#### ✅ Community FAQ Tab — ACTIVE
**What it solves**: Silent Members, Organizer Burnout

Every community gets a live FAQ tab. Members type a question; Gemini searches the entire community's post and comment history and returns an instant answer with a citation to the original thread. New members get answered in seconds without the organizer lifting a finger. The same question gets answered perfectly every time, forever.

**Behaviour**:
- Fetches last 200 posts + comments for the community
- Passes full context + question to Gemini with strict instruction: only synthesise from provided content, never invent
- Returns: `{ answer, source_post_id, source_excerpt, confidence }`
- Low confidence → returns "I couldn't find a confident answer — try asking in the community"
- Endpoint: `GET /communities/:slug/faq/ask?q=...`

#### ✅ Per-Post Fact Checker — ACTIVE
**What it solves**: Technical misinformation, trust erosion in dev communities

Every post has an inline AI analysis panel. When a member opens it, Gemini reads the post, identifies verifiable technical claims, and returns a structured verdict per claim. Bad advice about security vulnerabilities, deprecated APIs, or wrong configuration gets flagged before it misleads junior developers.

**Behaviour**:
- Lazy evaluation — runs on demand when panel is opened, not on post creation
- Gemini identifies each distinct claim and verdicts it independently
- Verdict shape: `{ claim: string, verdict: "supported"|"unverified"|"contradicted", explanation: string, confidence: float }`
- Multiple claims per post supported
- Endpoint: `POST /posts/:id/factcheck`

#### ✅ Sentiment Dashboard — ACTIVE (organizer only)
**What it solves**: No Signal on Health

The organizer dashboard shows a live community health report generated from recent posts and comments. Gives organizers the signal they've never had: is the community healthy or dying?

**Behaviour**:
- Reads last 100 posts + comments
- Returns: `{ score: 0–100, label: "healthy"|"neutral"|"at risk", trending_topics: string[], friction_signals: string[], churn_risk_members: string[] }`
- Accessible only to community creator (enforced in route handler)
- Endpoint: `GET /communities/:slug/sentiment`

#### 🔲 Revival Arc Agents — DESIGNED
**What it solves**: Cold start, Engagement Decay

AI agents populate new communities during the cold start phase with authentic content. Full state machine: Spark (agents post threads) → Pull (agents reply to humans) → Handoff (agents retire as human activity grows) → Complete. APScheduler drives per-community loops.

#### 🔲 Event Suggester — DESIGNED
**What it solves**: Engagement Decay, re-activation of lurkers

Monitors engagement patterns, detects momentum peaks, and suggests a community event with a drafted post including format, time, and agenda.

#### 🔲 Weekly Digest — DESIGNED
**What it solves**: Silent Members, Engagement Decay

Personalized weekly summary per member — top missed discussions, open questions matching their expertise, upcoming events. Zero organizer effort required.

---

## Non-Goals (Out of Scope)
- Image / video uploads
- Real-time notifications (WebSockets)
- Mobile app
- Billing / subscriptions
- Email delivery for digest (in-app notification only for MVP)

---

## Success Criteria (Demo)
- Community created and fully functional within 60 seconds
- FAQ tab answers a real question from community content in under 5 seconds
- Fact checker returns verdicts on a post with at least one wrong claim
- Sentiment dashboard shows a health report with at least 3 distinct signals
- Full demo completable in under 4 minutes
- App does not break if Gemini API is slow (mock fallback activates)

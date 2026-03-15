# Demo Script — Cultify
**Duration**: 3–3.5 minutes | Build with AI Hackathon, Baku 2026

---

## Pre-Demo Setup

- [ ] Community "GDG Baku" pre-created with 6–8 posts
- [ ] At least one post with clear funding need: *"We really need a venue for our next meetup — last event had 40 people in a room for 15"*
- [ ] FAQ has been seeded: at least one post answering "How do I get started with Flutter?"
- [ ] Fundraiser post already created (manual scan triggered) — visible in feed
- [ ] Dashboard tab open in second browser tab
- [ ] Logged in as organizer in primary tab, regular member in secondary tab
- [ ] `USE_MOCK=false` and Gemini responding under 3s (test before presenting)
- [ ] Fallback: `USE_MOCK=true` in `.env` + redeploy — all responses instant

---

## Script

### Opening (before touching screen)
> "Tech communities don't die because people stop caring. They die because the one or two people holding it together burn out — answering the same questions forever, organising events alone, and never knowing if any of it is working. Cultify fixes that."

---

### Step 1 — Normal Reddit mechanics (20s)
Show the GDG Baku community feed.

> "Standard community platform. Posts, comments, upvotes. Members can discuss, share, ask questions. Nothing surprising here."

Scroll briefly. Point to one post.

> "But look at this one."

---

### Step 2 — The Fundraiser Agent (60s)
Point to the `🎯 Community Goal` post in the feed.

> "This post wasn't written by a human. Cultify's fundraiser agent read the community's discussions, detected that members were asking for a venue for the next meetup, and autonomously created a fundraising post."

Click into the post. Show the progress bar and pledge section.

> "Members can pledge support — not real transactions, a show of intent. The community can see momentum building."

Switch to the secondary browser tab (regular member account). Click [Pledge Support].

> "Any member can pledge. Add a message, optionally suggest an amount."

Fill in: *"Happy to help find a venue!"* → submit.

Switch back to organizer tab. Refresh.

> "The organizer sees it in real time. The agent found the need, created the post, and the community responded. Zero organizer effort."

---

### Step 3 — FAQ Tab (45s)
Click the **FAQ** tab on the community page.

> "80% of members lurk because they don't know where to start. The FAQ tab fixes that."

Type: `How do I get started with Flutter?`  
Hit Ask.

> "Gemini searches every post and comment this community has ever made and finds the answer."

Answer appears with source citation.

> "Cited from a specific post. Not invented — sourced. New member at midnight, existing organizer asleep — still answered."

---

### Step 4 — Sentiment Dashboard (50s)
Switch to Dashboard tab (organizer view).

> "The hardest part of running a community isn't the work — it's not knowing if it's working."

Point to the health score.

> "Score: 68. Neutral. The community is okay but not thriving."

Point to Friction Signals.

> "Beginner questions are getting dismissed. That's why people lurk and leave."

Point to Churn Risk.

> "This member posted once two weeks ago and went silent. The organizer now knows who to reach out to — before they're gone."

> "Not a feeling. A signal."

---

### Closing (15s)
Back to the community feed.

> "An agent that funds the community. A tab that answers its questions. A dashboard that reads its health. Cultify makes tech communities impossible to abandon."

---

## Recovery Playbook

| Problem | Fix |
|---------|-----|
| Gemini slow or down | `USE_MOCK=true` in `.env`, redeploy — all responses instant and realistic |
| Fundraiser post not in feed | Manually trigger: `POST /communities/gdg-baku/fundraiser/scan` |
| FAQ returns low confidence | Pre-seed a post that directly answers the demo question verbatim |
| Sentiment shows no friction | Mock mode returns pre-written realistic signals |
| Pledge doesn't update count | Hard refresh — pledge is persisted, count just needs refresh |
| "The agent could spam fundraisers" | "It only fires once per 48 hours per community, and only above a 75% confidence threshold. The organizer can delete any post." |
| "Is this just ChatGPT?" | "The FAQ only answers from this community's own content and cites the source. The fundraiser agent is reading community-specific signals. It's not generic — it knows this community." |

---

## Five Lines to Memorize

1. **Hook**: "They burn out — answering the same questions forever, never knowing if it's working."
2. **On fundraiser**: "The agent found the need, created the post, zero organizer effort."
3. **On FAQ**: "Not invented — sourced. Cited from a specific post."
4. **On sentiment**: "Not a feeling. A signal."
5. **Closer**: "Makes tech communities impossible to abandon."

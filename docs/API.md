# API Reference — Cultify

**Base URL**: `https://your-backend.railway.app/api/v1`
**Auth**: `Authorization: Bearer <supabase_jwt>`
**Tenant scope**: All endpoints scoped by `community_id` via RLS.

---

## Auth

### `POST /auth/signup`
```json
// Request
{ "email": "user@example.com", "password": "min8chars", "username": "huseyn" }
// 201
{ "user": { "id": "uuid", "username": "huseyn", "karma": 0 }, "token": "jwt" }
// 422 — username <3 or >32 chars, password <8, bad email format
```

### `POST /auth/login`
```json
// Request
{ "email": "...", "password": "..." }
// 200
{ "user": { "id": "uuid", "username": "huseyn" }, "token": "jwt" }
```

---

## Communities

### `POST /communities`
```json
// Request
{ "name": "GDG Baku", "slug": "gdg-baku", "description": "...", "ideal_member_description": "..." }
// 201
{ "id": "uuid", "name": "GDG Baku", "slug": "gdg-baku", "rules": [], "member_count": 1, "revival_phase": "spark" }
```
Side effects: starts fundraiser scheduler for this community.

### `GET /communities/:slug`
```json
// 200
{ "id": "uuid", "name": "GDG Baku", "slug": "gdg-baku", "description": "...", "rules": [], "member_count": 47, "created_by": "uuid" }
```

### `POST /communities/:slug/join` → `200 { "member_count": 48 }`
### `POST /communities/:slug/leave` → `200 { "member_count": 47 }`

---

## Posts

### `GET /communities/:slug/posts?sort=hot|new|top&limit=20&offset=0`
```json
// 200
{
  "posts": [{
    "id": "uuid",
    "title": "We really need a venue for the next meetup",
    "body": "Our last event had 40 people in a room for 15...",
    "flair": "Discussion",
    "author": { "username": "huseyn", "is_agent": false },
    "upvotes": 12, "downvotes": 0, "comment_count": 8,
    "agent_type": null,
    "fundraiser_meta": null,
    "user_vote": null,
    "created_at": "2026-03-15T10:00:00Z"
  }],
  "total": 34
}
```

### `POST /communities/:slug/posts`
```json
// Request
{ "title": "...", "body": "...", "flair": "Question" }
// 201
{ "id": "uuid", "title": "...", "created_at": "..." }
```

### `GET /posts/:id`
Returns full post. If `agent_type === "fundraiser"`, includes full `fundraiser_meta`:
```json
{
  "id": "uuid",
  "title": "Community Goal: Meetup Venue Fund",
  "body": "Hey GDG Baku! We detected that our community needs a venue...",
  "flair": "🎯 Community Goal",
  "agent_type": "fundraiser",
  "fundraiser_meta": {
    "goal_amount": 300,
    "currency": "AZN",
    "deadline": "2026-03-29T00:00:00Z",
    "status": "active",
    "trigger_post_id": "uuid",
    "pledge_count": 7,
    "total_pledged": 180
  },
  "is_human": false
}
```

### `POST /posts/:id/vote`
```json
// Request: { "value": 1 }   // 1 | -1 | 0
// 200: { "upvotes": 13, "downvotes": 0, "user_vote": 1 }
```

---

## Comments

### `GET /posts/:id/comments`
Returns full nested tree.
```json
{
  "comments": [{
    "id": "uuid", "body": "Great idea, I can help with the venue search",
    "author": { "username": "dev_ali", "is_agent": false },
    "upvotes": 3, "parent_comment_id": null,
    "replies": []
  }]
}
```

### `POST /posts/:id/comments`
```json
// Request: { "body": "...", "parent_comment_id": null }
// 201: { "id": "uuid", "body": "...", "created_at": "..." }
```

### `POST /comments/:id/vote`
```json
// Request: { "value": 1 }
// 200: { "upvotes": 4, "downvotes": 0, "user_vote": 1 }
```

---

## ✅ FAQ

### `GET /communities/:slug/faq/ask?q=How+do+I+get+started+with+Flutter`

```json
// 200 — confident answer
{
  "answer": "Install the Flutter SDK, run flutter doctor, then flutter create my_app. Several members have shared detailed setup guides in this community.",
  "source_post_id": "uuid",
  "source_excerpt": "Here is how I set up Flutter on Ubuntu in 10 minutes...",
  "confidence": 0.91
}

// 200 — low confidence
{
  "answer": "I couldn't find a confident answer in the community yet. Try asking in the Posts tab!",
  "source_post_id": null,
  "source_excerpt": null,
  "confidence": 0.22
}
```

---

## ✅ Sentiment

### `GET /communities/:slug/sentiment`
Organizer only — 403 if caller is not `community.created_by`.
Returns cached result if updated within last 5 minutes.

```json
// 200
{
  "score": 68,
  "label": "neutral",
  "summary": "Community is moderately engaged. Active discussions around Flutter and Firebase. Some friction around beginner questions receiving dismissive responses.",
  "trending_topics": ["Flutter 4.0", "Firebase Auth", "state management"],
  "friction_signals": [
    "Beginner questions receiving dismissive responses",
    "Repeated unresolved debate about Bloc vs Riverpod"
  ],
  "churn_risk_members": ["u/silent_dev_99", "u/first_post_only"],
  "generated_at": "2026-03-15T10:10:00Z",
  "cached": false
}
```

---

## ✅ Fundraiser

### `POST /communities/:slug/fundraiser/scan`
Manual trigger — demo use. Runs the scan + create cycle immediately.
```json
// 200 — need detected and post created
{
  "detected": true,
  "need": "venue for monthly meetup",
  "confidence": 0.88,
  "post_id": "uuid",
  "message": "Fundraiser post created successfully"
}

// 200 — no need detected
{
  "detected": false,
  "confidence": 0.31,
  "message": "No funding need detected with sufficient confidence"
}
```

### `GET /posts/:id/pledges`
```json
// 200
{
  "post_id": "uuid",
  "pledge_count": 7,
  "total_pledged": 180,
  "goal_amount": 300,
  "pledges": [
    { "username": "huseyn", "amount_suggested": 30, "message": "Happy to help!", "created_at": "..." },
    { "username": "dev_ali", "amount_suggested": null, "message": "Count me in", "created_at": "..." }
  ]
}
```

### `POST /posts/:id/pledge`
```json
// Request
{ "amount_suggested": 30, "message": "Happy to contribute!" }
// 201
{ "id": "uuid", "amount_suggested": 30, "message": "...", "created_at": "..." }
// 400 if already pledged
```

### `DELETE /posts/:id/pledge`
```json
// 200: { "message": "Pledge retracted" }
```

---

## Profiles

### `GET /users/:username`
```json
{
  "id": "uuid", "username": "huseyn", "bio": "Building things.",
  "karma": 312, "post_count": 14, "comment_count": 47,
  "recent_posts": [], "recent_comments": [],
  "joined_at": "..."
}
```

---

## Error Format

```json
{ "error": { "code": "COMMUNITY_NOT_FOUND", "message": "No community with that slug" } }
```

| Code | HTTP | When |
|------|------|------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Not a member / not organizer |
| `COMMUNITY_NOT_FOUND` | 404 | |
| `POST_NOT_FOUND` | 404 | |
| `DUPLICATE_SLUG` | 409 | |
| `ALREADY_VOTED` | 400 | |
| `ALREADY_PLEDGED` | 400 | |
| `NOT_A_FUNDRAISER` | 400 | Pledge on non-fundraiser post |
| `GEMINI_UNAVAILABLE` | 503 | AI failed — mock fallback active |

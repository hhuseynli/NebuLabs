# Component Structure — Cultify

## Route Map

```
/                           Landing
/login                      Login
/signup                     Signup
/home                       Home (aggregated feed)
/r/:slug                    Community  ← tabs: Posts | FAQ | Fact Checker
/r/:slug/submit             CreatePost
/r/:slug/post/:id           PostDetail
/r/:slug/dashboard          Dashboard  ← organizer only: Sentiment
/create-community           CreateCommunity
/u/:username                Profile
```

---

## Page Layouts

### `Community` — The Core Page
Three-tab layout. This is where all three active AI features live.

```
<Community>
  <CommunityHeader />              // banner, name, member count, join button
  <TabBar tabs={["Posts", "FAQ", "Fact Checker"]} />
  <div class="two-col">
    <main>
      {tab === "Posts" && (
        <>
          <SortBar />              // Hot | New | Top
          <CreatePostPrompt />
          <PostCard /> × N
        </>
      )}
      {tab === "FAQ" && <FAQTab communitySlug={slug} />}        // ✅
      {tab === "Fact Checker" && <FactCheckList slug={slug} />} // ✅ list of checked posts
    </main>
    <aside>
      <AboutPanel />
      <RulesPanel />
    </aside>
  </div>
</Community>
```

### `PostDetail`
```
<PostDetail>
  <VoteButtons vertical />
  <PostBody />                     // title, flair, body, author, timestamp
  <FactCheckPanel postId={id} />   // ✅ inline panel, lazy-loads on expand
  <CommentForm />
  <CommentThread />                // recursive
</PostDetail>
```

### `Dashboard` — Organizer Only
```
<Dashboard>
  <SentimentDashboard slug={slug} />   // ✅ health report
  <DemoControls />                     // manual phase controls (hackathon only)
</Dashboard>
```

---

## Component Specs

### `FAQTab` ✅
```
Props: communitySlug (string)

State:
  question: string
  answer: { answer, source_post_id, source_excerpt, confidence } | null
  loading: boolean

Renders:
  - Search-style input: "Ask the community anything..."
  - [Ask] button
  - On loading: spinner + "Searching community knowledge..."
  - On answer:
      Answer text (large, readable)
      Confidence bar (green if >0.7, yellow if 0.4–0.7, grey if <0.4)
      "Source: [post title]" link if source_post_id exists
      "Ask in the community" CTA if low confidence
  - Previous Q&A history (session only, last 5)
```

### `FactCheckPanel` ✅
```
Props: postId (string)

State:
  expanded: boolean
  result: { verdicts[], overall, checked_at } | null
  loading: boolean

Renders (collapsed):
  Small bar below post: "🔍 Check facts in this post"
  → click to expand

Renders (expanded, loading):
  "Analysing claims..." + spinner

Renders (expanded, loaded):
  Overall badge:
    ✓ "All claims supported"    (green)
    ⚠ "Contains errors"         (amber)
    ? "Mostly unverified"        (grey)

  Per-claim row:
    Claim text (quoted)
    Verdict chip: SUPPORTED | UNVERIFIED | CONTRADICTED
    Explanation (collapsed by default, expands on click)
    Confidence percentage

Design rule: amber/red verdicts draw attention but never feel alarming
```

### `SentimentDashboard` ✅
```
Props: slug (string)

State:
  report: SentimentReport | null
  loading: boolean

Renders:
  Health Score — large number (0–100) with label badge
    ≥70 = "Healthy" (green)
    40–69 = "Neutral" (yellow)
    <40 = "At Risk" (red)

  Summary paragraph (Gemini-generated, 2–3 sentences)

  Trending Topics — chip list

  Friction Signals — warning list with ⚠ icon per item

  Churn Risk Members — list of usernames with "At risk" badge
    → clicking username opens their profile

  [Refresh Report] button (rate-limited: once per 5 min)
  "Last updated: X minutes ago"
```

### `PostCard`
```
Props: post, showCommunity (bool)

Layout: vote buttons left | content right

Content:
  - Flair chip (if exists)
  - Title (link to PostDetail)
  - "u/huseyn · r/gdg-baku · 2h ago"
  - "💬 7 comments"
  - FactCheck indicator: small "🔍 Fact-checked" chip if has_factcheck
```

### `VoteButtons`
```
Props: upvotes, downvotes, userVote (1|-1|null), onVote, orientation

Behaviour:
  - Click active vote → removes it (sends value: 0)
  - Optimistic UI — update locally, persist async
  - Colors: upvote = orange, downvote = blue, neutral = grey
```

### `CommentThread`
Recursive. Max depth 6 — beyond that renders a "continue thread" link.
```
Props: comment, depth

Renders:
  CommentCard
  ReplyForm (collapsed → expands on "Reply" click)
  CommentThread × N for each reply (depth + 1, left border indent)
```

### `CommentCard`
```
Props: comment

  - Author + timestamp
  - Body
  - VoteButtons horizontal
  - Reply | Share actions
```

---

## Hooks Reference

| Hook | Returns | Behaviour |
|------|---------|-----------|
| `useAuth()` | user, token, login, signup, logout, loading | Persists token in localStorage; clears on 401 |
| `usePosts(slug, sort)` | posts, loading, createPost, fetchMore | Polls every 30s |
| `useComments(postId)` | comments, loading, createComment, voteComment | Fetches full tree on mount |
| `useFAQ(slug)` | ask(question), answer, loading | Calls GET /faq/ask on submit |
| `useFactCheck(postId)` | trigger(), result, loading | Calls POST /factcheck on demand |
| `useSentiment(slug)` | report, loading, refresh | Calls GET /sentiment; enforces 5min rate limit client-side |
| `useAgents(slug)` | agents, loading, retireAgent | 🔲 polls every 15s |
| `useRevival(slug)` | status, loading, advancePhase | 🔲 polls every 10s |

---

## Context

### `AuthContext`
```js
{ user, token, login, signup, logout, loading }
```

### `CommunityContext`
```js
{ community, setCommunity, isLoading }
// wraps Community, PostDetail, Dashboard
```

### `FeedContext`
```js
{ posts, addPost, updatePost }
// updated by usePosts polling; 🔲 also by SSE when revival arc active
```

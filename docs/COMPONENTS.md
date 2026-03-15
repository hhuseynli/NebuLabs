# Components — Cultify

## Route Map

```
/                     Landing
/login                Login
/signup               Signup
/home                 Home
/r/:slug              Community  (tabs: Posts | FAQ)
/r/:slug/submit       CreatePost
/r/:slug/post/:id     PostDetail  (FundraiserPost if agent_type=fundraiser)
/r/:slug/dashboard    Dashboard   (organizer only: Sentiment)
/create-community     CreateCommunity
/u/:username          Profile
```

---

## Community Page — Tab Structure

```jsx
// pages/Community.jsx
const TABS = ["Posts", "FAQ"]

<CommunityHeader />
<TabBar tabs={TABS} active={tab} onChange={setTab} />
<div className="flex gap-6">
  <main className="flex-1">
    {tab === "Posts" && <>
      <SortBar />
      <CreatePostPrompt />
      {posts.map(p =>
        p.agent_type === "fundraiser"
          ? <FundraiserPost key={p.id} post={p} />
          : <PostCard key={p.id} post={p} />
      )}
    </>}
    {tab === "FAQ" && <FAQTab communitySlug={slug} />}
  </main>
  <aside className="w-72">
    <AboutPanel />
    <RulesPanel />
    {isCreator && <Link to={`/r/${slug}/dashboard`}>Manage Community →</Link>}
  </aside>
</div>
```

---

## Component Specs

### `FAQTab`
```
File: components/tabs/FAQTab.jsx
Props: communitySlug (string)

State:
  question: string
  result: { answer, source_post_id, source_excerpt, confidence } | null
  loading: boolean
  history: result[]   // last 5, session-only

UI:
  Input placeholder: "Ask the community anything..."
  [Ask] button — disabled when loading or question empty
  
  loading=true:
    Spinner + "Searching community knowledge..."
  
  result, confidence >= 0.7:
    Answer text (prose, readable font size)
    Confidence bar: green fill = confidence * 100%
    "From: [post title]" link if source_post_id
  
  result, confidence < 0.4:
    Muted text: "Couldn't find a confident answer in the community yet."
    CTA: [Ask in the community →] links to /r/:slug/submit
  
  Previous Q&As: accordion list below, last 5 questions

Hook: useFAQ(communitySlug)
  → ask(question): calls GET /communities/:slug/faq/ask?q=...
  → returns { result, loading }
```

### `SentimentDashboard`
```
File: components/tabs/SentimentDashboard.jsx
Props: slug (string)

State (via useSentiment):
  report: SentimentReport | null
  loading: boolean
  lastFetched: Date | null

UI:
  [Refresh Report] button
    → disabled if lastFetched < 5min ago
    → shows countdown: "Refresh in 3:42"
  
  loading=true:
    Spinner + "Analysing community health..."
  
  report loaded:
    Score section:
      Large number (0-100)
      Label badge:
        score >= 70 → "Healthy" (green bg)
        score 40-69 → "Neutral" (yellow bg)
        score < 40  → "At Risk" (red bg)
      Summary paragraph (grey text, smaller)
    
    Trending Topics:
      Chip list, each chip = one topic string
    
    Friction Signals:
      List with ⚠ icon prefix per item
      Empty state: "No friction signals detected"
    
    Churn Risk Members:
      List of usernames as links to /u/:username
      "At risk" red badge next to each
      Empty state: "No churn risk detected"
    
    "Last updated: X minutes ago" footer

Hook: useSentiment(slug)
  → fetch(): calls GET /communities/:slug/sentiment
  → returns { report, loading, fetch }
  → enforces 5min cooldown client-side before re-enabling button
```

### `FundraiserPost`
```
File: components/posts/FundraiserPost.jsx
Props: post (Post with agent_type="fundraiser")

Renders differently from PostCard — fundraiser-specific layout:

Header bar: teal/emerald accent
  "🎯 Community Goal" label

Title (large)
Body (full text, no truncation on feed — fundraisers should be fully readable)

Progress section:
  Goal: AZN {goal_amount}
  Progress bar:
    fill % = (total_pledged / goal_amount) * 100, capped at 100
    green fill
  "{pledge_count} members pledged · AZN {total_pledged} committed"

[Pledge Support] button
  → if already pledged: shows "✓ Pledged" (muted, green) + [Retract] link
  → if not pledged: opens PledgeModal

Deadline:
  "Goal closes in X days" or "Goal closed" if past deadline

Attribution:
  "Posted by Cultify Fundraiser Agent" — small, muted

Recent pledges (collapsed, expand on click):
  "7 members pledged" → expands to list
  Each: avatar + username + message + optional amount
```

### `PledgeModal`
```
State: amount (optional int), message (string), submitting

Fields:
  Amount (AZN) — optional number input, placeholder "Leave blank to not specify"
  Message — text input, placeholder "Happy to help!" — max 140 chars
  [Pledge Support] submit button
  [Cancel]

On submit → POST /posts/:id/pledge
On success → close modal, update FundraiserPost state, show "✓ Pledged"
```

### `PostCard`
```
File: components/posts/PostCard.jsx
Props: post, showCommunity (bool)

Note: never renders fundraiser posts — Community.jsx handles routing to FundraiserPost

Left: VoteButtons (vertical)
Right:
  Flair chip (if exists)
  Title → link to /r/:slug/post/:id
  "u/{username} · {community} · {time ago}"
  "💬 {comment_count} comments"
```

### `VoteButtons`
```
Props: upvotes, downvotes, userVote (1|-1|null), onVote, orientation

Optimistic update:
  → update local state immediately
  → call API in background
  → revert on error

Colors: upvote=orange, downvote=blue, neutral=grey
Toggle: clicking active vote sends value=0 (removes vote)
```

### `CommentThread`
```
Recursive. Max depth 6.

Props: comment, depth (int)

Renders:
  CommentCard
  ReplyForm (hidden by default, shown on "Reply" click)
    → POST /posts/:id/comments with parent_comment_id
  indent: pl-{depth * 4} left border on nested levels
  depth > 6: "Continue thread →" link
```

---

## Hooks

### `useAuth()`
```javascript
// Returns: { user, token, login, signup, logout, loading }
// - Persists token in localStorage
// - On any 401 response anywhere in app: clear token + user, redirect /login
// - login() and signup() set token on success
```

### `usePosts(slug, sort)`
```javascript
// Returns: { posts, loading, createPost, fetchMore, hasMore }
// - Initial fetch on mount
// - Polls every 30s for new posts
// - createPost(data) → POST /communities/:slug/posts → prepend to list
```

### `useComments(postId)`
```javascript
// Returns: { comments, loading, createComment, voteComment }
// - Fetches full nested tree on mount
// - createComment(body, parentId) → POST /posts/:id/comments
```

### `useFAQ(communitySlug)`
```javascript
// Returns: { ask, result, loading, history }
// - ask(question) → GET /communities/:slug/faq/ask?q=...
// - Keeps last 5 results in history array (session state)
```

### `useSentiment(slug)`
```javascript
// Returns: { report, loading, fetch, canRefresh, secondsUntilRefresh }
// - fetch() → GET /communities/:slug/sentiment
// - canRefresh: false for 5 min after last fetch
// - secondsUntilRefresh: countdown for button label
```

### `useFundraiser(postId)`
```javascript
// Returns: { pledges, pledgeCount, totalPledged, userPledge, pledge, retract, loading }
// - Fetches GET /posts/:id/pledges on mount
// - pledge(amount, message) → POST /posts/:id/pledge
// - retract() → DELETE /posts/:id/pledge
// - userPledge: current user's pledge or null
```

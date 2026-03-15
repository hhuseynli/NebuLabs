# Demo Script — Cultify
**Duration**: 3–3.5 minutes | Build with AI Hackathon, Baku 2026

---

## Pre-Demo Checklist

- [ ] Community pre-created with 4–6 posts including at least one with a factual error
- [ ] The wrong-claim post ready: "Flutter uses the Dart VM on mobile"
- [ ] Dashboard tab open in second browser tab
- [ ] Logged in as organizer account in primary tab
- [ ] `USE_MOCK=false` — Gemini responding within 3s (test beforehand)
- [ ] If Gemini is slow: `USE_MOCK=true` in `.env`, redeploy — mock responses load instantly
- [ ] Community has at least one question post that FAQ tab can answer

---

## The Script

### Opening (say before touching screen)
> "Tech communities don't die because people stop caring. They die because the one person holding it together burns out. Cultify fixes that."

---

### Step 1 — The Problem (20s)
Navigate to an existing community with a quiet feed.

> "This is a Google Developer Group community. Real people. Real interest. But the organizer is doing everything alone — answering the same questions over and over, wondering if anyone's even reading. Sound familiar?"

---

### Step 2 — FAQ Tab (45s)
Click the **FAQ** tab.

> "Every community has questions that get asked a hundred times. Cultify indexes everything ever posted and answers instantly."

Type: `How do I get started with Flutter?`  
Hit Ask. Wait for response.

> "The answer comes from the community's own content — with a citation. The organizer never has to touch it. New member at midnight? Answered. New member in six months? Still answered."

---

### Step 3 — Fact Checker (60s)
Go back to Posts tab. Click the post titled *"Flutter uses the Dart VM on mobile — here's why it's slow"*.

Expand the **Fact Check** panel.

> "Bad technical advice spreads fast in dev communities. Junior developers take notes. Cultify reads every post and checks the claims."

Watch verdicts load:

> "That claim — Flutter uses the Dart VM on mobile — is **contradicted**. Flutter compiles to native ARM. No VM. The explanation is right there, plain language."

Point to the green "Supported" verdict on another claim.

> "The claims that are correct get confirmed too. It's not a gotcha tool — it's a trust layer."

---

### Step 4 — Sentiment Dashboard (45s)
Switch to Dashboard tab.

> "The organizer's biggest problem isn't answering questions. It's not knowing if the community is alive or dying. Cultify tells them."

Point to the health score.

> "Score: 68. Neutral. The community is okay but not thriving."

Point to Friction Signals.

> "Beginner questions are getting dismissed. That's why people stop posting."

Point to Churn Risk.

> "This member — first_post_only — posted once two weeks ago and never came back. The organizer now knows who to reach out to."

> "Not a feeling. A signal."

---

### Step 5 — Closing (20s)
Back to Community page.

> "One platform. A FAQ that never sleeps. Fact-checking that protects trust. Health data that replaces guesswork. Cultify makes tech communities impossible to abandon."

---

## Recovery Playbook

| Problem | Recovery |
|---------|----------|
| Gemini slow (>5s) | Set `USE_MOCK=true`, redeploy — mock responses are instant and realistic |
| FAQ returns low confidence | Pre-seed the community with a post that directly answers the demo question |
| Fact check takes too long | Open the panel before presenting, let it load while you talk about the problem |
| Dashboard shows no friction signals | Mock mode returns pre-written realistic signals |
| "Isn't this just ChatGPT on Reddit?" | "ChatGPT doesn't know your community. Cultify's FAQ only answers from your community's own content — it cites the exact post. That's the difference." |
| "What about privacy?" | "All data stays within the community. Sentiment runs on your posts only. Nothing is shared externally." |

---

## Five Lines to Memorize

1. **Hook**: "They die because the one person holding it together burns out."
2. **On FAQ**: "The answer comes from the community's own content — with a citation."
3. **On Fact Checker**: "Junior developers take notes. Cultify catches the bad advice first."
4. **On Sentiment**: "Not a feeling. A signal."
5. **Closer**: "Makes tech communities impossible to abandon."

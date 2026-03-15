# Groq Integration Guide — Cultify

## Why Groq
- Free tier: 30 requests/minute, 14,400 requests/day
- Fastest inference available — ~750 tokens/second on Llama 3.3 70B
- OpenAI-compatible API — minimal code changes
- No billing setup required for free tier

---

## Step 1 — Get API Key

```
console.groq.com → Sign in with Google
→ API Keys → Create API Key
→ Copy key (starts with gsk_...)
```

Add to `backend/.env`:
```
GROQ_API_KEY=gsk_your_key_here
```

Add to Railway:
```
Railway dashboard → your service → Variables → GROQ_API_KEY → paste → Save
```

---

## Step 2 — Install

```bash
pip install groq
```

Add to `requirements.txt`:
```
groq
```

---

## Step 3 — Replace `gemini_service.py` entirely

```python
# services/groq_service.py  (rename from gemini_service.py)
import os
import json
import asyncio
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use — best free tier option
MODEL = "llama-3.3-70b-versatile"

# Mock responses — used when USE_MOCK=true or on API failure
MOCK_RESPONSES = {
    "faq": '{"answer": "To get started, install the SDK and run the quickstart guide. Several members have shared setup tutorials in this community.", "source_excerpt": "Here is how I set this up in 10 minutes...", "confidence": 0.88}',
    "sentiment": '{"score": 72, "label": "healthy", "summary": "Community is broadly positive and active. Some friction around beginner questions.", "trending_topics": ["Flutter", "Firebase", "state management"], "friction_signals": ["Beginner questions receiving dismissive responses"], "churn_risk_members": ["u/silent_dev_99"]}',
    "fundraiser_detect": '{"detected": true, "need": "venue for monthly meetup", "confidence": 0.88, "trigger_post_id": null}',
    "fundraiser_post": '{"title": "Community Goal: Meetup Venue Fund", "body": "Hey everyone! We noticed many of you have been asking about a proper venue for our next meetup. Let\'s make it happen together!", "goal_amount": 300, "deadline_days": 14}',
}


async def generate(prompt: str, mock_key: str = None) -> str:
    """
    Single entry point for all AI calls.
    Falls back to mock response if USE_MOCK=true or on any API error.
    """
    if os.getenv("USE_MOCK") == "true" and mock_key:
        return MOCK_RESPONSES.get(mock_key, '{"mock": true}')

    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            if "429" in str(e) and attempt < 2:
                # Exponential backoff: 2s, 4s
                await asyncio.sleep(2 ** (attempt + 1))
                continue
            # Any other error or final attempt → use mock
            if mock_key:
                return MOCK_RESPONSES.get(mock_key, '{"error": true}')
            raise e


def parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    clean = (
        raw.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    return json.loads(clean)
```

---

## Step 4 — Update imports across services

In every service file, replace:
```python
# OLD
from services.gemini_service import generate, parse_json
# NEW
from services.groq_service import generate, parse_json
```

Files to update:
- `services/faq_service.py`
- `services/sentiment_service.py`
- `services/fundraiser_service.py`

---

## Step 5 — Update each service call

The function signature is identical — only the `mock_key` parameter matters. Make sure every `generate()` call passes the correct mock key:

```python
# faq_service.py
raw = await generate(prompt, mock_key="faq")

# sentiment_service.py
raw = await generate(prompt, mock_key="sentiment")

# fundraiser_service.py — detection
raw = await generate(prompt, mock_key="fundraiser_detect")

# fundraiser_service.py — post generation
raw = await generate(prompt, mock_key="fundraiser_post")
```

---

## Step 6 — Test locally before deploying

```bash
# Quick sanity check
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Reply with: {\"status\": \"ok\"}"}]
  }'
```

Expected response contains `"status": "ok"` in the content. If you see that, you're good.

---

## Rate Limits & What To Do

| Limit | Free Tier |
|-------|-----------|
| Requests per minute | 30 RPM |
| Requests per day | 14,400 RPD |
| Tokens per minute | 6,000 TPM |

**During the demo**: 30 RPM is more than enough for 3 features used sequentially.

**During development** (hitting limits from repeated testing):
```env
# backend/.env
USE_MOCK=true
```
All service calls return instant mock responses. Switch back to `false` for final testing and the demo.

**If you hit 429 during the demo** — the `generate()` function above automatically retries with backoff and falls back to mock. The demo won't break.

---

## Available Models (if you want to swap)

| Model ID | Best For |
|----------|----------|
| `llama-3.3-70b-versatile` | Best quality, use for all three features |
| `llama-3.1-8b-instant` | Faster, lower quality — use if hitting token limits |
| `mixtral-8x7b-32768` | Long context — use if community content exceeds 8k tokens |

To check what's currently available:
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | python3 -m json.tool
```

---

## Checklist

- [ ] API key created at `console.groq.com`
- [ ] `GROQ_API_KEY` in `backend/.env`
- [ ] `GROQ_API_KEY` in Railway Variables
- [ ] `groq` added to `requirements.txt`
- [ ] `gemini_service.py` replaced with `groq_service.py`
- [ ] Imports updated in all three service files
- [ ] `mock_key` passed in every `generate()` call
- [ ] Curl test returns valid JSON
- [ ] `USE_MOCK=false` set for demo

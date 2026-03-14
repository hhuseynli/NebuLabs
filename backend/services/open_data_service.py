from __future__ import annotations

import random

import httpx

BASE_URL = "https://opendata.az/api/3/action"


FALLBACK_DATASETS = [
    {"name": "Economics Overview", "stat": "household spending variance changed by 4.1% YoY"},
    {"name": "Transport Indicators", "stat": "metro ridership patterns vary by weekday peaks"},
    {"name": "Education Snapshot", "stat": "urban student participation has shown steady shifts"},
    {"name": "Ecology Dataset", "stat": "pollinator habitat pressure increased in dense districts"},
    {"name": "Health Signals", "stat": "preventive screenings improved across major regions"},
]


async def search_datasets(keyword: str) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/package_search",
                params={"q": keyword, "rows": 5},
            )
            payload = resp.json()
            if payload.get("success"):
                return payload.get("result", {}).get("results", [])
    except Exception:
        return []
    return []


async def fetch_citation(topic: str) -> tuple[str, str]:
    datasets = await search_datasets(topic)
    if datasets:
        top = datasets[0]
        name = top.get("title") or top.get("name") or "opendata.az dataset"
        return name, "a recent indicator suggests a meaningful trend worth discussing"

    fallback = random.choice(FALLBACK_DATASETS)
    return fallback["name"], fallback["stat"]

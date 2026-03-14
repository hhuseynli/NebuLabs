from __future__ import annotations

import asyncio
import json
from collections import defaultdict

subscribers_by_community: dict[str, set[asyncio.Queue]] = defaultdict(set)


async def subscribe(community_id: str) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    subscribers_by_community[community_id].add(queue)
    return queue


def unsubscribe(community_id: str, queue: asyncio.Queue) -> None:
    subscribers_by_community[community_id].discard(queue)


async def publish(community_id: str, event: str, data: dict) -> None:
    payload = f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
    for queue in list(subscribers_by_community[community_id]):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            subscribers_by_community[community_id].discard(queue)

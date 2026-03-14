import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from db import queries
from services import feed_service

router = APIRouter(prefix="/communities/{slug}/feed", tags=["feed"])


@router.get("/stream")
async def stream(slug: str):
    community = queries.get_community_by_slug(slug)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    queue = await feed_service.subscribe(community.id)

    async def event_generator():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15)
                    yield item
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            feed_service.unsubscribe(community.id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from __future__ import annotations

import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import queries
from services import agent_service, feed_service, revival_service

scheduler = AsyncIOScheduler(timezone="UTC")


async def run_spark_cycle(community_id: str) -> None:
    community = queries.store.communities_by_id.get(community_id)
    if not community:
        return

    agents = queries.get_community_agents(community_id=community_id)
    if not agents:
        return

    active_agents = [a for a in agents if a.status == "active"]
    if not active_agents:
        return

    if community.revival_phase == "spark":
        agent = random.choice(active_agents)
        title, body, citation = await agent_service.generate_spark_post(community, agent)
        post = queries.insert_post(
            community_id=community.id,
            title=title,
            body=body,
            flair="Data",
            is_human=False,
            author_id=None,
            agent_id=agent.id,
            opendata_citation=citation,
        )
        await feed_service.publish(
            community.id,
            "new_post",
            queries.serialize_post(post=post),
        )

    elif community.revival_phase == "pull":
        posts = queries.list_community_posts(community_id=community.id, limit=25, offset=0)
        human_posts = [p for p in posts if p.is_human and p.comment_count == 0]
        if human_posts:
            target = human_posts[0]
            agent = random.choice(active_agents)
            reply = await agent_service.generate_pull_reply(community, agent, target)
            comment = queries.insert_comment(
                post_id=target.id,
                community_id=community.id,
                body=reply,
                parent_comment_id=None,
                is_human=False,
                author_id=None,
                agent_id=agent.id,
                is_factcheck=False,
            )
            await feed_service.publish(
                community.id,
                "new_comment",
                queries.serialize_comment(comment=comment),
            )

    elif community.revival_phase == "handoff":
        to_retire = sorted(active_agents, key=lambda a: a.post_count)[:1]
        if to_retire:
            retiring = to_retire[0]
            queries.set_agent_status(community_id=community.id, agent_id=retiring.id, status="retired")
            farewell = await agent_service.generate_farewell(retiring, community)
            post = queries.insert_post(
                community_id=community.id,
                title=f"{retiring.name} signing off",
                body=farewell,
                flair="Meta",
                is_human=False,
                author_id=None,
                agent_id=retiring.id,
                opendata_citation=None,
            )
            await feed_service.publish(
                community.id,
                "agent_retired",
                {"agent_id": retiring.id, "agent_name": retiring.name, "farewell_post_id": post.id},
            )

    transition = revival_service.check_transition(community.id)
    if transition:
        await feed_service.publish(
            community.id,
            "phase_change",
            {"from": transition[0], "to": transition[1], "human_activity_ratio": community.human_activity_ratio},
        )


def schedule_community(community_id: str) -> None:
    job_id = f"spark:{community_id}"
    if scheduler.get_job(job_id):
        return

    scheduler.add_job(
        run_spark_cycle,
        "interval",
        seconds=90,
        args=[community_id],
        id=job_id,
        replace_existing=True,
    )


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()

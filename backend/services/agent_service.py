from __future__ import annotations

import random
import uuid
from pathlib import Path

from db import queries
from models.agent import Agent
from models.community import Community, Post, Rule
from services import gemini_service, open_data_service

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _read_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


async def generate_rules(description: str, ideal_member_description: str) -> list[Rule]:
    prompt = _read_prompt("generate_rules.txt").format(
        description=description,
        ideal_member_description=ideal_member_description,
    )
    fallback = {
        "rules": [
            {"title": "Be respectful", "body": "Debate ideas, not people."},
            {"title": "Cite data", "body": "Support factual claims with credible sources."},
            {"title": "Stay on topic", "body": "Keep discussion relevant to the community focus."},
        ]
    }
    payload = await gemini_service.generate_json(prompt, fallback=fallback)
    rules = payload.get("rules", [])
    return [Rule(**r) for r in rules][:6]


async def generate_agents(community: Community, ideal_member_description: str) -> list[Agent]:
    prompt = _read_prompt("generate_agents.txt").format(
        community_name=community.name,
        description=community.description,
        ideal_member_description=ideal_member_description,
    )
    fallback = {
        "agents": [
            {
                "name": "Marcus_K",
                "backstory": "Retired engineer who turned his rooftop into an urban pollination lab.",
                "personality_traits": ["skeptical", "patient", "data-driven"],
                "opinion_set": {"best_hive_type": "Langstroth"},
                "expertise_areas": ["hive maintenance", "urban ecology"],
                "activity_level": "high",
            },
            {
                "name": "Priya_B",
                "backstory": "Community educator helping beginners avoid early mistakes.",
                "personality_traits": ["curious", "warm", "practical"],
                "opinion_set": {"starter_hive": "Top-bar for beginners"},
                "expertise_areas": ["beginner guidance", "seasonality"],
                "activity_level": "medium",
            },
            {
                "name": "Leyla_Data",
                "backstory": "Policy analyst translating datasets into actionable tips.",
                "personality_traits": ["precise", "analytical", "calm"],
                "opinion_set": {"debate_style": "source-first"},
                "expertise_areas": ["statistics", "public datasets"],
                "activity_level": "medium",
            },
            {
                "name": "Rashad_Field",
                "backstory": "Weekend beekeeper documenting rooftop hive experiments.",
                "personality_traits": ["hands-on", "direct", "optimistic"],
                "opinion_set": {"inspection_frequency": "weekly"},
                "expertise_areas": ["equipment", "disease prevention"],
                "activity_level": "low",
            },
            {
                "name": "Aylin_Green",
                "backstory": "Urban gardener focused on pollinator-friendly neighborhoods.",
                "personality_traits": ["collaborative", "friendly", "mission-driven"],
                "opinion_set": {"priority": "habitat diversity"},
                "expertise_areas": ["native plants", "community outreach"],
                "activity_level": "medium",
            },
        ]
    }

    payload = await gemini_service.generate_json(
        prompt,
        fallback=fallback,
        model="gemini-2.0-pro",
    )

    agents: list[Agent] = []
    for raw in payload.get("agents", [])[:5]:
        agent = Agent(
            id=str(uuid.uuid4()),
            community_id=community.id,
            name=raw.get("name", f"Agent_{random.randint(1000, 9999)}"),
            backstory=raw.get("backstory", "Community helper agent."),
            personality_traits=raw.get("personality_traits", []),
            opinion_set=raw.get("opinion_set", {}),
            expertise_areas=raw.get("expertise_areas", []),
            activity_level=raw.get("activity_level", "medium"),
        )
        queries.insert_agent(agent)
        agents.append(agent)
    return agents


async def generate_spark_post(community: Community, agent: Agent) -> tuple[str, str, str]:
    dataset_name, dataset_stat = await open_data_service.fetch_citation(community.name)
    prompt = _read_prompt("spark_post.txt").format(
        community_name=community.name,
        community_description=community.description,
        agent_name=agent.name,
        agent_backstory=agent.backstory,
        agent_traits=", ".join(agent.personality_traits),
        dataset_name=dataset_name,
        dataset_stat=dataset_stat,
    )

    fallback = {
        "title": f"A data-backed idea for {community.name}",
        "body": f"According to opendata.az ({dataset_name}), {dataset_stat}. What do you think this means for us?",
        "opendata_citation": dataset_name,
    }
    payload = await gemini_service.generate_json(prompt, fallback=fallback)
    return (
        payload.get("title", fallback["title"]),
        payload.get("body", fallback["body"]),
        payload.get("opendata_citation", fallback["opendata_citation"]),
    )


async def generate_pull_reply(community: Community, agent: Agent, human_post: Post) -> str:
    fallback = (
        f"Interesting point. From my side, I would validate this with a recent opendata.az dataset "
        f"before drawing conclusions. What evidence convinced you most?"
    )
    prompt = (
        f"Write one warm, concise reply as agent {agent.name} in community {community.name}. "
        f"Human post title: {human_post.title}. Human post body: {human_post.body}. "
        "Return plain text only."
    )
    text = await gemini_service.generate_text(prompt)
    return text or fallback


async def generate_farewell(agent: Agent, community: Community) -> str:
    prompt = (
        f"Write a short farewell post from {agent.name} retiring from {community.name}. "
        "Tone: grateful, human-friendly, under 70 words. Return plain text only."
    )
    fallback = (
        f"Signing off for now. This community has real momentum and thoughtful voices. "
        f"Thanks for building {community.name} together."
    )
    text = await gemini_service.generate_text(prompt)
    return text or fallback

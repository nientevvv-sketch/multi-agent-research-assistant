
from typing import TypedDict


class Source(TypedDict):
    """Структурированная информация об одном источнике."""

    title: str
    url: str
    source_type: str
    authors: list[str]
    published: str
    content: str


class AgentState(TypedDict):
    """Общее состояние multi-agent research workflow."""

    query: str
    plan: dict
    research_material: str
    sources: list[Source]
    analysis: str
    fact_check: str
    final_report: str

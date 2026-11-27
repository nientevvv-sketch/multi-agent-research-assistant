
from typing import Literal

from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.nodes import (
    planner_node,
    research_node,
    analysis_node,
    fact_checker_node,
    report_writer_node,
)


def route_after_research(
    state: AgentState
) -> Literal["continue", "stop"]:
    """Continue only when research sources are available."""

    if state.get("sources"):
        return "continue"

    return "stop"


def build_workflow():
    """Build and compile the multi-agent research workflow."""

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", research_node)
    graph.add_node("analyst", analysis_node)
    graph.add_node("fact_checker", fact_checker_node)
    graph.add_node("report_writer", report_writer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")

    graph.add_conditional_edges(
        "researcher",
        route_after_research,
        {
            "continue": "analyst",
            "stop": END
        }
    )

    graph.add_edge("analyst", "fact_checker")
    graph.add_edge("fact_checker", "report_writer")
    graph.add_edge("report_writer", END)

    return graph.compile()

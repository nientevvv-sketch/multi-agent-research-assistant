
from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.nodes import (
    planner_node,
    research_node,
    analysis_node,
    fact_checker_node,
    report_writer_node,
)


def build_workflow():
    """Создаёт и компилирует multi-agent workflow."""

    graph = StateGraph(AgentState)

    # Добавляем узлы агентов
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", research_node)
    graph.add_node("analyst", analysis_node)
    graph.add_node("fact_checker", fact_checker_node)
    graph.add_node("report_writer", report_writer_node)

    # Определяем последовательность выполнения
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "fact_checker")
    graph.add_edge("fact_checker", "report_writer")
    graph.add_edge("report_writer", END)

    return graph.compile()

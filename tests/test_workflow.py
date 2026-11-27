
import os
from unittest.mock import patch

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src import workflow


def test_workflow_compiles():
    graph = workflow.build_workflow()

    assert graph is not None


def test_workflow_executes_all_nodes(monkeypatch):
    execution_order = []

    def fake_planner(state):
        execution_order.append("planner")
        return {
            "plan": {
                "goal": "Test",
                "tasks": ["Task 1", "Task 2", "Task 3"]
            }
        }

    def fake_researcher(state):
        execution_order.append("researcher")
        return {
            "research_material": "Research results",
            "sources": [
                {
                    "title": "Test source",
                    "url": "https://example.com",
                    "source_type": "Wikipedia article",
                    "authors": [],
                    "published": "",
                    "content": "Test content"
                }
            ]
        }

    def fake_analyst(state):
        execution_order.append("analyst")
        return {"analysis": "Analysis results"}

    def fake_fact_checker(state):
        execution_order.append("fact_checker")
        return {"fact_check": "Fact check results"}

    def fake_report_writer(state):
        execution_order.append("report_writer")
        return {"final_report": "Final report"}

    monkeypatch.setattr(workflow, "planner_node", fake_planner)
    monkeypatch.setattr(workflow, "research_node", fake_researcher)
    monkeypatch.setattr(workflow, "analysis_node", fake_analyst)
    monkeypatch.setattr(workflow, "fact_checker_node", fake_fact_checker)
    monkeypatch.setattr(workflow, "report_writer_node", fake_report_writer)

    graph = workflow.build_workflow()
    result = graph.invoke({"query": "Test research topic"})

    assert execution_order == [
        "planner",
        "researcher",
        "analyst",
        "fact_checker",
        "report_writer"
    ]

    assert result["final_report"] == "Final report"
    assert result["research_material"] == "Research results"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["title"] == "Test source"


def test_workflow_preserves_user_query(monkeypatch):
    def fake_planner(state):
        return {"plan": {"goal": "Test", "tasks": ["A", "B", "C"]}}

    def fake_researcher(state):
        return {
            "research_material": "Sources",
            "sources": []
        }

    monkeypatch.setattr(workflow, "planner_node", fake_planner)
    monkeypatch.setattr(workflow, "research_node", fake_researcher)

    graph = workflow.build_workflow()
    result = graph.invoke({"query": "My research question"})

    assert result["query"] == "My research question"


def test_workflow_stops_when_no_sources(monkeypatch):
    execution_order = []

    def fake_planner(state):
        execution_order.append("planner")
        return {"plan": {"goal": "Test", "tasks": ["A", "B", "C"]}}

    def fake_researcher(state):
        execution_order.append("researcher")
        return {
            "research_material": "No sources found",
            "sources": []
        }

    def fake_analyst(state):
        execution_order.append("analyst")
        return {"analysis": "Should not execute"}

    def fake_fact_checker(state):
        execution_order.append("fact_checker")
        return {"fact_check": "Should not execute"}

    def fake_report_writer(state):
        execution_order.append("report_writer")
        return {"final_report": "Should not execute"}

    monkeypatch.setattr(workflow, "planner_node", fake_planner)
    monkeypatch.setattr(workflow, "research_node", fake_researcher)
    monkeypatch.setattr(workflow, "analysis_node", fake_analyst)
    monkeypatch.setattr(workflow, "fact_checker_node", fake_fact_checker)
    monkeypatch.setattr(workflow, "report_writer_node", fake_report_writer)

    graph = workflow.build_workflow()
    result = graph.invoke({"query": "Test research topic"})

    assert execution_order == ["planner", "researcher"]
    assert result["sources"] == []
    assert "final_report" not in result

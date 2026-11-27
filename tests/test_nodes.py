
from unittest.mock import patch

from src.nodes import research_node


def test_research_node_uses_planner_tasks():
    state = {
        "query": "AI in finance",
        "plan": {
            "goal": "Study AI in finance",
            "tasks": [
                "AI applications in banking",
                "Machine learning for risk assessment",
                "AI financial forecasting"
            ]
        }
    }

    mock_results = [
        {
            "research_material": f"Results for query {i}",
            "sources": []
        }
        for i in range(4)
    ]

    with patch(
        "src.nodes.researcher.run",
        side_effect=mock_results
    ) as mock_run:
        result = research_node(state)

    assert mock_run.call_count == 4

    expected_queries = [
        "AI in finance",
        "AI applications in banking",
        "Machine learning for risk assessment",
        "AI financial forecasting"
    ]

    actual_queries = [
        call.args[0]
        for call in mock_run.call_args_list
    ]

    assert actual_queries == expected_queries
    assert "Results for query 0" in result["research_material"]
    assert "Results for query 3" in result["research_material"]


def test_research_node_combines_sources():
    state = {
        "query": "AI research",
        "plan": {
            "goal": "Study AI",
            "tasks": ["Task 1", "Task 2", "Task 3"]
        }
    }

    mock_results = [
        {
            "research_material": f"Material {i}",
            "sources": [
                {
                    "title": f"Source {i}",
                    "url": f"https://example.com/{i}",
                    "source_type": "Wikipedia article",
                    "authors": [],
                    "published": "",
                    "content": f"Content {i}"
                }
            ]
        }
        for i in range(4)
    ]

    with patch(
        "src.nodes.researcher.run",
        side_effect=mock_results
    ):
        result = research_node(state)

    assert len(result["sources"]) == 4
    assert result["sources"][0]["title"] == "Source 0"
    assert result["sources"][3]["title"] == "Source 3"

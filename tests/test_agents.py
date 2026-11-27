
import os
import pytest
from unittest.mock import patch

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.agents import ResearchAgent


MOCK_SEARCH_RESULTS = [
    {
        "title": "AI Research",
        "url": "https://example.com/ai",
        "body": "Artificial intelligence research.",
        "source_type": "Wikipedia article"
    },
    {
        "title": "Machine Learning in Finance",
        "url": "https://arxiv.org/abs/2401.12345",
        "body": "A study of machine learning in financial risk.",
        "authors": ["John Smith", "Jane Doe"],
        "published": "2024-01-20T10:00:00Z",
        "source_type": "arXiv research paper"
    }
]


def test_research_agent_returns_response():
    with patch(
        "src.agents.combined_search",
        return_value=MOCK_SEARCH_RESULTS
    ) as mock_search, patch(
        "src.agents.fetch_url",
        return_value="Full page content about AI."
    ) as mock_fetch, patch(
        "src.agents.generate_response",
        return_value="Research result"
    ) as mock_generate:

        agent = ResearchAgent()
        result = agent.run("Study AI")

        assert result["research_material"] == "Research result"
        assert len(result["sources"]) == 2
        assert result["sources"][0]["title"] == "AI Research"
        assert result["sources"][1]["title"] == "Machine Learning in Finance"
        assert result["sources"][1]["authors"] == ["John Smith", "Jane Doe"]

        mock_search.assert_called_once_with(
            "Study AI",
            max_results=3
        )

        mock_fetch.assert_called_once_with(
            "https://example.com/ai",
            max_length=1200
        )

        mock_generate.assert_called_once()


def test_research_agent_rejects_empty_query():
    agent = ResearchAgent()

    with patch("src.agents.combined_search") as mock_search:
        with pytest.raises(ValueError):
            agent.run("")

        with pytest.raises(ValueError):
            agent.run("   ")

        mock_search.assert_not_called()


def test_research_agent_uses_system_prompt():
    with patch(
        "src.agents.combined_search",
        return_value=MOCK_SEARCH_RESULTS
    ), patch(
        "src.agents.fetch_url",
        return_value="AI research description."
    ), patch(
        "src.agents.generate_response",
        return_value="Research response"
    ) as mock_generate:

        agent = ResearchAgent()
        query = "Test query"

        agent.run(query)

        full_prompt = mock_generate.call_args.args[0]

        assert agent.system_prompt in full_prompt
        assert query in full_prompt
        assert "https://example.com/ai" in full_prompt
        assert "AI research description." in full_prompt


def test_research_agent_handles_empty_search_results():
    with patch(
        "src.agents.combined_search",
        return_value=[]
    ), patch(
        "src.agents.fetch_url"
    ) as mock_fetch, patch(
        "src.agents.generate_response",
        return_value="Response without sources"
    ) as mock_generate:

        agent = ResearchAgent()
        result = agent.run("Unknown topic")

        assert result["research_material"] == "Response without sources"
        assert result["sources"] == []

        mock_fetch.assert_not_called()

        full_prompt = mock_generate.call_args.args[0]

        assert "Не удалось получить материалы" in full_prompt


def test_research_agent_uses_search_snippet_if_fetch_fails():
    with patch(
        "src.agents.combined_search",
        return_value=MOCK_SEARCH_RESULTS
    ), patch(
        "src.agents.fetch_url",
        side_effect=RuntimeError("Connection timeout")
    ), patch(
        "src.agents.generate_response",
        return_value="Research response"
    ) as mock_generate:

        agent = ResearchAgent()
        agent.run("Study AI")

        full_prompt = mock_generate.call_args.args[0]

        assert "Artificial intelligence research." in full_prompt
        assert "https://example.com/ai" in full_prompt


def test_research_agent_includes_arxiv_metadata():
    with patch(
        "src.agents.combined_search",
        return_value=MOCK_SEARCH_RESULTS
    ), patch(
        "src.agents.fetch_url"
    ) as mock_fetch, patch(
        "src.agents.generate_response",
        return_value="Research response"
    ) as mock_generate:

        agent = ResearchAgent()
        agent.run("Study financial risks")

        full_prompt = mock_generate.call_args.args[0]

        assert "arXiv research paper" in full_prompt
        assert "John Smith" in full_prompt
        assert "Jane Doe" in full_prompt
        assert "2024-01-20" in full_prompt
        assert "A study of machine learning in financial risk." in full_prompt

        assert mock_fetch.call_count == 1

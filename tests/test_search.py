
from unittest.mock import MagicMock, patch

import pytest

from src.tools.search import web_search, combined_search


@pytest.fixture
def mock_requests_get():
    with patch("src.tools.search.requests.get") as mock:
        yield mock


def test_web_search_success(mock_requests_get):
    mock_response = MagicMock()

    mock_response.json.return_value = {
        "query": {
            "search": [
                {
                    "title": "Python",
                    "snippet": "Python is a programming language."
                },
                {
                    "title": "Software testing",
                    "snippet": "Software testing checks applications."
                }
            ]
        }
    }

    mock_requests_get.return_value = mock_response

    result = web_search("python testing")

    assert len(result) == 2

    assert result[0]["title"] == "Python"
    assert result[0]["url"] == "https://en.wikipedia.org/wiki/Python"
    assert result[0]["body"] == (
        "Python is a programming language."
    )
    assert result[0]["source_type"] == "Wikipedia article"

    mock_requests_get.assert_called_once()

    call_kwargs = mock_requests_get.call_args.kwargs

    assert call_kwargs["params"]["srsearch"] == "python testing"
    assert call_kwargs["params"]["srlimit"] == 5


def test_web_search_empty_results(mock_requests_get):
    mock_response = MagicMock()

    mock_response.json.return_value = {
        "query": {
            "search": []
        }
    }

    mock_requests_get.return_value = mock_response

    result = web_search("nonexistent query 12345")

    assert result == []


def test_web_search_empty_query():
    with pytest.raises(ValueError):
        web_search("")

    with pytest.raises(ValueError):
        web_search("   ")


def test_web_search_invalid_max_results():
    with pytest.raises(ValueError):
        web_search("python", max_results=0)

    with pytest.raises(ValueError):
        web_search("python", max_results=-1)

    with pytest.raises(ValueError):
        web_search("python", max_results=True)


def test_web_search_network_error(mock_requests_get):
    import requests

    mock_requests_get.side_effect = requests.RequestException(
        "Connection timeout"
    )

    with patch("src.tools.search.time.sleep"):
        with pytest.raises(
            RuntimeError,
            match="Ошибка при выполнении веб-поиска"
        ):
            web_search("python")

    assert mock_requests_get.call_count == 3

def test_web_search_invalid_json(mock_requests_get):
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")

    mock_requests_get.return_value = mock_response

    with patch("src.tools.search.time.sleep"):
        with pytest.raises(RuntimeError):
            web_search("python")

    assert mock_requests_get.call_count == 3

def test_combined_search_uses_arxiv_when_wikipedia_fails():
    arxiv_results = [
        {
            "title": "AI Research",
            "url": "https://arxiv.org/abs/1234.5678",
            "body": "Research abstract",
            "source_type": "arXiv research paper"
        }
    ]

    with patch(
        "src.tools.search.web_search",
        side_effect=RuntimeError("Wikipedia unavailable")
    ):
        with patch(
            "src.tools.search.search_arxiv",
            return_value=arxiv_results
        ):
            result = combined_search("AI research")

    assert result == arxiv_results

def test_combined_search_fails_when_all_sources_fail():
    with patch(
        "src.tools.search.web_search",
        side_effect=RuntimeError("Wikipedia unavailable")
    ):
        with patch(
            "src.tools.search.search_arxiv",
            side_effect=RuntimeError("arXiv unavailable")
        ):
            with pytest.raises(
                RuntimeError,
                match="Wikipedia.*arXiv"
            ):
                combined_search("AI research")

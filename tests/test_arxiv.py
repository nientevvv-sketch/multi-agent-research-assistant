
import pytest

from src.tools.arxiv import search_arxiv


def test_search_arxiv_returns_parsed_results(monkeypatch):
    xml_response = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <id>https://arxiv.org/abs/2401.12345</id>
            <title>Financial Risk Management with Machine Learning</title>
            <summary>A study of machine learning in financial risk.</summary>
            <published>2024-01-20T10:00:00Z</published>
            <author>
                <name>John Smith</name>
            </author>
        </entry>
    </feed>
    """

    class MockResponse:
        content = xml_response

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "src.tools.arxiv.requests.get",
        mock_get
    )

    results = search_arxiv("financial risk")

    assert len(results) == 1
    assert results[0]["title"] == (
        "Financial Risk Management with Machine Learning"
    )
    assert results[0]["url"] == (
        "https://arxiv.org/abs/2401.12345"
    )
    assert results[0]["authors"] == ["John Smith"]
    assert results[0]["source_type"] == "arXiv research paper"


def test_search_arxiv_rejects_empty_query():
    with pytest.raises(ValueError):
        search_arxiv("")


def test_search_arxiv_rejects_invalid_max_results():
    with pytest.raises(ValueError):
        search_arxiv("machine learning", max_results=0)


def test_search_arxiv_rejects_boolean_max_results():
    with pytest.raises(ValueError):
        search_arxiv("machine learning", max_results=True)


def test_search_arxiv_handles_request_error(monkeypatch):
    import requests

    def mock_get(*args, **kwargs):
        raise requests.RequestException("Connection failed")

    monkeypatch.setattr(
        "src.tools.arxiv.requests.get",
        mock_get
    )

    with pytest.raises(RuntimeError):
        search_arxiv("financial risk")

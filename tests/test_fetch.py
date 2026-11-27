
import pytest
from unittest.mock import Mock, patch

from src.tools.fetch import fetch_url


def test_fetch_url_extracts_text():
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <header>Header</header>
            <nav>Navigation</nav>
            <h1>Artificial Intelligence</h1>
            <p>AI is transforming technology.</p>
            <script>Some JavaScript</script>
            <footer>Footer</footer>
        </body>
    </html>
    """

    mock_response = Mock()
    mock_response.text = html
    mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_response.raise_for_status.return_value = None

    with patch("src.tools.fetch.requests.get", return_value=mock_response):
        result = fetch_url("https://example.com")

    assert "Artificial Intelligence" in result
    assert "AI is transforming technology." in result
    assert "Some JavaScript" not in result
    assert "Navigation" not in result
    assert "Footer" not in result


def test_fetch_url_respects_max_length():
    html = "<html><body><p>" + ("A" * 1000) + "</p></body></html>"

    mock_response = Mock()
    mock_response.text = html
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status.return_value = None

    with patch("src.tools.fetch.requests.get", return_value=mock_response):
        result = fetch_url("https://example.com", max_length=100)

    assert len(result) <= 100


def test_fetch_url_rejects_invalid_url():
    with pytest.raises(ValueError):
        fetch_url("")

    with pytest.raises(ValueError):
        fetch_url("not-a-url")

    with pytest.raises(ValueError):
        fetch_url("ftp://example.com")


def test_fetch_url_rejects_invalid_max_length():
    with pytest.raises(ValueError):
        fetch_url("https://example.com", max_length=0)

    with pytest.raises(ValueError):
        fetch_url("https://example.com", max_length=-1)

    with pytest.raises(ValueError):
        fetch_url("https://example.com", max_length=True)


def test_fetch_url_handles_network_error():
    with patch(
        "src.tools.fetch.requests.get",
        side_effect=Exception("Connection timeout")
    ):
        with pytest.raises(Exception):
            fetch_url("https://example.com")


def test_fetch_url_rejects_non_html_content():
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_response.raise_for_status.return_value = None

    with patch("src.tools.fetch.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="HTML-страницу"):
            fetch_url("https://example.com/file.pdf")

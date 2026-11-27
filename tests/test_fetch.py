
import pytest
import requests
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
            <style>Some CSS</style>
            <footer>Footer</footer>
        </body>
    </html>
    """

    mock_response = Mock()
    mock_response.text = html
    mock_response.headers = {
        "Content-Type": "text/html; charset=utf-8"
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ):
        result = fetch_url("https://example.com")

    assert "Artificial Intelligence" in result
    assert "AI is transforming technology." in result
    assert "Some JavaScript" not in result
    assert "Some CSS" not in result
    assert "Navigation" not in result
    assert "Footer" not in result
    assert "Header" not in result


def test_fetch_url_respects_max_length():
    html = (
        "<html><body><p>"
        + ("A" * 1000)
        + "</p></body></html>"
    )

    mock_response = Mock()
    mock_response.text = html
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ):
        result = fetch_url(
            "https://example.com",
            max_length=100
        )

    assert len(result) <= 100


def test_fetch_url_rejects_invalid_url():
    invalid_urls = [
        "",
        "   ",
        "not-a-url",
        "ftp://example.com",
        "https://",
        "example.com"
    ]

    for url in invalid_urls:
        with pytest.raises(ValueError):
            fetch_url(url)


def test_fetch_url_rejects_invalid_max_length():
    invalid_values = [
        0,
        -1,
        True,
        1.5,
        "100"
    ]

    for value in invalid_values:
        with pytest.raises(ValueError):
            fetch_url(
                "https://example.com",
                max_length=value
            )


def test_fetch_url_handles_network_error():
    with patch(
        "src.tools.fetch.requests.get",
        side_effect=requests.Timeout("Connection timeout")
    ):
        with pytest.raises(RuntimeError):
            fetch_url("https://example.com")


def test_fetch_url_handles_http_error():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("404 Not Found")
    )

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ):
        with pytest.raises(RuntimeError):
            fetch_url("https://example.com")


def test_fetch_url_rejects_non_html_content():
    mock_response = Mock()
    mock_response.headers = {
        "Content-Type": "application/pdf"
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ):
        with pytest.raises(ValueError):
            fetch_url("https://example.com/file.pdf")


def test_fetch_url_handles_empty_page():
    mock_response = Mock()
    mock_response.text = "<html><body></body></html>"
    mock_response.headers = {
        "Content-Type": "text/html"
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ):
        result = fetch_url("https://example.com")

    assert isinstance(result, str)
    assert result


def test_fetch_url_sends_request_with_timeout():
    mock_response = Mock()
    mock_response.text = "<html><body>Test content</body></html>"
    mock_response.headers = {
        "Content-Type": "text/html"
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.tools.fetch.requests.get",
        return_value=mock_response
    ) as mock_get:
        fetch_url("https://example.com")

    mock_get.assert_called_once()

    call_kwargs = mock_get.call_args.kwargs

    assert call_kwargs["timeout"] == 15
    assert "User-Agent" in call_kwargs["headers"]

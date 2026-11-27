
import os
import pytest
from unittest.mock import MagicMock, patch
from openai import RateLimitError
from openai import AuthenticationError
from openai import APIConnectionError
from openai import APIStatusError

# Подставляем тестовый ключ до импорта llm_client
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.llm_client import generate_response
    from src.config import OPENAI_MODEL


def test_generate_response_returns_text():
    mock_response = MagicMock()
    mock_response.output_text = "Привет! Я искусственный интеллект."

    with patch("src.llm_client.client.responses.create", return_value=mock_response):
        result = generate_response("Привет!")

    assert result == "Привет! Я искусственный интеллект."


def test_generate_response_rejects_empty_prompt():
    with pytest.raises(ValueError):
        generate_response("")

    with pytest.raises(ValueError):
        generate_response("   ")


def test_generate_response_calls_api():
    mock_response = MagicMock()
    mock_response.output_text = "Тестовый ответ"

    with patch(
        "src.llm_client.client.responses.create",
        return_value=mock_response
    ) as mock_create:

        prompt = "Напиши код на Python"
        generate_response(prompt)

        mock_create.assert_called_once_with(
            model=OPENAI_MODEL,
            input=prompt,
	    max_output_tokens=1200
        )
def test_generate_response_rejects_empty_api_response():
    mock_response = MagicMock()
    mock_response.output_text = "   "

    with patch(
        "src.llm_client.client.responses.create",
        return_value=mock_response
    ):
        with pytest.raises(RuntimeError, match="empty response"):
            generate_response("Test prompt")

def test_generate_response_handles_rate_limit_error():
    error = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(),
        body=None
    )

    with patch(
        "src.llm_client.client.responses.create",
        side_effect=error
    ):
        with pytest.raises(RuntimeError, match="rate limit exceeded"):
            generate_response("Test prompt")

def test_generate_response_handles_authentication_error():
    error = AuthenticationError(
        message="Invalid API key",
        response=MagicMock(),
        body=None
    )

    with patch(
        "src.llm_client.client.responses.create",
        side_effect=error
    ):
        with pytest.raises(RuntimeError, match="authentication failed"):
            generate_response("Test prompt")

def test_generate_response_handles_connection_error():
    error = APIConnectionError(request=MagicMock())

    with patch(
        "src.llm_client.client.responses.create",
        side_effect=error
    ):
        with pytest.raises(RuntimeError, match="Could not connect"):
            generate_response("Test prompt")

def test_generate_response_handles_api_status_error():
    mock_response = MagicMock()
    mock_response.status_code = 503

    error = APIStatusError(
        message="Service unavailable",
        response=mock_response,
        body=None
    )

    with patch(
        "src.llm_client.client.responses.create",
        side_effect=error
    ):
        with pytest.raises(RuntimeError, match="HTTP 503"):
            generate_response("Test prompt")
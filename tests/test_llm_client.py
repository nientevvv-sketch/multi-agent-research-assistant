
import os
import pytest
from unittest.mock import MagicMock, patch

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

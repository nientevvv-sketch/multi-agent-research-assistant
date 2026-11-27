
from openai import OpenAI
from src.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_response(prompt: str) -> str:
    """Отправляет запрос модели с ограничением длины ответа."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Запрос (prompt) не может быть пустым.")

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
        max_output_tokens=1200
    )

    return response.output_text

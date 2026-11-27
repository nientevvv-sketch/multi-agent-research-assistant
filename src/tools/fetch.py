
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def fetch_url(url: str, max_length: int = 10000) -> str:
    """
    Загружает веб-страницу и извлекает её текстовое содержимое.
    """

    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL не должен быть пустым.")

    parsed_url = urlparse(url.strip())

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise ValueError("Указан некорректный URL.")

    if (
        isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or max_length <= 0
    ):
        raise ValueError("max_length должен быть положительным целым числом.")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ResearchAssistant/1.0)"
    }

    try:
        response = requests.get(
            url.strip(),
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            raise ValueError("URL не ведёт на HTML-страницу.")

        soup = BeautifulSoup(response.text, "html.parser")

        # Удаляем элементы, которые не содержат полезный текст
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if not text:
            return "На странице не найден текст."

        return text[:max_length]

    except requests.RequestException as error:
        raise RuntimeError(
            f"Ошибка при загрузке страницы: {error}"
        ) from error
 
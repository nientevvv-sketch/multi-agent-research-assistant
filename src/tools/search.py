
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.tools.arxiv import search_arxiv


WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def web_search(query: str, max_results: int = 5) -> list[dict]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым.")

    if (
        isinstance(max_results, bool)
        or not isinstance(max_results, int)
        or max_results <= 0
    ):
        raise ValueError("max_results должен быть положительным целым числом.")

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query.strip(),
        "srlimit": max_results,
        "format": "json"
    }

    headers = {
        "User-Agent": "MultiAgentResearchAssistant/1.0",
        "Accept": "application/json"
    }

    last_error = None

    for attempt in range(1, 4):
        try:
            response = requests.get(
                WIKIPEDIA_API_URL,
                params=params,
                headers=headers,
                timeout=20
            )
            response.raise_for_status()

            data = response.json()
            search_results = data.get("query", {}).get("search", [])

            results = []

            for item in search_results:
                title = item.get("title", "")
                snippet = BeautifulSoup(
                    item.get("snippet", ""),
                    "html.parser"
                ).get_text(" ", strip=True)

                results.append({
                    "title": title,
                    "url": (
                        "https://en.wikipedia.org/wiki/"
                        + quote(title.replace(" ", "_"))
                    ),
                    "body": snippet,
                    "source_type": "Wikipedia article"
                })

            return results

        except (requests.RequestException, ValueError) as error:
            last_error = str(error)

        if attempt < 3:
            time.sleep(attempt * 2)

    raise RuntimeError(
        f"Ошибка при выполнении веб-поиска после 3 попыток: {last_error}"
    )


def combined_search(query: str, max_results: int = 5) -> list[dict]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым.")

    if (
        isinstance(max_results, bool)
        or not isinstance(max_results, int)
        or max_results <= 0
    ):
        raise ValueError("max_results должен быть положительным целым числом.")

    results = []
    errors = []

    try:
        wikipedia_results = web_search(
            query,
            max_results=max_results
        )
        results.extend(wikipedia_results)

    except RuntimeError as error:
        errors.append(f"Wikipedia: {error}")

    try:
        arxiv_results = search_arxiv(
            query,
            max_results=max_results
        )
        results.extend(arxiv_results)

    except RuntimeError as error:
        errors.append(f"arXiv: {error}")

    if not results and errors:
        raise RuntimeError(
            "Не удалось получить результаты ни из одного источника. "
            + " | ".join(errors)
        )

    return results

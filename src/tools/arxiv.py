
import time
import xml.etree.ElementTree as ET

import requests


ARXIV_API_URL = "https://export.arxiv.org/api/query"

ATOM_NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom"
}

_last_request_time = 0.0


def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    global _last_request_time

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым.")

    if (
        isinstance(max_results, bool)
        or not isinstance(max_results, int)
        or max_results <= 0
    ):
        raise ValueError("max_results должен быть положительным целым числом.")

    elapsed = time.monotonic() - _last_request_time

    if elapsed < 3:
        time.sleep(3 - elapsed)

    params = {
        "search_query": f"all:{query.strip()}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }

    headers = {
        "User-Agent": "MultiAgentResearchAssistant/1.0"
    }

    try:
        _last_request_time = time.monotonic()

        response = requests.get(
            ARXIV_API_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        entries = root.findall("atom:entry", ATOM_NAMESPACE)

        results = []

        for entry in entries:
            title = entry.findtext(
                "atom:title",
                default="",
                namespaces=ATOM_NAMESPACE
            ).strip()

            abstract = entry.findtext(
                "atom:summary",
                default="",
                namespaces=ATOM_NAMESPACE
            ).strip()

            url = entry.findtext(
                "atom:id",
                default="",
                namespaces=ATOM_NAMESPACE
            ).strip()

            published = entry.findtext(
                "atom:published",
                default="",
                namespaces=ATOM_NAMESPACE
            ).strip()

            authors = [
                author.findtext(
                    "atom:name",
                    default="",
                    namespaces=ATOM_NAMESPACE
                )
                for author in entry.findall(
                    "atom:author",
                    ATOM_NAMESPACE
                )
            ]

            results.append({
                "title": title,
                "url": url,
                "body": abstract,
                "authors": authors,
                "published": published,
                "source_type": "arXiv research paper"
            })

        return results

    except (requests.RequestException, ET.ParseError) as error:
        raise RuntimeError(
            f"Ошибка при поиске научных публикаций arXiv: {error}"
        ) from error

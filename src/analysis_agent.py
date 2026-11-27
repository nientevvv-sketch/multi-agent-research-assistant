
from src.llm_client import generate_response


class AnalysisAgent:
    def __init__(self):
        self.system_prompt = (
            "Ты — Analysis Agent в системе исследовательских AI-агентов.\n"
            "Твоя задача — анализировать предоставленные исследовательские материалы.\n"
            "В каждом ответе обязательно:\n"
            "1. Выделяй основные факты и закономерности.\n"
            "2. Сравнивай информацию из разных источников.\n"
            "3. Обращай внимание на противоречия и несоответствия.\n"
            "4. Отделяй факты от предположений.\n"
            "5. Формулируй аргументированные выводы.\n"
            "6. Указывай ограничения анализа и недостающие данные.\n"
            "7. При использовании информации указывай номер источника.\n"
            "Не придумывай факты, которых нет в материалах."
        )

    def run(
        self,
        query: str,
        research_material: str,
        sources: list[dict] | None = None
    ) -> str:

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Исследовательский запрос не может быть пустым.")

        if (
            not isinstance(research_material, str)
            or not research_material.strip()
        ):
            raise ValueError("Исследовательские материалы не могут быть пустыми.")

        if sources is None:
            sources = []

        if not isinstance(sources, list):
            raise ValueError("Список источников должен быть списком.")

        formatted_sources = []

        for index, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                continue

            formatted_sources.append(
                f"Источник {index}:\n"
                f"Название: {source.get('title', 'Не указано')}\n"
                f"Тип: {source.get('source_type', 'Не указан')}\n"
                f"URL: {source.get('url', 'Не указан')}\n"
                f"Авторы: {', '.join(source.get('authors', [])) or 'Не указаны'}\n"
                f"Дата публикации: {source.get('published', 'Не указана')}"
            )

        sources_text = (
            "\n\n".join(formatted_sources)
            if formatted_sources
            else "Структурированные источники не предоставлены."
        )

        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"Исследовательский запрос:\n{query.strip()}\n\n"
            f"Материалы для анализа:\n{research_material.strip()}\n\n"
            f"Реестр источников:\n{sources_text}\n\n"
            "Подготовь структурированный аналитический ответ. "
            "Не приписывай источникам информацию, которой они не содержат."
        )

        return generate_response(full_prompt)

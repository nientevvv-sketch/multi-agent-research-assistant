from src.llm_client import generate_response


class ReportWriterAgent:
    """Creates a structured research report."""

    def __init__(self):
        self.system_prompt = (
            "You are a Report Writer Agent in a multi-agent research system.\n"
            "Create a clear, structured research report.\n"
            "Use the following structure:\n"
            "1. Research title\n"
            "2. Research objective\n"
            "3. Key findings\n"
            "4. Analysis\n"
            "5. Fact-checking results\n"
            "6. Sources with titles and URLs\n"
            "7. Research limitations\n"
            "Do not invent facts, figures, or sources.\n"
            "Use only the provided source registry.\n"
            "This agent creates исследовательские отчёты."
        )

    def run(
        self,
        query: str,
        research_material: str,
        analysis: str,
        fact_check: str,
        sources: list[dict] | None = None
    ) -> str:

        inputs = {
            "query": query,
            "research_material": research_material,
            "analysis": analysis,
            "fact_check": fact_check
        }

        error_messages = {
            "query": "Исследовательский запрос не может быть пустым.",
            "research_material": "Исследовательские материалы не могут быть пустыми.",
            "analysis": "Аналитические выводы не могут быть пустыми.",
            "fact_check": "Результаты проверки фактов не могут быть пустыми."
        }

        for name, value in inputs.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(error_messages[name])

        if sources is None:
            sources = []

        if not isinstance(sources, list):
            raise ValueError("Sources must be a list.")

        formatted_sources = []

        for index, source in enumerate(sources[:3], start=1):
            if not isinstance(source, dict):
                continue

            formatted_sources.append(
                f"Source {index}:\n"
                f"Title: {source.get('title', 'Unknown')}\n"
                f"Type: {source.get('source_type', 'Unknown')}\n"
                f"URL: {source.get('url', 'Unknown')}"
            )

        sources_text = (
            "\n\n".join(formatted_sources)
            if formatted_sources
            else "No sources provided."
        )

        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"Research query:\n{query[:500]}\n\n"
            f"Research summary:\n{research_material[:2000]}\n\n"
            f"Analysis:\n{analysis[:3000]}\n\n"
            f"Fact-checking:\n{fact_check[:2000]}\n\n"
            f"Source registry:\n{sources_text}\n\n"
            "Write the final report using the required structure. "
            "Preserve source URLs exactly as provided."
        )

        return generate_response(full_prompt)
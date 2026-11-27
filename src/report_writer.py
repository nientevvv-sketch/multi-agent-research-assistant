
from src.llm_client import generate_response


class ReportWriterAgent:
    """Creates a structured research report."""

    MAX_SOURCES = 6
    MAX_QUERY_LENGTH = 500
    MAX_SUMMARY_LENGTH = 2000
    MAX_ANALYSIS_LENGTH = 3000
    MAX_FACT_CHECK_LENGTH = 2000

    def __init__(self):
        self.system_prompt = (
            "You are a Report Writer Agent. "
            "Create a clear, concise, evidence-based report with these sections: "
            "Research title, Research objective, Key findings, Analysis, "
            "Fact-checking results, Sources, Research limitations. "
            "Use only the provided source registry. "
            "Preserve source URLs exactly. "
            "Never invent facts, figures, or sources. "
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
        """Generate and validate the final research report."""

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

        for index, source in enumerate(
            sources[:self.MAX_SOURCES],
            start=1
        ):
            if not isinstance(source, dict):
                continue

            formatted_sources.append(
                f"Source {index}: "
                f"{source.get('title', 'Unknown')}; "
                f"Type: {source.get('source_type', 'Unknown')}; "
                f"URL: {source.get('url', 'Unknown')}"
            )

        sources_text = (
            "\n".join(formatted_sources)
            if formatted_sources
            else "No sources provided."
        )

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Research query:\n{query[:self.MAX_QUERY_LENGTH]}\n\n"
            f"Research summary:\n"
            f"{research_material[:self.MAX_SUMMARY_LENGTH]}\n\n"
            f"Analysis:\n{analysis[:self.MAX_ANALYSIS_LENGTH]}\n\n"
            f"Fact-checking:\n"
            f"{fact_check[:self.MAX_FACT_CHECK_LENGTH]}\n\n"
            f"Source registry:\n{sources_text}\n\n"
            "Write the final report using all required sections."
        )

        report = generate_response(prompt)

        if not isinstance(report, str) or not report.strip():
            raise ValueError("Generated report is empty.")

        required_sections = [
            "Research title",
            "Research objective",
            "Key findings",
            "Analysis",
            "Fact-checking results",
            "Sources",
            "Research limitations"
        ]

        missing_sections = [
            section
            for section in required_sections
            if section.lower() not in report.lower()
        ]

        if missing_sections:
            raise ValueError(
                f"Report structure is incomplete. "
                f"Missing sections: {missing_sections}"
            )

        return report

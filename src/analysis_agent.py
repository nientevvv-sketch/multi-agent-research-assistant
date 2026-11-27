
from src.llm_client import generate_response


class AnalysisAgent:
    """Analyses research materials and produces evidence-based conclusions."""

    def __init__(self):
        self.system_prompt = (
            "You are an analysis agent. "
            "Identify key facts and patterns, compare sources, "
            "highlight contradictions, and distinguish evidence from assumptions. "
            "Draw reasoned conclusions and state limitations or missing data. "
            "Reference source numbers when available. "
            "Never invent facts or attribute unsupported claims to sources."
        )

    def run(
        self,
        query: str,
        research_material: str,
        sources: list[dict] | None = None
    ) -> str:
        """Analyse research materials and return a structured analysis."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Research query cannot be empty.")

        if (
            not isinstance(research_material, str)
            or not research_material.strip()
        ):
            raise ValueError("Research materials cannot be empty.")

        if sources is None:
            sources = []

        if not isinstance(sources, list):
            raise ValueError("Sources must be a list.")

        formatted_sources = []

        for index, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                continue

            authors = source.get("authors", [])
            if not isinstance(authors, list):
                authors = []

            formatted_sources.append(
                f"Source {index}: "
                f"{source.get('title', 'Unknown')}; "
                f"Type: {source.get('source_type', 'Unknown')}; "
                f"URL: {source.get('url', 'Unknown')}; "
                f"Authors: {', '.join(str(author) for author in authors) or 'Unknown'}; "
                f"Published: {source.get('published', 'Unknown')}"
            )

        sources_text = (
            "\n".join(formatted_sources)
            if formatted_sources
            else "No structured source metadata provided."
        )

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Research question: {query.strip()}\n\n"
            f"Research materials:\n{research_material.strip()}\n\n"
            f"Source registry:\n{sources_text}\n\n"
            "Provide a concise, structured, evidence-based analysis."
        )

        return generate_response(prompt)

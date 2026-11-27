
from datetime import datetime
from pathlib import Path

from src.workflow import build_workflow


ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"


def format_sources(sources: list) -> str:
    """Format research sources as Markdown."""

    if not sources:
        return "No sources were collected."

    formatted_sources = []

    for index, source in enumerate(sources, start=1):
        title = source.get("title", "Untitled source")
        url = source.get("url", "URL unavailable")
        source_type = source.get("source_type", "Unknown source type")
        authors = ", ".join(source.get("authors", []))
        published = source.get("published", "Unknown")

        formatted_sources.append(
            f"### {index}. {title}\n"
            f"- **Type:** {source_type}\n"
            f"- **Authors:** {authors or 'Not specified'}\n"
            f"- **Published:** {published}\n"
            f"- **URL:** {url}\n"
        )

    return "\n".join(formatted_sources)


def save_report(result: dict, query: str) -> Path:
    """Save the research results as a Markdown file."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"research_report_{timestamp}.md"

    plan = result.get("plan") or {}
    tasks = plan.get("tasks", [])

    tasks_text = "\n".join(
        f"{index}. {task}"
        for index, task in enumerate(tasks, start=1)
    )

    if not tasks_text:
        tasks_text = "No research tasks available."

    report = f"""# Research Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Research Question

{query}

## Research Plan

**Goal:** {plan.get("goal", "Not available")}

{tasks_text}

## Research Material

{result.get("research_material", "No research material available.")}

## Analysis

{result.get("analysis", "No analysis available.")}

## Fact-Checking Results

{result.get("fact_check", "No fact-checking results available.")}

## Sources

{format_sources(result.get("sources", []))}

## Final Research Report

{result.get("final_report", "No final report available.")}
"""

    report_path.write_text(report, encoding="utf-8")

    return report_path


def main():
    print("=" * 60)
    print("       MULTI-AGENT RESEARCH ASSISTANT")
    print("=" * 60)

    query = input("\nEnter your research question: ").strip()

    if not query:
        print("\nError: Research question cannot be empty.")
        return

    print("\nStarting research workflow...")
    print("Agents are working. Please wait.\n")

    try:
        workflow = build_workflow()

        initial_state = {
            "query": query,
            "plan": {},
            "research_material": "",
            "sources": [],
            "analysis": "",
            "fact_check": "",
            "final_report": ""
        }

        result = workflow.invoke(initial_state)

        final_report = result.get("final_report", "")

        if not isinstance(final_report, str) or not final_report.strip():
            raise RuntimeError("The workflow returned an empty final report.")

        print("\n" + "=" * 60)
        print("                 FINAL RESEARCH REPORT")
        print("=" * 60)
        print(final_report)

        report_path = save_report(result, query)

        print("\n" + "=" * 60)
        print("REPORT SAVED SUCCESSFULLY")
        print("=" * 60)
        print(f"File: {report_path}")

    except Exception as error:
        print(f"\nWorkflow failed: {error}")


if __name__ == "__main__":
    main()

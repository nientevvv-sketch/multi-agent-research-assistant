
from src.state import AgentState
from src.planner import PlannerAgent
from src.agents import ResearchAgent
from src.analysis_agent import AnalysisAgent
from src.fact_checker import FactCheckerAgent
from src.report_writer import ReportWriterAgent


planner = PlannerAgent()
researcher = ResearchAgent()
analyst = AnalysisAgent()
fact_checker = FactCheckerAgent()
report_writer = ReportWriterAgent()


MAX_TOTAL_SOURCES = 6


def planner_node(state: AgentState) -> dict:
    """Create a research plan."""

    plan = planner.run(state["query"])
    return {"plan": plan}


def research_node(state: AgentState) -> dict:
    """Collect summaries from all queries and deduplicate sources."""

    query = state["query"]
    plan = state["plan"]

    research_queries = [query] + plan["tasks"]

    materials = []
    unique_sources = []
    seen_urls = set()

    for research_query in research_queries:
        result = researcher.run(research_query)

        materials.append(result["research_material"])

        for source in result["sources"]:
            if len(unique_sources) >= MAX_TOTAL_SOURCES:
                break

            url = source.get("url", "").strip()

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            unique_sources.append(source)

    return {
        "research_material": "\n\n".join(materials)[:12000],
        "sources": unique_sources
    }
    for research_query in research_queries:
        result = researcher.run(research_query)

        materials.append(result["research_material"])

        for source in result["sources"]:
            url = source.get("url", "").strip()

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            unique_sources.append(source)

            if len(unique_sources) >= MAX_TOTAL_SOURCES:
                break

        if len(unique_sources) >= MAX_TOTAL_SOURCES:
            break

    return {
        "research_material": "\n\n".join(materials)[:12000],
        "sources": unique_sources
    }


def analysis_node(state: AgentState) -> dict:
    """Analyse collected research material."""

    analysis = analyst.run(
        query=state["query"],
        research_material=state["research_material"],
        sources=state.get("sources", [])
    )

    return {"analysis": analysis}


def fact_checker_node(state: AgentState) -> dict:
    """Verify analytical claims against collected sources."""

    fact_check = fact_checker.run(
        claims=state["analysis"],
        research_material=state["research_material"],
        sources=state.get("sources", [])
    )

    return {"fact_check": fact_check}


def report_writer_node(state: AgentState) -> dict:
    """Generate the final research report."""

    final_report = report_writer.run(
        query=state["query"],
        research_material=state["research_material"],
        analysis=state["analysis"],
        fact_check=state["fact_check"],
        sources=state.get("sources", [])
    )

    return {"final_report": final_report}

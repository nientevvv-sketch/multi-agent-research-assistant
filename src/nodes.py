
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


def planner_node(state: AgentState) -> dict:
    """Создаёт план исследования."""
    plan = planner.run(state["query"])
    return {"plan": plan}




def research_node(state: AgentState) -> dict:
    """Collect research material using the planner's tasks."""

    query = state["query"]
    plan = state["plan"]

    research_queries = [query] + plan["tasks"]

    materials = []
    all_sources = []

    for research_query in research_queries:
        result = researcher.run(research_query)

        materials.append(result["research_material"])
        all_sources.extend(result["sources"])

    research_material = "\n\n".join(materials)

    return {
        "research_material": research_material[:12000],
        "sources": all_sources
    }


    research_queries = [query] + plan["tasks"]
    materials = []

    for research_query in research_queries:
        result = researcher.run(research_query)
        materials.append(result)

    research_material = "\n\n".join(materials)

    # Ограничиваем общий размер исследовательских материалов.
    research_material = research_material[:12000]

    return {"research_material": research_material}

def analysis_node(state: AgentState) -> dict:
    analysis = analyst.run(
        query=state["query"],
        research_material=state["research_material"],
        sources=state.get("sources", [])
    )

    return {"analysis": analysis}


def fact_checker_node(state: AgentState) -> dict:
    fact_check = fact_checker.run(
        claims=state["analysis"],
        research_material=state["research_material"],
        sources=state.get("sources", [])
    )

    return {"fact_check": fact_check}


def report_writer_node(state: AgentState) -> dict:
    final_report = report_writer.run(
        query=state["query"],
        research_material=state["research_material"],
        analysis=state["analysis"],
        fact_check=state["fact_check"],
        sources=state.get("sources", [])
    )

    return {"final_report": final_report}

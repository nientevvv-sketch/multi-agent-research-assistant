
import streamlit as st

from src.workflow import build_workflow
from main import save_report


st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    layout="wide"
)


def initialize_session():
    """Initialize Streamlit session state."""

    if "result" not in st.session_state:
        st.session_state.result = None

    if "query" not in st.session_state:
        st.session_state.query = ""

    if "report_path" not in st.session_state:
        st.session_state.report_path = None


def run_research(query: str):
    """Execute the multi-agent research workflow."""

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

    return workflow.invoke(initial_state)


def main():
    initialize_session()

    st.title("Multi-Agent Research Assistant")

    st.markdown(
        """
        An AI-powered research system built with **LangGraph**
        and the **OpenAI API**.

        Five specialized agents collaborate to research,
        analyse, fact-check and generate structured reports.
        """
    )

    st.divider()

    st.subheader("Research question")

    with st.form("research_form"):
        query = st.text_area(
            "What would you like to research?",
            placeholder=(
                "Example: How is artificial intelligence "
                "transforming financial risk management?"
            ),
            height=120
        )

        submitted = st.form_submit_button(
            "Start research",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not query.strip():
            st.warning("Please enter a research question.")

        else:
            st.session_state.result = None
            st.session_state.report_path = None
            st.session_state.query = query.strip()

            try:
                with st.spinner(
                    "The research workflow is running..."
                ):
                    result = run_research(query.strip())

                    sources = result.get("sources") or []
                    final_report = result.get("final_report", "")

                    if sources:
                        if (
                            not isinstance(final_report, str)
                            or not final_report.strip()
                        ):
                            raise RuntimeError(
                                "The workflow returned an empty report "
                                "despite collecting sources."
                            )

                        report_path = save_report(
                            result,
                            query.strip()
                        )

                        st.session_state.report_path = report_path

                    else:
                        st.session_state.report_path = None

                    st.session_state.result = result

                if sources:
                    st.success("Research completed successfully!")
                else:
                    st.warning(
                        "No sources were collected. "
                        "The remaining agents were skipped to avoid "
                        "unnecessary API calls."
                    )

            except Exception as error:
                st.error(f"Research failed: {error}")

    result = st.session_state.result

    if result:
        st.divider()

        st.header("Research results")

        plan = result.get("plan") or {}
        sources = result.get("sources") or []
        final_report = result.get("final_report", "")

        if not sources:
            st.warning(
                "The research was incomplete because no sources "
                "were collected. Analysis, fact-checking and "
                "report generation were skipped."
            )

        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric("Sources collected", len(sources))

        with metric_col2:
            st.metric(
                "Research tasks",
                len(plan.get("tasks", []))
            )

        (
            tab_report,
            tab_plan,
            tab_research,
            tab_analysis,
            tab_fact,
            tab_sources
        ) = st.tabs(
            [
                "Final report",
                "Research plan",
                "Research material",
                "Analysis",
                "Fact-checking",
                "Sources"
            ]
        )

        with tab_report:
            if final_report:
                st.markdown(final_report)

                report_path = st.session_state.report_path

                if report_path and report_path.exists():
                    report_content = report_path.read_text(
                        encoding="utf-8"
                    )

                    st.download_button(
                        label="Download full research report",
                        data=report_content,
                        file_name=report_path.name,
                        mime="text/markdown",
                        use_container_width=True
                    )

                    st.caption(
                        f"Report saved locally: {report_path}"
                    )
            else:
                st.info(
                    "No final report was generated."
                )

        with tab_plan:
            st.subheader("Research objective")
            st.write(plan.get("goal", "Not available"))

            st.subheader("Research tasks")

            tasks = plan.get("tasks", [])

            if tasks:
                for index, task in enumerate(tasks, start=1):
                    st.write(f"{index}. {task}")
            else:
                st.info("No research tasks available.")

        with tab_research:
            st.markdown(
                result.get(
                    "research_material",
                    "No research material available."
                )
            )

        with tab_analysis:
            analysis = result.get("analysis", "")

            if analysis:
                st.markdown(analysis)
            else:
                st.info("Analysis was not performed.")

        with tab_fact:
            fact_check = result.get("fact_check", "")

            if fact_check:
                st.markdown(fact_check)
            else:
                st.info("Fact-checking was not performed.")

        with tab_sources:
            if sources:
                for index, source in enumerate(sources, start=1):
                    with st.expander(
                        f"{index}. {source.get('title', 'Untitled source')}"
                    ):
                        st.write(
                            f"**Type:** "
                            f"{source.get('source_type', 'Unknown')}"
                        )

                        st.write(
                            f"**Authors:** "
                            f"{', '.join(source.get('authors', [])) or 'Not specified'}"
                        )

                        st.write(
                            f"**Published:** "
                            f"{source.get('published', 'Unknown')}"
                        )

                        st.write(
                            f"**URL:** {source.get('url', 'Unavailable')}"
                        )

                        st.write(source.get("content", ""))
            else:
                st.info("No sources were collected.")

    st.divider()

    st.caption(
        "Multi-Agent Research Assistant | "
        "Built with Python, LangGraph and Streamlit"
    )


if __name__ == "__main__":
    main()

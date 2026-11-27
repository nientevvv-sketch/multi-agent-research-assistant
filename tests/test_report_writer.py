
import os
from unittest.mock import patch

import pytest

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.report_writer import ReportWriterAgent

VALID_REPORT = """
# Research title
AI in Finance

## Research objective
Study AI applications in finance.

## Key findings
AI can support financial analysis.

## Analysis
AI improves automation.

## Fact-checking results
The claim is partially confirmed.

## Sources
No sources provided.

## Research limitations
The findings require further validation.
"""
@pytest.fixture
def writer():
    return ReportWriterAgent()


def test_report_writer_returns_response(writer):
    with patch(
        "src.report_writer.generate_response",
         return_value=VALID_REPORT
    ):
        result = writer.run(
            query="AI in finance",
            research_material="Source: example.com",
            analysis="AI improves automation.",
            fact_check="The claim is partially confirmed."
        )

    assert result == VALID_REPORT


def test_report_writer_rejects_empty_query(writer):
    with pytest.raises(ValueError, match="запрос"):
        writer.run("", "Sources", "Analysis", "Fact check")


def test_report_writer_rejects_empty_research_material(writer):
    with pytest.raises(ValueError, match="материалы"):
        writer.run("AI in finance", "", "Analysis", "Fact check")


def test_report_writer_rejects_empty_analysis(writer):
    with pytest.raises(ValueError, match="выводы"):
        writer.run("AI in finance", "Sources", "", "Fact check")


def test_report_writer_rejects_empty_fact_check(writer):
    with pytest.raises(ValueError, match="проверки фактов"):
        writer.run("AI in finance", "Sources", "Analysis", "")


def test_report_writer_includes_all_inputs(writer):
    with patch(
        "src.report_writer.generate_response",
        return_value=VALID_REPORT
    ) as mock_generate:
        writer.run(
            "AI in finance",
            "Research sources",
            "Analytical conclusions",
            "Fact-check results"
        )

    prompt = mock_generate.call_args[0][0]

    assert "AI in finance" in prompt
    assert "Research sources" in prompt
    assert "Analytical conclusions" in prompt
    assert "Fact-check results" in prompt


def test_report_writer_includes_system_prompt(writer):
    with patch(
        "src.report_writer.generate_response",
        return_value=VALID_REPORT

    ) as mock_generate:
        writer.run(
            "AI in finance",
            "Sources",
            "Analysis",
            "Fact check"
        )

    prompt = mock_generate.call_args[0][0]

    assert "Report Writer Agent" in prompt
    assert "исследовательские отчёты" in prompt

def test_report_writer_rejects_incomplete_report(writer):
    with patch(
        "src.report_writer.generate_response",
        return_value="# Research Report\n\n## Key findings\nSome findings."
    ):
        with pytest.raises(ValueError, match="structure"):
            writer.run(
                query="AI in finance",
                research_material="Research sources",
                analysis="Analytical conclusions",
                fact_check="Fact-check results"
            )

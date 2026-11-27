
import os
import pytest
from unittest.mock import patch

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.analysis_agent import AnalysisAgent


def test_analysis_agent_returns_response():
    with patch(
        "src.analysis_agent.generate_response",
        return_value="Аналитический отчёт"
    ) as mock_generate:

        agent = AnalysisAgent()

        result = agent.run(
            "Исследуй влияние ИИ на финансы",
            "ИИ используется для оценки кредитных рисков."
        )

        assert result == "Аналитический отчёт"
        mock_generate.assert_called_once()


def test_analysis_agent_rejects_empty_query():
    agent = AnalysisAgent()

    with pytest.raises(ValueError):
        agent.run("", "Материалы исследования")

    with pytest.raises(ValueError):
        agent.run("   ", "Материалы исследования")


def test_analysis_agent_rejects_empty_material():
    agent = AnalysisAgent()

    with pytest.raises(ValueError):
        agent.run("Исследуй ИИ", "")

    with pytest.raises(ValueError):
        agent.run("Исследуй ИИ", "   ")


def test_analysis_agent_uses_system_prompt():
    with patch(
        "src.analysis_agent.generate_response",
        return_value="Ответ"
    ) as mock_generate:

        agent = AnalysisAgent()

        query = "Исследуй финансовые технологии"
        materials = "Банки используют ИИ для оценки рисков."

        agent.run(query, materials)

        full_prompt = mock_generate.call_args.args[0]

        assert agent.system_prompt in full_prompt
        assert query in full_prompt
        assert materials in full_prompt


def test_analysis_agent_returns_llm_response():
    expected_response = "Основной вывод: ИИ повышает эффективность анализа."

    with patch(
        "src.analysis_agent.generate_response",
        return_value=expected_response
    ):
        agent = AnalysisAgent()

        result = agent.run(
            "Исследуй ИИ",
            "ИИ помогает анализировать большие объёмы данных."
        )

        assert result == expected_response
 
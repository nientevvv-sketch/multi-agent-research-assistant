
import os
import pytest
from unittest.mock import patch

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.fact_checker import FactCheckerAgent


def test_fact_checker_returns_response():
    with patch(
        "src.fact_checker.generate_response",
        return_value="Утверждение подтверждено источником."
    ) as mock_generate:

        agent = FactCheckerAgent()

        result = agent.run(
            "ИИ используется в банковской сфере.",
            "Источник 1: Банки применяют ИИ для оценки рисков."
        )

        assert result == "Утверждение подтверждено источником."
        mock_generate.assert_called_once()


def test_fact_checker_rejects_empty_claims():
    agent = FactCheckerAgent()

    with pytest.raises(ValueError):
        agent.run("", "Материалы исследования")

    with pytest.raises(ValueError):
        agent.run("   ", "Материалы исследования")


def test_fact_checker_rejects_empty_material():
    agent = FactCheckerAgent()

    with pytest.raises(ValueError):
        agent.run("ИИ используется в банках.", "")

    with pytest.raises(ValueError):
        agent.run("ИИ используется в банках.", "   ")


def test_fact_checker_uses_system_prompt():
    with patch(
        "src.fact_checker.generate_response",
        return_value="Результат проверки"
    ) as mock_generate:

        agent = FactCheckerAgent()

        claims = "ИИ повышает точность оценки рисков."
        materials = "Источник 1: Исследование применения ИИ в банках."

        agent.run(claims, materials)

        full_prompt = mock_generate.call_args.args[0]

        assert agent.system_prompt in full_prompt
        assert claims in full_prompt
        assert materials in full_prompt


def test_fact_checker_returns_llm_response():
    expected_response = (
        "Статус: Частично подтверждено. "
        "Недостаточно данных для окончательного вывода."
    )

    with patch(
        "src.fact_checker.generate_response",
        return_value=expected_response
    ):
        agent = FactCheckerAgent()

        result = agent.run(
            "ИИ снижает финансовые риски на 30%.",
            "Источник 1: ИИ применяется для оценки финансовых рисков."
        )

        assert result == expected_response

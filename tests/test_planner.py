
import os
import json
import pytest
from unittest.mock import patch

with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
    from src.planner import PlannerAgent


MOCK_PLAN = {
    "goal": "Исследовать влияние ИИ на финансы",
    "tasks": [
        "Изучить применение ИИ в банках",
        "Исследовать оценку кредитных рисков",
        "Проанализировать ИИ в инвестициях"
    ]
}


def test_planner_returns_valid_plan():
    with patch(
        "src.planner.generate_response",
        return_value=json.dumps(MOCK_PLAN)
    ) as mock_generate:

        agent = PlannerAgent()
        result = agent.run("Изучи влияние ИИ на финансы")

        assert result["goal"] == MOCK_PLAN["goal"]
        assert result["tasks"] == MOCK_PLAN["tasks"]
        assert len(result["tasks"]) == 3

        mock_generate.assert_called_once()


def test_planner_rejects_empty_query():
    agent = PlannerAgent()

    with pytest.raises(ValueError):
        agent.run("")

    with pytest.raises(ValueError):
        agent.run("   ")


def test_planner_rejects_invalid_json():
    with patch(
        "src.planner.generate_response",
        return_value="Это не JSON"
    ):
        agent = PlannerAgent()

        with pytest.raises(ValueError, match="некорректный JSON"):
            agent.run("Исследуй ИИ")


def test_planner_rejects_invalid_goal():
    invalid_plan = {
        "goal": "",
        "tasks": MOCK_PLAN["tasks"]
    }

    with patch(
        "src.planner.generate_response",
        return_value=json.dumps(invalid_plan)
    ):
        agent = PlannerAgent()

        with pytest.raises(ValueError, match="цель"):
            agent.run("Исследуй ИИ")


def test_planner_rejects_invalid_tasks():
    invalid_plan = {
        "goal": "Исследовать ИИ",
        "tasks": ["Первая задача"]
    }

    with patch(
        "src.planner.generate_response",
        return_value=json.dumps(invalid_plan)
    ):
        agent = PlannerAgent()

        with pytest.raises(ValueError, match="от 3 до 5"):
            agent.run("Исследуй ИИ")


def test_planner_rejects_non_string_tasks():
    invalid_plan = {
        "goal": "Исследовать ИИ",
        "tasks": [
            "Первая задача",
            123,
            "Третья задача"
        ]
    }

    with patch(
        "src.planner.generate_response",
        return_value=json.dumps(invalid_plan)
    ):
        agent = PlannerAgent()

        with pytest.raises(ValueError, match="от 3 до 5"):
            agent.run("Исследуй ИИ")

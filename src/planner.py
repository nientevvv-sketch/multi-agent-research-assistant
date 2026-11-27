
import json

from src.llm_client import generate_response


class PlannerAgent:
    """Агент, который разбивает исследовательский запрос на задачи."""

    def __init__(self):
        self.system_prompt = (
            "Ты — Planner Agent в системе исследовательских AI-агентов.\n"
            "Твоя задача — разбивать сложные запросы на конкретные "
            "исследовательские задачи.\n"
            "Верни результат строго в формате JSON:\n"
            "{\n"
            '  "goal": "Главная цель исследования",\n'
            '  "tasks": [\n'
            '    "Первая задача",\n'
            '    "Вторая задача",\n'
            '    "Третья задача"\n'
            "  ]\n"
            "}\n"
            "Создавай ровно 3 конкретные исследовательские задачи. "
            "Не добавляй Markdown и пояснения вне JSON."
        )

    def run(self, query: str) -> dict:
        """Создаёт план исследования в формате словаря."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Исследовательский запрос не может быть пустым.")

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Запрос пользователя: {query.strip()}"
        )

        response = generate_response(prompt)

        try:
            plan = json.loads(response)

        except json.JSONDecodeError as error:
            raise ValueError(
                "Planner Agent вернул некорректный JSON."
            ) from error

        if not isinstance(plan, dict):
            raise ValueError("План должен быть JSON-объектом.")

        goal = plan.get("goal")
        tasks = plan.get("tasks")

        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("В плане отсутствует корректная цель.")

        if (
            not isinstance(tasks, list)
            or not 3 <= len(tasks) <= 5
            or not all(
                isinstance(task, str) and task.strip()
                for task in tasks
            )
        ):
            raise ValueError("План должен содержать от 3 до 5 задач.")

        return {
            "goal": goal.strip(),
            "tasks": [task.strip() for task in tasks]
        }

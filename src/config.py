import os
from dotenv import load_dotenv

# 1. Загрузка переменных окружения из файла .env
load_dotenv()

# 2. Получение API-ключа и названия модели
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")  # значение по умолчанию, если в .env не указано

# 3. Проверка наличия API-ключа
if not OPENAI_API_KEY:
    raise ValueError("Ошибка: переменная OPENAI_API_KEY не найдена в .env или переменных окружения.")

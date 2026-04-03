import os
from dotenv import load_dotenv
from google import genai
from datetime import datetime, timedelta


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def parse_booking(text: str) -> dict:
    """
    Разбирает текст пользователя и возвращает словарь с данными бронирования.
    Например: {"master": "Иван", "service": "Стрижка", "date": "2026-04-03", "time": "15:00"}
    """

    # Формируем запрос к модели
    prompt = f"""
    Ты помощник барбершопа.

    Доступные мастера: Юлия, Мария

    Извлеки данные и верни JSON:

    {{
      "master": имя мастера из списка или null,
      "service": услуга или null,
      "date_word": сегодня | завтра | послезавтра | null,
      "time": время или null
    }}

    Текст: "{text}"
    """

    # Вызываем модель
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    # Получаем текст ответа
    answer = response.text.strip()

    # Пробуем превратить в dict
    import json
    try:
        booking_data = json.loads(answer)
    except json.JSONDecodeError:
        # Если модель выдала что-то некорректное — возвращаем пустой словарь
        booking_data = {}

    return booking_data

def parse_simple_booking(text: str):
    text = text.lower()

    result = {
        "date": None,
        "master": None,
        "service": None,
        "time": None
    }

    # 📅 ДАТА
    today = datetime.now()

    if "сегодня" in text:
        result["date"] = today.strftime("%Y-%m-%d")

    elif "завтра" in text:
        result["date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    elif "послезавтра" in text:
        result["date"] = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # 👨 МАСТЕРА (впиши своих)
    masters = ["Юлия", "Мария"]

    for m in masters:
        if m in text:
            result["master"] = m.capitalize()

    # 🧾 УСЛУГИ
    services = ["Стрижка мужская", "Стрижка Женская", "Комплекс"]

    for s in services:
        if s in text:
            result["service"] = s.capitalize()

    # ⏰ ВРЕМЯ (ищем 15:00)
    import re
    time_match = re.search(r"\b\d{1,2}:\d{2}\b", text)
    if time_match:
        result["time"] = time_match.group()

    return result
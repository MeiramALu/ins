# webapp/ai_assistant.py
import requests
import json
from .models import Project, Lab, NewsItem

# Твой ключ (убедись, что он из AI Studio, а не Cloud Console)
GENAI_API_KEY = "AIzaSyBd_qeRdyKOOLWg6v2KYxO-DWWdpDBGwqI"


def get_site_context():
    """Собирает информацию о сайте для контекста."""
    context = "Ты — AI-помощник на сайте KAZNU Institute. Твоя цель — помогать посетителям.\n\n"

    # Лаборатории
    labs = Lab.objects.all()
    context += "Лаборатории:\n"
    for lab in labs:
        name = getattr(lab, 'name_ru', lab.name)
        context += f"- {name}\n"

    # Проекты
    projects = Project.objects.all()
    context += "\nПроекты:\n"
    for p in projects:
        p_name = getattr(p, 'name_ru', p.name)
        context += f"- {p_name}\n"

    context += "\nОтвечай кратко и вежливо на русском языке."
    return context


def ask_gemini(user_message):
    """Прямой запрос к Google API через requests (обходит ошибки библиотеки)."""

    # Адрес API (используем модель gemini-1.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GENAI_API_KEY}"
    # Собираем контекст и вопрос
    full_prompt = f"{get_site_context()}\n\nВопрос пользователя: {user_message}"

    # Формируем тело запроса (JSON)
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    try:
        # Отправляем POST запрос
        response = requests.post(url, json=payload, timeout=10)

        # Проверяем статус
        if response.status_code == 200:
            result = response.json()
            # Вытаскиваем текст ответа
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return "ИИ ответил, но формат ответа непонятен."
        else:
            # Если ошибка - возвращаем код ошибки и текст от Google
            return f"Ошибка API ({response.status_code}): {response.text}"

    except Exception as e:
        return f"Ошибка соединения: {e}"
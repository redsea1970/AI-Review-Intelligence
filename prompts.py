# prompts.py
# Промпты проекта AI-Review-Intelligence.
# Формат: словарь с метаданными (модель, дата, автор, версия).

from datetime import date

PROMPTS = {
    "judge_sentiment": {
        "text": (
            "Ты — AI-судья. Оцени качество ИИ-анализа отзыва по шкале 1–5.\n"
            "Критерии:\n"
            "1. Релевантность: анализ относится к тексту отзыва.\n"
            "2. Согласованность: предсказанная тональность не противоречит тексту.\n"
            "3. Формат: ответ — одно слово (positive / negative / neutral).\n"
            "Отзыв: {review}\n"
            "Предсказание ИИ: {prediction}\n"
            "Эталон (если есть): {expected}\n"
            "Верни JSON: {{\"score\": 1-5, \"reason\": \"кратко\"}}"
        ),
        "model": "demo",
        "date_created": str(date.today()),
        "author": "redsea1970",
        "version": "1.0",
        "description": "AI-судья для оценки качества анализа отзывов."
    },
}

def get_prompt(name: str, **kwargs) -> str:
    """Возвращает текст промпта по имени, подставляя параметры."""
    if name not in PROMPTS:
        raise KeyError(f"Промпт '{name}' не найден. Доступны: {list(PROMPTS)}")
    return PROMPTS[name]["text"].format(**kwargs)

"""
Модуль локальной классификации тональности отзывов.

ВАЖНО: это ДЕМОНСТРАЦИОННЫЙ алгоритм на основе словарей ключевых слов,
а НЕ полноценная языковая модель.
"""

POSITIVE_WORDS = {
    "отличный", "отлично", "хороший", "хорошо", "супер", "класс",
    "прекрасный", "прекрасно", "быстро", "удобный", "удобно",
    "рекомендую", "доволен", "довольна", "качественный", "качество",
    "работает", "спасибо", "великолепно", "идеально",
}

NEGATIVE_WORDS = {
    "плохой", "плохо", "ужасный", "ужасно", "отвратительный",
    "сломался", "сломалось", "сломал", "брак", "обман",
    "недоволен", "недовольна", "разочарован", "разочарована",
    "медленно", "долго", "не работает", "не отвечает",
    "возврат", "жалоба", "кошмар", "развод",
}


def _count_matches(text: str, words: set[str]) -> int:
    lowered = text.lower()
    return sum(1 for word in words if word in lowered)


def classify_review(text: str) -> dict:
    pos_score = _count_matches(text, POSITIVE_WORDS)
    neg_score = _count_matches(text, NEGATIVE_WORDS)

    if pos_score > neg_score:
        sentiment = "positive"
        reason = (
            f"Найдено положительных маркеров: {pos_score}, "
            f"отрицательных: {neg_score}. Преобладает положительная оценка."
        )
    elif neg_score > pos_score:
        sentiment = "negative"
        reason = (
            f"Найдено отрицательных маркеров: {neg_score}, "
            f"положительных: {pos_score}. Преобладает недовольство."
        )
    else:
        sentiment = "neutral"
        reason = (
            f"Положительных маркеров: {pos_score}, "
            f"отрицательных: {neg_score}. Явного перевеса нет — оценка нейтральная."
        )

    return {"sentiment": sentiment, "reason": reason}
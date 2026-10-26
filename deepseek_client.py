"""
Клиент для DeepSeek API.

Задача: отправить текст отзыва модели и вернуть строго одну из категорий:
    positive / neutral / negative
плюс краткое объяснение.

ВАЖНО:
- Ключ читается из переменной окружения DEEPSEEK_API_KEY (из .env).
- Настоящий ключ НИКОГДА не пишется в этот файл.
- Любая ошибка сети/API/валидации -> контролируемое исключение DeepSeekError,
  которое вызывающий код (app.py) показывает пользователю.
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

# Загружаем .env один раз при импорте модуля.
load_dotenv()

# --- Параметры API (сверьте с актуальной официальной документацией DeepSeek) ---
# Base URL и имя модели вынесены в переменные окружения, чтобы их было легко
# обновить без правки кода. Значения по умолчанию — заглушки.
DEEPSEEK_BASE_URL = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com",  # <- сверьте с документацией
)
DEEPSEEK_MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-chat",  # <- сверьте с документацией
)
DEEPSEEK_TIMEOUT_SECONDS = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "30"))

ALLOWED_SENTIMENTS = {"positive", "neutral", "negative"}

# Системная инструкция: просим модель вернуть строго JSON заданной формы.
SYSTEM_PROMPT = (
    "Ты — аналитик клиентского опыта. Определи тональность отзыва покупателя. "
    "Ответь СТРОГО валидным JSON без пояснений и без markdown-разметки, "
    'в формате: {"sentiment": "positive|neutral|negative", "reason": "краткое объяснение на русском"}. '
    "sentiment должен быть одним из трёх значений: positive, neutral, negative."
)


class DeepSeekError(Exception):
    """Любая проблема при обращении к DeepSeek API."""


def _get_api_key() -> str:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise DeepSeekError(
            "Ключ DEEPSEEK_API_KEY не найден. Добавьте его в локальный .env."
        )
    return key


def _extract_json(text: str) -> dict[str, Any]:
    """
    Модель должна вернуть JSON, но иногда оборачивает его в ```json ... ```.
    Аккуратно вырезаем JSON-объект.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # убираем первую и последнюю строки с ```
        lines = [ln for ln in cleaned.splitlines() if not ln.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise DeepSeekError(
            f"Не удалось разобрать JSON в ответе модели: {exc}. "
            f"Начало ответа: {cleaned[:200]!r}"
        ) from exc


def _validate_result(data: dict[str, Any]) -> dict[str, str]:
    sentiment = str(data.get("sentiment", "")).strip().lower()
    reason = str(data.get("reason", "")).strip()

    if sentiment not in ALLOWED_SENTIMENTS:
        raise DeepSeekError(
            f"Модель вернула недопустимую категорию: {sentiment!r}. "
            f"Ожидалось одно из: {sorted(ALLOWED_SENTIMENTS)}."
        )
    if not reason:
        raise DeepSeekError("Модель вернула пустое объяснение (reason).")

    return {"sentiment": sentiment, "reason": reason}


def classify_with_deepseek(text: str) -> dict[str, str]:
    """
    Отправляет отзыв в DeepSeek API и возвращает:
        {"sentiment": "positive|neutral|negative", "reason": "..."}

    Бросает DeepSeekError при любой проблеме.
    """
    if not text or not text.strip():
        raise DeepSeekError("Пустой текст отзыва.")

    api_key = _get_api_key()
    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text.strip()},
        ],
        # Просим JSON-режим, если он поддерживается. Если нет — уберём этот блок.
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=DEEPSEEK_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise DeepSeekError(
            f"Тайм-аут при обращении к DeepSeek API ({DEEPSEEK_TIMEOUT_SECONDS} с)."
        ) from exc
    except requests.RequestException as exc:
        raise DeepSeekError(f"Сетевая ошибка при обращении к DeepSeek API: {exc}") from exc

    if response.status_code == 401:
        raise DeepSeekError("DeepSeek API отклонил ключ (401). Проверьте DEEPSEEK_API_KEY.")
    if response.status_code == 402:
        raise DeepSeekError(
            "DeepSeek API: требуется оплата (402). Проверьте баланс в кабинете DeepSeek."
        )
    if response.status_code == 403:
        raise DeepSeekError(
            "DeepSeek API: доступ запрещён (403). Проверьте права ключа и условия аккаунта."
        )
    if response.status_code == 429:
        raise DeepSeekError("DeepSeek API: превышен лимит запросов (429).")
    if response.status_code >= 400:
        raise DeepSeekError(
            f"DeepSeek API вернул ошибку HTTP {response.status_code}."
        )

    try:
        body = response.json()
        content = body["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise DeepSeekError(
            "Неожиданная структура ответа DeepSeek API."
        ) from exc

    data = _extract_json(content)
    return _validate_result(data)
"""
AI Review Intelligence — учебное Streamlit-приложение.

Два режима:
- Локальный алгоритм (classifier.py) — без сети и ключей.
- DeepSeek API (deepseek_client.py) — требует DEEPSEEK_API_KEY в .env.
"""

import streamlit as st

from classifier import classify_review
from deepseek_client import DeepSeekError, classify_with_deepseek

st.set_page_config(
    page_title="AI Review Intelligence",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 AI Review Intelligence")
st.caption(
    "Учебная версия. Локальный режим — демонстрационный алгоритм на ключевых словах. "
    "Режим DeepSeek использует языковую модель через API."
)

# --- Выбор режима ---
mode = st.radio(
    "Режим анализа:",
    options=["Локальный алгоритм", "DeepSeek API"],
    horizontal=True,
)

# --- Ввод отзыва ---
review_text = st.text_area(
    "Введите отзыв покупателя:",
    placeholder="Например: «Отличный товар, всё работает, доставили быстро»",
    height=150,
)

if st.button("Анализировать"):
    if not review_text.strip():
        st.warning("Пожалуйста, введите текст отзыва перед анализом.")
    else:
        result = None

        if mode == "Локальный алгоритм":
            result = classify_review(review_text)
        else:
            with st.spinner("Запрашиваем DeepSeek API…"):
                try:
                    result = classify_with_deepseek(review_text)
                except DeepSeekError as exc:
                    st.error(f"Не удалось получить ответ от DeepSeek API: {exc}")
                except Exception as exc:  # на всякий случай — не роняем приложение
                    st.error(f"Непредвиденная ошибка: {type(exc).__name__}: {exc}")

        if result:
            labels = {
                "positive": ("✅ Положительная", "green"),
                "neutral":  ("⚪ Нейтральная",  "gray"),
                "negative": ("❌ Отрицательная", "red"),
            }
            label, color = labels[result["sentiment"]]

            st.subheader("Результат анализа")
            st.markdown(f"**Тональность:** :{color}[{label}]")
            st.markdown(f"**Объяснение:** {result['reason']}")
            st.caption(f"Техническая категория: `{result['sentiment']}` · Режим: {mode}")
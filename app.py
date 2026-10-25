"""
AI Review Intelligence — учебное Streamlit-приложение.
"""

import streamlit as st
from classifier import classify_review

st.set_page_config(
    page_title="AI Review Intelligence",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 AI Review Intelligence")
st.caption(
    "Учебная версия: тональность определяется локальным демонстрационным "
    "алгоритмом на ключевых словах, а не полноценной языковой моделью."
)

review_text = st.text_area(
    "Введите отзыв покупателя:",
    placeholder="Например: «Отличный товар, всё работает, доставили быстро»",
    height=150,
)

if st.button("Анализировать"):
    if not review_text.strip():
        st.warning("Пожалуйста, введите текст отзыва перед анализом.")
    else:
        result = classify_review(review_text)
        sentiment = result["sentiment"]
        reason = result["reason"]

        labels = {
            "positive": ("✅ Положительная", "green"),
            "neutral":  ("⚪ Нейтральная",  "gray"),
            "negative": ("❌ Отрицательная", "red"),
        }
        label, color = labels[sentiment]

        st.subheader("Результат анализа")
        st.markdown(f"**Тональность:** :{color}[{label}]")
        st.markdown(f"**Объяснение:** {reason}")
        st.caption(f"Техническая категория: `{sentiment}`")
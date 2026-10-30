import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="AI Review Intelligence", page_icon="📊")
st.title("📊 AI Review Intelligence")
st.write("Загрузите CSV с отзывами, и я покажу базовую статистику и ИИ-анализ.")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

def demo_ai_analysis(text):
    """Заглушка ИИ-анализа (демо-режим). В реальности здесь будет вызов API."""
    time.sleep(0.1)  # имитация задержки
    text_lower = text.lower()
    if any(word in text_lower for word in ["отлично", "спасибо", "хорошо", "лучшая", "быстро", "вежлив"]):
        return "positive"
    elif any(word in text_lower for word in ["плохо", "ужас", "поздно", "не то", "сломалось", "разочарован"]):
        return "negative"
    else:
        return "neutral"

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Загруженные данные")
    st.dataframe(df)

    st.subheader("Статистика")
    st.write(f"Всего отзывов: **{len(df)}**")

    if "expected_sentiment" in df.columns:
        counts = df["expected_sentiment"].value_counts()
        st.bar_chart(counts)
        st.write("Распределение тональности (по эталонной разметке):")
        st.write(counts)

    st.subheader("🤖 ИИ-анализ отзывов")
    if st.button("Проанализировать через ИИ"):
        results = []
        progress_bar = st.progress(0)
        for i, row in df.iterrows():
            ai_sentiment = demo_ai_analysis(str(row["review"]))
            expected = row.get("expected_sentiment", "—")
            match = "✅" if ai_sentiment == expected else "❌"
            results.append({
                "id": row["id"],
                "review": row["review"],
                "expected": expected,
                "ai_prediction": ai_sentiment,
                "match": match
            })
            progress_bar.progress((i + 1) / len(df))

        st.success("Анализ завершён!")
        st.dataframe(pd.DataFrame(results))

        # Сводка точности
        if "expected_sentiment" in df.columns:
            correct = sum(1 for r in results if r["match"] == "✅")
            accuracy = correct / len(results) * 100
            st.metric("Точность ИИ (демо)", f"{accuracy:.1f}%")
            st.info("Это демо-режим с простыми правилами. Для реального анализа подключите API нейросети.")

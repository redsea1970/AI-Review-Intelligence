import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Review Intelligence", page_icon="📊")
st.title("📊 AI Review Intelligence")
st.write("Загрузите CSV с отзывами, и я покажу базовую статистику.")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

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
    else:
        st.warning("В файле нет колонки `expected_sentiment` — статистика по тональности недоступна.")

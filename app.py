import streamlit as st
import pandas as pd
import time
import json

from classifier import classify_review
from guardrails import apply_guardrails
from prompts import get_prompt

st.set_page_config(page_title="AI Review Intelligence", page_icon="📊")
st.title("📊 AI Review Intelligence")
st.write("Загрузите CSV с отзывами — покажу статистику, ИИ-анализ и оценку через AI-судью.")


@st.cache_data(show_spinner=False)
def cached_classify(text: str) -> dict:
    """Кэшируем классификацию: повторный анализ того же отзыва не тратит время."""
    time.sleep(0.1)  # имитация задержки вызова модели
    return classify_review(text)


def demo_judge(review: str, prediction: str, expected: str) -> dict:
    """Заглушка AI-судьи: оценивает качество анализа по шкале 1–5.
    В реальности здесь был бы вызов модели с промптом judge_sentiment.
    """
    prompt = get_prompt(
        "judge_sentiment",
        review=review,
        prediction=prediction,
        expected=expected if expected != "—" else "нет",
    )
    # Демо-логика: если предсказание совпало с эталоном — 5, иначе 3, если эталона нет — 4.
    if expected != "—" and prediction == expected:
        score, reason = 5, "Предсказание совпадает с эталоном."
    elif expected != "—" and prediction != expected:
        score, reason = 3, "Предсказание не совпало с эталоном, но формат корректен."
    else:
        score, reason = 4, "Эталона нет, оценка по формату и согласованности."
    return {"score": score, "reason": reason, "prompt_used": prompt[:80] + "..."}


uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file).dropna(how="all")
    st.subheader("Загруженные данные")
    st.dataframe(df)

    st.subheader("Статистика")
    st.write(f"Всего отзывов: **{len(df)}**")

    if "expected_sentiment" in df.columns:
        counts = df["expected_sentiment"].value_counts()
        st.bar_chart(counts)
        st.write("Распределение тональности (по эталонной разметке):")
        st.write(counts)

    tab_analysis, tab_judge = st.tabs(["🤖 ИИ-анализ", "⚖️ AI-судья"])

    with tab_analysis:
        if st.button("Проанализировать через ИИ"):
            results = []
            pii_flagged = 0
            progress_bar = st.progress(0)
            for i, row in df.iterrows():
                review_text = str(row["review"])
                # Guardrails: проверяем PII перед анализом
                gr = apply_guardrails(review_text)
                if gr["has_pii"]:
                    pii_flagged += 1
                    review_text = gr["masked_text"]

                analysis = cached_classify(review_text)
                ai_sentiment = analysis["sentiment"]
                expected = row.get("expected_sentiment", "—")
                match = "✅" if ai_sentiment == expected else "❌"
                results.append({
                    "id": row["id"],
                    "review": review_text,
                    "expected": expected,
                    "ai_prediction": ai_sentiment,
                    "reason": analysis["reason"],
                    "match": match,
                })
                progress_bar.progress(min(1.0, (i + 1) / len(df)))

            st.success("Анализ завершён!")
            if pii_flagged:
                st.warning(f"🛡️ Guardrails: PII обнаружен и замаскирован в {pii_flagged} отзыв(ах).")
            st.dataframe(pd.DataFrame(results))

            if "expected_sentiment" in df.columns:
                correct = sum(1 for r in results if r["match"] == "✅")
                accuracy = correct / len(results) * 100
                st.metric("Точность ИИ (демо)", f"{accuracy:.1f}%")
                st.info("Демо-режим: классификация по словарям, без API. Кэш ускоряет повторные прогоны.")

            st.session_state["last_results"] = results

    with tab_judge:
        st.write("AI-судья оценивает качество каждого анализа по шкале 1–5 (релевантность, согласованность, формат).")
        if st.button("Оценить через AI-судью"):
            results = st.session_state.get("last_results")
            if not results:
                st.warning("Сначала выполните анализ на вкладке «ИИ-анализ».")
            else:
                judged = []
                for r in results:
                    verdict = demo_judge(r["review"], r["ai_prediction"], r["expected"])
                    judged.append({**r, **verdict})
                st.dataframe(pd.DataFrame(judged))
                avg = sum(j["score"] for j in judged) / len(judged)
                st.metric("Средняя оценка судьи", f"{avg:.2f} / 5")
                st.caption("Промпт судьи хранится в prompts.py (см. judge_sentiment).")

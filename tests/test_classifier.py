"""Тесты локального классификатора."""

import pytest

from classifier import classify_review


def test_positive():
    result = classify_review("Отличный товар, всё работает, доставили быстро")
    assert result["sentiment"] == "positive"
    assert result["reason"]


def test_neutral():
    result = classify_review("Обычный товар. Ничего особенного")
    assert result["sentiment"] == "neutral"
    assert result["reason"]


def test_negative():
    result = classify_review("Оборудование сломалось через два дня, поддержка не отвечает")
    assert result["sentiment"] == "negative"
    assert result["reason"]


@pytest.mark.parametrize(
    "text",
    [
        "Отлично",
        "Отлично, быстро, рекомендую, спасибо",
    ],
)
def test_positive_variants(text):
    assert classify_review(text)["sentiment"] == "positive"


@pytest.mark.parametrize(
    "text",
    [
        "Ужасно, сломалось, брак",
        "Медленно, долго, разочарован",
    ],
)
def test_negative_variants(text):
    assert classify_review(text)["sentiment"] == "negative"


def test_result_has_required_keys():
    result = classify_review("Тест")
    assert set(result.keys()) == {"sentiment", "reason"}
    assert result["sentiment"] in {"positive", "neutral", "negative"}
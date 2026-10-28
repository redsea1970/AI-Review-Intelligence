"""Тесты клиента DeepSeek API с моками — без реальных запросов."""

from unittest.mock import Mock, patch

import pytest
import requests

from deepseek_client import DeepSeekError, classify_with_deepseek


def _mock_response(status: int = 200, json_body: dict | None = None):
    r = Mock()
    r.status_code = status
    r.json.return_value = json_body or {}
    return r


@pytest.fixture(autouse=True)
def _fake_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy-key-for-tests")


def test_empty_text_raises():
    with pytest.raises(DeepSeekError, match="Пустой текст"):
        classify_with_deepseek("   ")


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(DeepSeekError, match="DEEPSEEK_API_KEY"):
        classify_with_deepseek("тест")


def test_success_returns_validated_result():
    body = {"choices": [{"message": {"content": "{\"sentiment\": \"positive\", \"reason\": \"ok\"}"}}]}
    with patch("deepseek_client.requests.post", return_value=_mock_response(200, body)):
        result = classify_with_deepseek("Отличный товар")
    assert result == {"sentiment": "positive", "reason": "ok"}


@pytest.mark.parametrize("status", [401, 402, 403, 429])
def test_http_errors(status):
    with patch("deepseek_client.requests.post", return_value=_mock_response(status)):
        with pytest.raises(DeepSeekError, match=str(status)):
            classify_with_deepseek("тест")


def test_timeout():
    with patch("deepseek_client.requests.post", side_effect=requests.Timeout):
        with pytest.raises(DeepSeekError, match="Тайм-аут"):
            classify_with_deepseek("тест")


def test_network_error():
    with patch("deepseek_client.requests.post", side_effect=requests.RequestException("boom")):
        with pytest.raises(DeepSeekError, match="Сетевая ошибка"):
            classify_with_deepseek("тест")


def test_invalid_category_rejected():
    body = {"choices": [{"message": {"content": "{\"sentiment\": \"weird\", \"reason\": \"x\"}"}}]}
    with patch("deepseek_client.requests.post", return_value=_mock_response(200, body)):
        with pytest.raises(DeepSeekError, match="недопустимую категорию"):
            classify_with_deepseek("тест")


def test_invalid_json_rejected():
    body = {"choices": [{"message": {"content": "not a json"}}]}
    with patch("deepseek_client.requests.post", return_value=_mock_response(200, body)):
        with pytest.raises(DeepSeekError, match="JSON"):
            classify_with_deepseek("тест")


def test_empty_reason_rejected():
    body = {"choices": [{"message": {"content": "{\"sentiment\": \"positive\", \"reason\": \"\"}"}}]}
    with patch("deepseek_client.requests.post", return_value=_mock_response(200, body)):
        with pytest.raises(DeepSeekError, match="пустое объяснение"):
            classify_with_deepseek("тест")


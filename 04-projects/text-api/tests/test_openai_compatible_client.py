"""OpenAI 兼容客户端测试。

这些测试主要验证两件事：
1. 成功请求时会留下最小成功日志；
2. 请求失败时会留下失败日志并继续抛出异常。
"""

import logging

import pytest
import requests

from app import openai_compatible_client


class _FakeSuccessResponse:
    """用于模拟成功 HTTP 响应的最小假对象。"""

    status_code = 200

    def raise_for_status(self) -> None:
        """成功响应不抛异常。"""

    def json(self) -> dict:
        """返回一份最小可解析的上游成功响应。"""

        return {"id": "resp_123", "model": "test-model", "choices": []}


def test_chat_completion_logs_success(monkeypatch, caplog) -> None:
    """确认成功调用会记录发送日志和成功日志。"""

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setattr(openai_compatible_client.requests, "post", lambda *args, **kwargs: _FakeSuccessResponse())

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with caplog.at_level(logging.INFO):
        result = openai_compatible_client.chat_completion(payload)

    assert result["id"] == "resp_123"
    assert "Sending upstream chat completion request" in caplog.text
    assert "Upstream chat completion request succeeded" in caplog.text


def test_chat_completion_logs_failure(monkeypatch, caplog) -> None:
    """确认请求失败时会记录异常日志并继续抛错。"""

    def fake_post(*args, **kwargs):
        raise requests.Timeout("request timed out")

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请提取要点"}],
    }

    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.Timeout):
            openai_compatible_client.chat_completion(payload)

    assert "Upstream chat completion request failed" in caplog.text

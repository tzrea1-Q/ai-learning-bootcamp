"""MiniMax 客户端测试。

这些测试主要验证两件事：
1. 成功请求时会留下最小成功日志；
2. 请求失败时会留下失败日志并继续抛出异常。
"""

import logging

import pytest
import requests

from app import minimax_client


class _FakeSuccessResponse:
    """用于模拟成功 HTTP 响应的最小假对象。"""

    status_code = 200

    def raise_for_status(self) -> None:
        """成功响应不抛异常。"""

    def json(self) -> dict:
        """返回一份最小可解析的 MiniMax 成功响应。"""

        return {"id": "resp_123", "model": "MiniMax-M2.7", "choices": []}


def test_minimax_chat_logs_success(monkeypatch, caplog) -> None:
    """确认成功调用会记录发送日志和成功日志。"""

    monkeypatch.setattr(minimax_client, "API_KEY", "test-key")
    monkeypatch.setattr(minimax_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setattr(minimax_client.requests, "post", lambda *args, **kwargs: _FakeSuccessResponse())

    payload = {
        "model": "MiniMax-M2.7",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with caplog.at_level(logging.INFO):
        result = minimax_client.minimax_chat(payload)

    assert result["id"] == "resp_123"
    assert "Sending MiniMax request" in caplog.text
    assert "MiniMax request succeeded" in caplog.text


def test_minimax_chat_logs_failure(monkeypatch, caplog) -> None:
    """确认请求失败时会记录异常日志并继续抛错。"""

    def fake_post(*args, **kwargs):
        raise requests.Timeout("request timed out")

    monkeypatch.setattr(minimax_client, "API_KEY", "test-key")
    monkeypatch.setattr(minimax_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setattr(minimax_client.requests, "post", fake_post)

    payload = {
        "model": "MiniMax-M2.7",
        "messages": [{"role": "user", "content": "请提取要点"}],
    }

    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.Timeout):
            minimax_client.minimax_chat(payload)

    assert "MiniMax request failed" in caplog.text

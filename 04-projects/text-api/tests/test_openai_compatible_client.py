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

    captured = {}

    def fake_post(*args, **kwargs):
        captured.update(kwargs)
        return _FakeSuccessResponse()

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.delenv("UPSTREAM_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("UPSTREAM_RETRY_ATTEMPTS", raising=False)
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with caplog.at_level(logging.INFO):
        result = openai_compatible_client.chat_completion(
            payload,
            request_id="req-client-123",
            path="/summarize",
            task="summarize",
        )

    assert result["id"] == "resp_123"
    assert "Sending upstream chat completion request" in caplog.text
    assert "Upstream chat completion request succeeded" in caplog.text
    assert "request_id=req-client-123" in caplog.text
    assert "path=/summarize" in caplog.text
    assert "task=summarize" in caplog.text
    assert "timeout_seconds=60.0" in caplog.text
    assert "attempt=1/2" in caplog.text
    assert captured["timeout"] == 60.0


def test_chat_completion_logs_failure(monkeypatch, caplog) -> None:
    """确认请求失败时会记录异常日志并继续抛错。"""

    def fake_post(*args, **kwargs):
        raise requests.Timeout("request timed out")

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_RETRY_ATTEMPTS", "0")
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请提取要点"}],
    }

    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.Timeout):
            openai_compatible_client.chat_completion(
                payload,
                request_id="req-client-502",
                path="/key-points",
                task="key-points",
            )

    assert "Upstream chat completion request failed" in caplog.text
    assert "request_id=req-client-502" in caplog.text
    assert "path=/key-points" in caplog.text
    assert "task=key-points" in caplog.text
    assert "attempt=1/1" in caplog.text


def test_chat_completion_uses_configured_timeout(monkeypatch) -> None:
    """确认上游请求超时可通过环境变量覆盖。"""

    captured = {}

    def fake_post(*args, **kwargs):
        captured.update(kwargs)
        return _FakeSuccessResponse()

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_TIMEOUT_SECONDS", "7.5")
    monkeypatch.setenv("UPSTREAM_RETRY_ATTEMPTS", "0")
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    result = openai_compatible_client.chat_completion(payload)

    assert result["id"] == "resp_123"
    assert captured["timeout"] == 7.5


def test_chat_completion_rejects_invalid_timeout(monkeypatch) -> None:
    """确认非法超时配置会作为本地配置错误暴露出来。"""

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_TIMEOUT_SECONDS", "0")

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with pytest.raises(ValueError, match="UPSTREAM_TIMEOUT_SECONDS must be a positive number"):
        openai_compatible_client.chat_completion(payload)


def test_chat_completion_retries_once_on_timeout(monkeypatch, caplog) -> None:
    """确认连接失败或读超时时会触发有限重试。"""

    call_count = {"count": 0}

    def fake_post(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise requests.Timeout("read timed out")
        return _FakeSuccessResponse()

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_RETRY_ATTEMPTS", "1")
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with caplog.at_level(logging.INFO):
        result = openai_compatible_client.chat_completion(
            payload,
            request_id="req-retry-001",
            path="/summarize",
            task="summarize",
        )

    assert result["id"] == "resp_123"
    assert call_count["count"] == 2
    assert "Retrying upstream chat completion request" in caplog.text
    assert "retryable_error=Timeout" in caplog.text
    assert "attempt=1/2" in caplog.text
    assert "attempt=2/2" in caplog.text


def test_chat_completion_does_not_retry_http_error(monkeypatch, caplog) -> None:
    """确认上游 HTTP 错误不会进入有限重试。"""

    call_count = {"count": 0}

    class _FakeHttpErrorResponse:
        status_code = 502

        def raise_for_status(self) -> None:
            raise requests.HTTPError("502 upstream bad gateway")

        def json(self) -> dict:
            return {}

    def fake_post(*args, **kwargs):
        call_count["count"] += 1
        return _FakeHttpErrorResponse()

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_RETRY_ATTEMPTS", "1")
    monkeypatch.setattr(openai_compatible_client.requests, "post", fake_post)

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请提取要点"}],
    }

    with caplog.at_level(logging.ERROR):
        with pytest.raises(requests.HTTPError):
            openai_compatible_client.chat_completion(
                payload,
                request_id="req-no-retry-502",
                path="/key-points",
                task="key-points",
            )

    assert call_count["count"] == 1
    assert "Retrying upstream chat completion request" not in caplog.text


def test_chat_completion_rejects_invalid_retry_attempts(monkeypatch) -> None:
    """确认非法重试配置会作为本地配置错误暴露出来。"""

    monkeypatch.setattr(openai_compatible_client, "API_KEY", "test-key")
    monkeypatch.setattr(openai_compatible_client, "BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setenv("UPSTREAM_RETRY_ATTEMPTS", "-1")

    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "请总结这段内容"}],
    }

    with pytest.raises(ValueError, match="UPSTREAM_RETRY_ATTEMPTS must be a non-negative integer"):
        openai_compatible_client.chat_completion(payload)

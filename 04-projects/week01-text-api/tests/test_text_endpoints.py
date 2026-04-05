"""文本处理接口测试。

这些测试覆盖 6 类核心场景：
1. 正常总结；
2. 正常提取要点；
3. 正常改写；
4. 非法输入校验；
5. 统一错误响应格式；
6. 上游配置错误和上游异常的暴露方式。
"""

from uuid import UUID

from requests import RequestException

from fastapi.testclient import TestClient

from app import main


def assert_has_request_id(payload: dict) -> None:
    """确保统一错误响应里带有可解析的 request_id。"""

    request_id = payload.get("request_id")
    assert isinstance(request_id, str)
    assert request_id
    assert str(UUID(request_id)) == request_id


def test_summarize_returns_cleaned_result(monkeypatch, client: TestClient) -> None:
    """确认总结接口会清理 `<think>` 片段并返回统一响应结构。"""

    def fake_minimax_chat(payload: dict) -> dict:
        # 这里先校验 payload 是否按预期构造。
        # 如果 prompt 或 model 被误改，这个测试会第一时间失败。
        assert payload["model"] == "MiniMax-M2.7"
        assert payload["messages"][1]["content"].startswith("请用中文输出 2 到 3 句话总结下面的内容")
        return {
            "choices": [
                {
                    "message": {
                        "content": "<think>\ninternal reasoning\n</think>\n\n这是压缩后的总结。",
                    }
                }
            ]
        }

    # 用 monkeypatch 替换真实外部调用，保证测试稳定且不依赖网络。
    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/summarize", json={"text": "FastAPI 可以快速构建接口。"})

    assert response.status_code == 200
    assert response.json() == {
        "task": "summarize",
        "result": "这是压缩后的总结。",
        "model": "MiniMax-M2.7",
    }


def test_key_points_returns_bullets(monkeypatch, client: TestClient) -> None:
    """确认要点提取接口能返回列表风格的结果。"""

    def fake_minimax_chat(payload: dict) -> dict:
        # 这里检查的是“任务语义”而不是完整 prompt 文本，
        # 这样既能保证方向正确，也不会让测试对文案细节过度脆弱。
        assert "关键要点" in payload["messages"][1]["content"]
        return {
            "choices": [
                {
                    "message": {
                        "content": "- 要点一\n- 要点二\n- 要点三",
                    }
                }
            ]
        }

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/key-points", json={"text": "FastAPI 支持类型提示、自动文档和高性能。"})

    assert response.status_code == 200
    assert response.json()["task"] == "key-points"
    assert response.json()["result"] == "- 要点一\n- 要点二\n- 要点三"


def test_rewrite_returns_polished_text(monkeypatch, client: TestClient) -> None:
    """确认改写接口能返回一段更自然的重写文本。"""

    def fake_minimax_chat(payload: dict) -> dict:
        # 这里检查 prompt 已切到“改写”任务，避免错误复用其他接口的模板。
        assert "改写下面内容" in payload["messages"][1]["content"]
        assert "不要添加标题" in payload["messages"][1]["content"]
        assert "长度尽量控制在原文的 0.8 到 1.3 倍" in payload["messages"][1]["content"]
        return {
            "choices": [
                {
                    "message": {
                        "content": "FastAPI 可以帮助开发者更高效地构建清晰、可靠的 API 服务。",
                    }
                }
            ]
        }

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/rewrite", json={"text": "FastAPI 可以更快做 API。"})

    assert response.status_code == 200
    assert response.json() == {
        "task": "rewrite",
        "result": "FastAPI 可以帮助开发者更高效地构建清晰、可靠的 API 服务。",
        "model": "MiniMax-M2.7",
    }


def test_rewrite_strips_heading_and_leading_label(monkeypatch, client: TestClient) -> None:
    """确认 rewrite 输出会去掉自动标题和“改写后”之类的前缀。"""

    def fake_minimax_chat(payload: dict) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": "改写建议\n改写后：这个功能不要一开始做得太复杂，先把最小闭环跑通。",
                    }
                }
            ]
        }

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/rewrite", json={"text": "这个功能先别做太复杂，先把最小闭环跑通。"})

    assert response.status_code == 200
    assert response.json()["result"] == "这个功能不要一开始做得太复杂，先把最小闭环跑通。"


def test_text_endpoints_reject_blank_text(client: TestClient) -> None:
    """确认空白文本会被 Pydantic 校验拦下。"""

    response = client.post("/summarize", json={"text": "   "})

    # 当前实现使用字段校验器抛错，FastAPI 最终会返回 422。
    assert response.status_code == 422


def test_text_endpoints_reject_overlong_text(client: TestClient) -> None:
    """确认超长文本会被输入边界约束拦下。"""

    response = client.post("/summarize", json={"text": "a" * (main.MAX_TEXT_LENGTH + 1)})

    assert response.status_code == 422
    assert "at most" in response.text


def test_text_endpoints_surface_upstream_errors(monkeypatch, client: TestClient) -> None:
    """确认上游配置错误会被转换成统一的 500 错误结构。"""

    def fake_minimax_chat(payload: dict) -> dict:
        # 模拟本地配置缺失等非网络类错误。
        raise ValueError("MINIMAX_API_KEY is not set")

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/key-points", json={"text": "需要提炼的信息"})

    assert response.status_code == 500
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert_has_request_id(payload)
    assert response.headers["X-Request-ID"] == payload["request_id"]
    assert payload == {
        "code": "SERVER_MISCONFIGURED",
        "message": "Local service configuration is invalid",
        "detail": "MINIMAX_API_KEY is not set",
        "request_id": payload["request_id"],
    }


def test_text_endpoints_return_unified_502_on_request_failure(monkeypatch, client: TestClient) -> None:
    """确认 requests 层异常会被转换成统一的 502 错误结构。"""

    def fake_minimax_chat(payload: dict) -> dict:
        raise RequestException("request timed out")

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/summarize", json={"text": "需要总结的信息"})

    assert response.status_code == 502
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert_has_request_id(payload)
    assert response.headers["X-Request-ID"] == payload["request_id"]
    assert payload == {
        "code": "UPSTREAM_REQUEST_FAILED",
        "message": "MiniMax request failed",
        "detail": "request timed out",
        "request_id": payload["request_id"],
    }


def test_text_endpoints_return_unified_502_on_invalid_response(monkeypatch, client: TestClient) -> None:
    """确认上游返回结构异常时会走统一的 502 错误结构。"""

    def fake_minimax_chat(payload: dict) -> dict:
        return {"choices": []}

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/key-points", json={"text": "需要提炼的信息"})

    assert response.status_code == 502
    assert response.headers["X-Request-ID"]
    payload = response.json()
    assert_has_request_id(payload)
    assert response.headers["X-Request-ID"] == payload["request_id"]
    assert payload == {
        "code": "UPSTREAM_INVALID_RESPONSE",
        "message": "MiniMax returned an unexpected response",
        "detail": "choices[0].message.content is missing or malformed",
        "request_id": payload["request_id"],
    }

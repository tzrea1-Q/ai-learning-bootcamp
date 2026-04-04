"""文本处理接口测试。

这些测试覆盖 5 类核心场景：
1. 正常总结；
2. 正常提取要点；
3. 正常改写；
4. 非法输入校验；
5. 上游配置错误向外暴露的方式。
"""

from fastapi.testclient import TestClient

from app import main


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


def test_text_endpoints_reject_blank_text(client: TestClient) -> None:
    """确认空白文本会被 Pydantic 校验拦下。"""

    response = client.post("/summarize", json={"text": "   "})

    # 当前实现使用字段校验器抛错，FastAPI 最终会返回 422。
    assert response.status_code == 422


def test_text_endpoints_surface_upstream_errors(monkeypatch, client: TestClient) -> None:
    """确认上游配置错误会被转换成 500，而不是默默吞掉。"""

    def fake_minimax_chat(payload: dict) -> dict:
        # 模拟本地配置缺失等非网络类错误。
        raise ValueError("MINIMAX_API_KEY is not set")

    monkeypatch.setattr(main, "minimax_chat", fake_minimax_chat)

    response = client.post("/key-points", json={"text": "需要提炼的信息"})

    assert response.status_code == 500
    assert response.json() == {"detail": "MINIMAX_API_KEY is not set"}

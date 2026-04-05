"""健康检查接口测试。"""

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """确认 `/health` 在最小场景下可正常响应。

    这个测试的价值很基础，但很必要：
    - 能证明 FastAPI 应用本身能启动；
    - 能证明最小路由注册没有被后续改动破坏；
    - 当更复杂接口失败时，可以先用它判断是不是整个服务都挂了。
    """

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

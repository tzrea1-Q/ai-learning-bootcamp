"""pytest 共享测试夹具。

凡是多个测试文件都会重复用到的初始化逻辑，都应该集中放在这里。
当前只放了一个 `TestClient` fixture，后续如果增加假数据、临时配置或
mock 依赖，也优先放在本文件统一管理。
"""

from pathlib import Path
import sys

# 把项目根目录加入 Python 模块搜索路径，确保 pytest 在仓库根外执行时，
# 也能稳定导入 `app.main`。
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """返回一个绑定到 FastAPI 应用的测试客户端。

    各测试文件通过注入 `client` fixture，就可以直接发 HTTP 请求，
    不需要每个文件都重复创建 `TestClient(app)`。
    """

    return TestClient(app)

"""最小化的 OpenAI 兼容接口连通性验证脚本。

这个脚本的用途不是跑自动化测试，而是人工快速确认三件事：
1. 本地 `.env` 是否生效；
2. API Key / Base URL 是否可用；
3. 上游兼容接口是否能返回一份结构正确的响应。
"""

from pathlib import Path
import sys

# 把项目根目录加入 `sys.path`，这样脚本可以直接复用 `app.openai_compatible_client`。
# 否则从 `scripts/` 目录直接运行时，Python 默认找不到 `app` 包。
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.openai_compatible_client import DEFAULT_MODEL, chat_completion

# 使用一份足够简单的请求体验证“调用链是否打通”。
# 这里不追求复杂 prompt，只追求能稳定拿到一个最小成功响应。
payload = {
    "model": DEFAULT_MODEL,
    "messages": [
        {"role": "system", "content": "你是一个简洁的中文助手。"},
        {"role": "user", "content": "请用一句话解释什么是 FastAPI。"},
    ],
}

result = chat_completion(payload)
print(result)

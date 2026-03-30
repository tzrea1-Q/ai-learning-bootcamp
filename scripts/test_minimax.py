from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.minimax_client import minimax_chat

payload = {
    "model": "MiniMax-M2.7",
    "messages": [
        {"role": "system", "content": "你是一个简洁的中文助手。"},
        {"role": "user", "content": "请用一句话解释什么是 FastAPI。"},
    ],
}

result = minimax_chat(payload)
print(result)

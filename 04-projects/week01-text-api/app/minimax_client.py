"""MiniMax API 客户端封装。

这个模块只负责“如何请求 MiniMax”，不负责业务任务拆分。
这样做的目的是把 HTTP 通信细节和 FastAPI endpoint 逻辑分开：
1. `app/main.py` 只关心任务类型、输入输出和错误映射。
2. `app/minimax_client.py` 只关心鉴权、URL 拼接、请求发送和最小日志留痕。
"""

import logging
import os

import requests
from dotenv import load_dotenv

# 在模块导入时加载 `.env`，这样无论是 API 服务还是单独运行脚本，
# 只要当前工作目录下存在 `.env`，都能拿到本地配置。
load_dotenv()

# 从环境变量中读取 API Key、Base URL 和日志级别。
# 这里在导入阶段读取即可，因为当前项目还没有做运行时动态切换配置的需求。
API_KEY = os.getenv("MINIMAX_API_KEY")
BASE_URL = os.getenv("MINIMAX_BASE_URL")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# 这是当前项目的最小日志初始化：
# - 如果根 logger 还没有 handler，就按环境变量配置一个基础 handler；
# - 如果外部进程已经初始化过 logging，就直接复用，不重复覆盖。
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

LOGGER = logging.getLogger(__name__)


def _chat_completions_url() -> str:
    """生成最终的 Chat Completions 请求地址。

    支持两种输入形式：
    1. `MINIMAX_BASE_URL=https://api.minimaxi.com/v1`
    2. `MINIMAX_BASE_URL=https://api.minimaxi.com/v1/chat/completions`

    这样配置更宽容，避免因为 base URL 是否带完整路径而频繁改代码。
    """

    if not BASE_URL:
        raise ValueError("MINIMAX_BASE_URL is not set")

    # 去掉结尾斜杠，避免后续拼接时出现双斜杠。
    url = BASE_URL.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    return f"{url}/chat/completions"


def _payload_summary(payload: dict) -> dict:
    """提取一份安全、精简的 payload 摘要用于日志输出。

    这里刻意不直接打印完整原文，避免把用户输入全文打进日志。
    当前只记录排查所需的最小维度：
    - model
    - message_count
    - user_prompt_preview（截断后的首段）
    """

    messages = payload.get("messages", [])
    user_message = ""

    if isinstance(messages, list) and messages:
        last_message = messages[-1]
        if isinstance(last_message, dict):
            user_message = str(last_message.get("content", ""))

    return {
        "model": payload.get("model"),
        "message_count": len(messages) if isinstance(messages, list) else 0,
        "user_prompt_preview": user_message[:80],
    }


def minimax_chat(payload: dict) -> dict:
    """向 MiniMax 发送一次 chat completions 请求。

    参数：
    - payload: 已经准备好的请求体，通常由上层业务函数构造。

    返回：
    - 上游返回的 JSON 字典。

    这里不吞掉 `requests` 异常，原因是：
    - 底层网络错误应该继续向上抛；
    - 由 FastAPI 层统一决定应该返回 500、502 还是别的状态码。
    """

    if not API_KEY:
        raise ValueError("MINIMAX_API_KEY is not set")

    url = _chat_completions_url()
    payload_summary = _payload_summary(payload)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # 在请求发出前留一条最小 info 日志，帮助排查“是否真的发起了调用”。
    LOGGER.info("Sending MiniMax request: url=%s payload=%s", url, payload_summary)

    try:
        # 当前先使用固定 60 秒超时，避免请求无限挂起。
        # 后续如果项目变大，可以把超时也抽成配置项。
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        # 失败时记录异常堆栈和请求摘要，方便后续定位是网络问题、鉴权问题还是上游问题。
        LOGGER.exception("MiniMax request failed: url=%s payload=%s", url, payload_summary)
        raise

    # 成功时记录最小成功信息，便于后续对照真实返回是否异常。
    LOGGER.info(
        "MiniMax request succeeded: status_code=%s response_id=%s model=%s",
        response.status_code,
        data.get("id"),
        data.get("model"),
    )
    return data

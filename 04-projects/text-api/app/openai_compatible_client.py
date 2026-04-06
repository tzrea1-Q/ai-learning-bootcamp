"""OpenAI 兼容 Chat Completions 客户端封装。

这个模块只负责“如何请求上游兼容接口”，不负责业务任务拆分。
这样做的目的是把 HTTP 通信细节和 FastAPI endpoint 逻辑分开：
1. `app/main.py` 只关心任务类型、输入输出和错误映射。
2. `app/openai_compatible_client.py` 只关心鉴权、URL 拼接、请求发送和最小日志留痕。
"""

import logging
import os

import requests
from dotenv import load_dotenv

# 在模块导入时加载 `.env`，这样无论是 API 服务还是单独运行脚本，
# 只要当前工作目录下存在 `.env`，都能拿到本地配置。
load_dotenv()

# 从环境变量中读取 API Key、Base URL、模型名和日志级别。
# 当前优先使用通用命名，同时兼容旧的 `MINIMAX_*` 变量，避免已有本地环境立刻失效。
API_KEY = os.getenv("UPSTREAM_API_KEY") or os.getenv("MINIMAX_API_KEY")
BASE_URL = os.getenv("UPSTREAM_BASE_URL") or os.getenv("MINIMAX_BASE_URL")
DEFAULT_MODEL = os.getenv("UPSTREAM_MODEL") or os.getenv("MINIMAX_MODEL") or "MiniMax-M2.7"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEFAULT_UPSTREAM_TIMEOUT_SECONDS = 60.0

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
    1. `UPSTREAM_BASE_URL=https://api.minimaxi.com/v1`
    2. `UPSTREAM_BASE_URL=https://api.minimaxi.com/v1/chat/completions`

    这样配置更宽容，避免因为 base URL 是否带完整路径而频繁改代码。
    """

    if not BASE_URL:
        raise ValueError("UPSTREAM_BASE_URL is not set")

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


def _normalize_request_context(request_id: str | None, path: str | None, task: str | None) -> dict:
    """把可选请求上下文收敛成稳定的日志字段。"""

    return {
        "request_id": request_id or "-",
        "path": path or "-",
        "task": task or "-",
    }


def _request_timeout_seconds() -> float:
    """读取并校验上游请求超时时间。

    当前策略保持保守：
    - 默认 60 秒；
    - 允许通过 `UPSTREAM_TIMEOUT_SECONDS` 覆盖；
    - 只做超时配置，不在这一轮引入自动重试。
    """

    raw_timeout = os.getenv("UPSTREAM_TIMEOUT_SECONDS")
    if raw_timeout is None or not raw_timeout.strip():
        return DEFAULT_UPSTREAM_TIMEOUT_SECONDS

    try:
        timeout_seconds = float(raw_timeout)
    except ValueError as exc:
        raise ValueError("UPSTREAM_TIMEOUT_SECONDS must be a positive number") from exc

    if timeout_seconds <= 0:
        raise ValueError("UPSTREAM_TIMEOUT_SECONDS must be a positive number")

    return timeout_seconds


def chat_completion(payload: dict, request_id: str | None = None, path: str | None = None, task: str | None = None) -> dict:
    """向上游 OpenAI 兼容接口发送一次 chat completions 请求。

    参数：
    - payload: 已经准备好的请求体，通常由上层业务函数构造。

    返回：
    - 上游返回的 JSON 字典。

    这里不吞掉 `requests` 异常，原因是：
    - 底层网络错误应该继续向上抛；
    - 由 FastAPI 层统一决定应该返回 500、502 还是别的状态码。
    """

    if not API_KEY:
        raise ValueError("UPSTREAM_API_KEY is not set")

    url = _chat_completions_url()
    timeout_seconds = _request_timeout_seconds()
    payload_summary = _payload_summary(payload)
    request_context = _normalize_request_context(request_id, path, task)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # 在请求发出前留一条最小 info 日志，帮助排查“是否真的发起了调用”。
    LOGGER.info(
        "Sending upstream chat completion request: request_id=%s path=%s task=%s url=%s timeout_seconds=%s payload=%s",
        request_context["request_id"],
        request_context["path"],
        request_context["task"],
        url,
        timeout_seconds,
        payload_summary,
    )

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        # 失败时记录异常堆栈和请求摘要，方便后续定位是网络问题、鉴权问题还是上游问题。
        LOGGER.exception(
            "Upstream chat completion request failed: request_id=%s path=%s task=%s url=%s payload=%s",
            request_context["request_id"],
            request_context["path"],
            request_context["task"],
            url,
            payload_summary,
        )
        raise

    # 成功时记录最小成功信息，便于后续对照真实返回是否异常。
    LOGGER.info(
        "Upstream chat completion request succeeded: request_id=%s path=%s task=%s status_code=%s response_id=%s model=%s",
        request_context["request_id"],
        request_context["path"],
        request_context["task"],
        response.status_code,
        data.get("id"),
        data.get("model"),
    )
    return data

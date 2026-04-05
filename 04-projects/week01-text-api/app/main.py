"""Week01 Text API 的主入口。

当前文件负责 4 件事：
1. 定义 FastAPI 应用实例。
2. 定义请求/响应模型，约束接口输入输出。
3. 构造发给 MiniMax 的 payload，并解析上游返回。
4. 把内部异常转换成对客户端可理解的 HTTP 错误。
"""

import logging
import re
from uuid import uuid4
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from requests import RequestException

from app.minimax_client import minimax_chat

# 当前项目统一使用的模型名。后续如果切换模型，优先改这里，避免散落在各个接口里。
MODEL_NAME = "MiniMax-M2.7"
MAX_TEXT_LENGTH = 4000

# 某些模型响应会把推理过程包在 <think>...</think> 中。
# 对 API 客户端来说，这部分通常不是最终想要暴露的内容，因此在返回前清理掉。
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)
REWRITE_LABEL_RE = re.compile(r"^(改写后|优化后|润色后|重写后)[：:]\s*")

app = FastAPI(title="Week01 Text API")
REQUEST_ID_HEADER = "X-Request-ID"
LOGGER = logging.getLogger(__name__)


class TextTaskRequest(BaseModel):
    """文本处理接口的统一请求体。

    当前 summarize / key-points 两个接口都只需要一段原始文本，
    所以先复用同一个输入模型，后续增加 rewrite 等接口时也可以继续沿用。
    """

    text: str = Field(..., min_length=1, description=f"需要处理的原始文本，当前最大长度为 {MAX_TEXT_LENGTH} 个字符")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        # 先做 strip，避免用户传入全空格时绕过 min_length=1 的限制。
        normalized = value.strip()
        if not normalized:
            raise ValueError("text must not be empty")
        if len(normalized) > MAX_TEXT_LENGTH:
            raise ValueError(f"text must be at most {MAX_TEXT_LENGTH} characters")
        return normalized


class TextTaskResponse(BaseModel):
    """文本处理接口的统一响应体。

    task 用来标记当前执行的任务类型；
    result 是模型处理后的正文；
    model 方便后续排查“某个结果是哪个模型生成的”。
    """

    task: Literal["summarize", "key-points", "rewrite"]
    result: str
    model: str


class ErrorResponse(BaseModel):
    """统一错误响应结构。

    目前只强制覆盖 500 / 502 这两类服务侧和上游侧错误。
    422 仍保持 FastAPI 默认校验格式，避免过早侵入框架原生行为。
    """

    code: str
    message: str
    detail: str
    request_id: str


class ApiError(Exception):
    """项目内部统一错误对象。"""

    def __init__(self, status_code: int, code: str, message: str, detail: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


COMMON_ERROR_RESPONSES = {
    500: {
        "model": ErrorResponse,
        "description": "本地配置错误或服务端处理失败",
    },
    502: {
        "model": ErrorResponse,
        "description": "上游 MiniMax 请求失败或返回结构不符合预期",
    },
}


def _ensure_request_id(request: Request) -> str:
    """Return the current request id, generating one if the request has none yet."""

    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return request_id

    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    request.state.request_id = request_id
    return request_id


def _build_payload(task: Literal["summarize", "key-points", "rewrite"], text: str) -> dict:
    """根据任务类型构造发给 MiniMax 的请求体。

    这里把 prompt 模板集中管理，目的是：
    1. 避免每个 endpoint 各写一套 prompt；
    2. 让“接口职责”和“模型提示词”分层；
    3. 后续调 prompt 时只需要改一个地方。
    """

    prompts = {
        "summarize": "请用中文输出 2 到 3 句话总结下面的内容，只保留核心信息，不要添加额外解释。",
        "key-points": "请提取下面内容的 3 到 5 个关键要点，使用中文无序列表，每行以 - 开头。",
        "rewrite": (
            "请在不改变原意的前提下，用更清晰、更自然的中文改写下面内容。"
            "硬性要求："
            "1. 只输出改写后的最终文本；"
            "2. 不要添加标题、开场白、解释、列表或额外结论；"
            "3. 保持单段输出；"
            "4. 长度尽量控制在原文的 0.8 到 1.3 倍，不要明显扩写；"
            "5. 如果原文本来就很短，只做轻度润色。"
        ),
    }
    return {
        "model": MODEL_NAME,
        "messages": [
            # system message 负责约束助手整体风格，尽量保持输出稳定、简洁。
            {"role": "system", "content": "你是一个简洁、可靠的中文文本处理助手。"},
            # user message 负责注入具体任务说明和原始文本。
            {"role": "user", "content": f"{prompts[task]}\n\n原文：\n{text}"},
        ],
    }


def _extract_result(response_data: dict) -> str:
    """从 MiniMax 原始响应中抽取最终可返回给客户端的文本。

    这里不直接相信上游响应一定合法，而是显式做结构校验。
    如果 choices/message/content 任一层级缺失，就返回 502，说明问题在上游。
    """

    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ApiError(
            status_code=502,
            code="UPSTREAM_INVALID_RESPONSE",
            message="MiniMax returned an unexpected response",
            detail="choices[0].message.content is missing or malformed",
        ) from exc

    # 去掉 <think> 块，避免把模型推理痕迹直接暴露给前端或调用方。
    cleaned = THINK_BLOCK_RE.sub("", content).strip()
    if not cleaned:
        # 如果去掉推理块后内容为空，说明这次响应对客户端没有有效价值。
        raise ApiError(
            status_code=502,
            code="UPSTREAM_EMPTY_RESPONSE",
            message="MiniMax returned an empty response",
            detail="response content became empty after cleanup",
        )
    return cleaned


def _looks_like_rewrite_heading(line: str) -> bool:
    """识别 rewrite 输出中常见的“自动加标题”首行。"""

    stripped = line.strip()
    if not stripped:
        return False

    if stripped.startswith("#"):
        return True

    if stripped.startswith("《") and stripped.endswith("》"):
        return True

    if stripped.endswith(("：", ":")):
        return True

    return len(stripped) <= 16 and not re.search(r"[，。！？；,.!?;]", stripped)


def _normalize_rewrite_result(result: str) -> str:
    """把 rewrite 输出收敛成单段、无标题、无前缀的最终文本。"""

    lines = [line.strip() for line in result.splitlines() if line.strip()]
    if not lines:
        raise ApiError(
            status_code=502,
            code="UPSTREAM_EMPTY_REWRITE_RESPONSE",
            message="MiniMax returned an empty rewrite response",
            detail="rewrite result is empty after line normalization",
        )

    if _looks_like_rewrite_heading(lines[0]) and len(lines) > 1:
        lines = lines[1:]

    normalized = " ".join(lines).strip()
    normalized = REWRITE_LABEL_RE.sub("", normalized).strip()
    if not normalized:
        raise ApiError(
            status_code=502,
            code="UPSTREAM_EMPTY_REWRITE_RESPONSE",
            message="MiniMax returned an empty rewrite response",
            detail="rewrite result is empty after heading and label cleanup",
        )

    return normalized


def _format_request_exception(exc: RequestException) -> str:
    """把 requests 异常转换成更稳定的 detail 文案。"""

    request = getattr(exc, "request", None)
    request_url = getattr(request, "url", None)
    if request_url:
        return f"{exc.__class__.__name__} while requesting {request_url}"
    return str(exc)


def _run_text_task(task: Literal["summarize", "key-points", "rewrite"], text: str) -> TextTaskResponse:
    """执行一次完整的文本处理任务。

    调用链如下：
    1. 根据 task + text 生成 payload；
    2. 调用 minimax_chat 请求上游模型；
    3. 解析并清洗返回内容；
    4. 封装成统一响应模型返回。
    """

    try:
        response_data = minimax_chat(_build_payload(task, text))
    except ValueError as exc:
        # 这类错误通常是本地配置问题，比如 API Key / Base URL 未设置。
        raise ApiError(
            status_code=500,
            code="SERVER_MISCONFIGURED",
            message="Local service configuration is invalid",
            detail=str(exc),
        ) from exc
    except RequestException as exc:
        # 这类错误来自 requests 层，通常是超时、连接失败或上游非 2xx。
        raise ApiError(
            status_code=502,
            code="UPSTREAM_REQUEST_FAILED",
            message="MiniMax request failed",
            detail=_format_request_exception(exc),
        ) from exc

    result = _extract_result(response_data)
    if task == "rewrite":
        result = _normalize_rewrite_result(result)

    return TextTaskResponse(task=task, result=result, model=MODEL_NAME)


@app.exception_handler(ApiError)
async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    """把内部统一错误对象转换成稳定的 JSON 错误响应。"""

    request_id = _ensure_request_id(request)
    payload = ErrorResponse(
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
        request_id=request_id,
    )
    LOGGER.warning(
        "API error response: request_id=%s path=%s status_code=%s code=%s detail=%s",
        request_id,
        request.url.path,
        exc.status_code,
        exc.code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
        headers={REQUEST_ID_HEADER: request_id},
    )


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    """Attach a stable request id to the current request/response lifecycle."""

    request_id = _ensure_request_id(request)
    response = await call_next(request)
    response.headers.setdefault(REQUEST_ID_HEADER, request_id)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    """最小健康检查接口。

    当前只用于确认 FastAPI 进程是否正常启动。
    后续如果接入数据库、缓存或外部依赖，可以在这里补更细的健康状态。
    """

    return {"status": "ok"}


@app.post("/summarize", response_model=TextTaskResponse, responses=COMMON_ERROR_RESPONSES)
def summarize(request: TextTaskRequest) -> TextTaskResponse:
    """总结接口。

    输入一段原文，输出 2 到 3 句话的中文总结。
    """

    return _run_text_task("summarize", request.text)


@app.post("/key-points", response_model=TextTaskResponse, responses=COMMON_ERROR_RESPONSES)
def key_points(request: TextTaskRequest) -> TextTaskResponse:
    """要点提取接口。

    输入一段原文，输出 3 到 5 个中文关键要点列表。
    """

    return _run_text_task("key-points", request.text)


@app.post("/rewrite", response_model=TextTaskResponse, responses=COMMON_ERROR_RESPONSES)
def rewrite(request: TextTaskRequest) -> TextTaskResponse:
    """改写接口。

    输入一段原文，输出一段语义不变、表达更清晰的改写文本。
    """

    return _run_text_task("rewrite", request.text)

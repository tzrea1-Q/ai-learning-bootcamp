"""Week01 Text API 的主入口。

当前文件负责 4 件事：
1. 定义 FastAPI 应用实例。
2. 定义请求/响应模型，约束接口输入输出。
3. 构造发给 MiniMax 的 payload，并解析上游返回。
4. 把内部异常转换成对客户端可理解的 HTTP 错误。
"""

import re
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from requests import RequestException

from app.minimax_client import minimax_chat

# 当前项目统一使用的模型名。后续如果切换模型，优先改这里，避免散落在各个接口里。
MODEL_NAME = "MiniMax-M2.7"

# 某些模型响应会把推理过程包在 <think>...</think> 中。
# 对 API 客户端来说，这部分通常不是最终想要暴露的内容，因此在返回前清理掉。
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)

app = FastAPI(title="Week01 Text API")


class TextTaskRequest(BaseModel):
    """文本处理接口的统一请求体。

    当前 summarize / key-points 两个接口都只需要一段原始文本，
    所以先复用同一个输入模型，后续增加 rewrite 等接口时也可以继续沿用。
    """

    text: str = Field(..., min_length=1, description="需要处理的原始文本")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        # 先做 strip，避免用户传入全空格时绕过 min_length=1 的限制。
        normalized = value.strip()
        if not normalized:
            raise ValueError("text must not be empty")
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
        "rewrite": "请在不改变原意的前提下，用更清晰、更自然的中文改写下面内容，输出一段完整文本，不要解释改写过程。",
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
        raise HTTPException(status_code=502, detail="MiniMax returned an unexpected response") from exc

    # 去掉 <think> 块，避免把模型推理痕迹直接暴露给前端或调用方。
    cleaned = THINK_BLOCK_RE.sub("", content).strip()
    if not cleaned:
        # 如果去掉推理块后内容为空，说明这次响应对客户端没有有效价值。
        raise HTTPException(status_code=502, detail="MiniMax returned an empty response")
    return cleaned


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
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RequestException as exc:
        # 这类错误来自 requests 层，通常是超时、连接失败或上游非 2xx。
        raise HTTPException(status_code=502, detail=f"MiniMax request failed: {exc}") from exc

    return TextTaskResponse(task=task, result=_extract_result(response_data), model=MODEL_NAME)


@app.get("/health")
def health() -> dict[str, str]:
    """最小健康检查接口。

    当前只用于确认 FastAPI 进程是否正常启动。
    后续如果接入数据库、缓存或外部依赖，可以在这里补更细的健康状态。
    """

    return {"status": "ok"}


@app.post("/summarize", response_model=TextTaskResponse)
def summarize(request: TextTaskRequest) -> TextTaskResponse:
    """总结接口。

    输入一段原文，输出 2 到 3 句话的中文总结。
    """

    return _run_text_task("summarize", request.text)


@app.post("/key-points", response_model=TextTaskResponse)
def key_points(request: TextTaskRequest) -> TextTaskResponse:
    """要点提取接口。

    输入一段原文，输出 3 到 5 个中文关键要点列表。
    """

    return _run_text_task("key-points", request.text)


@app.post("/rewrite", response_model=TextTaskResponse)
def rewrite(request: TextTaskRequest) -> TextTaskResponse:
    """改写接口。

    输入一段原文，输出一段语义不变、表达更清晰的改写文本。
    """

    return _run_text_task("rewrite", request.text)

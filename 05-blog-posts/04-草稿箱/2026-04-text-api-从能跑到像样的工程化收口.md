# 把一个最小 LLM 文本 API 做出工程感：text-api 的第一轮收口

## 一、项目背景与本文范围

`text-api` 是当前训练系统里的第一个示例项目，目标不是做一个功能很多的产品，而是做一个最小但完整的 LLM 文本处理 API 基线。项目目录位于 [04-projects/text-api](https://github.com/tzrea1-Q/ai-learning-bootcamp/tree/main/04-projects/text-api)。

### 1. 项目定位

这一版项目对外暴露 4 个接口：

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`

对内结构保持得很轻，只分三层：

1. HTTP 接口层：FastAPI 路由与请求响应模型
2. 任务编排层：Prompt 构造、结果提取、输出清洗、错误映射
3. 上游客户端层：OpenAI 兼容 Chat Completions 调用与最小日志

也就是说，这个项目解决的不是“如何做一个聊天页面”，而是更基础也更关键的问题：如何把一次真实的 LLM 调用收成一个可测试、可回放、可继续扩展的 API 服务。

### 2. 运行前提

这个项目要跑起来，前提其实很少：

- 本地 Python 3.14
- 一个虚拟环境 `.venv`
- 一份可用的上游兼容接口 API Key
- 一组最小环境变量

环境变量目前只要求下面 5 个：

```env
UPSTREAM_API_KEY=your_api_key_here
UPSTREAM_BASE_URL=https://api.minimaxi.com/v1
UPSTREAM_MODEL=MiniMax-M2.7
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_bootcamp
APP_ENV=dev
LOG_LEVEL=INFO
```

其中真正影响第 1 周主流程的主要是前三个：

- `UPSTREAM_API_KEY`：决定上游调用是否能通过鉴权
- `UPSTREAM_BASE_URL`：决定请求最终打到哪里
- `UPSTREAM_MODEL`：决定默认示例使用哪个兼容模型标识

`DATABASE_URL` 在当前阶段还只是为后续数据库接入预留，`APP_ENV` 和 `LOG_LEVEL` 则分别用于环境标识和最小日志控制。这里继续使用 MiniMax 作为示例值，只是因为第 1 周真实联调是基于这组默认配置完成的；当前代码边界已经按 OpenAI 兼容接口抽象，不再绑定单一供应商。

本地启动方式也很直接：

```powershell
cd 04-projects/text-api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

服务启动后，最先可访问的是：

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

也就是说，这个项目在环境层面并不复杂，复杂度主要不在“怎么跑起来”，而在“跑起来以后怎样把接口收稳”。

### 3. 最小调用链

`text-api` 的核心不是路由本身，而是一次请求如何从 FastAPI 走到一个 OpenAI 兼容上游，再收回到统一响应。

上游调用方式接近 OpenAI `chat/completions` 风格，请求体非常直接：

```json
{
  "model": "MiniMax-M2.7",
  "messages": [
    {"role": "system", "content": "你是一个简洁、可靠的中文文本处理助手。"},
    {"role": "user", "content": "请用中文输出 2 到 3 句话总结下面的内容 ..."}
  ]
}
```

真正发请求的代码也很短，位于 `app/openai_compatible_client.py`：

```python
def chat_completion(payload: dict) -> dict:
    if not API_KEY:
        raise ValueError("UPSTREAM_API_KEY is not set")

    url = _chat_completions_url()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()
```

这一层只负责 4 件事：

- 读取环境变量
- 生成最终请求地址
- 带鉴权头发 HTTP 请求
- 返回上游 JSON，异常继续向上抛

路由层则只关心任务语义。比如 `POST /summarize` 的入口本身非常薄：

```python
@app.post("/summarize", response_model=TextTaskResponse, responses=COMMON_ERROR_RESPONSES)
def summarize(request: TextTaskRequest) -> TextTaskResponse:
    return _run_text_task("summarize", request.text)
```

真正的任务差异，主要集中在 `_build_payload()` 里。以 `summarize` 为例，当前实现会统一生成下面这样的 `messages`：

```python
{
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": "你是一个简洁、可靠的中文文本处理助手。"},
        {"role": "user", "content": "请用中文输出 2 到 3 句话总结下面的内容，只保留核心信息，不要添加额外解释。\n\n原文：\n{text}"},
    ],
}
```

这样做的好处是，任务定义、接口定义和上游 HTTP 通信被拆开了。后续要改 prompt、改错误映射、补日志或补测试时，不需要在路由里到处翻代码。

如果只想快速判断服务是不是已经通了，当前最小联调命令就是：

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/summarize' `
  -ContentType 'application/json' `
  -Body '{"text":"FastAPI 是一个现代、高性能的 Python Web 框架，适合快速构建 API。"}'
```

这一层内容在仓库文档里也有，但这里只保留最关键的运行前提和调用路径，避免正文把核心背景外包给 README。更完整的补充材料见：

- [README.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/README.md)
- [04-开发测试调试指南.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/docs/04-%E5%BC%80%E5%8F%91%E6%B5%8B%E8%AF%95%E8%B0%83%E8%AF%95%E6%8C%87%E5%8D%97.md)

这类项目最容易被低估的地方在于，功能看上去很简单，但只要打算继续接日志、测试、CI、数据库或者前端联调，接口契约是否稳定会立刻成为主问题。

![text-api 接口实跑结果](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/08-assets/week01/week01-api-demo.png?raw=1)

## 二、本文聚焦的问题

本文只聚焦一件事：为什么 `text-api` 在第 1 周没有继续扩接口，而是先做了一轮工程化收口。

原因不复杂。对 LLM API 来说，`HTTP 200` 只能说明请求已经发出并拿到了返回，不能说明返回结果已经具备可交付性。一个接口如果存在脏输出、错误结构不稳定、输入边界不明确、验证记录不可回放，那么下一轮迭代的成本会迅速抬高。

因此，第 1 周的核心目标不是追接口数量，而是把“能跑”的最小闭环收成“像样”的最小基线。

## 三、技术现场

第 1 周结束时，`text-api` 从接口数量上看已经完成了最小目标，但真实验证暴露了三类典型问题。

第一类问题来自模型原始输出。第 1 周默认示例上游 MiniMax 返回正文时曾混入 `<think>...</think>` 片段。这说明“调用成功”和“结果可直接返回给客户端”是两回事。相关复盘见 [2026-04-minimax-think-output-leak.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/07-postmortems/2026-04-minimax-think-output-leak.md)。

第二类问题来自 `POST /rewrite`。接口虽然可用，但在真实样例里会出现轻度扩写、偏书面化、偶发标题化的现象。这类问题不一定报错，却会直接破坏调用方对接口行为的预期。回归记录见 [06-rewrite-回归记录-2026-04-04.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/docs/traces/06-rewrite-%E5%9B%9E%E5%BD%92%E8%AE%B0%E5%BD%95-2026-04-04.md)。

第三类问题来自错误路径。第 1 周前半段，`500 / 502` 虽然能抛出，但缺少统一错误码、稳定错误摘要和请求级关联信息。测试、排查和后续前端消费都不够顺手。后续补齐 `request_id` 后的验证见 [10-request-id-错误响应验证记录-2026-04-05.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/docs/traces/10-request-id-%E9%94%99%E8%AF%AF%E5%93%8D%E5%BA%94%E9%AA%8C%E8%AF%81%E8%AE%B0%E5%BD%95-2026-04-05.md)。

这三类问题有一个共同点：不会阻止接口返回结果，但会直接影响这个项目是否具备继续工程化的条件。

## 四、处理原则与取舍

这一轮没有追求“大而全”，而是只收最容易破坏后续迭代的点。

处理顺序大致如下：

1. 先收输入和输出，因为这是接口契约最直接的部分。
2. 再收 `500 / 502` 错误结构，因为测试和调用方都依赖它。
3. 最后把验证固化到测试、traces 和 postmortem，而不是留在终端历史里。

同时也有两条明确边界：

- 当前只统一 `500 / 502`，暂不改写 FastAPI 默认 `422`
- 当前只补最小 `request_id` 链路，暂不把日志系统直接做成完整 trace 平台

这类取舍并不新鲜，但非常重要。对一个体量还很小的项目来说，先保证契约稳定，收益通常高于继续增加业务接口。

## 五、关键实现

### 1. LLM API 调用先收成一个明确的客户端层

对新手来说，最容易失控的地方往往是“路由里直接写 HTTP 调用”。`text-api` 没有这么做，而是把上游调用集中放在 [app/openai_compatible_client.py](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/app/openai_compatible_client.py)。

核心代码其实很短：

```python
def chat_completion(payload: dict) -> dict:
    if not API_KEY:
        raise ValueError("UPSTREAM_API_KEY is not set")

    url = _chat_completions_url()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()
```

这层抽出来以后，路由层就不需要关心鉴权、URL 拼接、超时和 `requests` 异常，只需要关心“当前任务是什么”“返回值要收成什么结构”。这一步看起来基础，但它决定了后续是不是能继续补日志、重试和 provider 适配。

### 2. 输入边界先在模型层收紧

文本接口共用了一个请求模型 `TextTaskRequest`。实现位于 [app/main.py](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/app/main.py)。

```python
class TextTaskRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("text must not be empty")
        if len(normalized) > MAX_TEXT_LENGTH:
            raise ValueError(f"text must be at most {MAX_TEXT_LENGTH} characters")
        return normalized
```

这里做了三件基础但必要的事：

- 统一三个文本接口的输入形态
- 拦住纯空格输入
- 把最大长度明确收在 `4000`

这类边界如果不尽早落到模型层，后面会在路由、上游调用、测试和文档里反复分叉。

### 3. 输出清洗不是 patch，而是契约的一部分

`text-api` 的一个关键问题，是上游返回并不天然等于最终结果。正文提取和输出清洗也放在 [app/main.py](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/app/main.py) 里统一处理。

```python
def _extract_result(response_data: dict) -> str:
    content = response_data["choices"][0]["message"]["content"]
    cleaned = THINK_BLOCK_RE.sub("", content).strip()
    if not cleaned:
        raise ApiError(
            status_code=502,
            code="UPSTREAM_EMPTY_RESPONSE",
            message="Upstream returned an empty response",
            detail="response content became empty after cleanup",
        )
    return cleaned
```

这段逻辑的价值在于，它把“去掉 `<think>` 之后才算有效结果”写成了规则，而不是一次性的手工处理。

`rewrite` 额外多做了一层归一化，用来去掉“改写后：”这类前缀，以及偶发自动生成的首行标题。也就是说，`POST /rewrite` 的问题不是靠 prompt 单点修掉，而是靠“prompt 收紧 + 结果清理”双侧收口。

### 4. 错误响应必须从“能抛”推进到“可判断”

当前统一后的 `500 / 502` 错误结构如下：

```json
{
  "code": "UPSTREAM_REQUEST_FAILED",
  "message": "Upstream request failed",
  "detail": "request timed out",
  "request_id": "01a1200e-5c70-4678-8d47-c951a9cd54f6"
}
```

对应实现仍在 [app/main.py](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/app/main.py)：

```python
def _ensure_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return request_id
    request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
    request.state.request_id = request_id
    return request_id

@app.exception_handler(ApiError)
async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    request_id = _ensure_request_id(request)
    payload = ErrorResponse(
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
        headers={REQUEST_ID_HEADER: request_id},
    )
```

这一步解决的是工程问题，而不是文案问题：

- 调用方可以按 `code` 做稳定分支
- 测试可以按固定结构断言
- 响应头、响应体和日志可以通过同一个 `request_id` 关联

### 5. 验证材料必须能回放

这一轮没有停在“代码已经改完”。验证被拆成了三层：

- 自动化测试放在 [tests/test_text_endpoints.py](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/tests/test_text_endpoints.py)
- 真实联调、回归、环境验证放在 `docs/traces/`
- 项目级失败案例放在 `07-postmortems/`

例如，下面这个断言测的就不是“接口有没有返回”，而是 `request_id` 是否真的进入了统一错误结构：

```python
def assert_has_request_id(payload: dict) -> None:
    request_id = payload.get("request_id")
    assert isinstance(request_id, str)
    assert request_id
    assert str(UUID(request_id)) == request_id
```

![text-api pytest 结果](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/08-assets/week01/week01-pytest-or-ci.png?raw=1)

到第 1 周结束时，本地 `pytest` 已经是 `12 passed`。这并不代表项目成熟，但至少说明当前实现不是一次性的终端演示。

## 六、阶段结果

这一轮收口之后，`text-api` 还没有完成所有工程化目标。`422` 还没统一，完整日志链路、超时 / 重试、GitHub 上实际 CI 跑通，也都还在下一轮计划里。

但有几件关键的基础件已经固定下来：

- 对外接口范围明确
- 输入边界明确
- 输出清洗明确
- `500 / 502` 错误契约明确
- `request_id` 最小链路明确
- 测试、traces 和 postmortem 已经能回放现场

这也是本文真正关心的结果：项目已经从“能跑”推进到“可以继续往下长”。

## 七、经验与实践建议

从 `text-api` 这一轮收口里，可以提炼出一张很小但很实用的检查单：

1. LLM 返回值是否经过显式清洗，而不是默认可信。
2. 文本输入边界是否在模型层就被约束，而不是拖到下游。
3. 最关键的错误路径是否有稳定 JSON 结构。
4. 是否存在一条最小请求关联链路，例如 `request_id`。
5. 测试、联调、回归和复盘是否能在一周后被快速回放。

对小型 LLM API 项目来说，工程化通常不是从大规模抽象开始，而是从这些看起来不大、但足够决定后续开发效率的小收口开始。

## 八、小结

第 1 周 `text-api` 的进展，并不只是多做了 4 个接口。更准确的说法是：一个最小 LLM 文本 API，已经具备了继续工程化的基础件。

除此之外，本文更想说明的是，LLM 项目的早期质量差异，往往不体现在“功能多少”，而体现在“契约是否稳定、问题是否可追踪、验证是否可回放”。`text-api` 这一轮收口，本质上收的正是这些东西。


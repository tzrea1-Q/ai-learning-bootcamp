# Week01 Text API

## 简介

第 1 周基准项目，用于打通 FastAPI + MiniMax API 的最小文本处理闭环，并保留 PostgreSQL / Docker 的基础工程骨架。

当前已完成：

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`
- 基础自动化测试

## 文档导航

如果你需要详细项目文档，请继续看 `docs/`：

- `docs/README.md`：文档索引和阅读顺序
- `docs/01-项目概览.md`：项目目标、目录结构、能力边界
- `docs/02-架构与调用链.md`：FastAPI 到 MiniMax 的内部调用路径
- `docs/03-接口契约.md`：HTTP 接口、上游接口格式、错误语义
- `docs/04-开发测试调试指南.md`：本地启动、测试、联调、日志
- `docs/05-已知问题与后续计划.md`：当前限制、风险与下一步计划
- `docs/traces/06-rewrite-回归记录-2026-04-04.md`：`POST /rewrite` 的真实样例回归、修正动作和残余风险
- `docs/traces/07-统一错误响应验证记录-2026-04-04.md`：统一错误响应格式的测试、联调和实际返回记录
- `docs/traces/08-docker-postgres-验证记录-2026-04-04.md`：PostgreSQL Docker 骨架的配置检查与本机验证结果
- `docs/traces/09-ci-与输入边界验证记录-2026-04-04.md`：最小 GitHub Actions 工作流草稿与输入边界约束的本地验证记录

## 环境变量

复制 `.env.example` 为 `.env`，至少配置以下变量：

- `MINIMAX_API_KEY`：MiniMax API Key
- `MINIMAX_BASE_URL`：默认使用 `https://api.minimaxi.com/v1`
- `DATABASE_URL`：预留给后续数据库接入
- `APP_ENV`：运行环境标记
- `LOG_LEVEL`：日志级别，当前已用于控制 MiniMax 请求链路的最小日志输出

## 启动方式

1. 创建并激活虚拟环境
2. 安装依赖
3. 准备 `.env`
4. 启动 FastAPI

```powershell
cd 04-projects/week01-text-api
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

服务启动后访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- 健康检查: `http://127.0.0.1:8000/health`

## PostgreSQL 骨架

当前应用主流程还没有用到数据库，但仓库已保留 `docker-compose.yml`，后续可直接启动 PostgreSQL：

```powershell
docker compose up -d postgres
```

本地验证结论：

- `docker compose config` 可正常解析，说明 Compose 结构和环境变量约定没有脱节
- 当前机器上的 Docker daemon 未启动，因此 2026-04-04 这次验证未能真正把容器拉起
- 详细记录见 `docs/traces/08-docker-postgres-验证记录-2026-04-04.md`

## 接口说明

### GET /health

返回服务健康状态：

```json
{
  "status": "ok"
}
```

### POST /summarize

请求体：

```json
{
  "text": "FastAPI 是一个现代、高性能的 Python Web 框架，适合快速构建 API。"
}
```

输入边界：

- `text` 去掉首尾空白后不能为空
- `text` 当前最大长度为 `4000` 个字符
- 超出边界会返回 `422`

返回体示例：

```json
{
  "task": "summarize",
  "result": "FastAPI 是一个现代、高性能的 Python Web 框架，可快速构建 API，并自动生成交互式文档。",
  "model": "MiniMax-M2.7"
}
```

### POST /key-points

请求体：

```json
{
  "text": "FastAPI 支持类型提示、自动文档和高性能，适合快速搭建 Web API。"
}
```

返回体示例：

```json
{
  "task": "key-points",
  "result": "- 支持 Python 类型提示\n- 自动生成 API 文档\n- 具备高性能\n- 适合快速搭建 Web API",
  "model": "MiniMax-M2.7"
}
```

### POST /rewrite

请求体：

```json
{
  "text": "FastAPI 可以更快做 API。"
}
```

返回体示例：

```json
{
  "task": "rewrite",
  "result": "FastAPI 可以帮助开发者更高效地构建清晰、可靠的 API 服务。",
  "model": "MiniMax-M2.7"
}
```

## 测试

运行全部测试：

```powershell
cd 04-projects/week01-text-api
.venv\Scripts\python.exe -m pytest
```

验证 MiniMax 实际连通性：

```powershell
.venv\Scripts\python.exe scripts/test_minimax.py
```

最小 GitHub Actions 工作流草稿已放在：

```text
.github/workflows/week01-text-api-pytest.yml
```

## 本地调试命令

下面这组命令可以在本地服务启动后直接复用，快速验证完整调用流程：

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/summarize' `
  -ContentType 'application/json' `
  -Body '{"text":"FastAPI 是一个现代、高性能的 Python Web 框架，适合快速构建 API。"}'

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/key-points' `
  -ContentType 'application/json' `
  -Body '{"text":"FastAPI 支持类型提示、自动文档和高性能，适合快速搭建 Web API。"}'

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/rewrite' `
  -ContentType 'application/json' `
  -Body '{"text":"FastAPI 可以更快做 API。"}'
```

## 当前实现说明

- 文本处理接口通过 `app/minimax_client.py` 调用 MiniMax Chat Completions。
- 接口会清理返回内容中的 `<think>...</think>` 片段，避免把推理痕迹直接暴露给客户端。
- `POST /rewrite` 会额外收紧输出风格：提示词明确禁止标题、解释和明显扩写；结果侧会清理常见的“改写后：”前缀和自动生成的首行标题。
- `500 / 502` 已统一为 `code + message + detail` 错误结构，便于前端、测试和日志做稳定判断。
- MiniMax 请求发出前、成功后和失败时都会留下最小日志，便于排查 URL、模型名、状态码和异常信息。

## 已记录失败案例

- `07-postmortems/2026-04-minimax-think-output-leak.md`：MiniMax 返回 `<think>` 片段导致接口输出不稳定。
- `07-postmortems/2026-04-week01-text-api-rewrite-style-drift.md`：`POST /rewrite` 的风格漂移与轻度扩写复盘。

## 下一步

- 补日志与请求级 trace 信息
- 引入数据库记录请求历史

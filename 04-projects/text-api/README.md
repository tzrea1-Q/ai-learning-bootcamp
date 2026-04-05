# Text API

第 1 周基准项目，用于打通 `FastAPI + OpenAI 兼容 Chat Completions API` 的最小文本处理闭环，并保留 PostgreSQL / Docker 的基础工程骨架。默认示例配置仍指向 MiniMax 兼容端点，但实现本身不绑定单一供应商。

这个 `README.md` 只承担两件事：

- 作为项目入口，帮助你快速知道项目是什么、现在做到哪一步
- 把你导向正确的文档真相源，而不是在这里重复维护完整操作手册

## 当前交付

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`
- `500 / 502` 统一错误结构
- 最小 `request_id` 错误链路
- OpenAI 兼容上游连通性验证脚本
- `pytest` 自动化测试
- PostgreSQL Docker 开发骨架与验证记录

## 先看哪里

如果你想把项目跑起来，先看：

- `ENVIRONMENT.md`

如果你要继续开发或接手维护，按这个顺序看：

1. `docs/README.md`
2. `docs/01-项目概览.md`
3. `docs/02-架构与调用链.md`
4. `docs/03-接口契约.md`
5. `docs/04-开发测试调试指南.md`
6. `docs/05-已知问题与后续计划.md`

## 文档分工

当前项目的文档职责固定如下：

- `README.md`
  - 项目入口和导航，不展开写完整环境配置、接口细节和调试手册
- `ENVIRONMENT.md`
  - 环境变量、`.env` 模板、启动方式、验证入口的唯一真相源
- `docs/03-接口契约.md`
  - HTTP 接口、错误结构、输入边界、输出清洗规则的唯一真相源
- `docs/04-开发测试调试指南.md`
  - 开发流程、自动化测试、联调、日志和排查动作的唯一真相源
- `docs/05-已知问题与后续计划.md`
  - 当前限制、明确决策和下一步优先级

## 关键实现

- 文本处理接口通过 `app/openai_compatible_client.py` 调用 OpenAI 兼容 Chat Completions
- 返回结果会清理 `<think>...</think>` 片段，避免把推理痕迹直接暴露给客户端
- `POST /rewrite` 会额外收紧输出风格，并清理常见的“改写后：”前缀和疑似自动生成标题
- `500 / 502` 已统一为 `code + message + detail + request_id` 结构，并通过 `X-Request-ID` 响应头回传同一个值
- 上游请求前、成功后和失败时都会留下最小日志，便于排查 URL、模型名、状态码和异常信息

## 证据链

项目把测试、联调、回归和环境验证放进了 `docs/traces/`，用于保留可回放的证据材料。当前可直接查看：

- `docs/traces/06-rewrite-回归记录-2026-04-04.md`
- `docs/traces/07-统一错误响应验证记录-2026-04-04.md`
- `docs/traces/10-request-id-错误响应验证记录-2026-04-05.md`
- `docs/traces/11-docker-postgres-验证尝试记录-2026-04-05.md`

已记录失败案例：

- `07-postmortems/2026-04-minimax-think-output-leak.md`
- `07-postmortems/2026-04-text-api-rewrite-style-drift.md`

## 下一步

- 继续补强日志链路
- 明确超时 / 重试策略
- 视真实需求决定是否统一 `422`
- 引入数据库记录请求历史

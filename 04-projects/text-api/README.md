# Text API

第 1 周基准项目，用于打通 `FastAPI + OpenAI 兼容 Chat Completions API` 的最小文本处理闭环，并保留 PostgreSQL / Docker 的基础工程骨架。默认示例配置仍指向 MiniMax 兼容端点，但实现本身不绑定单一供应商。

这个 `README.md` 是项目入口，负责说明当前范围、文档分工和关键跳转，不再重复维护完整环境手册或逐条验证记录。

## 项目入口

- 想把项目跑起来：先看 `ENVIRONMENT.md`
- 想继续开发或接手维护：先看 `docs/README.md`
- 想确认当前限制和下一步：直接看 `docs/05-已知问题与后续计划.md`
- 想回看测试、联调和环境验证：看 `docs/traces/README.md`

## 给 Agent 的环境配置指引

如果你想让 Agent 直接帮你完成环境配置，可以把下面这段话发给它：

`请先阅读这个环境配置文档，并按文档完成 text-api 的环境配置：https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/04-projects/text-api/ENVIRONMENT.md 。完成后告诉我还需要我补哪些真实配置。`

## 当前范围

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`
- `500 / 502` 统一错误结构
- 最小 `request_id` 请求链路
- 可配置的上游请求超时
- 保守的有限重试实验
- OpenAI 兼容上游连通性验证脚本
- `pytest` 自动化测试
- PostgreSQL Docker 开发骨架与验证记录

## 文档分工

- `README.md`
  - 项目入口、当前范围、关键链接
- `ENVIRONMENT.md`
  - 环境变量、`.env` 模板、启动方式、验证入口的唯一真相源
- `docs/03-接口契约.md`
  - HTTP 接口、错误结构、输入边界、输出清洗规则的唯一真相源
- `docs/04-开发测试调试指南.md`
  - 开发流程、自动化测试、联调、日志和排查动作的唯一真相源
- `docs/05-已知问题与后续计划.md`
  - 当前限制、明确决策和下一步优先级的唯一真相源
- `docs/traces/README.md`
  - 测试、联调、回归、环境验证等留痕材料的索引入口

## 证据链

项目把测试、联调、回归和环境验证放进 `docs/traces/`，把项目级失败案例放进 `07-postmortems/`。索引入口如下：

- 留痕索引：`docs/traces/README.md`
- 失败复盘：`07-postmortems/2026-04-minimax-think-output-leak.md`
- 失败复盘：`07-postmortems/2026-04-text-api-rewrite-style-drift.md`

## 下一步

当前限制、明确决策和下一步优先级统一维护在 `docs/05-已知问题与后续计划.md`，这里不再重复展开。

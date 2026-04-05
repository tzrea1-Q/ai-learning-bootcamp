# 第 1 周工程周报

## 本周目标

- 打通 `text-api` 的最小闭环，完成 `FastAPI + OpenAI 兼容 Chat Completions API` 的本地可运行版本，默认示例上游先使用 MiniMax。
- 至少交付 3 个文本处理接口，并补齐测试、README、调试命令和基础留痕。
- 在“能跑”基础上做一轮工程化收口，优先处理输出稳定性、错误结构、输入边界、CI 骨架和验证记录。

## 实际完成

- 完成 `GET /health`、`POST /summarize`、`POST /key-points`、`POST /rewrite` 四个接口，本地 `uvicorn` 联调已跑通。
- 完成第 1 轮工程化硬化：补了 `<think>` 清洗、`rewrite` 风格收紧、统一 `500 / 502` 错误响应、输入长度边界约束、最小请求级 `request_id` 链路。
- 补齐了自动化测试、README、接口契约、调试指南、`docs/traces/` 验证记录和 `07-postmortems/` 复盘文档，并完成本周关键 commit。

## 本周最小可交付

- 一个本地可运行、可测试、可回看留痕的 `text-api` 基线版本。
- 当前最小交付包含：
  - `GET /health`
  - `POST /summarize`
  - `POST /key-points`
  - `POST /rewrite`
  - `.venv\Scripts\python.exe -m pytest`
  - README / 接口契约 / 调试指南 / traces / postmortem

## 本周最大问题

- 问题描述：真实样例回归暴露了两个典型工程问题，一是 `rewrite` 输出风格漂移，二是错误响应缺少稳定结构和请求级关联信息。
- 影响范围：如果不处理，接口虽然“能返回结果”，但对调用方来说缺少稳定契约，测试、排查和后续扩展都会变得脆弱。
- 根因判断：LLM 输出天然不稳定；FastAPI 默认异常和上游异常的边界需要主动收口；前两天优先级放在打通闭环，工程化细节滞后是正常但必须补。
- 当前处理结果：本周已经完成 `rewrite` 第一轮收紧、`500 / 502` 统一错误层、`request_id` 最小链路、输入边界约束和测试/文档留痕，但 `422` 统一、完整日志链路、GitHub 上实际 CI 运行仍未完成。

## 本周技术决策

- 决策 1：本周只统一 `500 / 502`，暂不把 `422` 纳入统一错误层。
- 原因：当前阶段目标是最小可交付而不是过早重写框架默认行为；先把服务侧和上游侧错误收紧，复杂度和收益更匹配。
- 决策 2：`request_id` 先只打通“错误响应 JSON + `X-Request-ID` 响应头 + 统一异常处理日志”的最小链路。
- 原因：这次任务核心是收口，不是重构日志系统；先保证错误可追踪，再决定是否继续下沉。

## 测试与验证

- 单元测试：
  - 2026-04-03：`pytest` `8 passed in 0.02s`
  - 2026-04-04 / 2026-04-05：`pytest` `12 passed`，覆盖健康检查、OpenAI 兼容客户端、文本接口、错误映射、输入边界和 `request_id`
- 接口验证：
  - 本地用 `uvicorn + Invoke-RestMethod` 实测 `/health`、`/summarize`、`/key-points`、`/rewrite`
  - 已完成 `rewrite` 真实样例回归
  - 已完成 `500 / 502` 错误结构验证和 `request_id` 验证
- Docker 验证：
  - `docker compose config` 可正常解析
  - `DATABASE_URL` 与 Compose 配置一致
  - 2026-04-04 首次验证时 Docker engine 未就绪，但 2026-04-05 已补跑成功：`docker compose up -d postgres`、`docker compose ps` 和 `pg_isready` 全部通过
- 部署验证：
  - 无正式部署
  - 已补 `.github/workflows/text-api-pytest.yml` 作为第 2 周最小 CI 起点，但尚未在 GitHub 上实际跑通

## 相关产出

- 日报：
  - [2026-04-03.md](e:\ai-learning-bootcamp\02-daily-reports\2026-04-03.md)
  - [2026-04-04.md](e:\ai-learning-bootcamp\02-daily-reports\2026-04-04.md)
  - [2026-04-05.md](e:\ai-learning-bootcamp\02-daily-reports\2026-04-05.md)
- 项目入口：
  - [README.md](e:\ai-learning-bootcamp\04-projects\text-api\README.md)
  - [05-已知问题与后续计划.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\05-已知问题与后续计划.md)
  - [README.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\README.md)
- 阶段性输出：
  - [week-02-text-api-最小可交付拆解.md](e:\ai-learning-bootcamp\06-solution-docs\week-02-text-api-最小可交付拆解.md)
  - [01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md](e:\ai-learning-bootcamp\05-blog-posts\03-正式文章\01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md)
  - [2026-04-minimax-think-output-leak.md](e:\ai-learning-bootcamp\07-postmortems\2026-04-minimax-think-output-leak.md)
  - [2026-04-text-api-rewrite-style-drift.md](e:\ai-learning-bootcamp\07-postmortems\2026-04-text-api-rewrite-style-drift.md)
- 素材目录：
  - [08-assets/week01](e:\ai-learning-bootcamp\08-assets\week01)

## 下周最小可交付

- 明确是否把 `422` 纳入统一错误响应层，并写出清晰决策说明。
- 把 `request_id` 从最小错误链路继续下沉到更完整的日志链路，至少补请求开始/结束或异常日志的一致关联。
- 让 `.github/workflows/text-api-pytest.yml` 在 GitHub 上实际跑通，补一次真实 CI 成功记录。
- 如果 Docker 环境恢复可用，重新执行 `docker compose up -d postgres`、`docker compose ps` 和 `pg_isready`，补一份真实成功验证记录。

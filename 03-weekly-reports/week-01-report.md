# 第 1 周工程周报

## 本周目标
- 打通 `text-api` 的最小闭环，完成 `FastAPI + OpenAI 兼容 Chat Completions API` 的本地可运行版本，默认示例上游先使用 MiniMax。
- 至少交付 3 个文本处理接口，并补齐测试、README、调试命令和基础留痕。
- 在“能跑”基础上做一轮工程化收口，优先处理输出稳定性、错误结构、输入边界、CI 骨架和验证记录。

## 实际完成
- 完成 `GET /health`、`POST /summarize`、`POST /key-points`、`POST /rewrite` 四个接口，本地 `uvicorn` 联调已跑通。
- 完成第 1 轮工程化硬化：补了 `<think>` 清洗、`rewrite` 风格收紧、统一 `500 / 502` 错误响应、输入长度边界约束、最小请求级 `request_id` 链路。
- 补齐了自动化测试、README、接口契约、调试指南、已知问题文档、`docs/traces/` 验证记录和 `07-postmortems/` 复盘文档，并完成本周关键 commit。

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
- 问题描述：接口功能虽然很快打通，但真实样例回归暴露了两个典型工程问题，一是 `rewrite` 输出风格漂移，二是错误响应缺少稳定结构和请求级关联信息。
- 影响范围：如果不处理，接口虽然“能返回结果”，但对调用方来说缺少稳定契约，测试、排查和后续扩展都会变得脆弱。
- 根因判断：LLM 输出天然不稳定；FastAPI 默认异常和上游异常的边界需要主动收口；前两天优先级放在打通闭环，工程化细节滞后是正常但必须补。
- 当前处理结果：本周已经完成 `rewrite` 第一轮收紧、`500 / 502` 统一错误层、`request_id` 最小链路、输入边界约束和测试/文档留痕，但 `422` 统一、完整日志链路、Docker 真正启动验证和 GitHub 上实际 CI 运行仍未完成。

## 本周技术决策
- 决策 1：本周只统一 `500 / 502`，暂不把 `422` 纳入统一错误层。
- 备选方案：一并统一 `422`，让所有错误都返回同一结构。
- 最终选择：先统一 `500 / 502`，保留 FastAPI 默认 `422`。
- 原因：当前阶段目标是最小可交付而不是过早重写框架默认行为；先把服务侧和上游侧错误收紧，复杂度和收益更匹配。

- 决策 2：`request_id` 先只打通“错误响应 JSON + `X-Request-ID` 响应头 + 统一异常处理日志”的最小链路。
- 备选方案：本周直接做完整 trace、中间件日志、结构化日志和上游请求链路。
- 最终选择：先做最小链路。
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

## 本周输出沉淀
- 日报摘要：
  - [2026-4-3.md](e:\ai-learning-bootcamp\02-daily-reports\2026-4-3.md)
  - [2026-4-4.md](e:\ai-learning-bootcamp\02-daily-reports\2026-4-4.md)
  - [2026-4-5.md](e:\ai-learning-bootcamp\02-daily-reports\2026-4-5.md)
- README 更新：
  - [README.md](e:\ai-learning-bootcamp\04-projects\text-api\README.md)
- 博客素材：
  - 本周已形成可直接展开的主题素材：`rewrite` 风格漂移收口、统一错误响应、traces/postmortem/CI 草稿如何做最小工程化留痕
  - 演示素材已整理到 `08-assets/week01/`，其中“接口实跑结果”和“pytest 通过结果”保留为真实截图，其余更适合直接写成文字说明
- 方案文档：
  - [03-接口契约.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\03-接口契约.md)
  - [04-开发测试调试指南.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\04-开发测试调试指南.md)
  - [05-已知问题与后续计划.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\05-已知问题与后续计划.md)
- 复盘记录：
  - [2026-04-minimax-think-output-leak.md](e:\ai-learning-bootcamp\07-postmortems\2026-04-minimax-think-output-leak.md)
  - 说明：这条复盘对应的是默认示例上游仍使用 MiniMax 时暴露的真实问题
  - [2026-04-text-api-rewrite-style-drift.md](e:\ai-learning-bootcamp\07-postmortems\2026-04-text-api-rewrite-style-drift.md)

## 本周产出链接
- GitHub：
  - 关键 commit：`0713551` `feat: complete week01 text api baseline`
  - 关键 commit：`d4861fd` `Stabilize text API responses and validation traces`
  - 关键 commit：`23b8a57` `Finish week01 text API hardening`
- 演示视频：
  - 本周未录制成片，但已准备 demo 录制脚本与截图清单：[text-api-demo-script-and-shotlist-2026-04-05.md](e:\ai-learning-bootcamp\08-assets\week01\text-api-demo-script-and-shotlist-2026-04-05.md)
- 演示截图与文字化素材：
  - 截图 1“项目最小闭环总览”：不单独截图，直接由 [README.md](e:\ai-learning-bootcamp\04-projects\text-api\README.md) 和本周“本周最小可交付”段落承担展示。
  - 截图 2“本地接口实跑结果”：使用真实截图 [week01-api-demo.png](e:\ai-learning-bootcamp\08-assets\week01\week01-api-demo.png)。
  - 截图 3“rewrite 回归留痕”：不单独截图，直接引用 [06-rewrite-回归记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\06-rewrite-回归记录-2026-04-04.md) 并在博客中用文字概述“问题现象 + 修正动作 + 结论”。
  - 截图 4“统一错误响应与 request_id”：不单独截图，直接引用 [10-request-id-错误响应验证记录-2026-04-05.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\10-request-id-错误响应验证记录-2026-04-05.md) 并在周报/博客中用文字说明错误契约和最小链路。
  - 截图 5“测试或 CI 骨架”：使用真实截图 [week01-pytest-or-ci.png](e:\ai-learning-bootcamp\08-assets\week01\week01-pytest-or-ci.png)。
- 线上地址：
  - 无
- 相关文档：
  - [06-rewrite-回归记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\06-rewrite-回归记录-2026-04-04.md)
  - [07-统一错误响应验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\07-统一错误响应验证记录-2026-04-04.md)
  - [08-docker-postgres-验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\08-docker-postgres-验证记录-2026-04-04.md)
  - [09-ci-与输入边界验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\09-ci-与输入边界验证记录-2026-04-04.md)
  - [10-request-id-错误响应验证记录-2026-04-05.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\10-request-id-错误响应验证记录-2026-04-05.md)
  - [11-docker-postgres-验证尝试记录-2026-04-05.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\11-docker-postgres-验证尝试记录-2026-04-05.md)

## 下周最小可交付
- 明确是否把 `422` 纳入统一错误响应层，并写出清晰决策说明。
- 把 `request_id` 从最小错误链路继续下沉到更完整的日志链路，至少补请求开始/结束或异常日志的一致关联。
- 让 `.github/workflows/text-api-pytest.yml` 在 GitHub 上实际跑通，补一次真实 CI 成功记录。
- 如果 Docker 环境恢复可用，重新执行 `docker compose up -d postgres`、`docker compose ps` 和 `pg_isready`，补一份真实成功验证记录。



# 方案文档｜第 2 周最小可交付拆解（text-api）

## 1. 背景与目标

- 当前问题：
  - 第 1 周已经把 `text-api` 做到“本地可跑、接口可用、测试可过、文档可回看”，但还停留在偏基础的工程骨架阶段。
  - 现阶段最明显的缺口不在新接口数量，而在工程稳定性：日志链路还不完整，超时/重试策略还不明确，CI 只是草稿，Docker 还没完成真实稳定化验证。
- 目标用户：
  - 现在的主要用户仍然是自己，目标是让下周继续开发时不需要反复“重新理解现场”。
  - 次级用户是未来的面试官、协作者或自己两周后的自己，要求文档、日志和验证记录能直接回放。
- 目标结果：
  - 在不继续外扩业务功能的前提下，把当前项目从“能跑”推进到“更像一个可维护的最小工程项目”。
  - 交付第 2 周最小可用版本，重点覆盖日志、超时/重试、CI、Docker 稳定化四项。

## 2. 场景定义

- 输入：
  - 当前已有的 `text-api` 代码、README、接口契约、`docs/traces/` 留痕、postmortem 和本地 `.venv` 环境。
- 输出：
  - 一版更稳定的工程基线，包括最小日志链路、明确的请求超时/重试边界、可实际运行的 CI、可本机验证的 Docker/Postgres 骨架。
- 使用流程：
  1. 启动本地服务或运行测试。
  2. 通过日志和 `request_id` 能快速定位一次请求的关键链路。
  3. 当上游超时或失败时，行为可预测，且不会无限挂起或盲目重试。
  4. 代码提交后，CI 至少能自动跑基础测试。
  5. 需要数据库骨架时，本机能稳定启动 PostgreSQL 并通过健康检查。
- 成功标准：
  - 四个优先级事项都各自形成最小可验收结果。
  - 每一项都带至少一条验证记录，不靠口头说明。

## 3. 最小可交付范围

- 本次必须做：
  - 完成请求级最小日志链路，明确日志字段和写入位置。
  - 为上游兼容请求补清晰的超时配置与有限重试策略，避免无限等待或过度重试。
  - 让 `.github/workflows/text-api-pytest.yml` 在 GitHub 上实际跑通至少一次。
  - 在 Docker 环境可用前提下，完成 PostgreSQL 本机启动、`docker compose ps` 和 `pg_isready` 的真实验证留痕。
- 本次暂不做：
  - 不新增新的文本处理业务接口。
  - 不在第 2 周起步阶段统一 `422` 错误结构，除非出现明确的外部契约需求。
  - 不引入复杂监控栈，例如 ELK、OpenTelemetry、Prometheus、Grafana。
  - 不把当前项目抽象成多模型 provider 框架。
  - 不做生产级部署、灰度、鉴权和多环境编排。

## 4. 技术方案

- 技术栈：
  - `FastAPI + requests + pytest + GitHub Actions + Docker Compose`
- 模型或服务：
  - 继续使用 OpenAI 兼容 Chat Completions 抽象，默认示例供应商仍为 MiniMax。
- 数据存储：
  - 暂时只要求 PostgreSQL 骨架可本机启动验证，不强制接入主请求链路。
- 关键模块：
  - `app/main.py`：请求入口、异常处理、`request_id`、请求级日志
  - `app/openai_compatible_client.py`：超时、有限重试、上游请求日志
  - `tests/`：错误路径、超时/重试、配置边界测试
  - `.github/workflows/text-api-pytest.yml`：最小 CI
  - `docker-compose.yml`：PostgreSQL 本机稳定化验证

## 5. 四项优先级与边界

### 5.1 P0：日志链路补齐

- 必须做到：
  - 为每次请求打印开始、结束或失败日志中的至少两类关键事件。
  - 日志里带 `request_id`、路径、任务类型、状态码或耗时中的最小必要字段。
  - 上游请求失败时，能把应用层错误与请求级日志串起来。
- 边界：
  - 这周只做“足够排查”的最小结构，不做完整结构化日志平台。
  - 不要求所有日志都 JSON 化；先确保字段稳定、可 grep、可人工回看。
- 不做：
  - 不引入第三方日志平台。
  - 不做复杂日志采样和日志脱敏系统。

### 5.2 P1：超时 / 重试策略

- 必须做到：
  - 明确上游兼容请求超时时间来自哪里，最好可配置。
  - 只对有限范围的瞬时错误做有限重试，例如连接失败或读超时。
  - 重试次数、退避策略和不重试的场景要写入文档。
- 边界：
  - 只处理当前 `requests` 链路，不重构为异步客户端。
  - 只做保守重试，不因为“想提高成功率”而放大上游压力或隐藏真实错误。
- 不做：
  - 不引入复杂熔断、令牌桶、批量退避或队列系统。
  - 不做多供应商 fallback。

### 5.3 P2：CI 跑通

- 必须做到：
  - GitHub Actions 至少能在仓库里自动执行 `pytest`。
  - 至少保留一份真实成功记录，能在周报或 traces 中回链。
  - 如果失败，要补一份失败原因和修复动作说明。
- 边界：
  - 本周只要求最小测试流水线，不强制上 lint、type check、security scan。
  - 不追求矩阵构建或多 Python 版本。
- 不做：
  - 不把 CI 扩成完整发布流水线。
  - 不做自动部署。

### 5.4 P3：Docker 稳定化

- 必须做到：
  - 本机 Docker daemon 可用时，成功执行 `docker compose up -d postgres`。
  - 能拿到 `docker compose ps` 和 `pg_isready` 的真实结果。
  - README 和调试文档要与最终命令保持一致。
- 边界：
  - 本周目标是“本地开发骨架可验证”，不是容器化整个应用。
  - 只要求 PostgreSQL 服务本身稳定启动，不强制应用服务也进容器。
- 不做：
  - 不做生产环境镜像优化、Compose 多服务编排、Kubernetes 化。

## 6. 推荐执行顺序

1. 先补日志链路，因为它会影响后续排查超时/重试、CI 和 Docker 问题的效率。
2. 再补超时/重试，因为这项直接影响接口稳定性和错误表现。
3. 然后让 CI 真正跑通，把已有测试和后续改动固定下来。
4. 最后做 Docker 稳定化，因为它依赖本机环境状态，适合放在前面功能收口后执行。

## 7. 风险与边界

- 技术风险：
  - 日志、异常映射和上游调用容易相互牵连，小改动可能膨胀成半天级重构。
- 数据风险：
  - 当前没有真实数据库业务数据，Docker 验证主要是环境可用性，不代表数据链路已可用。
- 成本风险：
  - 如果把“最小工程化”做成“完整平台化”，时间会被日志和基础设施细节吞掉。
- 不确定项：
  - Docker daemon 是否稳定可用。
  - GitHub Actions 是否会暴露额外的路径、依赖或环境变量问题。
  - 如果后续要统一 `422`，需要重新评估测试面、文档面和调用方收益。

## 8. 验收标准

- [ ] 日志：至少 1 个请求链路可以通过 `request_id` 在响应和日志中串起来，并有对应验证记录。
- [ ] 超时 / 重试：至少 1 个测试或验证记录覆盖超时或重试行为，文档中写清策略边界。
- [ ] CI：GitHub Actions 中的 `pytest` 至少成功运行 1 次，并有回链记录。
- [ ] Docker：`docker compose up -d postgres`、`docker compose ps`、`pg_isready` 至少成功验证 1 次，并留下 `md` 记录。
- [ ] 文档：README / 调试指南 / 已知问题 / 周报中至少同步更新 2 处。

## 9. 关联文档

- README：
  - [README.md](e:\ai-learning-bootcamp\04-projects\text-api\README.md)
- 任务清单：
  - [2026-04-05.md](e:\ai-learning-bootcamp\02-daily-reports\2026-04-05.md)
  - [week-01-report.md](e:\ai-learning-bootcamp\03-weekly-reports\week-01-report.md)
- 原始留痕：
  - [07-统一错误响应验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\07-统一错误响应验证记录-2026-04-04.md)
  - [08-docker-postgres-验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\08-docker-postgres-验证记录-2026-04-04.md)
  - [09-ci-与输入边界验证记录-2026-04-04.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\09-ci-与输入边界验证记录-2026-04-04.md)
  - [10-request-id-错误响应验证记录-2026-04-05.md](e:\ai-learning-bootcamp\04-projects\text-api\docs\traces\10-request-id-错误响应验证记录-2026-04-05.md)



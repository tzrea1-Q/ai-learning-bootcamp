# AI 开发小白训练营

`中文` | [English](./README.en.md)

一个把 AI 学习、项目交付、工程化留痕和公开输出串成闭环的开源训练仓库。

它不是“资料合集”，而是一套可直接执行的训练系统：你在这里不仅要学会把项目做出来，还要学会把过程沉淀成 README、方案文档、测试记录、周报、博客和失败复盘。

## 项目定位

- 面向有一点 `Python / Web` 基础、想系统进入 AI 应用开发的人
- 强调“先交付，再扩展；先闭环，再谈高级架构”
- 训练目标不是刷知识点，而是持续产出可运行项目和可公开展示的作品链
- 仓库内容同时服务 3 类场景：学习执行、项目交付、博客连载

## 当前状态

截至 `2026-04-05`，仓库已经从“训练资料仓库”推进到“带真实示例项目和输出链路的开源项目雏形”。

已完成的核心内容：

- 完成仓库导航、训练主线、执行系统、输出系统、项目系统的基础文档
- 补齐日报、周报、博客、README、方案文档、失败复盘等模板体系
- 交付第 1 个示例项目 [`text-api`](./04-projects/text-api/README.md)
- 完成第 1 周工程周报、首篇博客草稿、第 2 周最小可交付拆解和失败复盘
- 建立 `docs/traces/` 留痕机制，把测试、联调、回归、环境验证沉淀成可回看的证据链

正在推进的下一阶段重点：

- 完整请求级日志链路
- 明确的超时 / 重试策略
- GitHub Actions 实际跑通
- Docker / PostgreSQL 开发骨架稳定化

## 这个仓库现在已经有什么

你可以直接拿到并复用的，不只是文档，还有一整套“从做项目到公开输出”的最小工作流：

- 可运行项目：`FastAPI + OpenAI 兼容 Chat Completions API` 的文本处理 API 基线，默认示例上游为 MiniMax
- 工程化文档：README、接口契约、开发调试指南、已知问题与后续计划
- 执行记录：日报、周报、方案拆解
- 内容素材：博客草稿、截图、demo 脚本、postmortem
- 留痕机制：`docs/traces/` 中的验证记录

如果你想做一个能持续连载的开源项目，这里的重点不是“做很多功能”，而是把每一轮迭代都固定成可复用、可传播、可回看的资产。

## 当前最值得看的内容

如果你第一次来到这个仓库，建议优先看这几部分：

1. 仓库定位与使用顺序
   - [00-docs/README.md](./00-docs/README.md)
   - [00-docs/00-导航/00-项目定位与使用方式.md](./00-docs/00-导航/00-项目定位与使用方式.md)
   - [00-docs/00-导航/01-新手启动路径.md](./00-docs/00-导航/01-新手启动路径.md)
2. 第 1 个真实示例项目
   - [04-projects/text-api/README.md](./04-projects/text-api/README.md)
   - [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
3. 最近一轮交付和规划
   - [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
   - [06-solution-docs/week02-text-api-最小可交付拆解.md](./06-solution-docs/week02-text-api-最小可交付拆解.md)
4. 对外输出素材
   - [05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md](./05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md)
   - [05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md](./05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md)
   - [07-postmortems/2026-04-minimax-think-output-leak.md](./07-postmortems/2026-04-minimax-think-output-leak.md)

## 当前示例项目

### `text-api`

这是仓库的第一个基准项目，用来打通一个最小但像样的 AI 文本处理 API。

当前已交付：

- `GET /health`
- `POST /summarize`
- `POST /key-points`
- `POST /rewrite`
- `pytest` 自动化测试
- `500 / 502` 统一错误结构
- 最小 `request_id` 错误链路
- Docker PostgreSQL 开发骨架验证记录

相关入口：

- 项目 README：[04-projects/text-api/README.md](./04-projects/text-api/README.md)
- 项目文档索引：[04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
- 第 1 周周报：[03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
- 博客草稿：[05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md](./05-blog-posts/04-草稿箱/2026-04-text-api-从能跑到像样的工程化收口.md)

## 仓库结构

```text
ai-learning-bootcamp/
├─ 00-docs/               # 导航、训练主线、执行系统、输出系统、项目系统
├─ 01-templates/          # 日报/周报/博客/README/方案/复盘等模板
├─ 02-daily-reports/      # 每日执行记录
├─ 03-weekly-reports/     # 每周周报
├─ 04-projects/           # 实际项目代码与项目级文档
├─ 05-blog-posts/         # 博客草稿与正式文章
├─ 06-solution-docs/      # 方案文档、拆解文档、设计说明
├─ 07-postmortems/        # 失败复盘与问题回看
├─ 08-assets/             # 截图、demo 脚本、录屏素材
└─ 09-archive/            # 归档内容
```

## 这个项目的工作方式

这个仓库和普通学习仓库最大的区别，在于它要求每次迭代都留下“完整证据链”。

最小闭环不是只有代码，还包括：

- 代码和可运行结果
- 测试与验证记录
- README / 方案文档 / 调试指南
- 周报 / 博客 / postmortem
- 截图、脚本或其他对外展示素材

换句话说，这里把“工程交付”和“内容输出”当成同一件事的两面，而不是开发完成后的附属工作。

## 推荐阅读与执行顺序

如果你想照着这个仓库开始训练，推荐按这个顺序：

1. 先看项目定位和新手启动路径
2. 再看训练主线和环境部署文档
3. 用 `01-templates/` 开始你的日报、周报和项目文档
4. 直接运行 `04-projects/text-api`
5. 对照 `docs/traces/`、周报和博客草稿理解“如何把一次开发过程沉淀成公开内容”

## 接下来会继续更新什么

短期路线图：

1. 继续把 `text-api` 从“能跑”推进到“更稳”
2. 让日志、超时 / 重试、CI、Docker 形成下一轮最小工程化收口
3. 按周沉淀工程周报、博客和 postmortem，形成可持续连载的公开输出
4. 继续补更多示例项目，把仓库从单一示例推进到系列化项目集

## 适合谁

这个仓库适合：

- 刚开始做 AI 应用开发，想走工程化路线的人
- 会一点开发，但缺少可执行训练系统的人
- 想把学习过程沉淀成作品集、博客和开源项目的人
- 想学习“如何把小项目做成有证据链的公开项目”的人

不适合：

- 完全零编程基础且暂时不打算动手做项目的人
- 只想看概念介绍、不想写代码和文档的人

## 参与方式

当前仓库仍在从“个人训练仓库”整理成“更成熟的开源项目”。

欢迎后续通过 `Issue / PR / Discussion` 参与改进，优先欢迎这几类反馈：

- 文档结构是否清晰
- 新手启动路径是否顺畅
- 示例项目是否真的可复现
- 博客连载和仓库结构是否便于传播

开源配套文档如 `LICENSE`、`CONTRIBUTING`、更明确的项目看板会在对外公开阶段继续补齐。

## 核心原则

- 先交付，再扩展
- 先闭环，再抽象
- 先有证据，再谈结论
- AI 是协作工具，不是替代判断
- 所有测试、联调、回归和样例验证都要留痕

英文入口见 [README.en.md](./README.en.md)。



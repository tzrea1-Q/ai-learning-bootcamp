# AI 开发小白训练营

`中文` | [English](./README.en.md)

一个把 AI 学习、项目交付、工程化留痕和公开输出串成闭环的开源训练仓库。

它不是“资料合集”，而是一套可直接执行的训练系统：你在这里不仅要学会把项目做出来，还要学会把过程沉淀成 README、方案文档、测试记录、周报、博客和失败复盘。

## 入口规则

- 根目录 `README.md`：仓库总入口，只负责说明仓库是什么、怎么进入、当前有哪些公开样本
- 各子目录 `README.md`：只做该目录内部索引，不重复承担仓库总入口职责
- 项目级可变事实：尽量收口到项目 README、项目已知问题文档、周报和留痕文档，而不是在多个层级重复维护

## 项目定位

- 面向有一点 `Python / Web` 基础、想系统进入 AI 应用开发的人
- 强调“先交付，再扩展；先闭环，再谈高级架构”
- 训练目标不是刷知识点，而是持续产出可运行项目和可公开展示的作品链
- 仓库内容同时服务 3 类场景：学习执行、项目交付、博客连载

## 建议进入路径

如果你第一次来到这个仓库，建议按这个顺序进入：

1. 仓库定位与启动路径
   - [00-docs/00-导航/00-项目定位与使用方式.md](./00-docs/00-导航/00-项目定位与使用方式.md)
   - [00-docs/00-导航/01-新手启动路径.md](./00-docs/00-导航/01-新手启动路径.md)
2. 训练主线与环境准备
   - [00-docs/01-训练主线/00-学习总览.md](./00-docs/01-训练主线/00-学习总览.md)
   - [00-docs/01-训练主线/07-详细可执行的环境部署指导.md](./00-docs/01-训练主线/07-详细可执行的环境部署指导.md)
3. 第 1 个真实示例项目
   - [04-projects/text-api/README.md](./04-projects/text-api/README.md)
   - [04-projects/text-api/ENVIRONMENT.md](./04-projects/text-api/ENVIRONMENT.md)
   - [04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
4. 最近一轮交付与规划
   - [03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
   - [06-solution-docs/week-02-text-api-最小可交付拆解.md](./06-solution-docs/week-02-text-api-最小可交付拆解.md)
5. 对外输出素材
   - [05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md](./05-blog-posts/02-专栏总览/2026-04-把-ai-开发练成真本事.md)
   - [05-blog-posts/03-正式文章/01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md](./05-blog-posts/03-正式文章/01-把一个最小%20LLM%20文本%20API%20做出工程感：text-api%20和第一轮收口.md)
   - [07-postmortems/2026-04-minimax-think-output-leak.md](./07-postmortems/2026-04-minimax-think-output-leak.md)

## 当前公开样本

### `text-api`

这是仓库当前的第一个基准项目，用来打通一个最小但像样的 AI 文本处理 API，并用它承载 README、接口契约、调试指南、周报、博客和复盘这一整套交付链路。

项目相关入口：

- 项目入口：[04-projects/text-api/README.md](./04-projects/text-api/README.md)
- 环境与启动：[04-projects/text-api/ENVIRONMENT.md](./04-projects/text-api/ENVIRONMENT.md)
- 项目文档索引：[04-projects/text-api/docs/README.md](./04-projects/text-api/docs/README.md)
- 最近一周交付：[03-weekly-reports/week-01-report.md](./03-weekly-reports/week-01-report.md)
- 下一轮方案：[06-solution-docs/week-02-text-api-最小可交付拆解.md](./06-solution-docs/week-02-text-api-最小可交付拆解.md)
- 对外文章：[05-blog-posts/03-正式文章/01-把一个最小 LLM 文本 API 做出工程感：text-api 和第一轮收口.md](./05-blog-posts/03-正式文章/01-把一个最小%20LLM%20文本%20API%20做出工程感：text-api%20和第一轮收口.md)

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

## 结构分工

这个仓库和普通学习仓库最大的区别，在于它要求每次迭代都留下“完整证据链”。最小闭环不是只有代码，还包括：

- 代码和可运行结果
- 测试与验证记录
- README / 方案文档 / 调试指南
- 周报 / 博客 / postmortem
- 截图、脚本或其他对外展示素材

换句话说，这里把“工程交付”和“内容输出”当成同一件事的两面，而不是开发完成后的附属工作。

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

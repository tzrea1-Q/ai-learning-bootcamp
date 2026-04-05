# text-api Demo 录制脚本与截图清单｜2026-04-05

## 1. 使用说明

- 这份素材分两部分：
  - `1~3` 分钟 demo 录制脚本
  - `5` 张建议截图清单
- 目标用途：
  - 第 1 周周报配图或演示说明
  - 后续博客《从“能跑”到“像样”的工程化收口》素材
- 建议录制方式：
  - 分辨率优先 `1920x1080`
  - 放大终端字号，避免周报里截图字太小
  - 录屏总时长控制在 `90~150` 秒

## 2. Demo 录制脚本

### 2.1 开场镜头（10~15 秒）

- 画面：
  - 打开仓库根目录，聚焦 `04-projects/text-api/README.md`
  - 顺手展示 `docs/traces/`、`07-postmortems/`、`.github/workflows/`
- 讲解词：
  - “这是我第 1 周完成的 `text-api`。这周目标不是做很多功能，而是把一个最小文本 API 从本地跑通，推进到有测试、有文档、有 traces、也有 postmortem 的最小工程闭环。”

### 2.2 展示接口能力（20~30 秒）

- 画面：
  - 在终端或 PowerShell 中依次展示 README 里的本地调试命令
  - 快速调用 `/health`、`/summarize`、`/key-points`、`/rewrite`
- 讲解词：
  - “当前项目已经有四个接口：健康检查、总结、要点提取和改写。这里重点不是业务复杂度，而是先把请求模型、响应模型、上游调用和本地调试链路全部打通。”

### 2.3 展示工程化收口（25~35 秒）

- 画面：
  - 打开 `docs/traces/06-rewrite-回归记录-2026-04-04.md`
  - 再切到 `docs/traces/07-统一错误响应验证记录-2026-04-04.md`
  - 最后切到 `docs/traces/10-request-id-错误响应验证记录-2026-04-05.md`
- 讲解词：
  - “这一周真正花时间的地方是工程化收口：我先对 `rewrite` 做了真实样例回归，再把 `500/502` 错误响应统一下来，最后补了 `request_id` 的最小链路，让错误响应、响应头和日志之间能串起来。”

### 2.4 展示测试与 CI 起点（15~20 秒）

- 画面：
  - 终端运行 `.venv\\Scripts\\python.exe -m pytest`
  - 展示 `.github/workflows/text-api-pytest.yml`
- 讲解词：
  - “除了接口本身，我还补了自动化测试和最小 CI 骨架。现在本地 `pytest` 已经覆盖健康检查、文本接口、错误映射、输入边界和 `request_id`，下一周的重点是把这条流水线真正跑到 GitHub 上。”

### 2.5 收尾镜头（10~15 秒）

- 画面：
  - 打开 `03-weekly-reports/week-01-report.md`
  - 停在“下周最小可交付”部分
- 讲解词：
  - “所以这周的交付，不只是一个能调用 LLM 的接口，更是一套可以继续往下迭代的最小工程基线。下周我会继续补日志链路、超时与重试、CI 跑通和 Docker 稳定化。”

## 3. 建议截图清单

### 截图 1：项目最小闭环总览

- 画面内容：
  - `04-projects/text-api/README.md`
  - 同时能看到 `GET /health`、`POST /summarize`、`POST /key-points`、`POST /rewrite`
- 用途：
  - 周报开头总览图
  - 博客里说明“本周交付范围”

### 截图 2：本地接口实跑结果

- 画面内容：
  - PowerShell 终端
  - 展示一次 `/summarize` 或 `/rewrite` 的真实返回
- 用途：
  - 说明“不是只写了代码，而是本地链路跑通”

### 截图 3：`rewrite` 回归留痕

- 画面内容：
  - `docs/traces/06-rewrite-回归记录-2026-04-04.md`
  - 最好包含“问题现象 / 修正动作 / 修正后结论”中的一段
- 用途：
  - 博客里说明为什么 AI 项目不能只看 happy path

### 截图 4：统一错误响应与 `request_id`

- 画面内容：
  - `docs/traces/10-request-id-错误响应验证记录-2026-04-05.md`
  - 最好包含 `500` 或 `502` 返回体中的 `request_id`
- 用途：
  - 周报或博客里说明“错误契约”和“最小可追踪链路”

### 截图 5：测试或 CI 骨架

- 二选一即可：
  - 终端中的 `12 passed` 测试结果
  - `.github/workflows/text-api-pytest.yml` 文件
- 用途：
  - 说明这周已经开始把项目从“脚本”往“工程”推进

## 4. 建议截图顺序

如果你只打算留 `3` 张图，优先顺序如下：

1. 项目最小闭环总览
2. 统一错误响应与 `request_id`
3. 测试或 CI 骨架

如果你能留 `5` 张图，就按上面的完整顺序来。

## 5. 建议文件命名

- `08-assets/week01-readme-overview.png`
- `08-assets/week01-api-demo.png`
- `08-assets/week01-rewrite-trace.png`
- `08-assets/week01-request-id-error.png`
- `08-assets/week01-pytest-or-ci.png`

## 6. 补充说明

- 如果你今天不录视频，只保留这份脚本和截图清单，也足够满足“周报/博客素材已准备”的要求。
- 如果你晚点录视频，可以直接按这份脚本顺序来，不需要再重新组织讲解结构。


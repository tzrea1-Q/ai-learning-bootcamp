# Text API Environment Setup

这份文件是 `04-projects/text-api` 的统一环境配置入口，既给人看，也给 agent 看。

目标只有两个：

- 让本地开发、测试、联调时的环境配置有一个单一可信入口
- 让 agent 在接手项目时，能直接按这里的约定完成 `.env`、启动和验证

## 1. 先看结论

在 `04-projects/text-api` 目录下执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

然后把 `.env` 至少改成这样：

```env
UPSTREAM_API_KEY=your_real_api_key
UPSTREAM_BASE_URL=https://api.minimaxi.com/v1
UPSTREAM_MODEL=MiniMax-M2.7
UPSTREAM_TIMEOUT_SECONDS=60
UPSTREAM_RETRY_ATTEMPTS=1
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_bootcamp
APP_ENV=dev
LOG_LEVEL=INFO
```

最后启动服务：

```powershell
uvicorn app.main:app --reload
```

## 2. 给 Agent 的执行约定

如果你是 agent，先按下面规则执行，不要自己猜：

1. 工作目录设为 `04-projects/text-api`
2. 优先读取本目录下的 `.env`
3. 如果 `.env` 不存在，就从 `.env.example` 复制一份再补真实值
4. 不要把真实密钥写回 `.env.example`、`README.md` 或任何提交给仓库的文档
5. 运行连通性脚本或本地服务前，先确认虚拟环境和依赖已准备好

当前代码在导入 [`app/openai_compatible_client.py`](E:/ai-learning-bootcamp/04-projects/text-api/app/openai_compatible_client.py) 时会调用 `load_dotenv()`。这意味着：

- 最稳妥的做法，是直接在 `04-projects/text-api` 目录下执行命令
- 如果你从仓库根目录运行命令，必须显式设置工作目录或自己保证 `.env` 可被加载

## 3. 环境变量说明

| 变量名 | 是否必须 | 示例值 | 作用 |
| --- | --- | --- | --- |
| `UPSTREAM_API_KEY` | 是 | `sk-...` | 上游 OpenAI 兼容接口的 API Key |
| `UPSTREAM_BASE_URL` | 是 | `https://api.minimaxi.com/v1` | 上游兼容接口基础地址 |
| `UPSTREAM_MODEL` | 建议显式配置 | `MiniMax-M2.7` | 调用的模型名；不配时当前默认回落到 `MiniMax-M2.7` |
| `UPSTREAM_TIMEOUT_SECONDS` | 否 | `60` | 上游兼容请求超时时间，当前默认 `60` 秒，必须是正数 |
| `UPSTREAM_RETRY_ATTEMPTS` | 否 | `1` | 瞬时网络错误的最大重试次数，当前只对连接失败和超时生效，必须是非负整数 |
| `DATABASE_URL` | 否 | `postgresql://postgres:postgres@localhost:5432/ai_bootcamp` | 预留给后续数据库接入 |
| `APP_ENV` | 否 | `dev` | 运行环境标记，当前主要用于环境识别 |
| `LOG_LEVEL` | 否 | `INFO` | 控制最小日志级别 |

### `UPSTREAM_BASE_URL` 的格式

当前客户端支持两种写法：

- `https://api.minimaxi.com/v1`
- `https://api.minimaxi.com/v1/chat/completions`

如果你只填到 `/v1`，客户端会自动补上 `/chat/completions`。

### 变量命名约定

当前项目只支持 `UPSTREAM_*` 命名：

- `UPSTREAM_API_KEY`
- `UPSTREAM_BASE_URL`
- `UPSTREAM_MODEL`

如果你本地还保留旧变量名，请直接改成以上新名字。

## 4. 推荐的 `.env` 模板

如果你要接任意 OpenAI 兼容供应商，优先从这份模板开始：

```env
UPSTREAM_API_KEY=replace_with_real_key
UPSTREAM_BASE_URL=replace_with_openai_compatible_base_url
UPSTREAM_MODEL=replace_with_model_name
UPSTREAM_TIMEOUT_SECONDS=60
UPSTREAM_RETRY_ATTEMPTS=1

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_bootcamp
APP_ENV=dev
LOG_LEVEL=INFO
```

如果你只是复用当前示例联调值，可以保留：

```env
UPSTREAM_BASE_URL=https://api.minimaxi.com/v1
UPSTREAM_MODEL=MiniMax-M2.7
```

然后只替换 `UPSTREAM_API_KEY`。

## 5. 配完后怎么验证

先跑最小上游连通性脚本：

```powershell
.venv\Scripts\python.exe scripts/test_openai_compatible.py
```

这个脚本如果失败，优先排查这几项：

- `.env` 没生效
- `UPSTREAM_API_KEY` 错了
- `UPSTREAM_BASE_URL` 错了
- 网络不通

通过后再启动服务：

```powershell
uvicorn app.main:app --reload
```

再验证本地接口：

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'
```

## 6. 常见误区

- `.env.example` 只是模板，不是实际运行配置
- `DATABASE_URL` 目前还没接进主流程，不要把接口故障误判成数据库问题
- `APP_ENV` 现在不是功能开关，改它不会改变接口行为
- 如果日志太少，优先提高 `LOG_LEVEL`，不要先去改业务逻辑
- 当前只做保守的有限重试实验：默认最多重试 1 次，而且只对连接失败和超时生效；不要误以为所有 `502` 或所有上游错误都会自动重试

## 7. 相关文件

- [`README.md`](E:/ai-learning-bootcamp/04-projects/text-api/README.md)
- [`docs/04-开发测试调试指南.md`](E:/ai-learning-bootcamp/04-projects/text-api/docs/04-开发测试调试指南.md)
- [`app/openai_compatible_client.py`](E:/ai-learning-bootcamp/04-projects/text-api/app/openai_compatible_client.py)

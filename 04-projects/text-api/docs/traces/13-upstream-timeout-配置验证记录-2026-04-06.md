# upstream timeout 配置验证记录｜2026-04-06

## 1. 背景

本次验证对应 2026-04-06 的第 2 周起步任务：

- 把上游请求的固定 `timeout=60` 收成明确配置项
- 至少补 1 个对应测试或验证场景
- 同步更新 README / 开发调试指南 / 已知问题中的说明

本轮只做最小收口：

- 默认超时时间仍为 `60` 秒
- 支持通过 `UPSTREAM_TIMEOUT_SECONDS` 覆盖
- 非法配置按本地配置错误处理
- 当前不自动启用重试

## 2. 本轮实现范围

代码落点：

- `app/openai_compatible_client.py`

文档落点：

- `ENVIRONMENT.md`
- `README.md`
- `docs/04-开发测试调试指南.md`
- `docs/05-已知问题与后续计划.md`

测试落点：

- `tests/test_openai_compatible_client.py`

## 3. 配置规则

当前上游超时策略如下：

- 环境变量名：`UPSTREAM_TIMEOUT_SECONDS`
- 默认值：`60`
- 读取方式：每次发起上游请求时从环境变量读取
- 合法值：正数
- 非法值：返回本地配置错误，不继续发请求
- 当前边界：只做超时配置，不做自动重试、退避或熔断

## 4. 自动化测试验证

### 4.1 运行命令

```powershell
.venv\Scripts\python.exe -m pytest
```

### 4.2 实际输出

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: E:\ai-learning-bootcamp\04-projects\text-api
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.13.0
collected 16 items

tests\test_health.py .                                                   [  6%]
tests\test_openai_compatible_client.py ....                              [ 31%]
tests\test_text_endpoints.py ...........                                 [100%]

============================= 16 passed in 0.08s ==============================
```

### 4.3 本轮新增验证点

- 默认不配置 `UPSTREAM_TIMEOUT_SECONDS` 时，`requests.post(..., timeout=60.0)` 生效
- 配置 `UPSTREAM_TIMEOUT_SECONDS=7.5` 时，`requests.post(..., timeout=7.5)` 生效
- 配置 `UPSTREAM_TIMEOUT_SECONDS=0` 时，会抛出 `ValueError("UPSTREAM_TIMEOUT_SECONDS must be a positive number")`

## 5. 本地最小验证样例

为了避免依赖真实上游，本轮用 mock 检查 `requests.post` 最终收到的 `timeout` 参数。

### 5.1 自定义超时样例

输入条件：

- `UPSTREAM_TIMEOUT_SECONDS=7.5`

验证结论：

- 上游请求实际拿到 `timeout=7.5`

### 5.2 非法超时样例

输入条件：

- `UPSTREAM_TIMEOUT_SECONDS=0`

验证结论：

- 当前实现不会继续发请求
- 会直接抛出本地配置错误，避免“看起来在重试或卡住，实际是配置本身非法”

## 6. 本轮验收结论

- [x] 固定 `timeout=60` 已收成显式配置项
- [x] 已补自动化测试覆盖默认值、自定义值和非法值
- [x] 已更新环境模板和项目文档说明
- [x] 已明确当前不做自动重试

## 7. 下一步建议

当前超时配置已经可用，但第 2 周还需要继续补：

1. 哪些瞬时错误允许有限重试
2. 重试次数、退避策略和上限如何定义
3. 哪些错误应立即失败，不做掩盖

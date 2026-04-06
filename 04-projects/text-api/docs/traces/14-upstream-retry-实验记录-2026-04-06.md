# upstream retry 实验记录｜2026-04-06

## 1. 背景

本次验证对应 2026-04-06 的可选任务：

- 在超时配置和日志链路都已经落地的前提下
- 补 1 个针对连接失败或读超时的有限重试实验
- 同时把“不重试哪些错误”写进文档，而不是只改代码不写边界

这轮目标不是把客户端做成完整容错系统，只验证一条最小策略：

- 默认最多重试 `1` 次
- 只对 `requests.Timeout` 和 `requests.ConnectionError` 生效
- `requests.HTTPError`、本地配置错误、上游返回结构异常不重试

## 2. 本轮实现范围

代码落点：

- `app/openai_compatible_client.py`

测试落点：

- `tests/test_openai_compatible_client.py`

文档落点：

- `ENVIRONMENT.md`
- `docs/04-开发测试调试指南.md`
- `docs/05-已知问题与后续计划.md`

## 3. 验证方法

本轮用 mock 做最小验证，不依赖真实上游：

1. 第 1 次 `requests.post` 抛出 `requests.Timeout`
2. 第 2 次 `requests.post` 返回最小成功响应
3. 检查最终返回是否成功
4. 检查日志里是否出现“发送 -> 重试 -> 再次发送 -> 成功”的链路

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
collected 19 items

tests\test_health.py .                                                   [  5%]
tests\test_openai_compatible_client.py .......                           [ 42%]
tests\test_text_endpoints.py ............                                [100%]

============================= 19 passed in 0.07s ==============================
```

### 4.3 本轮新增验证点

- 超时后会触发 1 次有限重试
- `requests.HTTPError` 不会进入重试
- 非法 `UPSTREAM_RETRY_ATTEMPTS` 会作为本地配置错误直接失败

## 5. 本地最小实验样例

### 5.1 模拟条件

- `UPSTREAM_RETRY_ATTEMPTS=1`
- 第 1 次请求抛出 `requests.Timeout("read timed out")`
- 第 2 次请求返回最小成功响应

### 5.2 关键日志

```text
INFO | app.openai_compatible_client | Sending upstream chat completion request: request_id=req-retry-001 path=/summarize task=summarize url=https://api.minimaxi.com/v1/chat/completions timeout_seconds=60.0 attempt=1/2
WARNING | app.openai_compatible_client | Retrying upstream chat completion request: request_id=req-retry-001 path=/summarize task=summarize attempt=1/2 retryable_error=Timeout detail=read timed out
INFO | app.openai_compatible_client | Sending upstream chat completion request: request_id=req-retry-001 path=/summarize task=summarize url=https://api.minimaxi.com/v1/chat/completions timeout_seconds=60.0 attempt=2/2
INFO | app.openai_compatible_client | Upstream chat completion request succeeded: request_id=req-retry-001 path=/summarize task=summarize attempt=2/2 status_code=200 response_id=resp_123 model=test-model
```

### 5.3 验证结论

- 第 1 次超时后确实触发了 1 次有限重试
- 第 2 次请求成功后立即返回，不再继续额外重试
- 日志已经能清楚区分“首次发送”“进入重试”“重试后成功”

## 6. 当前明确不重试的错误

- `requests.HTTPError`
- 本地配置错误，例如 `UPSTREAM_TIMEOUT_SECONDS` 或 `UPSTREAM_RETRY_ATTEMPTS` 非法
- 上游返回结构异常，例如 `choices[0].message.content` 缺失
- 业务层清洗后的空响应或格式错误

原因：

- 这些错误要么不是瞬时网络问题，要么重试收益很低，反而容易掩盖真实问题

## 7. 本轮结论

- [x] 已完成 1 个针对超时的有限重试实验
- [x] 已补自动化测试覆盖“重试”和“不重试”的边界
- [x] 已把不重试的错误类型写进文档
- [x] 当前实现仍保持保守，没有继续引入退避、抖动或熔断

## 8. 下一步建议

如果后续继续推进，可以按这个顺序：

1. 先决定是否要对 `429` 或上游临时 `5xx` 做单独分类
2. 再决定是否加入退避，而不是立即重试
3. 最后再考虑把“重试后成功 / 失败”沉淀成更细的可观测指标

# Docker PostgreSQL 骨架验证记录｜2026-04-04

## 1. 背景

本次验证的目标不是把数据库正式接进业务链路，而是确认 `text-api` 里预留的 PostgreSQL / Docker 骨架至少满足下面三件事：

1. `docker-compose.yml` 结构可解析
2. `DATABASE_URL` 和容器配置没有明显脱节
3. README 与实际启动命令保持一致

## 2. 验证对象

- Compose 文件：`docker-compose.yml`
- 环境变量模板：`.env.example`
- 项目文档：`README.md`
- 调试文档：`docs/04-开发测试调试指南.md`

## 3. 验证命令

```powershell
docker compose version
docker compose config
docker compose up -d postgres
docker compose ps
docker compose logs postgres --tail 20
docker exec ai_bootcamp_postgres pg_isready -U postgres -d ai_bootcamp
docker compose down
```

## 4. 配置一致性检查

### 4.1 `docker-compose.yml`

当前 PostgreSQL 容器配置为：

- image: `postgres:16`
- user: `postgres`
- password: `postgres`
- db: `ai_bootcamp`
- port: `5432:5432`

### 4.2 `.env.example`

当前 `DATABASE_URL` 为：

```text
postgresql://postgres:postgres@localhost:5432/ai_bootcamp
```

与 Compose 文件中的：

- 用户名 `postgres`
- 密码 `postgres`
- 数据库名 `ai_bootcamp`
- 端口 `5432`

是一致的。

### 4.3 文档一致性

本轮发现 1 处脱节并已修正：

- `.env.example` 中 `UPSTREAM_BASE_URL` 原本写成 `https://api.minimax.io/v1`
- README 和当前实际调用链路使用的是 `https://api.minimaxi.com/v1`

已在本轮修正为：

```text
UPSTREAM_BASE_URL=https://api.minimaxi.com/v1
```

## 5. 实际验证结果

### 5.1 `docker compose version`

```text
Docker Compose version v5.1.1
```

### 5.2 `docker compose config`

结论：

- Compose 文件可以被正确解析
- 服务名、端口、volume 和默认 network 都能正常展开

关键结果：

```text
name: text-api
services:
  postgres:
    container_name: ai_bootcamp_postgres
    environment:
      POSTGRES_DB: ai_bootcamp
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
    image: postgres:16
```

### 5.3 `docker compose up -d postgres`

实际结果：

```text
unable to get image 'postgres:16': failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

结论：

- 当前阻塞点不在 Compose 文件本身
- 当前机器上的 Docker daemon 没启动，因此无法真正拉起容器

### 5.4 `docker compose ps / logs / pg_isready`

由于容器未成功启动，这三步本轮无法继续验证。

## 6. 本轮判断

- [x] `docker-compose.yml` 结构可解析
- [x] `DATABASE_URL` 与 Compose 里的 PostgreSQL 配置一致
- [x] README 和调试文档已改成一致的启动命令 `docker compose up -d postgres`
- [ ] 本机已成功拉起 PostgreSQL 容器
- [ ] 已通过 `pg_isready` 验证数据库就绪

## 7. 结论

从项目配置角度看，PostgreSQL Docker 骨架是成立的，没有发现 Compose、环境变量和 README 之间的结构性脱节。

当前未完成的部分是运行环境问题：

- Docker Desktop / Docker daemon 未启动

这意味着“项目骨架没问题”，但“本机还没有具备完整验证条件”。

## 8. 后续动作

下一次继续验证前，先完成这 2 步：

1. 启动 Docker Desktop 或 Docker daemon
2. 重新执行 `docker compose up -d postgres`、`docker compose ps`、`pg_isready`



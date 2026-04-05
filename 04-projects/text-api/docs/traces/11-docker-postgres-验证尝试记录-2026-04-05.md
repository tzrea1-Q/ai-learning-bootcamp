# Docker PostgreSQL 验证记录｜2026-04-05

## 1. 背景

本次尝试对应 2026-04-05 的可选任务：

- 如果 Docker 环境可用，重新执行 `docker compose up -d postgres`
- 执行 `docker compose ps`
- 执行 `pg_isready`
- 补 1 份真实成功验证记录

本轮目标是确认今天是否已经满足“真实成功验证”的前提条件，并在环境恢复可用后补齐成功结果。

## 2. 实际执行命令

在 `04-projects/text-api` 目录下执行：

```powershell
docker version
docker compose up -d postgres
docker compose ps
docker exec ai_bootcamp_postgres pg_isready -U postgres -d ai_bootcamp
```

## 3. 第一次尝试：Docker Engine 尚未就绪

### 3.1 `docker version`

```text
Client:
 Version:           29.3.1
 API version:       1.54
 Go version:        go1.25.8
 Git commit:        c2be9cc
 Built:             Wed Mar 25 16:16:33 2026
 OS/Arch:           windows/amd64
 Context:           desktop-linux
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### 3.2 `docker compose up -d postgres`

```text
unable to get image 'postgres:16': failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### 3.3 `docker compose ps`

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### 3.4 第一次尝试结论

- Docker CLI 已安装，`docker version` 可以输出 client 信息。
- 当时 Docker Desktop Linux engine 尚未就绪，具体表现为无法连接 `//./pipe/dockerDesktopLinuxEngine`。
- 因为 daemon 未启动，`postgres` 容器无法拉起，`docker compose ps` 也无法返回有效服务状态。
- 在这个前提下，本轮不能执行 `pg_isready`，也不能伪造“成功验证记录”。

## 4. 第二次尝试：Docker Engine 恢复可用并验证成功

### 4.1 `docker version`

```text
Client:
 Version:           29.3.1
 API version:       1.54
 Go version:        go1.25.8
 Git commit:        c2be9cc
 Built:             Wed Mar 25 16:16:33 2026
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.67.0 (222858)
 Engine:
  Version:          29.3.1
  API version:      1.54 (minimum version 1.40)
  Go version:       go1.25.8
  Git commit:       f78c987
  Built:            Wed Mar 25 16:13:48 2026
  OS/Arch:          linux/amd64
  Experimental:     false
```

### 4.2 `docker compose up -d postgres`

```text
 Container ai_bootcamp_postgres Starting
 Container ai_bootcamp_postgres Started
```

### 4.3 `docker compose ps`

```text
NAME                   IMAGE         COMMAND                  SERVICE    CREATED      STATUS          PORTS
ai_bootcamp_postgres   postgres:16   "docker-entrypoint.s…"   postgres   5 days ago   Up 17 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```

### 4.4 `pg_isready`

```text
/var/run/postgresql:5432 - accepting connections
```

### 4.5 第二次尝试结论

- Docker engine 后续恢复可用，CLI 已能拿到 server 信息。
- `postgres` 容器已成功启动，并稳定处于 `Up` 状态。
- `pg_isready` 已返回 `accepting connections`，说明 PostgreSQL 已可接受连接。
- 这次任务在第二次尝试后已满足“真实成功验证记录”的要求。

## 5. 最终结论

- 2026-04-05 的 Docker 验证不是单次直达成功，而是“先阻塞、后成功”的真实过程。
- 根因不是 `docker-compose.yml` 配置错误，也不是当前用户权限问题。
- 更接近的原因是：第一次执行时 Docker Desktop Linux engine 尚未完全就绪，CLI 提前访问了 pipe。
- 在 engine 可用后，`docker compose up -d postgres`、`docker compose ps` 和 `pg_isready` 都已成功。

## 6. 下一步建议

1. 先确认 Docker Desktop 或对应 Linux Engine 是否已启动。
2. daemon 恢复可用后，重新执行：

```powershell
docker compose up -d postgres
docker compose ps
docker exec ai_bootcamp_postgres pg_isready -U postgres -d ai_bootcamp
```

3. 如果下次再遇到 pipe 不存在的问题，先执行 `docker version`，确认是否已经出现 `Server:` 段，再继续跑 Compose 和探活命令。


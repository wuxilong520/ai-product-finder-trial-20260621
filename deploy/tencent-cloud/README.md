# 腾讯云部署包

这个目录是给腾讯云服务器直接用的。现在已经统一为**单一生产部署入口**，后面只走这一套。

## 目录说明

- `frontend.Dockerfile`：前端镜像构建
- `backend.Dockerfile`：后端镜像构建
- `nginx.conf`：前后端反向代理
- `.env.tencent.example`：腾讯云环境变量模板
- `deploy.sh`：一键启动命令
- `check.sh`：部署后真实自检命令
- `repair-docker-runtime.sh`：腾讯云 Docker 构建异常时的修复命令

## 一、服务器准备

建议腾讯云服务器开放：

- `80`
- `443`

如果数据库不在本机，再确认数据库白名单和网络放通。

## 二、复制环境变量

先进入这个目录：

```bash
cd /root/publish_repo/deploy/tencent-cloud
```

复制模板：

```bash
cp .env.tencent.example .env.tencent
```

然后把下面这些值改成真实值：

- `OPENAI_API_KEY`
- `DATABASE_URL`
- `BACKEND_URL`
- `FRONTEND_URL`
- `FRONTEND_ORIGIN`
- `WS_URL`
- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_WS_URL`

## 三、修改域名

你需要把 `nginx.conf` 里的：

- `your-domain.com`
- `www.your-domain.com`
- `api.your-domain.com`

全部改成你的真实域名。

## 四、启动

现在推荐只用这一个命令：

```bash
chmod +x deploy.sh
./deploy.sh
```

这份脚本会自动做 4 件事：

- 先备份当前 SQLite 数据库
- 先清理旧版 `docker-compose` 留下的脏容器
- 重新构建后端镜像
- 重新构建前端镜像
- 按固定容器名重启公网服务
- 自动执行真实自检

这样可以避开旧版 `docker-compose` 在腾讯云机器上的兼容问题。

### 重要规则

以后腾讯云**不要再手动执行**：

```bash
docker-compose up
docker-compose build
docker compose up
docker compose build
```

统一只执行：

```bash
./deploy.sh
```

因为当前腾讯云机器上的旧 `docker-compose` 和新 Docker 版本混用时，容易留下脏容器状态，导致前端重建失败。

### 前台单独发布

如果这次只是前台页面改动，而后端没有改，可以直接这样发：

```bash
BUILD_BACKEND=0 ./deploy.sh
```

这样会：

- 跳过后端镜像重建
- 只重建前端
- 继续复用当前后端镜像

这套方式适合：

- 修页面
- 修按钮跳转
- 修登录页 / 注册页
- 修充值入口

这样可以避开腾讯云这台机器偶发的后端大镜像构建失败问题。

## 五、部署完成后检查

标准检查命令：

```bash
./check.sh
```

这一步会真实检查：

- 三个核心容器是否在运行
- 是否还有旧版遗留容器
- 后端 `/health` 是否正常
- 前端 `/login` 是否正常
- 当前运行容器携带的版本标签

## 六、如果腾讯云 Docker 构建报错怎么办

如果你看到这类真实报错：

- `failed to export layer`
- `failed to commit`
- `containerd ... no such file or directory`

不要再用旧命令反复重试，直接执行：

```bash
./repair-docker-runtime.sh
./deploy.sh
```

这套修复会做几件事：

- 清掉异常退出的临时构建容器
- 清掉无用构建缓存
- 清掉 containerd 的临时挂载残留
- 尝试补装更稳定的 `buildx`

## 七、HTTPS 说明

这份配置先走 `80` 端口。

如果你要正式公网使用，建议：

- 用腾讯云负载均衡或 CDN 配 HTTPS
- 或者你自己在 Nginx 上补证书配置

## 八、当前设计

前端不会再显示：

- 系统管理
- API 地址
- WS 地址
- 数据库状态
- AI 服务状态
- 环境变量状态

前端现在只保留业务页面。

## 九、以后怎么自动同步

仓库里已经预留了 GitHub Actions 自动部署文件：

- `.github/workflows/tencent-cloud-deploy.yml`

只要你把下面 4 个 GitHub Secrets 配好：

- `TENCENT_CLOUD_HOST`
- `TENCENT_CLOUD_PORT`
- `TENCENT_CLOUD_USER`
- `TENCENT_CLOUD_PATH`
- `TENCENT_CLOUD_SSH_KEY`

以后每次代码推送到 `main`：

- GitHub 仓库会先更新
- Actions 会自动 SSH 到腾讯云
- 服务器会自动切到最新 `main`
- 然后自动执行 `deploy/tencent-cloud/deploy.sh`
- 最后自动执行 `deploy/tencent-cloud/check.sh`

也就是说，后面要保持“仓库 + 公网”同步，标准动作就是：

```bash
git add .
git commit -m "你的更新说明"
git push origin main
```

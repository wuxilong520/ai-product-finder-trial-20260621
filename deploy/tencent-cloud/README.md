# 腾讯云部署包

这个目录是给腾讯云服务器直接用的。

## 目录说明

- `docker-compose.yml`：三服务启动文件
- `frontend.Dockerfile`：前端镜像构建
- `backend.Dockerfile`：后端镜像构建
- `nginx.conf`：前后端反向代理
- `.env.tencent.example`：腾讯云环境变量模板
- `deploy.sh`：一键启动命令

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
- 重新构建后端镜像
- 重新构建前端镜像
- 按固定容器名重启公网服务

这样可以避开旧版 `docker-compose` 在腾讯云机器上的兼容问题。

## 五、部署完成后检查

前端：

- `http://your-domain.com/login`

后端：

- `http://api.your-domain.com/health`

## 六、HTTPS 说明

这份配置先走 `80` 端口。

如果你要正式公网使用，建议：

- 用腾讯云负载均衡或 CDN 配 HTTPS
- 或者你自己在 Nginx 上补证书配置

## 七、当前设计

前端不会再显示：

- 系统管理
- API 地址
- WS 地址
- 数据库状态
- AI 服务状态
- 环境变量状态

前端现在只保留业务页面。

## 八、以后怎么自动同步

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
- 服务器会自动拉到最新 `main`
- 然后自动执行 `deploy/tencent-cloud/deploy.sh`

也就是说，后面要保持“仓库 + 公网”同步，标准动作就是：

```bash
git add .
git commit -m "你的更新说明"
git push origin main
```

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

```bash
chmod +x deploy.sh
./deploy.sh
```

或者直接：

```bash
docker compose --env-file ./.env.tencent up -d --build
```

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


# 腾讯云部署说明

## 一、部署目标

- 前端部署到腾讯云
- 后端部署到腾讯云
- 前端不再显示任何系统设置、后端状态、API/WS 地址
- 前端只通过环境变量连接后端

## 二、推荐域名结构

- 前端：`https://your-domain.com`
- 后端：`https://api.your-domain.com`

## 三、必须配置的环境变量

前端：

- `NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com`
- `NEXT_PUBLIC_WS_URL=wss://api.your-domain.com/ws`

后端：

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_URL=postgresql+psycopg://username:password@host:5432/product_mvp`
- `OPENAI_API_KEY=你的真实key`
- `OPENAI_MODEL=gpt-4o-mini`
- `OPENAI_BASE_URL=`（如果腾讯云服务器不能直连 OpenAI，这里填可用的兼容网关地址）
- `DEEPSEEK_API_KEY=`（如果你改走 DeepSeek，可直接配置这里）
- `BACKEND_URL=https://api.your-domain.com`
- `FRONTEND_URL=https://your-domain.com`
- `FRONTEND_ORIGIN=https://your-domain.com`
- `WS_URL=wss://api.your-domain.com/ws`
- `SECRET_KEY=一串足够长的随机密钥`
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- `JWT_ALGORITHM=HS256`
- `FIRST_SUPERUSER_EMAIL=admin@example.com`
- `FIRST_SUPERUSER_PASSWORD=你自己的密码`

## 四、前端部署

项目目录：

- `publish_repo/frontend`

构建命令：

```bash
pnpm install
pnpm build
```

启动命令：

```bash
pnpm start
```

## 五、后端部署

项目目录：

- `publish_repo/backend`

安装命令：

```bash
pip install -r requirements.txt
playwright install chromium
```

启动命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 六、反向代理建议

Nginx 建议：

- `your-domain.com` -> 前端服务
- `api.your-domain.com` -> 后端 `8000`
- 开启 HTTPS
- WebSocket 路由 `/ws` 必须放行升级头

## 七、主仓自动部署规则

- 国内主仓：Gitee
- 国外备份仓：GitHub
- 腾讯云服务器每分钟检查一次 Gitee `main`
- 发现以下任一变化后会自动：
  - Gitee `main` 有新提交
  - 生产环境文件 `deploy/tencent-cloud/.env.tencent` 内容发生变化
- 自动动作：
  - 拉取 Gitee 最新代码
  - 同步 GitHub 备份仓
  - 执行 `deploy/tencent-cloud/deploy.sh`
- 自动部署状态文件：
  - `/home/ubuntu/publish_repo_runtime/state/last_deployed_commit`
  - `/home/ubuntu/publish_repo_runtime/state/last_env_hash`
- 自动检查日志位置：
  - `/home/ubuntu/publish_repo/logs/auto-deploy.log`
  - 实际运行文件已迁移到 `/home/ubuntu/publish_repo_runtime/auto-deploy.log`

本地标准更新动作：

```bash
./scripts/push-primary-then-backup.sh
```

## 八、上线前检查

- 前端 `.env` 已填真实公网 API 地址
- 后端 CORS 已允许前端域名
- 数据库公网或内网已连通
- OpenAI key 可正常使用
- `https://your-domain.com/login` 可打开
- `https://api.your-domain.com/health` 可返回成功

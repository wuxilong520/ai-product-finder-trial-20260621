## 公网访问固定规则

- 后端监听地址：`0.0.0.0`
- 后端默认端口：`8000`
- 前端生产环境只能通过 `NEXT_PUBLIC_API_BASE_URL` 访问后端
- WebSocket 生产环境只能通过 `NEXT_PUBLIC_WS_URL` 访问

## 必填生产环境变量

- `BACKEND_URL`
- `FRONTEND_URL`
- `FRONTEND_ORIGIN`
- `WS_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_WS_URL`

## 开发和生产的区别

- 开发环境：允许回退到本机地址，方便本地联调
- 生产环境：必须使用公网域名，不能依赖 `localhost` 或 `127.0.0.1`

## 当前项目状态

- FastAPI 已按公网监听方式配置
- CORS 已允许所有来源
- 前端 API 已走环境变量
- 前端 WS 地址已预留环境变量入口

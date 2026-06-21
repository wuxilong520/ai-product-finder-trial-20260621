# Deployment Network Report

## 审计范围

检查目录：`/Users/Admin/Documents/商品上传/publish_repo`

本次只检查“最终上线前部署条件”，重点看公网访问、跨域、cookie、环境变量和外部接口调用条件。

---

## 1. frontend 是否必须依赖 localhost

### 代码检查结果

前端主请求封装文件：

- `frontend/lib/api.ts`

当前逻辑：

- 生产环境主要走 `NEXT_PUBLIC_API_BASE_URL`
- 生产环境主要走 `NEXT_PUBLIC_WS_URL`
- 如果生产环境缺少 `NEXT_PUBLIC_API_BASE_URL`，`EnvGuard` 会直接报配置错误，不会假装可用

### 当前发现

仍然存在开发兜底：

- `http://127.0.0.1:8000`
- `ws://127.0.0.1:8000/ws`

但这个兜底只在：

- `process.env.NODE_ENV === "development"`

时才会启用。

### 结论

- **前端不必须依赖 localhost 才能部署**
- **生产环境不依赖 localhost**
- **开发环境仍保留本机兜底，属于开发方便，不是部署阻断项**

---

## 2. backend 是否必须依赖 127.0.0.1

### 检查结果

后端启动脚本：

- `backend/start.sh`

实际启动方式：

- `uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"`

说明：

- 后端不是只监听本机回环地址
- 后端已经支持外部网络访问

### 实测结果

后端真实启动成功：

- `Uvicorn running on http://0.0.0.0:8015`

### 结论

- **backend 不依赖 127.0.0.1**
- **具备公网监听条件**

---

## 3. 是否所有 API 都支持跨域访问

### 代码检查结果

FastAPI CORS 配置：

- `allow_origins=["*"]`
- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

### 实测结果

对以下接口做了真实预检验证：

- `OPTIONS /api/v1/products/extract`
- `OPTIONS /api/v1/products/analyze`

返回结果包含：

- `access-control-allow-origin: https://example-client.com`
- `access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT`
- `access-control-allow-headers: authorization,content-type`
- `access-control-allow-credentials: true`

### 结论

- **API 跨域访问条件已具备**
- **外部前端调用后端 API 没有被 CORS 卡住**

---

## 4. cookie / session 是否支持跨域域名

### 当前实现

前端登录态保存在 cookie：

- key: `cbp_access_token`
- `path=/`
- `SameSite=Lax`
- HTTPS 下自动追加 `Secure`

### 检查结果

- 没有把 cookie 绑定到 `localhost`
- 没有把 cookie 绑定到 `127.0.0.1`
- 更适合部署到真实域名后使用

### 结论

- **cookie 逻辑支持公网域名使用**
- **不会因为写死 localhost 导致部署后登录失效**

---

## 5. API 外部调用条件检查

### `/health`

实测：`200 OK`

说明：

- 可直接被外部检测系统或前端状态面板访问

### `/auth/login`

实测：`200 OK`

说明：

- 可被外部前端正常调用

### `/products/extract`

实测：`200 OK`

示例返回：

- `status: OK`
- `title: Example Domain`

说明：

- 公开 extract 接口支持外部访问

### `/products/analyze`

实测：接口可访问，但当前返回：`502 Bad Gateway`

返回体：

- `error_code: AI_CALL_FAILED`
- `stage: ai`
- 真实原因：`insufficient_quota`

说明：

- 不是公网访问被挡住
- 不是跨域问题
- 是当前 OpenAI 配额不足

---

## 网络层总结

### 已通过

- frontend 生产模式不依赖 localhost
- backend 生产监听不依赖 127.0.0.1
- API CORS 可用
- cookie 支持公网域名
- `/health` / `/login` / `/extract` 外部调用条件成立

### 当前阻断项

- `/analyze` 真实被 OpenAI quota 卡住

### 网络层结论

**网络与公网访问条件基本通过**  
**当前主要阻断不是网络，而是 AI 配额**

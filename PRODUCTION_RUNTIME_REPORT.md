# Production Runtime Report

## 1. backend 是否可启动

- **结果：可以**
- 实际启动方式：
  - 使用 `/Users/Admin/Documents/商品上传/publish_repo/backend/.venv`
  - 使用 Python 3.12
  - 实际成功启动：
    - `uvicorn app.main:app --host 127.0.0.1 --port 8000`

### 运行前修复

- 修复了 `backend/requirements.txt`
  - `psycopg[binary]==3.2.1` → `psycopg[binary]==3.2.13`
- 原因：
  - 旧版本在当前环境装不上
- 重新创建了后端虚拟环境
- 安装了 Playwright Chromium

### 实际健康检查结果

请求：

`GET http://127.0.0.1:8000/health`

响应：

```json
{
  "status": "ok",
  "version": "v2",
  "env_status": {
    "app_env": "development",
    "backend_url": true,
    "frontend_url": true,
    "frontend_origin": true,
    "ws_url": true,
    "next_public_api_base_url": true,
    "next_public_ws_url": true
  },
  "services": {
    "database": "ok",
    "ai": "ok",
    "crawler": "ok"
  }
}
```

---

## 2. frontend 是否可启动

- **结果：没有完全成功**

### 实际问题

- 前端依赖安装过程中，公网 DNS 多次失败
- 后来改回官方源后，`pnpm` 继续执行时又卡在：
  - `ERR_PNPM_IGNORED_BUILDS`
  - 被拦的是 `sharp@0.34.5`

### 结论

- 前端代码本身这次没有发现新的运行报错证据
- 但 **这次真实验收里，前端没有成功完整启动**

---

## 3. 登录验证

请求：

`POST http://127.0.0.1:8000/api/v1/auth/login`

表单：

- username=`admin@example.com`
- password=`admin123456`

结果：

- **成功**

响应摘要：

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@example.com"
  }
}
```

---

## 4. 商品采集接口验证

请求：

`POST http://127.0.0.1:8000/api/v1/products/crawl`

测试 URL：

`https://kyliecosmetics.com/products/matte-lip-kit`

结果：

- **成功**
- 返回了：
  - `product_id`
  - `title`
  - `price`
  - `images`
  - `rating`
  - `reviews`
  - `url`

### 实际响应要点

- `product_id`: `1`
- `title`: `Matte Lip Kit`
- `images`: 有真实图片链接
- `url`: 正确

### 发现的问题

- `price` 字段抓到了大量页面正文，不是干净价格
- `rating` 抓成了 `(4945)`
- `current_price` 入库后变成了 `1`
- `rating` 入库后变成了 `4945`

### 结论

- **采集链路是通的**
- **但字段清洗明显有问题**

---

## 5. AI 分析接口验证

请求：

`POST http://127.0.0.1:8000/api/v1/products/analyze`

请求体：

```json
{
  "product_id": 1
}
```

结果：

- **接口有响应**
- **没有 500**
- **但 AI 实际调用失败**

响应：

```json
{
  "success": false,
  "error_code": "AI_CALL_FAILED",
  "message": "Error code: 429 - insufficient_quota",
  "stage": "ai"
}
```

### 结论

- AI 调用是真实调用，不是 mock
- 失败原因是：
  - **OpenAI 额度不足（429 insufficient_quota）**

---

## 6. task status flow 验证

### crawl 状态

采集前：

```json
{
  "success": true,
  "status": "idle",
  "message": "采集任务空闲中"
}
```

采集后：

```json
{
  "success": true,
  "status": "success",
  "message": "采集完成",
  "detail": {
    "url": "https://kyliecosmetics.com/products/matte-lip-kit",
    "product_id": 1
  }
}
```

### analyze 状态

分析前后都还是：

```json
{
  "success": true,
  "status": "idle",
  "message": "分析任务空闲中"
}
```

### 结论

- `crawl` 状态流：**通过**
- `analyze` 状态流：**没有完整更新**
- 也就是说：
  - 分析接口失败时，没有把任务状态切到 `error`

---

## 7. WebSocket 真实验证

连接地址：

`ws://127.0.0.1:8000/ws/crawl`

### 实际日志

```text
WS_CONNECT ws://127.0.0.1:8000/ws/crawl
WS_MSG_1 {"success":true,"status":"success","message":"采集完成",...}
WS_MSG_2 {"success":true,"status":"running","message":"正在采集商品页面",...}
WS_MSG_3 {"success":true,"status":"success","message":"采集完成",...}
```

### 结论

- **WebSocket 真实可连**
- **真实有推送**
- 顺序上先收到旧状态、再收到新运行状态、再收到成功状态
- 说明：
  - WS 功能是通的
  - 但第一次连接会先拿到旧缓存状态

---

## 8. polling fallback 验证

- 已验证存在：
  - `GET /task-status/{task_name}`
- 前端代码里已有轮询降级逻辑
- 但因为前端这次没成功启动，
  - **这次没有完成浏览器侧真实轮询切换验收**

---

## 9. 数据库一致性验证

实际读取 SQLite：

### products

```text
id=1
title=Matte Lip Kit
title_zh=None
source_url=https://kyliecosmetics.com/products/matte-lip-kit
current_price=1
review_count=7112
rating=4945
```

### ai_analysis_results

- **没有新增记录**

### sourcing_links

- **没有新增记录**

### 结论

- crawl → db 写入：**成功**
- analyze → db 更新：**失败**
- 没有脏空行爆炸，但有 **脏字段值**
  - 价格错
  - 评分错

---

## 10. 是否完成完整链路

### backend 链路

- 登录：**成功**
- 健康检查：**成功**
- 商品采集：**成功**
- 数据库写入：**成功**
- WebSocket：**成功**
- AI 分析：**失败（429 quota）**

### frontend 链路

- **未完成真实启动**

---

## 11. 是否存在断点

- **有**

### 断点 1

- 前端未成功真实启动
- 原因：
  - `pnpm` 安全拦截 `sharp` 构建脚本
  - 此次没有完成 UI 实机验收

### 断点 2

- AI 分析失败
- 原因：
  - OpenAI 配额不足

### 断点 3

- 采集字段清洗不准确
- 影响：
  - 价格、评分等关键数据不可靠

### 断点 4

- analyze 失败时 task status 没更新成 error

---

## 12. 是否 production ready

- **结论：NO**

### 原因

1. 前端本次未完成真实启动
2. AI 真调用失败（额度问题）
3. 采集结果字段清洗不稳定
4. analyze 状态流异常时未完整落地

---

## 总结

- **backend 可启动：YES**
- **frontend 可启动：NO（本次未跑通）**
- **完整链路：NO**
- **主要断点：前端启动、AI quota、采集字段清洗**
- **production ready：NO**


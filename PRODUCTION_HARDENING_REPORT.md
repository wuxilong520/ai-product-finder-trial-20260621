# Production Hardening Report

## 修改文件列表

- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/core/config.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/core/startup_checks.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/main.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/ws_manager.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/services/task_status.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/api/deps.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/core/security.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/services/auth.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/api/v1/endpoints/auth.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/api/v1/endpoints/products.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/api/v1/endpoints/analyze.py`
- `/Users/Admin/Documents/商品上传/publish_repo/backend/app/services/product.py`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/lib/api.ts`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/lib/types.ts`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/app/layout.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/app/page.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/app/dashboard/page.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/app/crawl/page.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/app/analyze/page.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/components/products/crawl-panel.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/components/products/analyze-panel.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/components/system/system-status-panel.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/components/system/env-guard.tsx`
- `/Users/Admin/Documents/商品上传/publish_repo/frontend/hooks/use-task-status.ts`

## 新增机制说明

### 1. 启动环境变量校验

- 后端启动时现在会强制检查：
  - `BACKEND_URL`
  - `FRONTEND_URL`
  - `FRONTEND_ORIGIN`
  - `WS_URL`
  - `NEXT_PUBLIC_API_BASE_URL`
  - `NEXT_PUBLIC_WS_URL`
- 缺任何一个，后端会直接启动失败，并给出明确报错。

### 2. 健康检查

- 新增 `/health`
- 返回内容包括：
  - 系统状态
  - 版本
  - 环境变量是否配齐
  - 数据库状态
  - AI 服务状态
  - 采集器状态

### 3. API 统一错误格式

- 统一返回：

```json
{
  "success": false,
  "error_code": "",
  "message": "",
  "stage": ""
}
```

- 登录、鉴权、商品不存在这类错误，已经尽量统一到这一套。

### 4. WebSocket + 自动降级

- 后端新增：
  - `/ws/{task_name}`
  - `/task-status/{task_name}`
- 前端会优先走 WebSocket 实时看任务状态。
- 如果 WebSocket 连不上，会自动切到轮询模式，不会静悄悄失效。

### 5. 前端部署保护

- 生产环境如果没配 `NEXT_PUBLIC_API_BASE_URL`
- 前端会直接显示错误页，不再出现“页面能打开但点什么都没反应”的假正常情况。

### 6. 系统状态面板

- 首页、商品列表页、采集页、分析页都加了系统状态面板。
- 可以直接看到：
  - API 地址
  - WS 地址
  - 当前环境
  - 数据库状态
  - AI 状态
  - 采集器状态

## 当前是否达到 production ready

- **结论：部分达到，还不是完全生产可交付。**

### 已达到的部分

- 启动前自检更完整
- 报错不再乱飞
- 前端不会 silent fail
- 任务状态能实时看，WS 不通也有兜底
- 部署时更容易发现配置问题

### 还没完全达到的部分

- 当前机器里缺少后端运行依赖，没法在这里完成最终真实启动验证
- AI 服务你之前明确说先跳过额度检查，所以这里只做了状态检测，没有做真实调用验收
- WebSocket 已落代码，但还没在真实公网环境做连通验收

## 风险点列表

### P0

- 当前本地环境缺少 `fastapi`，所以这次没法在这里直接把后端真正跑起来验收

### P1

- 如果云端没装 Playwright 相关依赖，`crawler` 会在 `/health` 中显示 fail
- 如果没配 `OPENAI_API_KEY`，AI 状态会显示 fail
- `analyze/full/public` 还保留了“系统忙稍后再试”的试用返回，不适合当完全严格的真实 AI 成功证明

### P2

- 前端开发环境仍保留了 `127.0.0.1` 的开发兜底地址，这个是开发方便用，不影响生产


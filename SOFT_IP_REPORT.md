# 软件著作权申报前校验报告

> 说明：本报告仅依据当前项目代码结构与真实引用关系整理，不包含预测功能、不包含未接入功能、不包含未来规划。

## 1. 当前系统真实功能清单

- **用户认证模块**：支持管理员账号注册、登录、读取当前用户信息；前端当前实际接入登录功能。
- **首页营销与公开试用模块**：首页支持输入商品 URL 进行公开分析；`/product-demo` 页面支持试用分析与示例 URL 测试。
- **商品采集模块**：支持输入商品 URL，调用真实采集接口抓取标题、价格、评分、评论数、图片，并保存为商品记录。
- **商品列表模块**：支持读取商品列表、按关键词搜索、单个删除、批量删除。
- **商品详情模块**：支持查看单个商品的基础信息、图片、已保存的 AI 分析结果与采购链接（如果数据库已有）。
- **商品分析模块**：支持对公开商品 URL 进行一键分析，输出分数、推荐结论、利润估算、竞争等级、原因、采购链接。
- **公开提取模块**：后端支持只做商品页面提取，返回标题、价格、评分、评论数、图片等结构化字段。
- **AI 标题分析模块**：后端支持基于商品标题调用 OpenAI，输出中文标题、核心关键词、卖点、拿货关键词。
- **商品智能评分模块**：后端支持基于商品标题、价格、图片、评分、评论数、来源 URL 调用 OpenAI 输出选品评分与建议。
- **规则降级模块**：当 AI 分析失败时，后端会返回规则模型降级结果（`FALLBACK`），而不是直接崩溃。
- **任务状态模块**：维护 `crawl` 与 `analyze` 两类任务状态，支持 pending / running / success / error / blocked 状态读取。
- **Dashboard 概览模块**：支持读取商品总数、启用商品数、采集任务数、分析结果数、最新商品、类目统计、近 7 天趋势、任务状态、数据源状态。
- **实时刷新模块**：前端已接入 Dashboard 的 SSE/轮询刷新，以及任务状态的 WebSocket/轮询刷新。
- **系统状态面板模块**：前端可读取后端 `/health`，显示运行环境、API 地址、WS 地址、数据库、AI、采集器状态。
- **多语言文案模块**：前端支持中文 / 英文文案切换，已实际用于登录页、首页、分析页、采集页、商品页、Dashboard。

---

## 2. 前端页面结构

### 2.1 `frontend/app/` 路由列表

#### 实际使用中的路由
- `/` → `frontend/app/page.tsx`
  - 首页营销页
  - 实际使用组件：`LandingAnalyzer`、`SystemStatusPanel`
- `/login` → `frontend/app/login/page.tsx`
  - 登录页
  - 实际使用组件：`LoginForm`
- `/dashboard` → `frontend/app/dashboard/page.tsx`
  - Dashboard 入口页
  - 根据 `NEXT_PUBLIC_ENABLE_NEW_DASHBOARD` 决定渲染 `NewDashboard` 或 `OldDashboard`
- `/crawl` → `frontend/app/crawl/page.tsx`
  - 商品采集页
  - 实际使用组件：`XBorderLayout`、`TaskPanel`、`SystemStatusPanel`、`CrawlPanel`
- `/analyze` → `frontend/app/analyze/page.tsx`
  - 商品分析页
  - 实际使用组件：`XBorderLayout`、`TaskPanel`、`SystemStatusPanel`、`AnalyzePanel`
- `/products` → `frontend/app/products/page.tsx`
  - 商品列表页
  - 实际使用组件：`XBorderLayout`、`TaskPanel`、`SystemStatusPanel`、`ProductList`
- `/products/[id]` → `frontend/app/products/[id]/page.tsx`
  - 商品详情页
  - 实际使用组件：`XBorderLayout`、`TaskPanel`、`SystemStatusPanel`、`ProductDetail`
- `/product-demo` → `frontend/app/product-demo/page.tsx`
  - 公开试用页
  - 实际使用组件：`ProductDemoPanel`

#### 辅助文件
- `frontend/app/layout.tsx`
  - 根布局，实际接入 `EnvGuard`
- `frontend/app/globals.css`
  - 全局样式
- `frontend/app/dashboard/loading.tsx`
  - Dashboard 加载态文件

### 2.2 `frontend/modules/` 结构

#### 实际使用中的模块
- `frontend/modules/dashboard/new-dashboard.tsx`
  - 新版 Dashboard 服务端入口
- `frontend/modules/dashboard/new-dashboard-client.tsx`
  - 新版 Dashboard 客户端展示
- `frontend/modules/dashboard/layout.tsx`
  - 新版 Dashboard / XBorder 布局骨架
- `frontend/modules/analytics/dashboard-charts.tsx`
  - Dashboard 图表与统计卡片模块

#### 旧代码但仍存在
- `frontend/modules/dashboard/old-dashboard.tsx`
  - 旧版 Dashboard 组件仍存在
  - 当前是否实际使用：**有条件使用**
  - 条件：`NEXT_PUBLIC_ENABLE_NEW_DASHBOARD !== "true"`
- `frontend/modules/realtime/use-dashboard-live.ts`
  - 存在但当前未被任何页面直接引用
  - 可判定为：**旧实时实现残留 / 未实际接入**

### 2.3 `frontend/components/` 结构

#### 实际使用中的组件
- `components/auth/login-form.tsx`：登录表单
- `components/dashboard/task-panel.tsx`：右侧任务状态面板
- `components/dashboard/realtime/use-dashboard-stream.ts`：Dashboard SSE 基础订阅
- `components/dashboard/realtime/use-kpi-realtime.ts`：KPI 实时更新
- `components/dashboard/realtime/use-task-stream.ts`：任务列表实时更新
- `components/dashboard/realtime/use-trend-stream.ts`：趋势图与数据源状态刷新
- `components/layouts/xborder-layout.tsx`：当前主布局导出层
- `components/marketing/landing-analyzer.tsx`：首页公开分析组件
- `components/marketing/product-demo-panel.tsx`：试用页分析组件
- `components/products/crawl-panel.tsx`：商品采集表单与结果展示
- `components/products/analyze-panel.tsx`：商品分析表单与结果展示
- `components/products/product-list.tsx`：商品列表、搜索、单删、批删
- `components/products/product-detail.tsx`：商品详情展示
- `components/system/env-guard.tsx`：生产环境变量守卫
- `components/system/system-status-panel.tsx`：系统状态面板

#### 旧代码但仍存在
- `components/app-shell.tsx`
  - 旧布局别名层，实际仅被 `old-dashboard.tsx` 引用
- `components/language-switcher.tsx`
  - 只是 `LanguageToggle` 的别名导出，当前无直接引用

#### 说明
- `frontend/components/ui/` 目录当前存在，但扫描结果没有实际组件文件，且项目检查脚本中将 `@/components/ui/` 视为禁止导入来源。

---

## 3. 后端 API 列表

### 3.1 认证接口 `/api/v1/auth/*`

- `POST /api/v1/auth/register`
  - 功能：注册用户
  - 当前状态：**存在但前端未实际使用**
- `POST /api/v1/auth/login`
  - 功能：用户登录，返回 access token 和用户信息
  - 当前状态：**前端实际使用**
- `GET /api/v1/auth/me`
  - 功能：读取当前用户
  - 当前状态：**存在但前端当前未实际使用**

### 3.2 商品接口 `/api/v1/products/*`

- `POST /api/v1/products/extract`
  - 功能：公开商品页面提取
  - 当前状态：**存在但前端当前未实际使用**
- `POST /api/v1/products/crawl`
  - 功能：真实采集商品并入库
  - 当前状态：**前端实际使用**
- `POST /api/v1/products/analyze`
  - 功能：对已存在商品或标题做 AI 分析并写入数据库
  - 当前状态：**接口存在；前端 API 封装存在；当前页面未直接触发使用**
- `GET /api/v1/products`
  - 功能：读取商品列表
  - 当前状态：**前端实际使用**
- `DELETE /api/v1/products/batch-delete`
  - 功能：批量删除商品
  - 当前状态：**前端实际使用**
- `GET /api/v1/products/{product_id}`
  - 功能：读取商品详情
  - 当前状态：**前端实际使用**
- `DELETE /api/v1/products/{product_id}`
  - 功能：删除单个商品
  - 当前状态：**前端实际使用**

### 3.3 分析接口 `/api/v1/analyze/*`

- `POST /api/v1/analyze/full`
  - 功能：登录态一键分析（提取 + 分析）
  - 当前状态：**存在但前端当前未实际使用**
- `POST /api/v1/analyze/full/public`
  - 功能：公开一键分析（提取 + 分析）
  - 当前状态：**前端实际使用**

### 3.4 Dashboard 接口 `/api/v1/dashboard/*`

- `GET /api/v1/dashboard/summary`
  - 功能：读取概览统计、最新商品、类目统计
  - 当前状态：**前端实际使用**
- `GET /api/v1/dashboard/trends`
  - 功能：读取近 7 天商品趋势
  - 当前状态：**前端实际使用**
- `GET /api/v1/dashboard/tasks`
  - 功能：读取任务状态与最近运行记录
  - 当前状态：**前端实际使用**
- `GET /api/v1/dashboard/sources`
  - 功能：读取数据源状态与存储概览
  - 当前状态：**前端实际使用**

### 3.5 SSE / WebSocket / task 接口

- `GET /api/v1/stream/dashboard`
  - 类型：SSE
  - 功能：推送 Dashboard `summary` 与 `tasks` 事件
  - 当前状态：**前端实际使用**
- `GET /task-status/{task_name}`
  - 功能：读取 `crawl` / `analyze` 任务状态
  - 当前状态：**前端实际使用（轮询 fallback）**
- `GET /health`
  - 功能：系统健康检查
  - 当前状态：**前端实际使用**
- `WS /ws/{task_name}`
  - 类型：WebSocket
  - 功能：推送单个任务状态
  - 当前状态：**前端实际使用**

---

## 4. 系统架构说明（真实版）

### 4.1 前端
- 技术框架：Next.js App Router
- 路由目录：`frontend/app/`
- 主要 UI 结构：
  - 登录页
  - 首页营销页
  - Dashboard 页
  - 商品采集页
  - 商品分析页
  - 商品列表页
  - 商品详情页
  - 试用页
- 样式体系：`frontend/design-system/` + `frontend/modules/dashboard/layout.tsx`
- 当前运行中的主布局：`XBorderLayout`
- Dashboard 版本切换：由 `NEXT_PUBLIC_ENABLE_NEW_DASHBOARD` 控制新旧 Dashboard 组件切换

### 4.2 后端
- 技术框架：FastAPI
- API 前缀：`/api/v1`
- 结构分层：
  - `api/`：接口层
  - `services/`：业务服务层
  - `repositories/`：数据库访问层
  - `schemas/`：接口与数据结构定义
  - `models/`：数据库模型
- 根接口：
  - `/health`
  - `/task-status/{task_name}`
  - `/ws/{task_name}`

### 4.3 数据库
- 当前数据库：SQLite（`product_mvp.db`）
- ORM：SQLAlchemy
- 主要表模型：
  - `users`
  - `platforms`
  - `categories`
  - `products`
  - `product_images`
  - `product_keywords`
  - `sourcing_links`
  - `ai_analysis_results`
  - `crawl_runs`

### 4.4 AI 调用
- 实现位置：
  - `backend/app/services/ai.py`
  - `backend/app/services/product_intelligence.py`
- 外部依赖：OpenAI API
- 真实用途：
  - 标题翻译、关键词、卖点、采购词生成
  - 商品评分、推荐建议、利润估算、竞争等级生成
- 降级策略：AI 失败时，一键分析接口可返回规则模型 `FALLBACK` 结果

### 4.5 爬虫模块
- 真实采集服务：`backend/app/services/crawler.py`
  - 通过 Playwright 打开页面并解析 Amazon / AliExpress / Shopify 商品信息
- 公开提取服务：`backend/app/services/product_extractor.py`
  - 通过 Playwright 解析公开商品页面并识别 BLOCKED 场景

### 4.6 实时通信
- Dashboard 实时：SSE（`/api/v1/stream/dashboard`）
- 任务状态实时：WebSocket（`/ws/{task_name}`）
- 轮询兜底：
  - Dashboard：`summary/tasks/trends/sources` 轮询
  - 任务状态：`/task-status/{task_name}` 轮询

---

## 5. 当前存在的模块依赖关系

### 5.1 主业务链路
- 登录 → Dashboard / 商品页访问
- 商品采集 → 商品入库 → 商品列表 / 商品详情
- 商品详情（已有数据） → 可展示历史分析结果与采购链接
- 公开 URL 分析 → 页面提取 → AI 分析 / 规则降级 → 前端展示结果
- 商品数据 / 采集记录 / 分析结果 → Dashboard 概览统计

### 5.2 依赖关系（按模块）
- `auth` → `products / dashboard / crawl / analyze` 页面访问控制
- `crawl` → `product` 入库与图片写入
- `product` → `analyze`（可基于商品标题做 AI 分析）
- `product / crawl_run / analysis` → `dashboard`
- `task_status` → `crawl / analyze / dashboard / ws`
- `dashboard` → `task_status + products + crawl_runs + platforms + categories`
- `system-status-panel` → `/health`

可简化表示为：

`auth → crawl → product → analyze → dashboard`

以及：

`task_status → ws/sse/polling → 前端实时展示`

---

## 6. 是否存在重复逻辑 / 冗余模块

### 6.1 重复 UI
- `NewDashboard` 与 `OldDashboard` 两套 Dashboard UI 同时存在
  - 当前是否都存在代码：**是**
  - 当前是否同时运行：**否**（通过环境变量切换）
- `components/app-shell.tsx` 与 `components/layouts/xborder-layout.tsx`
  - 前者服务旧 Dashboard
  - 后者服务新 Dashboard
- `components/language-switcher.tsx`
  - 只是 `LanguageToggle` 的别名层，存在冗余

### 6.2 重复 API / 接口能力
- `/api/v1/analyze/full` 与 `/api/v1/analyze/full/public`
  - 两者核心能力相近，区别在于是否依赖登录态
- `/api/v1/products/analyze` 与 `/api/v1/analyze/full*`
  - 都包含分析能力，但输入来源不同：
    - 一个基于已有商品或标题
    - 一个基于公开 URL

### 6.3 重复业务逻辑
- Dashboard 实时存在两套实现路径：
  - `frontend/components/dashboard/realtime/*`（当前实际使用）
  - `frontend/modules/realtime/use-dashboard-live.ts`（存在但当前未实际接入）
- 商品分析存在两条业务入口：
  - `products/analyze`：基于商品或标题分析
  - `analyze/full/public`：基于公开 URL 一键分析
- 首页公开分析组件与试用页分析组件均调用 `analyzeFullPublic`
  - 页面不同，但能力重复

---

## 7. 前端结构补充说明（软著校验视角）

### 7.1 实际使用中的 `modules/`
- `dashboard/`：当前 Dashboard 主模块
- `analytics/`：Dashboard 图表模块

### 7.2 旧代码但仍存在的 `modules/`
- `dashboard/old-dashboard.tsx`
- `realtime/use-dashboard-live.ts`

### 7.3 实际使用中的 `components/`
- `auth/`
- `dashboard/`
- `layouts/`
- `marketing/`
- `products/`
- `system/`

### 7.4 旧代码或冗余层
- `components/app-shell.tsx`
- `components/language-switcher.tsx`

---

## 8. 申报风险判断

### 8.1 是否存在“功能与代码不一致”
- **YES**
- 原因：
  - 项目中存在新旧 Dashboard 双实现；如果申报材料写成“只有单一 Dashboard 实现”，会与代码不完全一致。
  - 部分接口存在但前端未实际使用，如 `/auth/register`、`/auth/me`、`/products/extract`、`/analyze/full`。
  - 部分实时实现代码存在但未接入，如 `modules/realtime/use-dashboard-live.ts`。

### 8.2 是否可以用于软著申报
- **YES**
- 前提：
  - 申报材料必须按“当前真实已实现功能”描述
  - 不能把未接入或未来计划功能当成已上线核心功能描述

### 8.3 是否存在风险描述夸大
- **YES**
- 风险点：
  - 若将所有存在的接口都描述成“前端完整使用中”，会夸大
  - 若将所有实时机制都描述成“统一成熟方案”，会夸大
  - 若将 AI 能力描述成“稳定输出且无降级”，会夸大
  - 若将系统描述成“只有一套 Dashboard 体系”，会夸大

---

## 9. 适合软著申报的真实表述建议

建议使用以下真实表述口径：
- 本系统为一套跨境商品采集与智能分析系统。
- 系统包含用户登录、商品采集、商品列表管理、商品详情展示、公开链接分析、Dashboard 数据概览、任务状态监控等功能。
- 系统后端基于 FastAPI，前端基于 Next.js，数据库采用 SQLite，商品采集通过 Playwright 完成，智能分析通过 OpenAI 接口完成，并具备任务状态实时刷新能力。
- 系统包含新旧两套 Dashboard 组件代码，其中当前运行版本通过前端环境变量控制切换。


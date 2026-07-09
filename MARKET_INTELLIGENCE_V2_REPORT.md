# Market Intelligence V2 Report

## 1. 当前版本
- 本地提交：`84706d4`
- 腾讯云服务器提交：`84706d4`
- 腾讯云运行容器标签：`84706d4`
- 部署时间基准：`2026-07-09`

## 2. 本次实际完成内容
- 新增 `backend/app/core/market_signal_engine.py`
- 新增 `backend/app/core/market_opportunity_model.py`
- 升级 Google / Amazon / TikTok / Shopify 市场适配器
- 升级 `backend/app/core/market_intelligence_engine.py`
- 升级 `backend/app/core/analysis_orchestrator.py`
- 升级 `backend/app/models/market_analysis_history.py`
- 升级 `backend/app/repositories/market_analysis_history.py`
- 升级 `backend/app/services/decision_service.py`
- 补齐并上线 `POST /api/v1/market/intelligence`

## 3. 本地真实校验结果
### Backend compileall
- 命令结果：通过
- 范围：`backend/app` + `backend/alembic`

### Frontend production build
- 命令结果：通过
- 结果：Next.js 生产构建完成
- 关键页面已进入产物：
  - `/action-center/suppliers`
  - `/dashboard/execution`
  - `/dashboard/product`
  - `/login`
  - `/register`
  - `/settings`

## 4. 腾讯云部署真实结果
### 部署修复点
- 首次线上缺口：`/api/v1/market/intelligence` 没进入已提交版本
- 修复提交：`84706d4`
- 修复内容：`backend/app/api/v1/endpoints/market.py`

### 腾讯云自检结果
- `/health`：200 OK
- 后端容器：运行中
- 前端容器：运行中
- Nginx 容器：运行中
- 当前运行标签：全部为 `84706d4`

## 5. 公网真实接口验证
### 登录验证
- 接口：`POST http://121.4.35.33/api/v1/auth/login`
- 结果：成功
- 令牌长度：`165`

### 市场接口验证
- 接口：`POST http://121.4.35.33/api/v1/market/intelligence`
- 输入：
  - `keyword = wireless earbuds`
  - `region = global`
- 结果：`200 OK`

### 本次公网真实返回核心字段
- `market_opportunity.score`：`49.32`
- `market_opportunity.level`：`LOW`
- `recommendation`：`IGNORE`
- `demand_score`：`31.25`
- `trend_score`：`23.25`
- `trend_direction`：`up`
- `competition_level`：`medium`
- `market_saturation`：`36.8`
- `market_score`：`5.54`
- `confidence`：`0.28`
- `is_mock`：`true`
- `market_growth`：`17.0`

## 6. 当前真实数据源状态
### Google
- `source_status`：`fallback_mock`
- `is_mock`：`true`
- `confidence`：`0.3`
- 实际状态：真实 Google Trends 拉取失败，当前走 fallback

### Amazon
- `source_status`：`partial`
- `is_mock`：`false`
- `confidence`：`0.46`
- 实际状态：当前四个源里只有 Amazon 返回了部分真实信号

### TikTok
- `source_status`：`pending`
- `is_mock`：`true`
- `confidence`：`0.18`
- 实际状态：真实接入未完成，当前仍是占位待接入状态

### Shopify
- `source_status`：`pending`
- `is_mock`：`true`
- `confidence`：`0.2`
- 实际状态：`SHOPIFY_API_NOT_CONFIGURED`

## 7. mock 占比
### 按数据源计算
- 总数据源：4
- 非 mock 数据源：1（Amazon partial）
- mock / pending 数据源：3（Google / TikTok / Shopify）
- 当前 mock 占比：`75%`

### 按 market_signals 计算
- 总信号数：11
- `is_real = true`：3
- `is_real = false`：8
- 当前 mock 信号占比：`72.73%`

## 8. 评分变化追踪
- 本次返回包含风险标记：`DECLINING`
- 说明：历史分数对比后，系统已经把当前关键词识别为下降机会
- 当前机会分：`49.32`
- 当前最终市场分：`5.54`

## 9. 当前生产状态判断
### 已经完成
- 市场信号层已接入主链路
- 市场机会评分模型已接入主链路
- `/api/v1/market/intelligence` 已真实上线
- 腾讯云生产环境与仓库版本已同步到 `84706d4`
- 公网接口可真实返回结构化结果

### 仍未完成
- Google 真实趋势未稳定接通
- TikTok 真实趋势未接通
- Shopify 真实市场信号未接通
- 当前返回仍以 mock / pending 为主

## 10. 当前唯一真实结论
- `Market Intelligence V2` 的接口链路、部署链路、线上返回链路已经打通。
- 但当前市场数据真实性还没有达成“生产级真实市场雷达”的最终标准。
- 现在真正可用的真实市场来源只有 Amazon partial。
- 当前系统可以返回结构化市场判断，但不能宣称“已完成全真实市场数据驱动”。

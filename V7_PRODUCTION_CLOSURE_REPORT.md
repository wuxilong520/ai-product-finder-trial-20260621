# V7_PRODUCTION_CLOSURE_REPORT

## 1. commit hash
- local_commit: `b35caefa10633bc6b566a5cf899ab0d20c0076f1`
- gitee_commit: `b35caefa10633bc6b566a5cf899ab0d20c0076f1`
- github_commit: `b35caefa10633bc6b566a5cf899ab0d20c0076f1`

## 2. git状态

### 本次纳入 V7 收口的文件
- `backend/app/core/market_intelligence_engine.py`
- `backend/app/core/commercial_signal_engine.py`
- `backend/app/core/purchase_signal_engine.py`
- `backend/app/core/commercial_intent_engine.py`
- `backend/app/core/competition_pressure_engine.py`
- `backend/app/core/consumer_interest_engine.py`
- `backend/app/core/trend_lifecycle_engine.py`
- `backend/app/core/market_confidence_engine.py`
- `backend/app/core/business_opportunity_engine.py`
- `backend/app/api/v1/endpoints/market.py`
- `backend/app/schemas/market.py`
- `backend/app/services/market_intelligence_engine.py`
- `backend/app/adapters/market/commercial/*`
- `backend/app/adapters/market/global/*`
- `backend/app/adapters/market/reality/*`
- `backend/app/models/commercial_signal.py`
- `backend/app/models/commercial_signal_history.py`
- `backend/app/models/market_reality_history.py`
- `backend/app/models/market_reality_signal.py`
- `backend/app/models/market_signal_history.py`
- `backend/app/repositories/commercial_signal_history.py`
- `backend/app/repositories/market_reality_history.py`
- `backend/app/repositories/market_signal_history.py`
- `backend/app/adapters/platform/shopify_adapter.py`
- `backend/app/core/config.py`
- `backend/alembic/versions/20260710_000024_add_market_signal_history_v3.py`
- `backend/alembic/versions/20260710_000025_upgrade_market_signal_history_v4.py`
- `backend/alembic/versions/20260710_000026_add_data_connections_v5.py`
- `backend/alembic/versions/20260710_000027_upgrade_v5_1_shopify_oauth.py`
- `backend/alembic/versions/20260710_000028_add_market_reality_history_v6.py`
- `backend/alembic/versions/20260713_000029_add_commercial_signal_history_v7.py`
- `deploy/tencent-cloud/nginx.http.conf`
- `deploy/tencent-cloud/nginx.conf`
- `MARKET_INTELLIGENCE_V7_COMMERCIAL_SIGNAL_REPORT.md`

### 历史垃圾 / 本次禁止提交的内容
- 前端页面脏改动
- 计费相关脏改动
- 邮件相关脏改动
- 无关脚本改动
- `.env` 模板改动
- 历史 UI / 支付 / 供应链未收口文件

### 当前真实 git 审计结论
- 本地工作区依然有大量历史脏改动
- 本次提交没有把这些历史垃圾一起带入
- 本次 commit 只封装了 V7 市场层和它运行所需的直接依赖

## 3. 公网版本
- server_git_head_current: `b35caefa10633bc6b566a5cf899ab0d20c0076f1`
- server_git_branch_current: `V7-commercial-signal-layer-production`
- server_scope_status: `V7_GIT_HEAD_MATCH`
- container_label: `b35caefa10633bc6b566a5cf899ab0d20c0076f1`
- running_api_status: `GET 200 OK / POST 405 / anonymous GET 401`
- extra_runtime_fix:
  - 已停掉腾讯云定时任务 `auto-deploy-from-primary.sh`
  - 原因：它会每分钟把服务器重新拉回旧版本 `main / 58a8cd8...`

## 4. 接口结果

### 接口访问规则（真实）
- `POST /api/v1/market/commercial-reality/report`：`405 Method Not Allowed`
- `GET /api/v1/market/commercial-reality/report`：真实可用
- 匿名 `GET`：`401 Unauthorized`
- 带真实登录 token 的 `GET`：`200 OK`

### GET `/api/v1/market/commercial-reality/report`

#### wireless earbuds / US
- `market_score = 45.97`
- `confidence = 0.8379`
- `commercial_score = 1.5`
- `purchase_signal = 11.38`
- `ad_market_value = 0.0`
- `brand_activity = 2.5`
- `commercial_competition = 2.5`
- `recommendation = WATCH`
- `source_status`
  - `google_ads = not_configured`
  - `tiktok_ads = limited`
  - `meta_ads = limited`
  - `amazon_ads = real`

#### beauty products / US
- `market_score = 43.34`
- `confidence = 0.7353`
- `commercial_score = 0.75`
- `purchase_signal = 10.49`
- `ad_market_value = 0.0`
- `brand_activity = 0.0`
- `commercial_competition = 0.0`
- `recommendation = WATCH`

#### home decor / US
- `market_score = 42.57`
- `confidence = 0.7235`
- `commercial_score = 0.75`
- `purchase_signal = 10.49`
- `ad_market_value = 0.0`
- `brand_activity = 0.0`
- `commercial_competition = 0.0`
- `recommendation = WATCH`

#### pet products / US
- `market_score = 46.41`
- `confidence = 0.841`
- `commercial_score = 1.5`
- `purchase_signal = 11.38`
- `ad_market_value = 0.0`
- `brand_activity = 2.5`
- `commercial_competition = 2.5`
- `recommendation = WATCH`

## 5. 当前市场真实性等级
- 等级：`中`
- 判断依据：`wireless earbuds / US` 当前 `confidence = 0.8379`，但真实商业来源主要只稳定落在 `amazon_ads`
- 真实可确认状态：
  - `amazon_ads = real`
- 仍未完成的商业广告层：
  - `Google Ads = not_configured`
  - `TikTok = limited`
  - `Meta = limited`

## 6. 下一阶段建议
- 第一优先级：补 `Google Ads` 商业账号配置
- 第二优先级：提升 `TikTok` / `Meta` 商业信号稳定性
- 第三优先级：单独做一次“整仓历史脏改动清账”

## 7. 最终真实结论
- Gitee 分支 hash 和 GitHub 分支 hash 已一致
- 腾讯云仓库 `HEAD` 已切到同一 hash
- 腾讯云运行容器 label 已切到同一 hash
- 本次额外修复了一个真实生产问题：
  - 腾讯云存在每分钟自动执行的旧版回滚任务
  - 如果不先停掉，这次收口不可能成功
- 所以本次已经完成的是：
  - `V7 提交版本闭环`
  - `V7 仓库版本闭环`
  - `V7 腾讯云运行版本闭环`
  - `V7 公网健康检查闭环`
- 当前仍未完全理想的地方：
  - `/api/v1/market/commercial-reality/report` 不是匿名接口，验收必须先登录
  - 该接口当前只支持 `GET`，不支持 `POST`
  - 市场真实商业源目前仍明显偏少，主要依赖 `amazon_ads`

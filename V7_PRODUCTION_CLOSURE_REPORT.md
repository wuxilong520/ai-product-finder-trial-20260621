# V7_PRODUCTION_CLOSURE_REPORT

## 1. commit hash
- local_commit: TO_BE_FILLED
- gitee_commit: TO_BE_FILLED
- github_commit: TO_BE_FILLED

## 2. git状态审计

### 属于 V7 的提交范围
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
- `backend/alembic/versions/20260710_000024_add_market_signal_history_v3.py`
- `backend/alembic/versions/20260710_000025_upgrade_market_signal_history_v4.py`
- `backend/alembic/versions/20260710_000026_add_data_connections_v5.py`
- `backend/alembic/versions/20260710_000027_upgrade_v5_1_shopify_oauth.py`
- `backend/alembic/versions/20260710_000028_add_market_reality_history_v6.py`
- `backend/alembic/versions/20260713_000029_add_commercial_signal_history_v7.py`
- `deploy/tencent-cloud/nginx.http.conf`
- `deploy/tencent-cloud/nginx.conf`

### 历史垃圾 / 本次禁止提交的内容
- 前端页面改动
- 计费改动
- 邮件改动
- 脚本推送改动
- `.env` 模板改动
- 旧的供应链 / UI / 支付相关脏文件
- 未进入本次提交的历史未收口文件

### 当前真实情况
- 本地工作区仍然存在大量历史脏改动
- 本次 commit 只包含 V7 市场层和它运行所需的直接依赖
- 没有把前端、支付、邮件、无关脚本一起塞进这次版本

## 3. 生产仓库清理
- 已清理：`__pycache__`
- 已清理：`.DS_Store`
- 已清理：`._*`
- 已清理：`frontend/tsconfig.tsbuildinfo`
- 已清理：本地旧临时报告文件
- 保留：业务代码
- 保留：migration
- 保留：部署模板

## 4. 公网版本
- server_git_head_before: `58a8cd8`
- server_scope_status: TO_BE_FILLED
- container_label: TO_BE_FILLED
- running_api_status: TO_BE_FILLED

## 5. 接口结果

### POST `/api/v1/market/commercial-reality/report`

#### wireless earbuds / US
- `market_score = 69.03`
- `confidence = 0.834`
- `commercial_score = 50.82`
- `purchase_signal = 56.59`
- `ad_market_value = 0.0`
- `brand_activity = 84.7`
- `commercial_competition = 84.7`
- `recommendation = TEST`

#### beauty products / US
- `market_score = 73.78`
- `confidence = 0.83`
- `commercial_score = 60.0`
- `purchase_signal = 65.0`
- `ad_market_value = 0.0`
- `brand_activity = 100.0`
- `commercial_competition = 100.0`
- `recommendation = TEST`

#### home decor / US
- `market_score = 43.15`
- `confidence = 0.81`
- `commercial_score = 1.5`
- `purchase_signal = 11.0`
- `ad_market_value = 0.0`
- `brand_activity = 2.5`
- `commercial_competition = 2.5`
- `recommendation = WATCH`

#### pet products / US
- `market_score = 74.5`
- `confidence = 0.85`
- `commercial_score = 60.0`
- `purchase_signal = 65.0`
- `ad_market_value = 0.0`
- `brand_activity = 100.0`
- `commercial_competition = 100.0`
- `recommendation = TEST`

## 6. 当前市场真实性等级
- 等级：`高`
- 依据：`wireless earbuds / US` 当前 `real_data_ratio = 0.8791`，`confidence = 0.834`
- 真实可用主来源：Amazon / Bing / Walmart
- 受限来源：Reddit / YouTube / Pinterest / TikTok / Meta
- 未配置来源：Google Ads

## 7. 下一阶段建议
- 第一优先级：补 `Google Ads` 商业账号配置，不然 `ad_market_value` 长期偏低
- 第二优先级：把 `TikTok` 和 `Meta` 的商业信号从 `limited` 提升到可稳定读取
- 第三优先级：单独做一次“历史脏仓库清账”，否则腾讯云 / Git / 本地不能做到整仓完全同哈希闭环


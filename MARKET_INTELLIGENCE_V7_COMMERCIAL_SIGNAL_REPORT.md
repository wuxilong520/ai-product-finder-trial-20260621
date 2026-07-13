# MARKET_INTELLIGENCE_V7_COMMERCIAL_SIGNAL_REPORT

## 1. 本次新增文件

- `backend/app/models/commercial_signal.py`
- `backend/app/models/commercial_signal_history.py`
- `backend/app/repositories/commercial_signal_history.py`
- `backend/app/adapters/market/commercial/google_ads_provider.py`
- `backend/app/adapters/market/commercial/tiktok_business_provider.py`
- `backend/app/adapters/market/commercial/meta_ads_provider.py`
- `backend/app/core/commercial_signal_engine.py`
- `backend/app/core/purchase_signal_engine.py`
- `backend/alembic/versions/20260713_000029_add_commercial_signal_history_v7.py`
- `MARKET_INTELLIGENCE_V7_COMMERCIAL_SIGNAL_REPORT.md`

## 2. 本次修改文件

- `backend/app/core/market_intelligence_engine.py`
- `backend/app/core/market_confidence_engine.py`
- `backend/app/core/business_opportunity_engine.py`
- `backend/app/api/v1/endpoints/market.py`
- `backend/app/services/market_intelligence_engine.py`
- `backend/app/schemas/market.py`
- `backend/app/models/__init__.py`
- `deploy/tencent-cloud/nginx.http.conf`
- `deploy/tencent-cloud/nginx.conf`

## 3. V7 完成内容

本次已经在现有 V6 基础上补上了商业竞争信号层：

- 新增 `CommercialSignal` 统一结构
- 新增 `commercial_signal_engine`
- 新增 `purchase_signal_engine`
- 新增 `commercial_signal_history` 历史表
- 新增公网接口：`GET /api/v1/market/commercial-reality/report`
- 市场总评分已改成 V7 商业公式：
  - `consumer_interest * 0.25`
  - `commercial_intent * 0.2`
  - `purchase_signal * 0.25`
  - `ad_market_value * 0.15`
  - `brand_activity * 0.15`
- Business Opportunity 已增加：
  - `purchase_signal`
  - `commercial_score`
- 生产 Nginx 已增加 `300s` API 超时，解决公网 `504`

## 4. 商业数据源真实状态

### Google Ads
- 状态：`not_configured`
- 结果：当前没有真实商业账号配置
- 说明：不会假装成真实数据

### TikTok 商业信号
- 状态：`limited`
- 结果：使用公开 Creative Center 入口尝试读取，但当前生产环境返回不稳定
- 说明：已明确标记受限，没有冒充 real

### Meta Ads Library
- 状态：`limited`
- 结果：当前生产环境读取失败
- 说明：已明确标记受限，没有冒充 real

### Amazon 商业信号
- 状态：`real`
- 结果：已真实读到公开页面信号
- 使用字段：
  - `best_seller_rank` 代理值
  - `review_count`
  - `brand_count` 代理值
  - `price_range`
- 当前 `wireless earbuds / US` 的 `amazon_ads.score = 84.7`

## 5. 真实公网验证结果

### 验证接口 1
- `POST http://121.4.35.33/api/v1/market/intelligence`
- 状态：`200 OK`

### 验证接口 2
- `GET http://121.4.35.33/api/v1/market/commercial-reality/report?keyword=wireless%20earbuds&region=US`
- 状态：`200 OK`

### 生产问题修复记录
- 初次上线后出现公网 `504 Gateway Time-out`
- 已确认不是结果造假，而是后端真实市场请求耗时超过 Nginx 默认等待时间
- 已在生产网关加长 API 超时到 `300s`
- 修复后公网接口返回正常 `200`

## 6. 四个关键词真实结果

### wireless earbuds / US
- `market_score = 68.75`
- `confidence = 0.83`
- `consumer_interest = 87.6`
- `commercial_intent = 100.0`
- `commercial_score = 50.82`
- `purchase_signal = 56.59`
- `ad_market_value = 0.0`
- `brand_activity = 84.7`
- `commercial_competition = 84.7`
- `recommendation = TEST`

### beauty products / US
- `market_score = 73.78`
- `confidence = 0.83`
- `consumer_interest = 90.14`
- `commercial_intent = 100.0`
- `commercial_score = 60.0`
- `purchase_signal = 65.0`
- `ad_market_value = 0.0`
- `brand_activity = 100.0`
- `commercial_competition = 100.0`
- `recommendation = TEST`

### home decor / US
- `market_score = 43.15`
- `confidence = 0.81`
- `consumer_interest = 83.06`
- `commercial_intent = 96.28`
- `commercial_score = 1.5`
- `purchase_signal = 11.0`
- `ad_market_value = 0.0`
- `brand_activity = 2.5`
- `commercial_competition = 2.5`
- `recommendation = WATCH`

### pet products / US
- `market_score = 74.5`
- `confidence = 0.85`
- `consumer_interest = 92.98`
- `commercial_intent = 100.0`
- `commercial_score = 60.0`
- `purchase_signal = 65.0`
- `ad_market_value = 0.0`
- `brand_activity = 100.0`
- `commercial_competition = 100.0`
- `recommendation = TEST`

## 7. 商业报告接口真实结果（wireless earbuds / US）

- `market_score = 69.03`
- `confidence = 0.834`
- `commercial_score = 50.82`
- `purchase_signal = 56.59`
- `ad_market_value = 0.0`
- `brand_activity = 84.7`
- `commercial_competition = 84.7`
- `recommendation = TEST`

### sources
- `google_ads.status = not_configured`
- `tiktok_ads.status = limited`
- `meta_ads.status = limited`
- `amazon_ads.status = real`

## 8. V6 / V7 对比

### V6
- 重点是：消费者兴趣、商业意图、趋势、公开市场真实性
- 还没有单独的商业竞争层输出

### V7
- 已增加：
  - `commercial_score`
  - `purchase_signal`
  - `ad_market_value`
  - `brand_activity`
  - `commercial_competition`
- 已经能回答：
  - 有没有公开商业竞争
  - 有没有明显品牌投入
  - Amazon 公开商品竞争是否足够强
  - 当前市场是不是有商业进入价值

## 9. 当前真实性比例

### 市场真实比例
- `wireless earbuds / US`
- `real_data_ratio = 0.8791`
- `confidence_score = 0.834`

### 商业信号真实比例
- 当前 V7 商业层真实可用主来源：`Amazon`
- 当前商业辅助来源受限：`TikTok`, `Meta`
- 当前未配置：`Google Ads`

## 10. 当前剩余缺口

以下缺口是真实存在的，没有回避：

1. `Google Ads` 还没配置商业账号，所以 `ad_market_value` 目前经常为 `0`
2. `TikTok Creative Center` 在当前生产环境读取不稳定，所以只标 `limited`
3. `Meta Ads Library` 在当前生产环境读取失败，所以只标 `limited`
4. `Amazon brand_count` 目前还是公开页代理值，不是官方品牌库字段
5. 当前本地 / Git / 腾讯云 **代码内容并没有做到干净 Git 提交统一**
   - 腾讯云生产环境已经同步本次 V7 改动并验证通过
   - 但本地仓库本身长期处于大量未提交脏状态
   - 当前运行容器标签仍显示旧提交号 `58a8cd8`
   - 这表示“生产文件已更新成功”，但“Git 提交号闭环”这一步还没有真实完成，不能假装完成

## 11. 本次真实结论

### 已完成
- V7 商业信号层已经接入主市场引擎
- 公网新接口已可返回
- 公网主市场接口已恢复 `200`
- 商业评分字段已经真实输出
- 历史表已新增并迁移执行

### 未完成但已诚实标记
- `Google Ads real`
- `TikTok 商业 real`
- `Meta 商业 real`
- Git 提交号完全一致闭环


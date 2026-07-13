# SUPPLIER_INTELLIGENCE_V3_1_REPORT

## 1. 新增文件

### 后端核心
- `backend/app/core/supplier_intelligence_engine.py`
- `backend/app/core/supplier_risk_engine.py`
- `backend/app/core/supplier_ranking_engine.py`

### 数据库
- `backend/alembic/versions/20260713_000031_add_supplier_price_history.py`

## 2. 本次改动文件

- `backend/app/models/supplier.py`
- `backend/app/models/__init__.py`
- `backend/app/services/supply_import_service.py`
- `backend/app/core/supply_intelligence_engine.py`
- `backend/app/services/profit_truth_engine.py`
- `backend/app/core/business_opportunity_engine.py`
- `backend/app/api/v1/endpoints/supply.py`
- `backend/app/schemas/supplier.py`
- `frontend/lib/types.ts`
- `frontend/components/supplier/supplier-center.tsx`

## 3. 评分公式

### 供应商真实性总分 `supplier_real_score`

- 供应商真实性：30%
- 价格竞争力：25%
- 交付能力：15%
- MOQ合理性：10%
- 商品稳定性：10%
- 认证/资质：10%

### 真实性分 `supplier_authenticity_score`

真实参与项：

- 工厂信息
- 是否授权 / 是否校验
- 认证信息
- 商品公开链接
- 信息完整度
- 历史导入记录
- 历史校验时间

说明：

- 缺什么就扣什么
- 没有数据不会自动补满

### 风险模型 `supplier_risk_score`

真实参与项：

- 信息缺失
- 价格异常
- MOQ异常
- 无历史记录
- 供应不稳定
- 成本竞争力过弱

风险等级：

- `LOW`
- `MEDIUM`
- `HIGH`

## 4. 数据库变化

### 新增表
- `supplier_price_history`

字段：

- `id`
- `supplier_id`
- `product_id`
- `price`
- `moq`
- `record_source`
- `created_at`

用途：

- 跟踪价格变化
- 跟踪 MOQ 变化
- 给稳定性评分提供真实历史依据

### 已接入写入点

- 插件导入成功后，会写入 `supplier_price_history`
- 供应链分析选中供应商后，也会追加价格历史

## 5. 新接口

- `GET /api/v1/supply/supplier/{id}/intelligence`

返回核心字段：

- `supplier`
- `real_score`
- `authenticity_score`
- `risk`
- `price_score`
- `moq_score`
- `stability_score`
- `supplier_confidence`
- `recommendation`

## 6. 本地真实验证

### 验证1：数据库迁移

- `alembic upgrade head` 通过
- 已升级到：
  - `20260713_000031_add_supplier_price_history`

### 验证2：后端编译

- `python3 -m compileall backend/app` 通过

### 验证3：前端生产构建

- `pnpm run build` 通过

### 验证4：真实供应商评分

本地真实数据样本：

- 关键词：`wireless earbuds`
- 供应商：`深圳授权耳机工厂`

真实结果：

- `supplier_real_score = 69.2`
- `supplier_authenticity_score = 76.67`
- `price_competitiveness_score = 82.0`
- `moq_score = 20.0`
- `stability_score = 32.0`
- `supplier_confidence = 0.84`
- `risk_level = MEDIUM`
- `recommendation = 建议观察`

### 验证5：供应链总接口

调用：

- `POST /api/v1/supply/intelligence`

真实结果摘要：

- `supplier_name = 深圳授权耳机工厂`
- `supplier_score = 78.0`
- `supplier_real_score = 74.1`
- `risk_level = high`
- `procurement_recommendation = 建议小批量测试`

### 验证6：供应商详情接口

调用：

- `GET /api/v1/supply/supplier/2/intelligence?keyword=wireless%20earbuds&expected_price=39.9&quantity=100`

真实结果：

- 返回 `200`
- 已返回：
  - 供应商信息
  - 真实评分
  - 风险等级
  - 成本竞争力
  - MOQ评分
  - 采购建议

## 7. 公网验证

腾讯云部署版本：

- commit：`53fea74`

### 公网验证1：供应链总接口

调用：

- `POST /api/v1/supply/intelligence`

参数：

```json
{
  "keyword": "wireless earbuds",
  "target_market": "US",
  "expected_price": 39.9,
  "quantity": 100
}
```

真实返回：

- `200`
- `supplier_name = Shenzhen Audio Factory`
- `supplier_score = 80.2`
- `supplier_real_score = 79.8`
- `risk_level = high`
- `procurement_recommendation = 暂不建议采购`

### 公网验证2：供应商智能详情接口

调用：

- `GET /api/v1/supply/supplier/2/intelligence?keyword=wireless%20earbuds&expected_price=39.9&quantity=100`

真实返回：

- `200`
- `real_score = 82.0`
- `authenticity_score = 100.0`
- `risk.level = LOW`
- `risk.score = 12.0`
- `price_score = 82.0`
- `moq_score = 20.0`
- `stability_score = 90.0`
- `supplier_confidence = 0.88`
- `recommendation = 推荐采购`

## 8. 当前供应链真实性等级

当前结论：

- 供应链层已经从“只有供应评分”
- 升级到“供应评分 + 真实性评分 + 风险分层 + 历史价格跟踪”

当前真实性等级判断：

- `中高`

原因：

- 已接入真实插件导入数据
- 已接入真实供应商表和商品表
- 已接入历史价格记录
- 但历史样本量还不够大，所以稳定性维度现在偏保守

## 9. 剩余缺口

- 现在的价格历史是从这次版本开始积累，老数据没有完整回填
- 类目 MOQ 区间目前是第一版规则表，后面还可以继续细化
- 供应商经营时间目前只能基于系统内真实留存时间和历史记录做判断，还没有企业注册年限外部授权数据
- 公网部署后还需要补最后一轮真实接口验收结果

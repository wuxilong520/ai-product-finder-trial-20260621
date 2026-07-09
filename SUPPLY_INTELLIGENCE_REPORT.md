# Supply Intelligence Report

## 本次真实完成文件

- `backend/app/core/supply_intelligence_engine.py`
- `backend/app/adapters/supply/supply_base.py`
- `backend/app/adapters/supply/alibaba_1688_adapter.py`
- `backend/app/adapters/supply/pinduoduo_supply_adapter.py`
- `backend/app/adapters/supply/supplier_database_adapter.py`
- `backend/app/core/supplier_scoring_engine.py`
- `backend/app/services/supply_cost_engine.py`
- `backend/app/services/profit_truth_engine.py`
- `backend/app/services/decision_service.py`
- `backend/app/api/v1/endpoints/supply.py`
- `backend/app/services/supplier_matching_engine.py`
- `backend/app/models/supplier.py`
- `backend/alembic/versions/20260708_000018_add_supply_intelligence_tables.py`

## 当前真实链路

`Market Intelligence -> Supply Intelligence -> Profit Engine -> Decision Service -> Shopify`

当前已经接上的真实部分：

- 供应链智能引擎会先统一汇总多个供应来源
- 利润真实性引擎会读取供应链成本，不再只吃固定参数
- 决策服务会读取供应商评分、供应质量、真实成本、毛利率
- 供应链接口已经可返回统一结构
- 供应链分析历史会落库

## 真实数据情况

### 1. 1688

真实验证结果：

- 公开搜索地址可以访问
- 当前公开页会跳到登录逻辑
- 不能稳定拿到真实商品明细、真实 MOQ、真实交易字段

当前系统处理方式：

- 不伪装成真实明细
- 标记 `source_status = public_login_required`
- 标记 `is_mock = true`
- 保留真实搜索地址用于后续人工核对

### 2. 拼多多供应链

当前状态：

- 只预留适配层结构
- 未接入真实数据
- 返回 `pending`

### 3. 内部供应商数据库

当前状态：

- 已接入真实数据库读取
- 可读取过去写入的供应商缓存记录
- 当前会作为 `cached` 数据源参与排序和决策

## mock 情况

当前仍然存在 mock / pending 的来源：

- `1688`：因为公开页登录限制，当前仍是 mock fallback
- `pinduoduo`：当前仅预留结构，仍是 pending mock

当前已经修复的问题：

- 老 `1688` 假样例商品入口已移除，不再硬编码三条演示商品
- 供应链排序已改为优先真实 / 缓存数据，mock 不再抢第一名
- 供应链总标记按“当前选中的供应商”判断，不再因为混合来源误导后续链路

## 接口状态

### `POST /api/v1/supply/intelligence`

真实验证结果：

- 未带鉴权：返回 `401`
- 带合法请求上下文：返回 `200`

返回结构已包含：

- `suppliers`
- `supplier_score`
- `confidence`
- `risk_flags`
- `cost_estimate`
- `profit_preview`
- `is_mock`

## 真实测试结果

### 测试一：直接供应链引擎

输入：

- `keyword = wireless earbuds`
- `target_market = US`
- `expected_price = 49.9`
- `quantity = 500`

真实结果：

- 返回供应商数量：`2`
- 当前结果：`is_mock = true`
- 原因：1688 为 mock，拼多多为 pending，数据库命中为空

### 测试二：供应链接口

输入：

- `keyword = wireless earbuds`

真实结果：

- HTTP 状态：`200`
- 返回供应商数量：`3`
- `supplier_score = 65.65`
- `confidence = 0.4103`
- `is_mock = false`

首个供应商当前为：

- `supplier_name = 义乌优选工厂`
- `platform = 1688`
- `data_source = cached`
- `supplier_price = 17.7`
- `moq = 200`

说明：

- 这里的 `false` 不是说全链都是真实接口
- 它表示当前选中的第一供应商来自数据库缓存，不是 mock 占位
- 整体结果依然混有 mock 来源，所以 `risk_flags` 仍会出现 `mock_data_used`

### 测试三：分析 + 决策主链

输入：

- `keyword = wireless earbuds`
- `market = shopify`

真实结果：

- 选中供应商：`义乌优选工厂`
- 供应商来源：`cached`
- 利润预估：`60.9`
- 利润真实性分：`0.5`
- 整体 trust_level：`0.6221`
- 决策结果：`watch`

## 当前限制

1. 1688 真实商品详情还没打通，原因是公开搜索页登录限制
2. 拼多多供应链接口还只是预留结构，没有真实接入
3. 当前“真实”供应链主要来自内部数据库缓存，不是实时抓取
4. 如果数据库里没有历史供应商缓存，系统会退回 mock / pending 来源

## 当前结论

这次不是“页面改了看起来像完成”，而是供应链底层链路已经真的接入到：

- 数据汇总
- 评分
- 成本
- 利润
- 决策
- 接口输出

但我要跟你说实话：

当前还不能说“供应链已经完全真实化”。

现在真实程度最高的是：

- 内部供应商数据库缓存链路

现在仍未完全真实打通的是：

- 1688 实时公开明细
- 拼多多实时供应链

## 下一步唯一动作

下一步唯一应该做的是：

**把 1688 的真实供应商抓取能力换成可合法落地的真实供应来源，或者接入你自己的真实供应商库批量导入入口。**

from __future__ import annotations

from app.core.contracts import StrategyPlan


class StrategyLayer:
    def build(
        self,
        *,
        strategy_mode: str,
        keyword: str,
        market: str,
        business_constraints: dict | None = None,
    ) -> StrategyPlan:
        mode = (strategy_mode or "sourcing").lower()
        constraints = business_constraints or {}
        if mode == "listing":
            return StrategyPlan(
                strategy_mode=mode,
                objective=f"把 {keyword} 在 {market} 做成可上架商品",
                action_plan=[
                    "确认价格区间和上架节奏",
                    "检查供应稳定性和备货能力",
                    "准备标题、卖点、图片结构",
                ],
                execution_steps=[
                    "锁定目标售价与毛利底线",
                    "校对供应链 MOQ、交期、履约风险",
                    "生成上架文案并进入发布前检查",
                ],
                listing_recommendation="优先做小批量测试上架，再根据转化数据迭代。",
                supply_validation=[
                    "确认拿货价是否稳定",
                    "确认发货时效是否能支撑上架承诺",
                    "确认是否存在高退货风险",
                ],
                business_constraints=constraints,
            )
        if mode == "scaling":
            return StrategyPlan(
                strategy_mode=mode,
                objective=f"把 {keyword} 在 {market} 从验证阶段推进到放量阶段",
                action_plan=[
                    "核对转化率与利润真实性",
                    "检查广告预算承受能力",
                    "确认供应和履约能否承接放量",
                ],
                execution_steps=[
                    "先看真实利润而不是只看销量",
                    "按渠道分配广告预算并设止损线",
                    "扩大库存和供应冗余后再放量",
                ],
                listing_recommendation="只有真实利润和转化都稳定，才建议放量。",
                supply_validation=[
                    "确认供应商是否能承接更高订单量",
                    "确认物流成本不会因为放量失控",
                    "确认售后压力可控",
                ],
                business_constraints=constraints,
            )
        return StrategyPlan(
            strategy_mode="sourcing",
            objective=f"判断 {keyword} 在 {market} 值不值得做",
            action_plan=[
                "先看市场需求和竞争度",
                "再看供货价格和利润空间",
                "最后决定是否进入上架验证",
            ],
            execution_steps=[
                "验证需求趋势是否持续",
                "验证供应链价格是否真实可拿",
                "验证利润是否能覆盖平台和投放成本",
            ],
            listing_recommendation="先做选品验证，不建议直接大规模上架。",
            supply_validation=[
                "确认至少两条供货路径",
                "确认 MOQ 不会卡住试单",
                "确认单件成本可支撑目标利润",
            ],
            business_constraints=constraints,
        )


strategy_layer = StrategyLayer()

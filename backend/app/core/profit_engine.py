from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import MarketInsight, ProfitBreakdown, SupplyOffer


class ProfitEngineBase(ABC):
    @abstractmethod
    def calculate(
        self,
        *,
        market_insight: MarketInsight,
        supply_offer: SupplyOffer,
        platform_data: dict | None = None,
        supply_context: dict | None = None,
        cost_context: dict | None = None,
    ) -> ProfitBreakdown:
        raise NotImplementedError


class ProfitEngine(ProfitEngineBase):
    def calculate(
        self,
        *,
        market_insight: MarketInsight,
        supply_offer: SupplyOffer,
        platform_data: dict | None = None,
        supply_context: dict | None = None,
        cost_context: dict | None = None,
    ) -> ProfitBreakdown:
        platform_data = platform_data or {}
        supply_context = supply_context or {}
        cost_context = cost_context or {}
        shopify_candidates = platform_data.get('shopify_candidates') or []
        alibaba_suppliers = platform_data.get('alibaba_suppliers') or []
        shopify_reference_price = float(shopify_candidates[0].get('price')) if shopify_candidates else round(max(supply_offer.price * 2.9, 39.9 + market_insight.demand_score * 0.1), 2)
        alibaba_reference_cost = float(alibaba_suppliers[0].get('price')) if alibaba_suppliers else float(supply_offer.price)
        selling_price = round(max(shopify_reference_price, 39.9 + market_insight.demand_score * 0.1), 2)
        cost_price = round(float(cost_context.get("product_cost", alibaba_reference_cost)), 2)
        shipping_cost = round(float(cost_context.get("shipping_estimate", 6.5 + supply_offer.shipping_days * 0.35)), 2)
        platform_fee = round(float(cost_context.get("platform_fee", selling_price * 0.12)), 2)
        ad_cost = round(float(cost_context.get("marketing_cost", selling_price * 0.08)), 2)
        profit = round(selling_price - cost_price - shipping_cost - platform_fee - ad_cost, 2)
        margin = round(profit / selling_price, 4) if selling_price else 0
        break_even_price = round(cost_price + shipping_cost + platform_fee + ad_cost, 2)
        supply_source = 'mock' if supply_context.get('is_mock', False) else 'real'
        data_source_types = {item.get('data_source_type', 'mock') for item in [*shopify_candidates, *alibaba_suppliers]} if (shopify_candidates or alibaba_suppliers) else {supply_source}
        profit_truth_score = 1.0 if data_source_types == {'real'} else 0.5 if 'real' in data_source_types or 'partial' in data_source_types else 0.0
        return ProfitBreakdown(
            cost_price=cost_price,
            selling_price=selling_price,
            estimated_sell_price=selling_price,
            supply_cost=cost_price,
            shipping_cost=shipping_cost,
            platform_fee=platform_fee,
            ad_cost=ad_cost,
            profit=profit,
            margin=margin,
            break_even_price=break_even_price,
            estimated_profit=profit,
            estimated_margin_rate=margin,
            cost_estimate=cost_price,
            profit_margin=margin,
            shopify_reference_price=shopify_reference_price,
            alibaba_reference_cost=alibaba_reference_cost,
            profit_truth_score=profit_truth_score,
        )


profit_engine: ProfitEngineBase = ProfitEngine()

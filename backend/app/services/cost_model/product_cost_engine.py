from __future__ import annotations

from statistics import mean


class ProductCostEngine:
    def calculate(
        self,
        *,
        suppliers: list[dict],
        selling_price: float,
        target_market: str = "amazon_us",
        package_weight_kg: float = 0.45,
    ) -> dict:
        supplier_cost_candidates = [float(item.get("supplier_price") or 0) for item in suppliers if item.get("supplier_price")]
        base_supplier_cost = min(supplier_cost_candidates) if supplier_cost_candidates else round(max(selling_price * 0.42, 1), 2)

        exchange_rate = self._exchange_rate("USD", "USD")
        shipping_cost = self._shipping_cost(package_weight_kg, target_market)
        platform_fee = self._platform_fee(selling_price, target_market)
        packaging_cost = self._packaging_cost(target_market)

        total_cost = round(base_supplier_cost + shipping_cost + platform_fee + packaging_cost, 2)
        source_platforms = sorted({item.get("platform") for item in suppliers if item.get("platform")})

        simulated_dependencies: list[str] = []
        if not supplier_cost_candidates:
            simulated_dependencies.append("supplier_cost_fallback")
        if any(platform in {"1688", "拼多多"} for platform in source_platforms):
            simulated_dependencies.append("provider_price_is_search_reference")
        simulated_dependencies.extend(
            [
                "shipping_cost_rules",
                "platform_fee_rules",
                "packaging_cost_rules",
                "factory_quote_not_connected",
            ]
        )

        return {
            "total_cost": total_cost,
            "cost_breakdown": {
                "supplier_cost": round(base_supplier_cost, 2),
                "shipping_cost": round(shipping_cost, 2),
                "platform_fee": round(platform_fee, 2),
                "exchange_rate": round(exchange_rate, 4),
                "packaging_cost": round(packaging_cost, 2),
                "factory_quote": None,
                "source_platforms": source_platforms,
                "average_supplier_reference": round(mean(supplier_cost_candidates), 2) if supplier_cost_candidates else None,
            },
            "still_uses_simulated_data": True,
            "simulated_dependencies": simulated_dependencies,
        }

    def _shipping_cost(self, package_weight_kg: float, target_market: str) -> float:
        if target_market == "amazon_us":
            return round(4.8 + package_weight_kg * 6.5, 2)
        if target_market == "shopee_sea":
            return round(3.2 + package_weight_kg * 4.2, 2)
        return round(4.0 + package_weight_kg * 5.0, 2)

    def _platform_fee(self, selling_price: float, target_market: str) -> float:
        if target_market == "amazon_us":
            return round(selling_price * 0.15, 2)
        if target_market == "shopee_sea":
            return round(selling_price * 0.085, 2)
        return round(selling_price * 0.1, 2)

    def _packaging_cost(self, target_market: str) -> float:
        return 0.8 if target_market == "amazon_us" else 0.5

    def _exchange_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0
        return 7.2


product_cost_engine = ProductCostEngine()

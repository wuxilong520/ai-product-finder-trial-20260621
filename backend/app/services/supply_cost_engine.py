from __future__ import annotations


class SupplyCostEngine:
    def calculate(
        self,
        *,
        product_cost: float,
        shipping_estimate: float,
        platform_fee: float,
        marketing_cost: float,
        expected_price: float | None = None,
    ) -> dict:
        landed_cost = round(
            float(product_cost)
            + float(shipping_estimate)
            + float(platform_fee)
            + float(marketing_cost),
            2,
        )
        suggested_price = round(float(expected_price or landed_cost * 2.2), 2)
        margin = round(((suggested_price - landed_cost) / suggested_price), 4) if suggested_price > 0 else 0.0
        return {
            "product_cost": round(float(product_cost), 2),
            "shipping_estimate": round(float(shipping_estimate), 2),
            "platform_fee": round(float(platform_fee), 2),
            "marketing_cost": round(float(marketing_cost), 2),
            "landed_cost": landed_cost,
            "suggested_price": suggested_price,
            "margin": margin,
        }


supply_cost_engine = SupplyCostEngine()

from __future__ import annotations


class ProfitTruthEngine:
    def calculate(
        self,
        *,
        selling_price: float,
        platform_fee: float,
        shipping_cost: float,
        ad_cost: float,
        product_cost: float,
        currency_loss: float,
    ) -> dict:
        real_profit = round(
            float(selling_price)
            - float(platform_fee)
            - float(shipping_cost)
            - float(ad_cost)
            - float(product_cost)
            - float(currency_loss),
            2,
        )
        return {
            "selling_price": round(float(selling_price), 2),
            "platform_fee": round(float(platform_fee), 2),
            "shipping_cost": round(float(shipping_cost), 2),
            "ad_cost": round(float(ad_cost), 2),
            "product_cost": round(float(product_cost), 2),
            "currency_loss": round(float(currency_loss), 2),
            "real_profit_estimate": real_profit,
        }


profit_truth_engine = ProfitTruthEngine()

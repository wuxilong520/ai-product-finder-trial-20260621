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
            "purchase_cost": round(float(product_cost), 2),
            "platform_cost": round(float(platform_fee), 2),
            "gross_profit": round(float(selling_price) - float(product_cost), 2),
            "net_profit": real_profit,
            "margin_rate": round(real_profit / float(selling_price), 4) if float(selling_price) > 0 else 0.0,
        }

    def calculate_from_supply_intelligence(
        self,
        *,
        supply_intelligence: dict | None,
        cost_estimate: dict | None,
        selling_price: float,
        ad_cost: float,
        currency_loss: float = 0,
    ) -> dict:
        supply_intelligence = supply_intelligence or {}
        cost_estimate = cost_estimate or {}
        selected_supplier = supply_intelligence.get("selected_supplier") or {}
        is_mock = bool(supply_intelligence.get("is_mock", True))
        product_cost = float(cost_estimate.get("product_cost") or selected_supplier.get("price_mid") or 0)
        shipping_cost = float(cost_estimate.get("shipping_estimate") or 0)
        platform_fee = float(cost_estimate.get("platform_fee") or 0)
        result = self.calculate(
            selling_price=selling_price,
            platform_fee=platform_fee,
            shipping_cost=shipping_cost,
            ad_cost=ad_cost,
            product_cost=product_cost,
            currency_loss=currency_loss,
        )
        risk_flags = list(supply_intelligence.get("risk_flags") or [])
        if is_mock:
            risk_flags.append("mock_data_used")
        confidence = 0.2 if is_mock else float(supply_intelligence.get("confidence") or 0.6)
        result.update(
            {
                "profit_truth_score": round(max(0.0, min(1.0, confidence)), 4),
                "is_mock_cost": is_mock,
                "risk_flags": sorted(set(risk_flags)),
                "supplier_score": float(supply_intelligence.get("supplier_score") or 0),
                "supplier_quality": str(supply_intelligence.get("supplier_quality") or "not_recommended"),
                "confidence": round(max(0.0, min(1.0, confidence)), 4),
            }
        )
        return result


profit_truth_engine = ProfitTruthEngine()

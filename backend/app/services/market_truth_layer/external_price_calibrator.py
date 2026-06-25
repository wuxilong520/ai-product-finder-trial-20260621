from __future__ import annotations

from statistics import mean


class ExternalPriceCalibrator:
    def calibrate(
        self,
        *,
        keyword: str,
        product_title: str,
        current_price: float,
        market_payload: dict,
    ) -> dict:
        normalized_keyword = (keyword or product_title or "").strip()
        market_reference = float(market_payload.get("recommendation_score") or 0)

        amazon_price = round(max(current_price * 1.08, current_price + 2.5), 2)
        shopee_price = round(max(current_price * 0.92, current_price - 1.2), 2)
        tiktok_price = round(max(current_price * 0.97, current_price - 0.5), 2)
        prices = [amazon_price, shopee_price, tiktok_price]
        real_market_price = round(mean(prices), 2)

        if market_reference >= 70:
            demand_signal = "strong"
        elif market_reference >= 45:
            demand_signal = "medium"
        else:
            demand_signal = "weak"

        return {
            "real_market_price": real_market_price,
            "price_range": {
                "min": round(min(prices), 2),
                "max": round(max(prices), 2),
                "amazon": amazon_price,
                "shopee": shopee_price,
                "tiktok_shop": tiktok_price,
            },
            "demand_signal": demand_signal,
            "still_uses_simulated_data": True,
            "simulated_dependencies": [
                "amazon_market_price_rules",
                "shopee_market_price_rules",
                "tiktok_market_price_rules",
                "external_market_api_not_connected",
            ],
            "source": {
                "keyword": normalized_keyword,
                "mode": "rule_calibrated_external_shadow",
            },
        }


external_price_calibrator = ExternalPriceCalibrator()

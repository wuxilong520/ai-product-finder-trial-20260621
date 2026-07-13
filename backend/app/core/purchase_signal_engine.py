from __future__ import annotations


class PurchaseSignalEngine:
    def score(
        self,
        *,
        amazon_signal: float,
        advertising_signal: float,
        brand_signal: float,
        search_intent: float,
    ) -> float:
        value = (
            float(amazon_signal or 0) * 0.35
            + float(advertising_signal or 0) * 0.35
            + float(brand_signal or 0) * 0.2
            + float(search_intent or 0) * 0.1
        )
        return round(max(0.0, min(100.0, value)), 2)


purchase_signal_engine = PurchaseSignalEngine()


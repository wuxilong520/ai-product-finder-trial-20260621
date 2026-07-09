from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.supply_intelligence_engine import SupplyQuery, supply_intelligence_engine
from app.repositories.supplier_match import supplier_match_repository


class SupplierMatchingEngine:
    def match(
        self,
        db: Session,
        keyword: str,
        *,
        category: str | None = None,
        target_market: str = "global",
        expected_price: float | None = None,
        quantity: int = 100,
    ) -> dict:
        normalized_keyword = keyword.strip()
        supply_result = supply_intelligence_engine.analyze(
            db,
            SupplyQuery(
                keyword=normalized_keyword,
                category=category,
                target_market=target_market,
                expected_price=expected_price,
                quantity=quantity,
            ),
        )
        unique_matches = self._deduplicate(
            [
                {
                    "product_id": None,
                    "supplier_name": item.get("name"),
                    "platform": item.get("platform"),
                    "supplier_title": item.get("product_title") or normalized_keyword,
                    "supplier_url": item.get("product_url") or item.get("search_url") or "",
                    "supplier_price": item.get("price_mid"),
                    "currency": item.get("currency"),
                    "match_score": item.get("market_match", 0),
                    "availability": "available" if not item.get("is_mock") else "mock",
                    "moq": item.get("min_order_quantity"),
                    "supplier_score": item.get("supplier_score"),
                    "supplier_level": item.get("supplier_level"),
                    "supplier_confidence": item.get("supplier_confidence"),
                    "profit_estimate": item.get("estimated_profit"),
                    "risk_flags": item.get("risk_flags", []),
                    "data_source": item.get("data_source"),
                    "source_type": item.get("source_type") or item.get("data_source"),
                    "supplier_type": item.get("supplier_type"),
                    "location": item.get("location"),
                    "certification": item.get("certification"),
                    "delivery_time": item.get("delivery_time"),
                    "price_change": item.get("price_change"),
                    "stock_change": item.get("stock_change"),
                    "procurement_recommendation": supply_result.get("procurement_recommendation", {}).get("decision"),
                    "risk_level": self._risk_level(
                        supplier_confidence=item.get("supplier_confidence"),
                        supplier_score=item.get("supplier_score"),
                        risk_flags=item.get("risk_flags", []),
                        is_mock=item.get("is_mock"),
                    ),
                }
                for item in supply_result.get("suppliers", [])
                if item.get("product_url") or item.get("search_url")
            ]
        )
        supplier_match_repository.upsert_many(db, unique_matches)
        return {
            "suppliers": unique_matches,
            "supplier_score": supply_result.get("supplier_score"),
            "supplier_confidence": supply_result.get("supplier_confidence"),
            "confidence": supply_result.get("confidence"),
            "risk_flags": supply_result.get("risk_flags", []),
            "cost_estimate": supply_result.get("cost_estimate"),
            "profit_preview": supply_result.get("profit_preview"),
            "procurement_recommendation": supply_result.get("procurement_recommendation"),
            "is_mock": supply_result.get("is_mock"),
            "source_type": (supply_result.get("selected_supplier") or {}).get("source_type") or supply_result.get("data_source"),
            "risk_level": self._risk_level(
                supplier_confidence=supply_result.get("supplier_confidence"),
                supplier_score=supply_result.get("supplier_score"),
                risk_flags=supply_result.get("risk_flags", []),
                is_mock=supply_result.get("is_mock"),
            ),
        }

    def _deduplicate(self, matches: list[dict]) -> list[dict]:
        seen: set[tuple[int | None, str, str]] = set()
        unique: list[dict] = []
        for item in matches:
            key = (item.get("product_id"), item["platform"], item["supplier_url"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique[:8]

    def _risk_level(
        self,
        *,
        supplier_confidence: float | None,
        supplier_score: float | None,
        risk_flags: list[str] | None,
        is_mock: bool | None,
    ) -> str:
        flags = set(risk_flags or [])
        confidence = float(supplier_confidence or 0)
        score = float(supplier_score or 0)
        if is_mock or confidence < 0.6 or {"mock_data_used", "supplier_unverified", "high_moq"} & flags:
            return "high"
        if score >= 80 and confidence >= 0.8 and not flags:
            return "low"
        return "medium"


supplier_matching_engine = SupplierMatchingEngine()

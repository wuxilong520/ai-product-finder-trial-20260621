from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.supplier_match import supplier_match_repository
from app.services.data_hub import data_hub


class SupplierMatchingEngine:
    def match(self, db: Session, keyword: str) -> dict:
        normalized_keyword = keyword.strip()
        offers = data_hub.get_supplier_data(db, keyword=normalized_keyword)
        unique_matches = self._deduplicate(
            [
                {
                    "product_id": item.product_id,
                    "supplier_name": item.supplier_name,
                    "platform": item.platform,
                    "supplier_title": item.supplier_title or item.product_keyword,
                    "supplier_url": item.supplier_url or "",
                    "supplier_price": item.price,
                    "currency": item.currency,
                    "match_score": item.match_score,
                    "availability": item.availability or "pending",
                }
                for item in offers
                if item.supplier_url
            ]
        )
        supplier_match_repository.upsert_many(db, unique_matches)
        return {"suppliers": unique_matches}

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


supplier_matching_engine = SupplierMatchingEngine()

from __future__ import annotations

from difflib import SequenceMatcher

from app.services.providers.base import SupplierProviderBase


class PddProvider(SupplierProviderBase):
    provider_code = "pdd"
    provider_label = "拼多多"

    def search(self, keyword: str) -> list[dict]:
        results: list[dict] = []
        for candidate in self.candidates:
            keyword_source = candidate.keyword_text or candidate.title_zh or candidate.title
            title_similarity = SequenceMatcher(None, keyword.lower(), keyword_source.lower()).ratio() * 52
            category_bonus = 15 if candidate.category_name and keyword.lower() in candidate.category_name.lower() else 0
            price_bonus = 12 if candidate.current_price and candidate.current_price > 0 else 0
            price_reference = float(candidate.current_price) if candidate.current_price else None
            match_score = max(0.0, min(100.0, 22 + title_similarity + category_bonus + price_bonus))
            results.append(
                {
                    "product_id": candidate.product_id,
                    "supplier_name": "拼多多 搜索入口",
                    "platform": self.provider_label,
                    "supplier_title": candidate.keyword_text or candidate.title,
                    "supplier_url": candidate.supplier_url,
                    "supplier_price": price_reference,
                    "currency": candidate.currency_code,
                    "match_score": round(match_score, 2),
                    "availability": "search_link_ready",
                }
            )
        return results

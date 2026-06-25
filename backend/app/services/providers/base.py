from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SupplierProviderCandidate:
    product_id: int | None
    title: str
    title_zh: str | None
    category_name: str | None
    keyword_text: str
    supplier_url: str
    current_price: float | None
    original_price: float | None
    currency_code: str | None


class SupplierProviderBase:
    provider_code: str = ""
    provider_label: str = ""

    def __init__(self, candidates: list[SupplierProviderCandidate]) -> None:
        self.candidates = candidates

    def search(self, keyword: str) -> list[dict]:
        raise NotImplementedError

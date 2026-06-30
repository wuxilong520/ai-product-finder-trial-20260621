from __future__ import annotations

from sqlalchemy.orm import Session

from app.decision import DecisionPolicy
from app.core.schemas import SupplierOfferSchema
from app.providers import MockSupplierProvider, Provider1688, ProviderFactoryDirect, ProviderPDD


class SupplierSyncPipeline:
    def __init__(self) -> None:
        self.providers = [
            MockSupplierProvider(),
            Provider1688(),
            ProviderPDD(),
            ProviderFactoryDirect(),
        ]

    def sync_keyword(self, db: Session, keyword: str) -> list[SupplierOfferSchema]:
        dedup: dict[tuple[int | None, str, str | None], SupplierOfferSchema] = {}
        for provider in self.providers:
            for item in provider.search_suppliers(db, keyword):
                key = (item.product_id, item.platform, item.supplier_url)
                existing = dedup.get(key)
                if not existing or item.match_score > existing.match_score:
                    dedup[key] = item
        items = list(dedup.values())
        items.sort(key=lambda item: item.match_score, reverse=True)
        return items[:12]

    def sync_keyword_with_policy(self, db: Session, keyword: str, policy: DecisionPolicy | None) -> list[SupplierOfferSchema]:
        items = self.sync_keyword(db, keyword)
        if not policy:
            return items

        strategy = policy.supplier_strategy
        provider_name = policy.provider_routing.get("supplier_provider") or policy.provider_routing.get("supplier") or "MixedSupplierProvider"

        if strategy == "cheapest":
            items = [item for item in items if item.price is not None]
        elif strategy == "quality":
            items = [item for item in items if item.rating is not None]

        def rank(item: SupplierOfferSchema) -> float:
            price_score = 100 - float(item.price or 100) if item.price is not None else 0
            rating_score = float(item.rating or 0) * 20
            base_match = float(item.match_score)
            if strategy == "cheapest":
                return price_score * 0.6 + rating_score * 0.2 + base_match * 0.2
            if strategy == "quality":
                return rating_score * 0.6 + price_score * 0.2 + base_match * 0.2
            return price_score * 0.4 + rating_score * 0.4 + base_match * 0.2

        items.sort(key=rank, reverse=True)
        selected = items[:12]
        for item in selected:
            item.provider_name = provider_name
            item.lineage_chain = [*list(item.lineage_chain or []), provider_name, f"supplier_strategy:{strategy}"]
            item.transform_steps = [*list(item.transform_steps or []), "provider_router_supplier_select"]
        return selected


supplier_sync_pipeline = SupplierSyncPipeline()

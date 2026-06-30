from __future__ import annotations

from sqlalchemy.orm import Session

from app.decision import DecisionPolicy
from app.core.schemas import MarketSignalSchema
from app.providers import FutureAmazonProvider, FutureShopeeProvider, FutureTikTokProvider, MockMarketProvider


class MarketSyncPipeline:
    def __init__(self) -> None:
        self.providers = [
            MockMarketProvider(),
            FutureAmazonProvider(),
            FutureShopeeProvider(),
            FutureTikTokProvider(),
        ]

    def sync_keyword(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        items: list[MarketSignalSchema] = []
        for provider in self.providers:
            items.extend(provider.fetch_market_signals(db, keyword))
        return items

    def sync_keyword_with_policy(self, db: Session, keyword: str, policy: DecisionPolicy | None) -> list[MarketSignalSchema]:
        if not policy:
            return self.sync_keyword(db, keyword)

        selected = []
        provider_name = policy.provider_routing.get("market_provider") or policy.provider_routing.get("market")
        if provider_name == "AmazonProvider":
            selected = [MockMarketProvider(), FutureAmazonProvider()]
        elif provider_name == "AlibabaProvider":
            selected = [MockMarketProvider()]
        elif provider_name == "ShopifyProvider":
            selected = [MockMarketProvider(), FutureShopeeProvider()]
        else:
            selected = [MockMarketProvider()]

        items: list[MarketSignalSchema] = []
        for provider in selected:
            items.extend(provider.fetch_market_signals(db, keyword))
        for item in items:
            item.provider_name = provider_name or item.provider_name
            item.source_platform = policy.market_type
            item.lineage_chain = [*list(item.lineage_chain or []), provider_name or "unknown_market_provider", f"market_type:{policy.market_type}"]
            item.transform_steps = [*list(item.transform_steps or []), "provider_router_market_select"]
        return items

    def sync_category(self, db: Session, category: str) -> list[MarketSignalSchema]:
        items: list[MarketSignalSchema] = []
        for provider in self.providers:
            items.extend(provider.fetch_category_trends(db, category))
        return items


market_sync_pipeline = MarketSyncPipeline()

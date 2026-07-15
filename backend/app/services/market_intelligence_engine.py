from __future__ import annotations

import asyncio

from sqlalchemy.orm import Session

from app.core.market_report_cache import market_report_cache
from app.core.market_intelligence_engine import market_intelligence_engine as core_market_intelligence_engine


class MarketIntelligenceEngineService:
    def cache_key(
        self,
        *,
        report_type: str,
        keyword: str,
        region: str = "US",
        category: str | None = None,
        user_id: int | None = None,
    ) -> str:
        return market_report_cache.build_key(
            report_type=report_type,
            keyword=keyword,
            region=region,
            category=category,
            user_id=user_id,
        )

    def get_cached_report(
        self,
        *,
        report_type: str,
        keyword: str,
        region: str = "US",
        category: str | None = None,
        user_id: int | None = None,
    ) -> dict | None:
        return market_report_cache.get(
            self.cache_key(
                report_type=report_type,
                keyword=keyword,
                region=region,
                category=category,
                user_id=user_id,
            )
        )

    def set_cached_report(
        self,
        *,
        report_type: str,
        keyword: str,
        region: str = "US",
        category: str | None = None,
        user_id: int | None = None,
        payload: dict,
    ) -> dict:
        return market_report_cache.set(
            self.cache_key(
                report_type=report_type,
                keyword=keyword,
                region=region,
                category=category,
                user_id=user_id,
            ),
            payload,
        )

    def analyze_keyword(self, db: Session, keyword: str, region: str = "US", category: str | None = None, user_id: int | None = None) -> dict:
        cached = self.get_cached_report(
            report_type="market_intelligence",
            keyword=keyword,
            region=region,
            category=category,
            user_id=user_id,
        )
        if cached:
            return cached
        payload = core_market_intelligence_engine.analyze_keyword(db, keyword=keyword, region=region, category=category, user_id=user_id)
        return self.set_cached_report(
            report_type="market_intelligence",
            keyword=keyword,
            region=region,
            category=category,
            user_id=user_id,
            payload=payload,
        )

    async def analyze_keyword_async(self, db: Session, keyword: str, region: str = "US", category: str | None = None, user_id: int | None = None) -> dict:
        cached = self.get_cached_report(
            report_type="market_intelligence",
            keyword=keyword,
            region=region,
            category=category,
            user_id=user_id,
        )
        if cached:
            return cached
        payload = await asyncio.to_thread(
            core_market_intelligence_engine.analyze_keyword,
            db,
            keyword,
            region,
            category,
            user_id,
        )
        return self.set_cached_report(
            report_type="market_intelligence",
            keyword=keyword,
            region=region,
            category=category,
            user_id=user_id,
            payload=payload,
        )

    def reality_report(self, *, keyword: str, region: str = "US", category: str | None = None) -> dict:
        cached = self.get_cached_report(
            report_type="market_reality",
            keyword=keyword,
            region=region,
            category=category,
        )
        if cached:
            return cached
        payload = core_market_intelligence_engine.reality_report(keyword=keyword, region=region, category=category)
        return self.set_cached_report(
            report_type="market_reality",
            keyword=keyword,
            region=region,
            category=category,
            payload=payload,
        )

    async def reality_report_async(self, *, keyword: str, region: str = "US", category: str | None = None) -> dict:
        cached = self.get_cached_report(
            report_type="market_reality",
            keyword=keyword,
            region=region,
            category=category,
        )
        if cached:
            return cached
        payload = await asyncio.to_thread(
            core_market_intelligence_engine.reality_report,
            keyword,
            region,
            category,
        )
        return self.set_cached_report(
            report_type="market_reality",
            keyword=keyword,
            region=region,
            category=category,
            payload=payload,
        )

    def commercial_reality_report(self, *, db: Session, keyword: str, region: str = "US") -> dict:
        cached = self.get_cached_report(
            report_type="market_commercial_reality",
            keyword=keyword,
            region=region,
        )
        if cached:
            return cached
        payload = core_market_intelligence_engine.commercial_reality_report(db=db, keyword=keyword, region=region)
        return self.set_cached_report(
            report_type="market_commercial_reality",
            keyword=keyword,
            region=region,
            payload=payload,
        )

    async def commercial_reality_report_async(self, *, db: Session, keyword: str, region: str = "US") -> dict:
        cached = self.get_cached_report(
            report_type="market_commercial_reality",
            keyword=keyword,
            region=region,
        )
        if cached:
            return cached
        payload = await asyncio.to_thread(
            core_market_intelligence_engine.commercial_reality_report,
            db,
            keyword,
            region,
        )
        return self.set_cached_report(
            report_type="market_commercial_reality",
            keyword=keyword,
            region=region,
            payload=payload,
        )

    def analyze_v3(self, db: Session, keyword: str, region: str = "US", category: str | None = None) -> dict:
        return core_market_intelligence_engine.analyze_keyword(db, keyword=keyword, region=region, category=category)


market_intelligence_engine = MarketIntelligenceEngineService()

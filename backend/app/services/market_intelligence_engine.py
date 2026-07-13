from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.market_intelligence_engine import market_intelligence_engine as core_market_intelligence_engine


class MarketIntelligenceEngineService:
    def analyze_keyword(self, db: Session, keyword: str, region: str = "US", category: str | None = None, user_id: int | None = None) -> dict:
        return core_market_intelligence_engine.analyze_keyword(db, keyword=keyword, region=region, category=category, user_id=user_id)

    def reality_report(self, *, keyword: str, region: str = "US", category: str | None = None) -> dict:
        return core_market_intelligence_engine.reality_report(keyword=keyword, region=region, category=category)

    def commercial_reality_report(self, *, db: Session, keyword: str, region: str = "US") -> dict:
        return core_market_intelligence_engine.commercial_reality_report(db=db, keyword=keyword, region=region)

    def analyze_v3(self, db: Session, keyword: str, region: str = "US", category: str | None = None) -> dict:
        return core_market_intelligence_engine.analyze_keyword(db, keyword=keyword, region=region, category=category)


market_intelligence_engine = MarketIntelligenceEngineService()

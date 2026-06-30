from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.schemas import MarketSignalSchema
from app.models.analysis import AIAnalysisResult
from app.models.product import Product


class MarketProviderBase(ABC):
    provider_name = "base_market_provider"

    @abstractmethod
    def fetch_market_signals(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        raise NotImplementedError

    @abstractmethod
    def fetch_category_trends(self, db: Session, category: str) -> list[MarketSignalSchema]:
        raise NotImplementedError


class MockMarketProvider(MarketProviderBase):
    provider_name = "mock_market_provider"

    def fetch_market_signals(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        matches = self._find_matches(db, keyword.strip())
        return [self._build_signal(keyword.strip(), matches)]

    def fetch_category_trends(self, db: Session, category: str) -> list[MarketSignalSchema]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.analysis_results),
                selectinload(Product.crawl_runs),
                selectinload(Product.sourcing_links),
                selectinload(Product.category),
            )
            .where(Product.category.has(name=category))
            .order_by(Product.updated_at.desc())
        )
        matches = list(db.scalars(stmt))
        return [self._build_signal(category.strip(), matches, category=category.strip())]

    def _find_matches(self, db: Session, keyword: str) -> list[Product]:
        pattern = f"%{keyword}%"
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.analysis_results),
                selectinload(Product.crawl_runs),
                selectinload(Product.sourcing_links),
                selectinload(Product.category),
            )
            .where(
                or_(
                    Product.title.ilike(pattern),
                    Product.title_zh.ilike(pattern),
                    Product.description_text.ilike(pattern),
                )
            )
            .order_by(Product.updated_at.desc())
        )
        products = list(db.scalars(stmt))
        if products:
            return products

        analysis_stmt = (
            select(Product)
            .join(AIAnalysisResult, AIAnalysisResult.product_id == Product.id)
            .options(
                selectinload(Product.images),
                selectinload(Product.analysis_results),
                selectinload(Product.crawl_runs),
                selectinload(Product.sourcing_links),
                selectinload(Product.category),
            )
            .where(
                or_(
                    AIAnalysisResult.title_zh.ilike(pattern),
                    AIAnalysisResult.raw_response.is_not(None),
                )
            )
        )
        deduplicated: dict[int, Product] = {}
        for product in db.scalars(analysis_stmt):
            if self._analysis_contains_keyword(product.analysis_results, keyword):
                deduplicated[product.id] = product
        return list(deduplicated.values())

    def _analysis_contains_keyword(self, analysis_results: list[AIAnalysisResult], keyword: str) -> bool:
        needle = keyword.lower()
        for analysis in analysis_results:
            fields = [
                analysis.title_zh or "",
                " ".join(analysis.core_keywords or []),
                " ".join(analysis.selling_points or []),
                " ".join(analysis.sourcing_keywords or []),
            ]
            if any(needle in field.lower() for field in fields):
                return True
        return False

    def _build_signal(self, keyword: str, matches: list[Product], category: str | None = None) -> MarketSignalSchema:
        match_count = len(matches)
        review_total = sum(int(product.review_count or 0) for product in matches)
        avg_rating = self._average([self._to_float(product.rating) for product in matches if product.rating is not None])
        recent_count = sum(1 for product in matches[:10] if product.last_crawled_at is not None)
        analysis_count = sum(1 for product in matches if product.analysis_results)
        top_category = category or self._top_category(matches)

        trend_score = self._clamp(
            18
            + min(match_count * 8, 32)
            + min(recent_count * 4, 18)
            + (12 if analysis_count >= max(1, match_count // 2) else 4 if analysis_count else 0)
            + (10 if review_total >= 300 else 5 if review_total >= 80 else 0)
        )
        demand_level = self._clamp(
            20
            + min(review_total / 15, 36)
            + (12 if avg_rating >= 4.3 else 6 if avg_rating >= 4.0 else 0)
            + (10 if match_count >= 4 else 5 if match_count >= 2 else 0)
        )
        competition_index = self._clamp(
            15
            + min(match_count * 9, 36)
            + min(review_total / 18, 24)
            + (12 if avg_rating >= 4.4 and match_count >= 3 else 0)
        )
        growth_rate = self._clamp((trend_score * 0.55) + (demand_level * 0.45) - 40)
        confidence_score = self._clamp(35 + min(match_count * 9, 35) + min(analysis_count * 6, 20))

        return MarketSignalSchema(
            id=f"market:{keyword}:{top_category or 'uncategorized'}",
            keyword=keyword,
            category=top_category,
            trend_score=round(trend_score, 2),
            growth_rate=round(growth_rate, 2),
            competition_index=round(competition_index, 2),
            demand_level=round(demand_level, 2),
            source_platform="internal_product_library",
            confidence_score=round(confidence_score, 2),
            source_type="mock",
            source_id=f"mock_market:{keyword}:{top_category or 'uncategorized'}",
            truth_level="semi_real" if match_count > 0 else "simulated",
            sync_status="success",
            provider_name=self.provider_name,
            lineage_chain=[self.provider_name],
            transform_steps=["internal_match_scan", "market_signal_build"],
        )

    def _top_category(self, matches: list[Product]) -> str | None:
        categories = [product.category.name for product in matches if product.category and product.category.name]
        if not categories:
            return None
        return Counter(categories).most_common(1)[0][0]

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _to_float(self, value: Decimal | float | int | None) -> float:
        if value is None:
            return 0.0
        return float(value)

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))


class FutureAmazonProvider(MarketProviderBase):
    provider_name = "future_amazon_provider"

    def fetch_market_signals(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        return []

    def fetch_category_trends(self, db: Session, category: str) -> list[MarketSignalSchema]:
        return []


class FutureShopeeProvider(MarketProviderBase):
    provider_name = "future_shopee_provider"

    def fetch_market_signals(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        return []

    def fetch_category_trends(self, db: Session, category: str) -> list[MarketSignalSchema]:
        return []


class FutureTikTokProvider(MarketProviderBase):
    provider_name = "future_tiktok_provider"

    def fetch_market_signals(self, db: Session, keyword: str) -> list[MarketSignalSchema]:
        return []

    def fetch_category_trends(self, db: Session, category: str) -> list[MarketSignalSchema]:
        return []

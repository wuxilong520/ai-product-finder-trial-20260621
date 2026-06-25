from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.analysis import AIAnalysisResult
from app.models.market_intelligence import MarketIntelligence
from app.models.product import Product
from app.repositories.market_intelligence import market_intelligence_repository


class ExternalMarketSignalProvider(Protocol):
    provider_name: str

    def search(self, keyword: str) -> list[dict]:
        ...


@dataclass
class InternalMarketSignalProvider:
    provider_name: str = "internal_product_library"

    def search(self, keyword: str) -> list[dict]:
        return []


class MarketIntelligenceEngine:
    def __init__(self) -> None:
        self.providers: dict[str, ExternalMarketSignalProvider] = {
            "internal": InternalMarketSignalProvider(),
        }

    def analyze_keyword(self, db: Session, keyword: str) -> dict:
        normalized_keyword = keyword.strip()
        matches = self._find_matches(db, normalized_keyword)
        payload = self._build_payload(normalized_keyword, matches)
        market_intelligence_repository.create(db, keyword=normalized_keyword, **payload)
        return payload

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
                    AIAnalysisResult.raw_response.cast(db.bind.dialect.type_descriptor(MarketIntelligence.__table__.c.reasons.type)).isnot(None),
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

    def _build_payload(self, keyword: str, matches: list[Product]) -> dict:
        match_count = len(matches)
        review_total = sum(int(product.review_count or 0) for product in matches)
        avg_rating = self._average([self._to_float(product.rating) for product in matches if product.rating is not None])
        avg_price = self._average([self._to_float(product.current_price) for product in matches if product.current_price is not None])
        recent_count = sum(1 for product in matches[:10] if product.last_crawled_at is not None)
        analysis_count = sum(1 for product in matches if product.analysis_results)
        sourcing_count = sum(1 for product in matches if product.sourcing_links)
        category = self._top_category(matches)

        trend_score = self._clamp(
            18
            + min(match_count * 8, 32)
            + min(recent_count * 4, 18)
            + (12 if analysis_count >= max(1, match_count // 2) else 4 if analysis_count else 0)
            + (10 if review_total >= 300 else 5 if review_total >= 80 else 0)
        )
        demand_score = self._clamp(
            20
            + min(review_total / 15, 36)
            + (12 if avg_rating >= 4.3 else 6 if avg_rating >= 4.0 else 0)
            + (10 if match_count >= 4 else 5 if match_count >= 2 else 0)
        )
        competition_score = self._clamp(
            15
            + min(match_count * 9, 36)
            + min(review_total / 18, 24)
            + (12 if avg_rating >= 4.4 and match_count >= 3 else 0)
        )
        opportunity_score = self._clamp(
            22
            + (18 if 15 <= avg_price <= 80 else 8 if avg_price > 0 else 0)
            + (12 if sourcing_count >= max(1, match_count // 2) else 0)
            + (14 if demand_score >= 55 and competition_score <= 60 else 4)
            + (8 if analysis_count else 0)
        )
        recommendation_score = self._clamp(
            trend_score * 0.25
            + demand_score * 0.3
            + (100 - competition_score) * 0.2
            + opportunity_score * 0.25
        )
        recommendation = self._recommendation(recommendation_score, competition_score)
        reasons = self._reasons(
            keyword=keyword,
            match_count=match_count,
            review_total=review_total,
            avg_rating=avg_rating,
            avg_price=avg_price,
            trend_score=trend_score,
            demand_score=demand_score,
            competition_score=competition_score,
            opportunity_score=opportunity_score,
            analysis_count=analysis_count,
            sourcing_count=sourcing_count,
        )

        return {
            "category": category,
            "trend_score": round(trend_score, 2),
            "demand_score": round(demand_score, 2),
            "competition_score": round(competition_score, 2),
            "opportunity_score": round(opportunity_score, 2),
            "recommendation_score": round(recommendation_score, 2),
            "recommendation": recommendation,
            "reasons": reasons,
            "source": "internal_product_library",
        }

    def _reasons(
        self,
        *,
        keyword: str,
        match_count: int,
        review_total: int,
        avg_rating: float,
        avg_price: float,
        trend_score: float,
        demand_score: float,
        competition_score: float,
        opportunity_score: float,
        analysis_count: int,
        sourcing_count: int,
    ) -> list[str]:
        reasons: list[str] = []
        if match_count > 0:
            reasons.append(f"在现有商品库里，关键词“{keyword}”匹配到 {match_count} 条真实商品记录。")
        else:
            reasons.append(f"现有商品库里暂时没有找到大量“{keyword}”相关记录，本次按库内真实空缺做保守判断。")

        if trend_score >= 65:
            reasons.append("趋势分较高：说明这个词在现有采集和分析数据里出现频率不错。")
        elif trend_score >= 45:
            reasons.append("趋势分中等：有一定热度，但还没到明显爆发阶段。")
        else:
            reasons.append("趋势分偏低：目前库内出现频率还不高。")

        if demand_score >= 65:
            reasons.append(f"需求分较高：相关商品累计评论约 {review_total}，整体评分约 {avg_rating:.1f}。")
        elif demand_score >= 45:
            reasons.append(f"需求分中等：累计评论约 {review_total}，说明有需求但还需要更多样本。")
        else:
            reasons.append("需求分偏弱：当前库内评论和口碑样本还不够多。")

        if competition_score >= 70:
            reasons.append("竞争分偏高：同类商品数量和评论基础都不低，新切入要更谨慎。")
        elif competition_score >= 45:
            reasons.append("竞争分中等：能做，但最好找差异化卖点。")
        else:
            reasons.append("竞争分相对可控：库内同类竞争压力暂时不算大。")

        if opportunity_score >= 65:
            reasons.append(f"机会指数较好：当前均价约 {avg_price:.2f}，且已有 {analysis_count} 条分析数据、{sourcing_count} 条供应链线索。")
        elif opportunity_score >= 45:
            reasons.append("机会指数中等：可以继续观察，适合补充更多供应链和平台数据。")
        else:
            reasons.append("机会指数偏弱：现有样本太少，暂时不适合下强结论。")

        return reasons[:6]

    def _recommendation(self, recommendation_score: float, competition_score: float) -> str:
        if recommendation_score >= 70 and competition_score < 68:
            return "推荐关注"
        if recommendation_score >= 48:
            return "继续观察"
        return "暂不推荐"

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


market_intelligence_engine = MarketIntelligenceEngine()

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.models.analysis import AIAnalysisResult
from app.models.crawl_run import CrawlRun
from app.models.product import Product
from app.repositories.product import product_repository
from app.repositories.product_intelligence import product_intelligence_repository


class ProductIntelligenceEngine:
    def get_or_create_intelligence(self, db: Session, product_id: int, workspace_id: int | None = None) -> dict:
        try:
            product = product_repository.get_by_id(db, product_id, workspace_id=workspace_id)
        except Exception as exc:
            raise AppError("PRODUCT_QUERY_FAILED", f"读取商品失败：{exc}", "db", 500) from exc
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        latest_analysis = self._get_latest_analysis(product)
        latest_crawl = self._get_latest_crawl(product)
        payload = self._build_scores(product, latest_analysis, latest_crawl)
        try:
            product_intelligence_repository.upsert(db, product_id=product.id, **payload)
        except Exception as exc:
            raise AppError("PRODUCT_INTELLIGENCE_SAVE_FAILED", f"保存商品情报失败：{exc}", "db", 500) from exc
        return payload

    def _get_latest_analysis(self, product: Product) -> AIAnalysisResult | None:
        if not product.analysis_results:
            return None
        return max(product.analysis_results, key=lambda item: item.id)

    def _get_latest_crawl(self, product: Product) -> CrawlRun | None:
        if not product.crawl_runs:
            return None
        return max(product.crawl_runs, key=lambda item: item.id)

    def _build_scores(
        self,
        product: Product,
        latest_analysis: AIAnalysisResult | None,
        latest_crawl: CrawlRun | None,
    ) -> dict:
        price = self._to_float(product.current_price)
        original_price = self._to_float(product.original_price)
        rating = self._to_float(product.rating)
        review_count = int(product.review_count or 0)
        image_count = len(product.images or [])
        has_translation = bool(product.title_zh)
        has_analysis = latest_analysis is not None
        has_sourcing = bool(product.sourcing_links)
        crawl_success = bool(latest_crawl and latest_crawl.status == "success")

        market_score = self._clamp(
            20
            + min(review_count / 20, 35)
            + (12 if rating >= 4.2 else 6 if rating >= 3.8 else 0)
            + (8 if crawl_success else 0)
            + (8 if image_count >= 3 else 4 if image_count >= 1 else 0)
            + (7 if has_analysis else 0)
        )

        competition_score = self._clamp(
            10
            + min(review_count / 18, 55)
            + (15 if rating >= 4.5 and review_count >= 200 else 8 if rating >= 4.0 else 0)
            + (8 if has_analysis and len(latest_analysis.core_keywords or []) >= 4 else 0)
        )

        margin_gap = max(price - original_price, 0) if price and original_price else 0
        raw_margin_rate = (margin_gap / original_price) if original_price and original_price > 0 else 0
        profit_score = self._clamp(
            18
            + (20 if 15 <= price <= 80 else 10 if price > 0 else 0)
            + min(raw_margin_rate * 100, 25)
            + (15 if has_sourcing else 0)
            + (12 if has_analysis and len(latest_analysis.sourcing_keywords or []) >= 2 else 0)
        )

        risk_score = self._clamp(
            18
            + (20 if rating and rating < 3.8 else 8 if rating and rating < 4.2 else 0)
            + (18 if review_count < 10 else 8 if review_count < 50 else 0)
            + (14 if image_count == 0 else 0)
            + (12 if not has_translation else 0)
            + (10 if not has_analysis else 0)
            + (8 if not crawl_success else 0)
        )

        recommendation_score = self._clamp(
            market_score * 0.28
            + (100 - competition_score) * 0.2
            + profit_score * 0.32
            + (100 - risk_score) * 0.2
        )

        recommendation = self._pick_recommendation(recommendation_score, risk_score)
        reasons = self._build_reasons(
            product=product,
            market_score=market_score,
            competition_score=competition_score,
            profit_score=profit_score,
            risk_score=risk_score,
            recommendation_score=recommendation_score,
            has_analysis=has_analysis,
            has_sourcing=has_sourcing,
            has_translation=has_translation,
            price=price,
            review_count=review_count,
            rating=rating,
        )

        return {
            "market_score": round(market_score, 2),
            "competition_score": round(competition_score, 2),
            "profit_score": round(profit_score, 2),
            "risk_score": round(risk_score, 2),
            "recommendation_score": round(recommendation_score, 2),
            "recommendation": recommendation,
            "reasons": reasons,
        }

    def _build_reasons(
        self,
        *,
        product: Product,
        market_score: float,
        competition_score: float,
        profit_score: float,
        risk_score: float,
        recommendation_score: float,
        has_analysis: bool,
        has_sourcing: bool,
        has_translation: bool,
        price: float,
        review_count: int,
        rating: float,
    ) -> list[str]:
        reasons: list[str] = []

        if market_score >= 70:
            reasons.append(f"市场热度较好：评论量约 {review_count}，商品页面信息较完整。")
        elif market_score >= 45:
            reasons.append(f"市场热度中等：目前评论量约 {review_count}，还需要继续观察趋势。")
        else:
            reasons.append(f"市场热度偏弱：当前评论量约 {review_count}，公开数据偏少。")

        if competition_score >= 70:
            reasons.append("竞争度偏高：同类商品可能已经有较多成熟卖家在做。")
        elif competition_score >= 45:
            reasons.append("竞争度中等：可以切入，但要进一步看差异化空间。")
        else:
            reasons.append("竞争度相对可控：公开迹象看，强势竞争压力不算大。")

        if profit_score >= 70:
            reasons.append("利润潜力较好：价格带合适，且已有采购线索可继续核算成本。")
        elif profit_score >= 45:
            reasons.append("利润潜力一般：建议补充供应链成本后再做最终判断。")
        else:
            reasons.append("利润潜力偏弱：当前公开价格和线索不足以支撑高利润判断。")

        if risk_score >= 65:
            reasons.append("风险偏高：信息缺口较多，或者评分/评论基础不够稳。")
        elif risk_score >= 40:
            reasons.append("风险中等：建议结合更多采集和人工判断再决定。")
        else:
            reasons.append("风险相对可控：当前公开信息完整度还不错。")

        if not has_analysis:
            reasons.append("当前缺少 AI 分析结果，本次部分评分由规则引擎补足。")
        if not has_sourcing:
            reasons.append("当前还没有稳定供应链链接，利润判断会偏保守。")
        if not has_translation:
            reasons.append("当前还没有中文标题，后续人工研判效率会受一点影响。")
        if price <= 0:
            reasons.append("当前没有拿到有效价格，利润评分已按保守逻辑处理。")
        if rating and rating < 4:
            reasons.append(f"当前评分约 {rating:.1f}，用户口碑需要重点关注。")
        if recommendation_score >= 75 and product.title:
            reasons.append(f"综合看，这个商品更适合优先进入上架候选：{product.title[:36]}")

        return reasons[:7]

    def _pick_recommendation(self, recommendation_score: float, risk_score: float) -> str:
        if recommendation_score >= 72 and risk_score < 60:
            return "推荐上架"
        if recommendation_score >= 48:
            return "观察"
        return "不推荐"

    def _to_float(self, value: Decimal | float | int | None) -> float:
        if value is None:
            return 0.0
        return float(value)

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))


product_intelligence_engine = ProductIntelligenceEngine()

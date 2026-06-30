from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.models.product import Product
from app.repositories.business_truth_decision import business_truth_decision_repository
from app.repositories.product import product_repository
from app.services.data_hub import data_hub
from app.services.decision_engine import decision_engine
from app.services.decision_truth_wrapper import decision_truth_wrapper
from app.services.product_intelligence_engine import product_intelligence_engine


@dataclass
class P5ProductSnapshot:
    product: Product
    keyword: str
    category: str | None
    product_intelligence: dict
    market_intelligence: dict
    supplier_matches: list[dict]
    decision: dict
    business_truth: dict


class AIGlobalProductDecisionEngine:
    def predict(self, db: Session, product_id: int, horizon_days: int = 30) -> dict:
        snapshot = self._build_snapshot(db, product_id)
        prediction = self._build_prediction(snapshot, horizon_days)
        return {
            "product_id": snapshot.product.id,
            "keyword": snapshot.keyword,
            "forecast_window_days": horizon_days,
            **prediction,
        }

    def get_rankings(self, db: Session) -> dict:
        snapshots = self._build_all_snapshots(db)
        return {
            "scanned_products": len(snapshots),
            "profit_ranking": self._ranking_group(snapshots, lambda item: float(item.business_truth["profit_margin"]) * 100),
            "growth_ranking": self._ranking_group(snapshots, lambda item: self._build_prediction(item, 30)["growth_forecast"]),
            "risk_ranking": self._ranking_group(snapshots, lambda item: float(item.product_intelligence["risk_score"]), reverse=False),
        }

    def get_recommendations(
        self,
        db: Session,
        keyword: str | None = None,
        category: str | None = None,
        limit: int = 10,
        truth_level: str | None = None,
        source_type: str | None = None,
        freshness_min: float | None = None,
    ) -> dict:
        snapshots = self._build_all_snapshots(db)
        filtered = self._filter_snapshots(
            snapshots,
            keyword=keyword,
            category=category,
            truth_level=truth_level,
            source_type=source_type,
            freshness_min=freshness_min,
        )
        items: list[dict] = []

        for snapshot in filtered:
            prediction = self._build_prediction(snapshot, 30)
            truth_score = float(snapshot.business_truth["truth_score"])
            estimated_profit = float(snapshot.business_truth["profit"])
            recommendation_score = self._clamp(
                truth_score * 0.45
                + float(snapshot.decision["final_score"]) * 0.25
                + prediction["explosion_probability"] * 0.20
                + prediction["profit_forecast"] * 0.10
            )
            items.append(
                {
                    "product_id": snapshot.product.id,
                    "title": snapshot.product.title,
                    "title_zh": snapshot.product.title_zh,
                    "keyword": snapshot.keyword,
                    "category": snapshot.category,
                    "recommendation_score": round(recommendation_score, 2),
                    "estimated_profit": round(estimated_profit, 2),
                    "recommendation": self._recommendation_label(recommendation_score),
                    "truth_level": snapshot.business_truth.get("truth_level"),
                    "source_type": snapshot.supplier_matches[0].get("source_type") if snapshot.supplier_matches else None,
                    "freshness_score": snapshot.supplier_matches[0].get("freshness_score") if snapshot.supplier_matches else None,
                    "reasons": [
                        f"真实性决策分 {truth_score:.1f}，说明利润和风险校准后仍有业务价值。",
                        f"未来 30 天爆发概率约 {prediction['explosion_probability']:.1f} / 100，具备继续跟进的理由。",
                        f"当前预估利润约 {estimated_profit:.2f}，利润预测分约 {prediction['profit_forecast']:.1f} / 100。",
                    ],
                }
            )

        items.sort(key=lambda item: item["recommendation_score"], reverse=True)
        return {
            "keyword": keyword,
            "category": category,
            "truth_level": truth_level,
            "source_type": source_type,
            "freshness_min": freshness_min,
            "total_scanned": len(filtered),
            "items": items[:limit],
        }

    def _build_all_snapshots(self, db: Session) -> list[P5ProductSnapshot]:
        products, _ = product_repository.list(db, search=None, skip=0, limit=100)
        return [self._build_snapshot(db, product.id) for product in products]

    def _build_snapshot(self, db: Session, product_id: int) -> P5ProductSnapshot:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        keyword = self._pick_keyword(product)
        category = product.category.name if product.category else None
        product_intelligence = product_intelligence_engine.get_or_create_intelligence(db, product.id)
        market_signals = data_hub.get_market_data(db, keyword=keyword)
        supplier_offer_items = data_hub.get_supplier_data(db, keyword=keyword)
        market_intelligence = {
            "trend_score": round(self._mean_attr_dict(market_signals, "trend_score"), 2),
            "demand_score": round(self._mean_attr_dict(market_signals, "demand_level"), 2),
            "competition_score": round(self._mean_attr_dict(market_signals, "competition_index"), 2),
            "opportunity_score": round(
                max(
                    0.0,
                    min(
                        100.0,
                        self._mean_attr_dict(market_signals, "trend_score") * 0.35
                        + self._mean_attr_dict(market_signals, "demand_level") * 0.35
                        + (100 - self._mean_attr_dict(market_signals, "competition_index")) * 0.20
                        + self._mean_attr_dict(market_signals, "confidence_score") * 0.10,
                    ),
                ),
                2,
            ),
        }
        supplier_matches = [
            {
                "platform": item.platform,
                "match_score": item.match_score,
                "supplier_name": item.supplier_name,
                "supplier_title": item.supplier_title,
                "supplier_url": item.supplier_url,
                "truth_level": item.truth_level,
                "source_type": item.source_type,
                "freshness_score": item.freshness_score,
            }
            for item in supplier_offer_items
        ]
        decision = decision_engine.recommend(db, product.id)

        truth_record = business_truth_decision_repository.get_by_product_id(db, product.id)
        if truth_record:
            business_truth = {
                "truth_score": float(truth_record.truth_score),
                "truth_recommendation": truth_record.truth_recommendation,
                "truth_level": truth_record.truth_level,
                "profit": float(truth_record.profit),
                "profit_margin": float(truth_record.profit_margin),
                "demand_signal": truth_record.demand_signal,
                "reasons": list(truth_record.reasons or []),
            }
        else:
            truth_payload = decision_truth_wrapper.recommend(db, product.id)
            business_truth = {
                "truth_score": float(truth_payload["truth_score"]),
                "truth_recommendation": truth_payload["truth_recommendation"],
                "truth_level": truth_payload["truth_level"],
                "profit": float(truth_payload["profit"]),
                "profit_margin": float(truth_payload["profit_margin"]),
                "demand_signal": truth_payload["demand_signal"],
                "reasons": list(truth_payload["reasons"] or []),
            }

        return P5ProductSnapshot(
            product=product,
            keyword=keyword,
            category=category,
            product_intelligence=product_intelligence,
            market_intelligence=market_intelligence,
            supplier_matches=supplier_matches,
            decision=decision,
            business_truth=business_truth,
        )

    def _build_prediction(self, snapshot: P5ProductSnapshot, horizon_days: int) -> dict:
        day_factor = 0.82 if horizon_days <= 7 else 1.0
        intelligence = snapshot.product_intelligence
        market = snapshot.market_intelligence
        truth = snapshot.business_truth
        supplier_score = self._supplier_score(snapshot.supplier_matches)

        growth_forecast = self._clamp(
            (
                float(market["trend_score"]) * 0.34
                + float(market["opportunity_score"]) * 0.22
                + float(snapshot.decision["final_score"]) * 0.20
                + float(truth["truth_score"]) * 0.14
                + supplier_score * 0.10
            )
            * day_factor
        )
        demand_forecast = self._clamp(
            (
                float(market["demand_score"]) * 0.55
                + float(intelligence["market_score"]) * 0.20
                + float(snapshot.decision["market_score"]) * 0.15
                + (10 if truth["demand_signal"] == "strong" else 5 if truth["demand_signal"] == "medium" else 0)
            )
            * day_factor
        )
        competition_forecast = self._clamp(
            (
                float(market["competition_score"]) * 0.58
                + float(intelligence["competition_score"]) * 0.30
                + max(0.0, supplier_score - 55) * 0.12
            )
            * (1.0 if horizon_days <= 7 else 1.05)
        )
        profit_forecast = self._clamp(
            (
                float(intelligence["profit_score"]) * 0.30
                + float(snapshot.decision["profit_score"]) * 0.20
                + float(truth["truth_score"]) * 0.18
                + min(max(float(truth["profit_margin"]) * 100, 0), 35) * 0.22
                + supplier_score * 0.10
            )
            * day_factor
        )
        explosion_probability = self._clamp(
            growth_forecast * 0.30
            + demand_forecast * 0.25
            + (100 - competition_forecast) * 0.15
            + profit_forecast * 0.18
            + float(truth["truth_score"]) * 0.12
        )

        return {
            "growth_forecast": round(growth_forecast, 2),
            "demand_forecast": round(demand_forecast, 2),
            "competition_forecast": round(competition_forecast, 2),
            "profit_forecast": round(profit_forecast, 2),
            "explosion_probability": round(explosion_probability, 2),
            "reasons": [
                f"增长预测主要参考市场热度 {float(market['trend_score']):.1f}、机会指数 {float(market['opportunity_score']):.1f} 和真实性分 {float(truth['truth_score']):.1f}。",
                f"需求预测参考需求分 {float(market['demand_score']):.1f} 与商品热度分 {float(intelligence['market_score']):.1f}。",
                f"竞争预测参考市场竞争分 {float(market['competition_score']):.1f} 与商品竞争分 {float(intelligence['competition_score']):.1f}。",
                f"利润预测参考利润率 {float(truth['profit_margin']) * 100:.2f}% 与供应链匹配度 {supplier_score:.1f}。",
            ],
        }

    def _ranking_group(self, snapshots: list[P5ProductSnapshot], metric, reverse: bool = True) -> dict:
        ranked = sorted(
            (
                {
                    "product_id": snapshot.product.id,
                    "title": snapshot.product.title,
                    "score": round(float(metric(snapshot)), 2),
                    "category": snapshot.category,
                }
                for snapshot in snapshots
            ),
            key=lambda item: item["score"],
            reverse=reverse,
        )
        return {
            "top_10": ranked[:10],
            "top_50": ranked[:50],
            "top_100": ranked[:100],
        }

    def _filter_snapshots(
        self,
        snapshots: list[P5ProductSnapshot],
        keyword: str | None,
        category: str | None,
        truth_level: str | None = None,
        source_type: str | None = None,
        freshness_min: float | None = None,
    ) -> list[P5ProductSnapshot]:
        result = snapshots
        if keyword:
            needle = keyword.lower()
            result = [
                item for item in result
                if needle in item.keyword.lower()
                or needle in item.product.title.lower()
                or (item.product.title_zh and needle in item.product.title_zh.lower())
            ]
        if category:
            needle = category.lower()
            result = [item for item in result if item.category and needle in item.category.lower()]
        if truth_level:
            result = [item for item in result if item.business_truth.get("truth_level") == truth_level]
        if source_type:
            result = [item for item in result if any(match.get("source_type") == source_type for match in item.supplier_matches)]
        if freshness_min is not None:
            result = [
                item
                for item in result
                if item.supplier_matches and max(float(match.get("freshness_score") or 0) for match in item.supplier_matches[:3]) >= freshness_min
            ]
        return result

    def _supplier_score(self, suppliers: list[dict]) -> float:
        if not suppliers:
            return 0.0
        return mean(float(item["match_score"]) for item in suppliers[:3])

    def _pick_keyword(self, product: Product) -> str:
        source = product.title_zh or product.title or product.description_text or f"product-{product.id}"
        cleaned = " ".join(str(source).split())
        parts = cleaned.split(" ")
        return " ".join(parts[:3]) if parts else cleaned

    def _recommendation_label(self, score: float) -> str:
        if score >= 80:
            return "优先推荐"
        if score >= 65:
            return "建议跟进"
        if score >= 50:
            return "继续观察"
        return "暂不推荐"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, value))

    def _mean_attr_dict(self, items: list, field: str) -> float:
        if not items:
            return 0.0
        values = [float(getattr(item, field, 0) or 0) for item in items]
        if not values:
            return 0.0
        return mean(values)


p5_global_product_decision_engine = AIGlobalProductDecisionEngine()

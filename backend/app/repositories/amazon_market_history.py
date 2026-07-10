from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.amazon_market_signal import AmazonMarketHistory, AmazonMarketSignal


class AmazonMarketHistoryRepository:
    def create_signal_snapshot(
        self,
        db: Session,
        *,
        keyword: str,
        marketplace: str,
        signal: dict,
        status: str,
        confidence: float,
        timestamp: str,
    ) -> AmazonMarketSignal:
        record = AmazonMarketSignal(
            keyword=keyword,
            marketplace=marketplace,
            bsr_rank=int(signal.get("bsr_rank") or 0) or None,
            category_rank=int(signal.get("category_rank") or 0) or None,
            review_count=int(signal.get("review_count") or 0),
            rating=float(signal.get("rating") or 0),
            seller_count=int(signal.get("seller_count") or 0),
            price_min=float((signal.get("price_range") or {}).get("min") or 0),
            price_max=float((signal.get("price_range") or {}).get("max") or 0),
            price_average=float((signal.get("price_range") or {}).get("average") or 0),
            competition_density=float(signal.get("competition_density") or 0),
            demand_signal=float(signal.get("demand_score") or 0),
            captured_at=timestamp,
            status=status,
            confidence=float(confidence or 0),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def create_history_point(
        self,
        db: Session,
        *,
        keyword: str,
        marketplace: str,
        signal: dict,
        captured_at: datetime,
    ) -> AmazonMarketHistory:
        record = AmazonMarketHistory(
            keyword=keyword,
            marketplace=marketplace,
            bsr=int(signal.get("bsr_rank") or 0) or None,
            reviews=int(signal.get("review_count") or 0),
            price=float((signal.get("price_range") or {}).get("average") or 0),
            seller_count=int(signal.get("seller_count") or 0),
            captured_at=captured_at,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def latest(self, db: Session, *, keyword: str, marketplace: str) -> AmazonMarketSignal | None:
        stmt = (
            select(AmazonMarketSignal)
            .where(AmazonMarketSignal.keyword == keyword)
            .where(AmazonMarketSignal.marketplace == marketplace)
            .order_by(AmazonMarketSignal.created_at.desc(), AmazonMarketSignal.id.desc())
        )
        return db.scalar(stmt)

    def growth_windows(self, db: Session, *, keyword: str, marketplace: str) -> dict:
        now = datetime.now(UTC)
        windows = {"7d": 7, "30d": 30, "90d": 90}
        latest_stmt = (
            select(AmazonMarketHistory)
            .where(AmazonMarketHistory.keyword == keyword)
            .where(AmazonMarketHistory.marketplace == marketplace)
            .order_by(AmazonMarketHistory.captured_at.desc(), AmazonMarketHistory.id.desc())
        )
        latest = db.scalar(latest_stmt)
        if not latest:
            return {"7d": 0.0, "30d": 0.0, "90d": 0.0}

        result: dict[str, float] = {}
        for key, days in windows.items():
            cutoff = now - timedelta(days=days)
            baseline_stmt = (
                select(AmazonMarketHistory)
                .where(AmazonMarketHistory.keyword == keyword)
                .where(AmazonMarketHistory.marketplace == marketplace)
                .where(AmazonMarketHistory.captured_at >= cutoff)
                .order_by(AmazonMarketHistory.captured_at.asc(), AmazonMarketHistory.id.asc())
            )
            baseline = db.scalar(baseline_stmt)
            if not baseline or float(baseline.reviews or 0) <= 0:
                result[key] = 0.0
                continue
            result[key] = round(((float(latest.reviews or 0) - float(baseline.reviews or 0)) / float(baseline.reviews or 1)) * 100, 2)
        return result


amazon_market_history_repository = AmazonMarketHistoryRepository()

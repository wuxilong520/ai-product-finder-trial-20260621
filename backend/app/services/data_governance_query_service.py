from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.data_governance import DataLineageRecord, DataQualityHistory, DataSourceRegistryRecord
from app.models.market_intelligence import MarketIntelligence
from app.models.supplier_match import SupplierMatch
from app.repositories.business_truth_decision import business_truth_decision_repository


class DataGovernanceQueryService:
    def get_trusted_market_signals(
        self,
        db: Session,
        *,
        workspace_id: int | None = None,
        truth_level: str | None = None,
        source_type: str | None = None,
        freshness_min: float | None = None,
    ) -> list[dict]:
        quality_map = self._quality_map(db)
        rows = db.scalars(select(MarketIntelligence).order_by(desc(MarketIntelligence.updated_at)).limit(100)).all()
        items = []
        for row in rows:
            data_id = f"market:{row.keyword}:{row.category or 'uncategorized'}"
            quality = quality_map.get(data_id, {})
            item = {
                "data_id": data_id,
                "keyword": row.keyword,
                "category": row.category,
                "trend_score": float(row.trend_score),
                "truth_level": quality.get("truth_level"),
                "confidence_score": quality.get("confidence_score"),
                "freshness_score": quality.get("freshness_score"),
                "source_type": "mock",
            }
            if self._matches(item, truth_level, source_type, freshness_min):
                items.append(item)
        return items

    def get_supplier_offers(
        self,
        db: Session,
        *,
        workspace_id: int | None = None,
        truth_level: str | None = None,
        source_type: str | None = None,
        freshness_min: float | None = None,
    ) -> list[dict]:
        quality_map = self._quality_map(db)
        rows = db.scalars(select(SupplierMatch).order_by(desc(SupplierMatch.updated_at)).limit(200)).all()
        items = []
        for row in rows:
            data_id = f"{row.platform}:{row.product_id or 0}"
            quality = quality_map.get(data_id, {})
            item = {
                "data_id": data_id,
                "supplier_name": row.supplier_name,
                "platform": row.platform,
                "match_score": float(row.match_score),
                "truth_level": quality.get("truth_level"),
                "confidence_score": quality.get("confidence_score"),
                "freshness_score": quality.get("freshness_score"),
                "source_type": "mock",
            }
            if self._matches(item, truth_level, source_type, freshness_min):
                items.append(item)
        return items

    def get_decision_trace(self, db: Session, record_id: int, workspace_id: int | None = None) -> dict:
        truth = business_truth_decision_repository.get_by_product_id(db, record_id, workspace_id=workspace_id)
        if not truth:
            return {}
        return {
            "product_id": truth.product_id,
            "task_id": getattr(truth, "task_id", None),
            "workspace_id": getattr(truth, "workspace_id", None),
            "user_id": getattr(truth, "user_id", None),
            "api_key_id": getattr(truth, "api_key_id", None),
            "truth_score": float(truth.truth_score),
            "truth_level": truth.truth_level,
            "source_id": getattr(truth, "source_id", None),
            "lineage_chain": getattr(truth, "lineage_chain", []),
            "reasons": list(truth.reasons or []),
        }

    def get_lineage(self, db: Session, record_id: str, workspace_id: int | None = None) -> list[dict]:
        stmt = select(DataLineageRecord).where(DataLineageRecord.source_id == record_id).order_by(desc(DataLineageRecord.id))
        if workspace_id is not None:
            stmt = stmt.where(DataLineageRecord.workspace_id == workspace_id)
        rows = db.scalars(stmt).all()
        return [
            {
                "id": row.id,
                "event_id": getattr(row, "event_id", None),
                "event_key": getattr(row, "event_key", None),
                "event_stage": getattr(row, "event_stage", None),
                "task_id": getattr(row, "task_id", None),
                "workspace_id": getattr(row, "workspace_id", None),
                "user_id": getattr(row, "user_id", None),
                "api_key_id": getattr(row, "api_key_id", None),
                "source_id": row.source_id,
                "provider_name": row.provider_name,
                "node_type": getattr(row, "node_type", None),
                "lineage_chain": row.lineage_chain,
                "transform_steps": row.transform_steps,
                "payload_json": getattr(row, "payload_json", None),
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def get_expired_data(self, db: Session, workspace_id: int | None = None) -> list[dict]:
        rows = db.scalars(
            select(DataQualityHistory)
            .where(DataQualityHistory.freshness_score < 0.4)
            .where(DataQualityHistory.workspace_id == workspace_id if workspace_id is not None else True)
            .order_by(desc(DataQualityHistory.updated_at))
        ).all()
        return [
            {
                "data_id": row.data_id,
                "truth_level": row.truth_level,
                "freshness_score": float(row.freshness_score),
                "reliability_score": float(row.reliability_score),
            }
            for row in rows
        ]

    def get_source_breakdown(self, db: Session, workspace_id: int | None = None) -> list[dict]:
        stmt = select(DataSourceRegistryRecord)
        if workspace_id is not None:
            stmt = stmt.where(DataSourceRegistryRecord.workspace_id == workspace_id)
        rows = db.scalars(stmt.order_by(desc(DataSourceRegistryRecord.updated_at)).limit(200)).all()
        return [
            {
                "id": row.id,
                "source_type": row.source_type,
                "provider_name": row.provider_name,
                "status": row.status,
                "updated_at": row.updated_at.isoformat(),
            }
            for row in rows
        ]

    def _quality_map(self, db: Session, workspace_id: int | None = None) -> dict[str, dict]:
        stmt = select(DataQualityHistory)
        if workspace_id is not None:
            stmt = stmt.where(DataQualityHistory.workspace_id == workspace_id)
        rows = db.scalars(stmt.order_by(desc(DataQualityHistory.updated_at)).limit(500)).all()
        result: dict[str, dict] = {}
        for row in rows:
            result.setdefault(
                row.data_id,
                {
                    "truth_level": row.truth_level,
                    "confidence_score": float(row.confidence_score),
                    "freshness_score": float(row.freshness_score),
                    "reliability_score": float(row.reliability_score),
                },
            )
        return result

    def _matches(self, item: dict, truth_level: str | None, source_type: str | None, freshness_min: float | None) -> bool:
        if truth_level and item.get("truth_level") != truth_level:
            return False
        if source_type and item.get("source_type") != source_type:
            return False
        if freshness_min is not None and float(item.get("freshness_score") or 0) < freshness_min:
            return False
        return True


data_governance_query_service = DataGovernanceQueryService()

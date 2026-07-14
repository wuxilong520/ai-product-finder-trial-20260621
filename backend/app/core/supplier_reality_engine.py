from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.supplier_intelligence_engine import supplier_intelligence_engine
from app.models.procurement import SupplierRealityHistory
from app.models.supplier import Supplier


class SupplierRealityEngine:
    def evaluate(
        self,
        db: Session,
        *,
        supplier: Supplier,
        pool_item_id: int | None = None,
        keyword: str | None = None,
        expected_price: float | None = None,
        quantity: int | None = None,
    ) -> dict:
        report = supplier_intelligence_engine.analyze_supplier(
            db,
            supplier=supplier,
            keyword=keyword,
            expected_price=expected_price,
            quantity=quantity,
        )
        truth_score = round(
            min(
                100.0,
                float(report.get("supplier_authenticity_score") or 0) * 0.4
                + float(report.get("price_competitiveness_score") or 0) * 0.25
                + float(report.get("stability_score") or 0) * 0.2
                + max(0.0, 100.0 - float(report.get("supplier_risk_score") or 0)) * 0.15,
            ),
            2,
        )
        db.add(
            SupplierRealityHistory(
                supplier_id=supplier.id,
                pool_item_id=pool_item_id,
                truth_score=truth_score,
                price_truth_score=float(report.get("price_competitiveness_score") or 0),
                stability_score=float(report.get("stability_score") or 0),
                risk_score=float(report.get("supplier_risk_score") or 0),
                snapshot=report,
            )
        )
        return {
            **report,
            "supplier_truth_score": truth_score,
        }


supplier_reality_engine = SupplierRealityEngine()

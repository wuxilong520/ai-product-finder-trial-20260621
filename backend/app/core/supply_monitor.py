from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.supplier import SupplySupplierHistory


class SupplyMonitor:
    def inspect(
        self,
        db: Session,
        *,
        supplier_name: str,
        platform: str,
        keyword: str,
        product_title: str,
    ) -> dict:
        rows = db.scalars(
            select(SupplySupplierHistory)
            .where(SupplySupplierHistory.supplier_name == supplier_name)
            .where(SupplySupplierHistory.platform == platform)
            .where(SupplySupplierHistory.keyword == keyword)
            .where(SupplySupplierHistory.product_title == product_title)
            .order_by(desc(SupplySupplierHistory.created_at))
            .limit(2)
        ).all()
        if not rows:
            return {
                "price_change": 0.0,
                "stock_change": "unknown",
                "risk_alert": [],
            }
        latest = rows[0]
        previous = rows[1] if len(rows) > 1 else None
        latest_price = float(latest.price_min or 0)
        previous_price = float(previous.price_min or latest_price) if previous else latest_price
        price_change = round(latest_price - previous_price, 2)
        stock_change = str(latest.stock_change or "unknown")
        risk_alert: list[str] = []
        if previous and previous_price > 0:
            change_ratio = abs(price_change) / previous_price
            if change_ratio >= 0.15:
                risk_alert.append("price_change_large")
        if stock_change.lower() in {"down", "low", "out"}:
            risk_alert.append("stock_risk")
        return {
            "price_change": price_change,
            "stock_change": stock_change,
            "risk_alert": risk_alert,
        }


supply_monitor = SupplyMonitor()

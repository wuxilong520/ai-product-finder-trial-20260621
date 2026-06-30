from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.billing.order import BillingOrder


class BillingOrderRepository:
    def create(
        self,
        db: Session,
        *,
        workspace_id: int,
        user_id: int | None,
        plan_name: str,
        amount_cents: int,
        currency: str = "CNY",
        provider_name: str | None = None,
        status: str = "pending",
        external_order_id: str | None = None,
        note: str | None = None,
    ) -> BillingOrder:
        record = BillingOrder(
            workspace_id=workspace_id,
            user_id=user_id,
            plan_name=plan_name,
            amount_cents=amount_cents,
            currency=currency,
            provider_name=provider_name,
            status=status,
            external_order_id=external_order_id,
            note=note,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_by_id(self, db: Session, order_id: int) -> BillingOrder | None:
        return db.get(BillingOrder, order_id)

    def list_by_workspace(self, db: Session, *, workspace_id: int, limit: int = 20) -> list[BillingOrder]:
        stmt = (
            select(BillingOrder)
            .where(BillingOrder.workspace_id == workspace_id)
            .order_by(BillingOrder.id.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt))

    def update_status(
        self,
        db: Session,
        *,
        record: BillingOrder,
        status: str,
        external_order_id: str | None = None,
        note: str | None = None,
    ) -> BillingOrder:
        record.status = status
        if external_order_id is not None:
            record.external_order_id = external_order_id
        if note is not None:
            record.note = note
        db.add(record)
        db.commit()
        db.refresh(record)
        return record


billing_order_repository = BillingOrderRepository()

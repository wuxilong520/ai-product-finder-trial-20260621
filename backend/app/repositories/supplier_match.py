from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier_match import SupplierMatch


class SupplierMatchRepository:
    _fields = {
        "product_id",
        "supplier_name",
        "platform",
        "supplier_title",
        "supplier_url",
        "supplier_price",
        "currency",
        "match_score",
        "availability",
    }

    def get_existing(
        self,
        db: Session,
        *,
        product_id: int | None,
        platform: str,
        supplier_url: str,
    ) -> SupplierMatch | None:
        stmt = select(SupplierMatch).where(
            SupplierMatch.product_id == product_id,
            SupplierMatch.platform == platform,
            SupplierMatch.supplier_url == supplier_url,
        )
        return db.scalar(stmt)

    def upsert_many(self, db: Session, items: list[dict]) -> list[SupplierMatch]:
        records: list[SupplierMatch] = []
        for item in items:
            normalized_item = {key: value for key, value in item.items() if key in self._fields}
            existing = self.get_existing(
                db,
                product_id=normalized_item.get("product_id"),
                platform=normalized_item["platform"],
                supplier_url=normalized_item["supplier_url"],
            )
            if existing:
                existing.supplier_name = normalized_item.get("supplier_name")
                existing.supplier_title = normalized_item["supplier_title"]
                existing.supplier_price = normalized_item.get("supplier_price")
                existing.currency = normalized_item.get("currency")
                existing.match_score = normalized_item["match_score"]
                existing.availability = normalized_item["availability"]
                db.add(existing)
                records.append(existing)
            else:
                record = SupplierMatch(**normalized_item)
                db.add(record)
                records.append(record)
        db.commit()
        for record in records:
            db.refresh(record)
        return records


supplier_match_repository = SupplierMatchRepository()

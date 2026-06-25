from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier_match import SupplierMatch


class SupplierMatchRepository:
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
            existing = self.get_existing(
                db,
                product_id=item.get("product_id"),
                platform=item["platform"],
                supplier_url=item["supplier_url"],
            )
            if existing:
                existing.supplier_name = item.get("supplier_name")
                existing.supplier_title = item["supplier_title"]
                existing.supplier_price = item.get("supplier_price")
                existing.currency = item.get("currency")
                existing.match_score = item["match_score"]
                existing.availability = item["availability"]
                db.add(existing)
                records.append(existing)
            else:
                record = SupplierMatch(**item)
                db.add(record)
                records.append(record)
        db.commit()
        for record in records:
            db.refresh(record)
        return records


supplier_match_repository = SupplierMatchRepository()

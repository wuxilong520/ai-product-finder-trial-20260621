from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplierProduct, SupplySupplierHistory


class BrowserImportPayload(BaseModel):
    url: str
    title: str
    price: float | str | None = None
    images: list[str] = Field(default_factory=list)
    supplier: str
    moq: int | None = None
    category: str | None = None
    location: str | None = None
    certification: str | None = None
    delivery_time: int | None = None
    keyword: str | None = None


class BrowserImportService:
    def import_record(self, db: Session, payload: BrowserImportPayload) -> dict:
        keyword = (payload.keyword or payload.title).strip()
        price_value = self._parse_price(payload.price)
        supplier = db.scalar(
            select(Supplier)
            .where(Supplier.name == payload.supplier.strip())
            .where(Supplier.platform == "1688")
        )
        if not supplier:
            supplier = Supplier(
                name=payload.supplier.strip(),
                platform="1688",
                supplier_type="factory",
                location=payload.location,
                product_category=payload.category,
                min_order_quantity=int(payload.moq or 0),
                price_range={"min": price_value, "max": price_value},
                transaction_score=0.0,
                factory_score=75.0,
                trust_score=78.0,
                certification=payload.certification,
                delivery_time_days=payload.delivery_time,
                source_type="browser_extension",
                confidence_score=0.88,
                supplier_verified=True,
                product_url=payload.url,
                factory_level="browser_authorized",
                delivery_score=80.0 if payload.delivery_time and payload.delivery_time <= 7 else 60.0,
                price_history=[{"price": price_value, "source": "browser_extension"}],
                verification_status="verified",
                is_authorized=True,
                last_feedback="用户浏览器主动授权导入",
                last_verified_time=datetime.now(UTC),
            )
            db.add(supplier)
            db.flush()
        else:
            supplier.location = payload.location or supplier.location
            supplier.product_category = payload.category or supplier.product_category
            supplier.min_order_quantity = int(payload.moq or supplier.min_order_quantity or 0)
            supplier.price_range = {"min": price_value, "max": price_value}
            supplier.certification = payload.certification or supplier.certification
            supplier.delivery_time_days = payload.delivery_time or supplier.delivery_time_days
            supplier.source_type = "browser_extension"
            supplier.confidence_score = max(float(supplier.confidence_score or 0), 0.88)
            supplier.supplier_verified = True
            supplier.product_url = payload.url
            supplier.factory_level = "browser_authorized"
            supplier.delivery_score = 80.0 if payload.delivery_time and payload.delivery_time <= 7 else 60.0
            supplier.price_history = [*list(supplier.price_history or []), {"price": price_value, "source": "browser_extension"}][-10:]
            supplier.verification_status = "verified"
            supplier.is_authorized = True
            supplier.last_feedback = "用户浏览器主动授权导入"
            supplier.last_verified_time = datetime.now(UTC)
            db.add(supplier)
            db.flush()

        product = db.scalar(
            select(SupplierProduct)
            .where(SupplierProduct.supplier_id == supplier.id)
            .where(SupplierProduct.keyword == keyword)
            .where(SupplierProduct.product_url == payload.url)
        )
        if not product:
            product = SupplierProduct(
                supplier_id=supplier.id,
                keyword=keyword,
                product_title=payload.title.strip(),
                product_image=(payload.images[0] if payload.images else None),
                product_url=payload.url,
                price_min=price_value,
                price_max=price_value,
                currency="CNY",
                images=payload.images,
                source_type="browser_extension",
                confidence_score=0.88,
                factory_info="浏览器授权导入",
                transaction_info="用户主动打开页面并授权插件回传",
                raw_snapshot=payload.model_dump(mode="json"),
            )
            db.add(product)
        else:
            product.product_title = payload.title.strip()
            product.product_image = payload.images[0] if payload.images else product.product_image
            product.product_url = payload.url
            product.price_min = price_value
            product.price_max = price_value
            product.images = payload.images
            product.source_type = "browser_extension"
            product.confidence_score = 0.88
            product.factory_info = "浏览器授权导入"
            product.transaction_info = "用户主动打开页面并授权插件回传"
            product.raw_snapshot = payload.model_dump(mode="json")
            db.add(product)

        db.add(
            SupplySupplierHistory(
                supplier_name=supplier.name,
                platform=supplier.platform,
                keyword=keyword,
                product_title=payload.title.strip(),
                product_url=payload.url,
                source_type="browser_extension",
                price_min=price_value,
                price_max=price_value,
                currency="CNY",
                min_order_quantity=int(payload.moq or 0),
                feedback_status="browser_imported",
                snapshot=payload.model_dump(mode="json"),
            )
        )
        db.commit()
        return {
            "imported": True,
            "source_type": "browser_extension",
            "supplier_name": supplier.name,
            "product_title": payload.title.strip(),
            "keyword": keyword,
        }

    def _parse_price(self, value: float | str | None) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return round(float(value), 2)
        cleaned = str(value).strip().replace("¥", "").replace("￥", "").replace(",", "")
        try:
            return round(float(cleaned), 2)
        except ValueError:
            return 0.0


browser_import_service = BrowserImportService()

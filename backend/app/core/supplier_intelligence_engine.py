from __future__ import annotations

from statistics import mean

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.core.supplier_risk_engine import supplier_risk_engine
from app.core.supplier_scoring_engine import supplier_scoring_engine
from app.models.supplier import Supplier, SupplierExtensionImport, SupplierPriceHistory, SupplierProduct, SupplySupplierHistory


class SupplierIntelligenceEngine:
    category_moq_benchmark = {
        "consumer electronics": (50, 200, 500),
        "electronics": (50, 200, 500),
        "beauty": (30, 120, 300),
        "home": (20, 100, 250),
        "pet": (20, 80, 200),
        "fashion": (50, 150, 400),
    }

    def analyze_supplier(
        self,
        db: Session,
        *,
        supplier: Supplier,
        product: SupplierProduct | None = None,
        keyword: str | None = None,
        expected_price: float | None = None,
        quantity: int | None = None,
    ) -> dict:
        if product is None:
            product = self._latest_product(db, supplier_id=supplier.id, keyword=keyword)
        import_count = self._import_count(db, supplier_name=supplier.name)
        history_rows = self._history_rows(db, supplier_id=supplier.id, product_id=product.id if product else None)
        peer_prices = self._peer_prices(db, supplier=supplier, product=product, keyword=keyword)
        current_price = self._current_price(supplier=supplier, product=product)
        peer_average = round(mean(peer_prices), 2) if peer_prices else 0.0
        price_ratio = round(current_price / peer_average, 4) if current_price > 0 and peer_average > 0 else None
        missing_fields = self._missing_fields(supplier=supplier, product=product)

        authenticity_score = self._authenticity_score(
            supplier=supplier,
            product=product,
            import_count=import_count,
            missing_fields=missing_fields,
        )
        price_score = self._price_competitiveness_score(
            current_price=current_price,
            peer_average=peer_average,
            expected_price=expected_price,
        )
        delivery_score = float(supplier.delivery_score or supplier_scoring_engine.delivery_score(delivery_time_days=supplier.delivery_time_days))
        moq_score = self._moq_score(
            moq=int(supplier.min_order_quantity or 0),
            category=supplier.product_category or (product.raw_snapshot.get("category") if product and isinstance(product.raw_snapshot, dict) else None),
            quantity=quantity,
        )
        stability_score = self._stability_score(history_rows=history_rows)
        certification_score = supplier_scoring_engine.certification_score(certification=supplier.certification)

        supplier_real_score = round(
            max(
                0.0,
                min(
                    100.0,
                    authenticity_score * 0.30
                    + price_score * 0.25
                    + delivery_score * 0.15
                    + moq_score * 0.10
                    + stability_score * 0.10
                    + certification_score * 0.10,
                ),
            ),
            2,
        )
        risk_meta = supplier_risk_engine.evaluate(
            authenticity_score=authenticity_score,
            price_score=price_score,
            moq_score=moq_score,
            stability_score=stability_score,
            has_history=bool(history_rows),
            missing_fields=missing_fields,
            price_ratio=price_ratio,
        )
        supplier_confidence = self._confidence_score(
            supplier=supplier,
            product=product,
            missing_fields=missing_fields,
            import_count=import_count,
            history_count=len(history_rows),
        )
        recommendation = self._recommendation(
            supplier_real_score=supplier_real_score,
            risk_level=str(risk_meta["risk_level"]),
        )
        return {
            "supplier": {
                "id": supplier.id,
                "name": supplier.name,
                "platform": supplier.platform,
                "location": supplier.location,
                "product_category": supplier.product_category,
                "product_url": supplier.product_url,
            },
            "product": {
                "id": product.id if product else None,
                "keyword": product.keyword if product else keyword,
                "title": product.product_title if product else None,
                "price_min": float(product.price_min or 0) if product else 0.0,
                "price_max": float(product.price_max or 0) if product else 0.0,
            } if product else {},
            "supplier_real_score": supplier_real_score,
            "supplier_authenticity_score": round(authenticity_score, 2),
            "price_competitiveness_score": round(price_score, 2),
            "delivery_score": round(delivery_score, 2),
            "moq_score": round(moq_score, 2),
            "stability_score": round(stability_score, 2),
            "certification_score": round(certification_score, 2),
            "supplier_confidence": round(supplier_confidence, 4),
            "supplier_risk_score": risk_meta["supplier_risk_score"],
            "risk_level": risk_meta["risk_level"],
            "risk_flags": risk_meta["risk_flags"],
            "recommendation": recommendation,
            "current_price": round(current_price, 2),
            "peer_average_price": peer_average,
            "price_ratio": price_ratio,
            "import_history_count": import_count,
            "price_history_count": len(history_rows),
            "missing_fields": missing_fields,
        }

    def analyze_candidate(
        self,
        db: Session,
        *,
        item: dict,
        keyword: str,
        category: str | None,
        expected_price: float | None,
        quantity: int,
    ) -> dict:
        supplier = self._candidate_supplier(item=item, category=category)
        product = self._candidate_product(item=item, keyword=keyword)
        persisted = db.scalar(
            select(Supplier)
            .where(Supplier.name == supplier.name)
            .where(Supplier.platform == supplier.platform)
        )
        persisted_product = None
        if persisted:
            persisted_product = self._latest_product(db, supplier_id=persisted.id, keyword=keyword)
            supplier = self._merge_supplier(persisted, supplier)
            product = self._merge_product(persisted_product, product)
        return self.analyze_supplier(
            db,
            supplier=supplier,
            product=product,
            keyword=keyword,
            expected_price=expected_price,
            quantity=quantity,
        )

    def _candidate_supplier(self, *, item: dict, category: str | None) -> Supplier:
        return Supplier(
            id=int(item.get("supplier_id") or 0),
            name=str(item.get("name") or ""),
            platform=str(item.get("platform") or "1688"),
            supplier_type=str(item.get("supplier_type") or "trader"),
            location=item.get("location"),
            product_category=category,
            min_order_quantity=int(item.get("min_order_quantity") or 0),
            price_range={"min": float(item.get("price_min") or 0), "max": float(item.get("price_max") or 0)},
            transaction_score=float(item.get("transaction_score") or 0),
            factory_score=float(item.get("factory_score") or 0),
            trust_score=float(item.get("trust_score") or item.get("supplier_score") or 0),
            certification=str(item.get("certification") or ""),
            delivery_time_days=self._delivery_days(item.get("delivery_time")),
            source_type=str(item.get("source_type") or "cache_database"),
            confidence_score=float(item.get("confidence_score") or item.get("supplier_confidence") or 0),
            supplier_verified=bool(item.get("supplier_verified") or False),
            product_url=item.get("product_url"),
            factory_level=str(item.get("factory_level") or item.get("factory_info") or ""),
            delivery_score=float(item.get("delivery_score") or 0),
            price_history=list(item.get("price_history") or []),
            verification_status=str(item.get("verification_status") or "unverified"),
            is_authorized=str(item.get("source_type") or "") in {"merchant_authorized", "browser_extension"},
            last_feedback=" | ".join(item.get("score_reasons") or []),
            last_verified_time=None,
        )

    def _candidate_product(self, *, item: dict, keyword: str) -> SupplierProduct:
        return SupplierProduct(
            id=int(item.get("product_id") or 0),
            supplier_id=int(item.get("supplier_id") or 0),
            keyword=keyword,
            product_title=str(item.get("product_title") or keyword),
            product_image=item.get("product_image"),
            product_url=item.get("product_url") or item.get("search_url"),
            price_min=float(item.get("price_min") or 0),
            price_max=float(item.get("price_max") or 0),
            currency=str(item.get("currency") or "CNY"),
            images=list(item.get("images") or []),
            source_type=str(item.get("source_type") or "cache_database"),
            confidence_score=float(item.get("confidence_score") or item.get("supplier_confidence") or 0),
            factory_info=str(item.get("factory_info") or ""),
            transaction_info=str(item.get("transaction_info") or ""),
            raw_snapshot=dict(item),
        )

    def _merge_supplier(self, persisted: Supplier, fallback: Supplier) -> Supplier:
        for field in (
            "location",
            "product_category",
            "min_order_quantity",
            "price_range",
            "transaction_score",
            "factory_score",
            "trust_score",
            "certification",
            "delivery_time_days",
            "source_type",
            "confidence_score",
            "supplier_verified",
            "product_url",
            "factory_level",
            "delivery_score",
            "price_history",
            "verification_status",
            "is_authorized",
            "last_feedback",
            "last_verified_time",
        ):
            value = getattr(persisted, field)
            if value not in (None, "", [], {}, 0):
                setattr(fallback, field, value)
        fallback.id = persisted.id
        return fallback

    def _merge_product(self, persisted: SupplierProduct | None, fallback: SupplierProduct) -> SupplierProduct:
        if persisted is None:
            return fallback
        for field in (
            "id",
            "supplier_id",
            "product_title",
            "product_image",
            "product_url",
            "price_min",
            "price_max",
            "currency",
            "images",
            "source_type",
            "confidence_score",
            "factory_info",
            "transaction_info",
            "raw_snapshot",
            "keyword",
        ):
            value = getattr(persisted, field)
            if value not in (None, "", [], {}, 0):
                setattr(fallback, field, value)
        return fallback

    def _latest_product(self, db: Session, *, supplier_id: int, keyword: str | None) -> SupplierProduct | None:
        stmt: Select = select(SupplierProduct).where(SupplierProduct.supplier_id == supplier_id)
        if keyword:
            stmt = stmt.where(SupplierProduct.keyword == keyword)
        stmt = stmt.order_by(SupplierProduct.created_at.desc())
        return db.scalar(stmt)

    def _import_count(self, db: Session, *, supplier_name: str) -> int:
        return int(
            db.scalar(
                select(func.count(SupplierExtensionImport.id)).where(
                    SupplierExtensionImport.supplier_name == supplier_name
                )
            )
            or 0
        )

    def _history_rows(self, db: Session, *, supplier_id: int, product_id: int | None) -> list[SupplierPriceHistory]:
        stmt = select(SupplierPriceHistory).where(SupplierPriceHistory.supplier_id == supplier_id).order_by(SupplierPriceHistory.created_at.desc())
        if product_id:
            stmt = stmt.where(or_(SupplierPriceHistory.product_id == product_id, SupplierPriceHistory.product_id.is_(None)))
        return list(db.scalars(stmt).all())

    def _peer_prices(self, db: Session, *, supplier: Supplier, product: SupplierProduct | None, keyword: str | None) -> list[float]:
        stmt = select(SupplierProduct.price_min, SupplierProduct.price_max).where(SupplierProduct.supplier_id != int(supplier.id or 0))
        if keyword:
            stmt = stmt.where(SupplierProduct.keyword == keyword)
        elif product:
            stmt = stmt.where(SupplierProduct.keyword == product.keyword)
        rows = db.execute(stmt).all()
        prices = []
        for price_min, price_max in rows:
            values = [float(price_min or 0), float(price_max or 0)]
            values = [value for value in values if value > 0]
            if values:
                prices.append(round(sum(values) / len(values), 2))
        return prices

    def _current_price(self, *, supplier: Supplier, product: SupplierProduct | None) -> float:
        if product:
            values = [float(product.price_min or 0), float(product.price_max or 0)]
            values = [value for value in values if value > 0]
            if values:
                return round(sum(values) / len(values), 2)
        price_range = supplier.price_range or {}
        values = [float(price_range.get("min") or 0), float(price_range.get("max") or 0)]
        values = [value for value in values if value > 0]
        return round(sum(values) / len(values), 2) if values else 0.0

    def _missing_fields(self, *, supplier: Supplier, product: SupplierProduct | None) -> list[str]:
        fields = {
            "location": supplier.location,
            "factory_level": supplier.factory_level,
            "certification": supplier.certification,
            "delivery_time_days": supplier.delivery_time_days,
            "product_url": product.product_url if product else supplier.product_url,
            "images": product.images if product else [],
        }
        missing = []
        for key, value in fields.items():
            if value in (None, "", [], {}):
                missing.append(key)
        return missing

    def _authenticity_score(
        self,
        *,
        supplier: Supplier,
        product: SupplierProduct | None,
        import_count: int,
        missing_fields: list[str],
    ) -> float:
        score = 0.0
        if str(supplier.factory_level or "").strip():
            score += 20
        if supplier.supplier_verified or supplier.is_authorized:
            score += 18
        if str(supplier.certification or "").strip():
            score += 16
        if product and str(product.product_url or "").strip():
            score += 10
        completeness = max(0.0, 1 - (len(missing_fields) / 6))
        score += completeness * 20
        if supplier.created_at:
            score += 8
        if supplier.last_verified_time:
            score += 8
        score += min(10, import_count * 2)
        return round(max(0.0, min(100.0, score)), 2)

    def _price_competitiveness_score(
        self,
        *,
        current_price: float,
        peer_average: float,
        expected_price: float | None,
    ) -> float:
        if current_price <= 0:
            return 20.0
        if peer_average > 0:
            ratio = current_price / peer_average
            if ratio <= 0.65:
                return 42.0
            if ratio <= 0.85:
                return 92.0
            if ratio <= 1.0:
                return 82.0
            if ratio <= 1.15:
                return 65.0
            if ratio <= 1.3:
                return 45.0
            return 25.0
        return supplier_scoring_engine.price_competitiveness(price_mid=current_price, expected_price=expected_price)

    def _moq_score(self, *, moq: int, category: str | None, quantity: int | None) -> float:
        if moq <= 0:
            return 25.0
        normalized = str(category or "").strip().lower()
        low, medium, high = self.category_moq_benchmark.get(normalized, (50, 200, 500))
        if any(token in normalized for token in self.category_moq_benchmark):
            for token, bench in self.category_moq_benchmark.items():
                if token in normalized:
                    low, medium, high = bench
                    break
        if quantity and quantity > 0:
            return supplier_scoring_engine.moq_reasonableness(moq=moq, quantity=quantity)
        if moq <= low:
            return 92.0
        if moq <= medium:
            return 76.0
        if moq <= high:
            return 52.0
        return 25.0

    def _stability_score(self, *, history_rows: list[SupplierPriceHistory]) -> float:
        if not history_rows:
            return 32.0
        prices = [float(item.price or 0) for item in history_rows if float(item.price or 0) > 0]
        if not prices:
            return 32.0
        average_price = sum(prices) / len(prices)
        deviation = sum(abs(price - average_price) for price in prices) / len(prices)
        deviation_ratio = deviation / average_price if average_price > 0 else 1
        history_bonus = min(18.0, len(prices) * 4.0)
        if deviation_ratio <= 0.03:
            base = 82.0
        elif deviation_ratio <= 0.08:
            base = 70.0
        elif deviation_ratio <= 0.15:
            base = 56.0
        else:
            base = 35.0
        return round(max(0.0, min(100.0, base + history_bonus)), 2)

    def _confidence_score(
        self,
        *,
        supplier: Supplier,
        product: SupplierProduct | None,
        missing_fields: list[str],
        import_count: int,
        history_count: int,
    ) -> float:
        base = float(supplier.confidence_score or product.confidence_score if product else 0.45)
        base = max(0.25, min(0.95, base))
        completeness_penalty = len(missing_fields) * 0.04
        history_bonus = min(0.12, history_count * 0.02)
        import_bonus = min(0.08, import_count * 0.02)
        return round(max(0.1, min(0.98, base - completeness_penalty + history_bonus + import_bonus)), 4)

    def _recommendation(self, *, supplier_real_score: float, risk_level: str) -> str:
        if risk_level == "HIGH":
            return "暂不建议采购"
        if supplier_real_score >= 75:
            return "推荐采购"
        if supplier_real_score >= 50:
            return "建议观察"
        return "暂不建议采购"

    def _delivery_days(self, raw_value: object) -> int | None:
        if raw_value in (None, "", 0):
            return None
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            digits = "".join(ch for ch in str(raw_value) if ch.isdigit())
            return int(digits) if digits else None


supplier_intelligence_engine = SupplierIntelligenceEngine()

from __future__ import annotations

import hashlib
from statistics import mean

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.product_matching_engine import product_matching_engine
from app.core.procurement_analysis_engine import procurement_analysis_engine
from app.core.runtime import AppError
from app.core.security import decode_access_token
from app.core.supplier_reality_engine import supplier_reality_engine
from app.models.procurement import ProcurementPoolItem, ProcurementSupplierItem, ProductGroup
from app.models.supplier import Supplier, SupplierProduct
from app.repositories.user import user_repository
from app.services.supply_import_service import supply_import_service


class ProcurementPoolService:
    def import_from_extension_payload(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None = None,
        payload: dict,
    ) -> dict:
        supply_record = {
            "keyword": str(payload.get("metadata", {}).get("keyword") or payload.get("title") or "").strip(),
            "supplier_name": str((payload.get("supplier") or {}).get("name") or "").strip(),
            "product_title": str(payload.get("title") or "").strip(),
            "product_url": str(payload.get("url") or "").strip(),
            "price": self._extract_mid_price(str(payload.get("price_range") or "")),
            "moq": self._extract_moq(str(payload.get("moq") or "")),
            "images": list(payload.get("images") or []),
            "category": str(payload.get("metadata", {}).get("category") or "").strip() or None,
            "location": str((payload.get("supplier") or {}).get("location") or "").strip() or None,
            "certification": str(payload.get("metadata", {}).get("certification") or "").strip() or None,
            "delivery_time": self._extract_delivery_time(payload.get("metadata") or {}),
        }
        supply_import_service.import_records(db, records=[supply_record], source_type="browser_extension")
        supplier = db.scalar(
            select(Supplier)
            .where(Supplier.name == supply_record["supplier_name"])
            .where(Supplier.platform == "1688")
            .order_by(Supplier.id.desc())
        )
        product = db.scalar(
            select(SupplierProduct)
            .where(SupplierProduct.supplier_id == supplier.id if supplier else -1)
            .where(SupplierProduct.product_title == supply_record["product_title"])
            .order_by(SupplierProduct.id.desc())
        ) if supplier else None
        if not supplier:
            raise AppError("PROCUREMENT_IMPORT_FAILED", "供应商数据导入失败，采购池没有拿到供应商记录。", "procurement", 500)
        result = self._upsert_pool_item_from_supplier_product(
            db,
            user_id=user_id,
            workspace_id=workspace_id,
            supplier=supplier,
            product=product,
            source_type="1688_EXTENSION",
        )
        db.commit()
        return result

    def list_pool(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None = None,
        keyword: str | None = None,
        category: str | None = None,
        price_range: tuple[float | None, float | None] | None = None,
        profit_range: tuple[float | None, float | None] | None = None,
        supplier_score: float | None = None,
        risk_level: str | None = None,
        sort: str = "latest",
    ) -> dict:
        if keyword:
            self.hydrate_from_existing_supply(
                db,
                user_id=user_id,
                workspace_id=workspace_id,
                keyword=keyword,
                category=category,
            )
        stmt: Select = select(ProcurementPoolItem).where(ProcurementPoolItem.user_id == user_id)
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        if keyword:
            stmt = stmt.where(ProcurementPoolItem.keyword.ilike(f"%{keyword.strip()}%"))
        if category:
            stmt = stmt.where(ProcurementPoolItem.category.ilike(f"%{category.strip()}%"))
        items = list(db.scalars(stmt).all())
        enriched = [self._serialize_pool_item(db, item) for item in items]
        enriched = self._apply_filters(
            enriched,
            price_range=price_range,
            profit_range=profit_range,
            supplier_score=supplier_score,
            risk_level=risk_level,
        )
        enriched = self._sort_items(enriched, sort=sort)
        return {
            "items": enriched,
            "total": len(enriched),
        }

    def hydrate_from_existing_supply(self, db: Session, *, user_id: int, workspace_id: int | None = None, keyword: str, category: str | None = None) -> int:
        rows = db.execute(
            select(Supplier, SupplierProduct)
            .join(SupplierProduct, SupplierProduct.supplier_id == Supplier.id)
            .where(SupplierProduct.keyword == keyword)
            .order_by(SupplierProduct.id.asc())
        ).all()
        created = 0
        for supplier, product in rows:
            result = self._upsert_pool_item_from_supplier_product(
                db,
                user_id=user_id,
                workspace_id=workspace_id,
                supplier=supplier,
                product=product,
                category_override=category,
                source_type=self._normalize_source_type(supplier.source_type),
            )
            created += 1 if result.get("created") else 0
        db.commit()
        return created

    def get_pool_item(self, db: Session, *, user_id: int, pool_item_id: int, workspace_id: int | None = None) -> dict:
        stmt = (
            select(ProcurementPoolItem)
            .where(ProcurementPoolItem.user_id == user_id)
            .where(ProcurementPoolItem.id == pool_item_id)
        )
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        item = db.scalar(stmt)
        if not item:
            raise AppError("PROCUREMENT_ITEM_NOT_FOUND", "采购池里没有这个商品。", "procurement", 404)
        return self._serialize_pool_item(db, item, include_suppliers=True, include_analysis=True)

    def favorite(self, db: Session, *, user_id: int, pool_item_id: int, action: str, workspace_id: int | None = None) -> dict:
        stmt = (
            select(ProcurementPoolItem)
            .where(ProcurementPoolItem.user_id == user_id)
            .where(ProcurementPoolItem.id == pool_item_id)
        )
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        item = db.scalar(stmt)
        if not item:
            raise AppError("PROCUREMENT_ITEM_NOT_FOUND", "采购池里没有这个商品。", "procurement", 404)
        normalized = action.strip().upper()
        if normalized == "FAVORITE":
            item.status = "FAVORITE"
        elif normalized in {"ARCHIVE", "HIDE", "ARCHIVED"}:
            item.status = "ARCHIVED"
        elif normalized in {"ANALYZING", "ANALYZED", "NEW"}:
            item.status = normalized
        else:
            raise AppError("PROCUREMENT_ACTION_INVALID", "采购池操作不支持。", "procurement", 400)
        db.add(item)
        db.commit()
        return {"ok": True, "status": item.status, "pool_item_id": item.id}

    def compare(self, db: Session, *, user_id: int, pool_item_ids: list[int], workspace_id: int | None = None) -> dict:
        limited_ids = pool_item_ids[:5]
        stmt = (
            select(ProcurementPoolItem)
            .where(ProcurementPoolItem.user_id == user_id)
            .where(ProcurementPoolItem.id.in_(limited_ids))
        )
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        items = list(
            db.scalars(stmt).all()
        )
        result = [self._serialize_pool_item(db, item, include_suppliers=True, include_analysis=True) for item in items]
        return {"items": result, "count": len(result)}

    def analyze_pool_item(self, db: Session, *, user_id: int, pool_item_id: int, workspace_id: int | None = None) -> dict:
        stmt = (
            select(ProcurementPoolItem)
            .where(ProcurementPoolItem.user_id == user_id)
            .where(ProcurementPoolItem.id == pool_item_id)
        )
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        item = db.scalar(stmt)
        if not item:
            raise AppError("PROCUREMENT_ITEM_NOT_FOUND", "采购池里没有这个商品。", "procurement", 404)
        suppliers = list(
            db.scalars(
                select(ProcurementSupplierItem)
                .where(ProcurementSupplierItem.pool_item_id == item.id)
                .order_by(ProcurementSupplierItem.supplier_truth_score.desc(), ProcurementSupplierItem.price.asc())
            ).all()
        )
        item.status = "ANALYZING"
        db.add(item)
        db.commit()
        return procurement_analysis_engine.analyze(db, pool_item=item, supplier_items=suppliers)

    def count_pool_items(self, db: Session, *, user_id: int, workspace_id: int | None = None) -> int:
        stmt = select(func.count(ProcurementPoolItem.id)).where(ProcurementPoolItem.user_id == user_id)
        if workspace_id is not None:
            stmt = stmt.where(ProcurementPoolItem.workspace_id == workspace_id)
        return int(db.scalar(stmt) or 0)

    def resolve_user_from_token(self, db: Session, *, authorization: str | None) -> int:
        user_id, _workspace_id = self.resolve_user_context_from_token(db, authorization=authorization)
        return user_id

    def resolve_user_context_from_token(self, db: Session, *, authorization: str | None) -> tuple[int, int | None]:
        if not authorization or not authorization.startswith("Bearer "):
            raise AppError("AUTH_MISSING", "缺少登录信息", "auth", 401)
        raw_token = authorization.removeprefix("Bearer ").strip()
        payload = decode_access_token(raw_token)
        user_id = payload.get("sub")
        if not user_id:
            raise AppError("AUTH_INVALID", "登录信息无效", "auth", 401)
        user = user_repository.get_by_id(db, int(user_id))
        if not user:
            raise AppError("AUTH_USER_INVALID", "用户不存在", "auth", 401)
        workspace_id = payload.get("workspace_id")
        if workspace_id is None:
            workspace_id = getattr(user, "workspace_id", None)
        return int(user.id), int(workspace_id) if workspace_id is not None else None

    def _upsert_pool_item_from_supplier_product(
        self,
        db: Session,
        *,
        user_id: int,
        workspace_id: int | None,
        supplier: Supplier,
        product: SupplierProduct | None,
        category_override: str | None = None,
        source_type: str,
    ) -> dict:
        keyword = str(product.keyword if product else supplier.product_category or "").strip() or "unknown"
        title = str(product.product_title if product else supplier.name).strip()
        image = str(product.product_image if product else "") or ((product.images or [""])[0] if product and product.images else "")
        specs = []
        if product and isinstance(product.raw_snapshot, dict):
            specs = list(product.raw_snapshot.get("sku") or product.raw_snapshot.get("metadata", {}).get("sku") or [])
        group = self._find_or_create_group(
            db,
            keyword=keyword,
            title=title,
            image=image or None,
            specs=specs,
        )
        item = db.scalar(
            select(ProcurementPoolItem)
            .where(ProcurementPoolItem.user_id == user_id)
            .where(ProcurementPoolItem.product_group_id == group.id)
        )
        if workspace_id is not None:
            item = db.scalar(
                select(ProcurementPoolItem)
                .where(ProcurementPoolItem.user_id == user_id)
                .where(ProcurementPoolItem.workspace_id == workspace_id)
                .where(ProcurementPoolItem.product_group_id == group.id)
            )
        created = False
        if not item:
            item = ProcurementPoolItem(
                user_id=user_id,
                workspace_id=workspace_id,
                product_group_id=group.id,
                keyword=keyword,
                category=category_override or supplier.product_category,
                title=title,
                image=image or None,
                description=self._description_from_product(product),
                source_platform=str(supplier.platform or "1688"),
                source_url=str(product.product_url if product else supplier.product_url or ""),
                supplier_count=0,
                min_price=0.0,
                max_price=0.0,
                avg_price=0.0,
                estimated_profit=0.0,
                market_score=0.0,
                status="NEW",
                metadata_json={
                    "source_type": source_type,
                    "group_key": group.group_key,
                },
            )
            db.add(item)
            db.flush()
            created = True
        self._upsert_supplier_item(db, item=item, supplier=supplier, product=product, source_type=source_type)
        self._refresh_pool_metrics(db, item)
        return {"pool_item_id": item.id, "created": created}

    def _find_or_create_group(self, db: Session, *, keyword: str, title: str, image: str | None, specs: list[str]) -> ProductGroup:
        candidates = list(db.scalars(select(ProductGroup).where(ProductGroup.canonical_keyword == keyword)).all())
        best_group = None
        best_score = 0.0
        for candidate in candidates:
            snapshot = candidate.similarity_snapshot or {}
            result = product_matching_engine.match(
                title_a=title,
                title_b=candidate.canonical_title,
                keyword_a=keyword,
                keyword_b=candidate.canonical_keyword,
                image_a=image,
                image_b=candidate.representative_image,
                specs_a=specs,
                specs_b=snapshot.get("specs") or [],
            )
            if float(result["similarity_score"]) > best_score:
                best_score = float(result["similarity_score"])
                best_group = candidate
        if best_group and best_score >= 78:
            return best_group
        digest = hashlib.sha1(f"{keyword}|{title}".encode("utf-8")).hexdigest()[:16]
        group = ProductGroup(
            group_key=f"pg-{digest}",
            canonical_keyword=keyword,
            canonical_title=title,
            representative_image=image,
            similarity_snapshot={"specs": specs},
        )
        db.add(group)
        db.flush()
        return group

    def _upsert_supplier_item(
        self,
        db: Session,
        *,
        item: ProcurementPoolItem,
        supplier: Supplier,
        product: SupplierProduct | None,
        source_type: str,
    ) -> None:
        existing = db.scalar(
            select(ProcurementSupplierItem)
            .where(ProcurementSupplierItem.pool_item_id == item.id)
            .where(ProcurementSupplierItem.supplier_id == supplier.id)
        )
        reality = supplier_reality_engine.evaluate(
            db,
            supplier=supplier,
            pool_item_id=item.id,
            keyword=item.keyword,
            expected_price=float(item.avg_price or 0) if float(item.avg_price or 0) > 0 else None,
            quantity=int(supplier.min_order_quantity or 0) or None,
        )
        price = self._product_mid_price(product, supplier)
        if not existing:
            existing = ProcurementSupplierItem(
                pool_item_id=item.id,
                workspace_id=item.workspace_id,
                supplier_id=supplier.id,
                supplier_product_id=product.id if product else None,
                supplier_name=supplier.name,
                price=price,
                moq=supplier.min_order_quantity,
                delivery_time=supplier.delivery_time_days,
                supplier_score=float(supplier.trust_score or 0),
                risk_score=float(reality.get("supplier_risk_score") or 0),
                supplier_truth_score=float(reality.get("supplier_truth_score") or 0),
                source_type=source_type,
                metadata_json=reality,
            )
            db.add(existing)
            db.flush()
            return
        existing.supplier_product_id = product.id if product else existing.supplier_product_id
        existing.supplier_name = supplier.name
        existing.price = price
        existing.moq = supplier.min_order_quantity
        existing.delivery_time = supplier.delivery_time_days
        existing.supplier_score = float(supplier.trust_score or 0)
        existing.risk_score = float(reality.get("supplier_risk_score") or 0)
        existing.supplier_truth_score = float(reality.get("supplier_truth_score") or 0)
        existing.source_type = source_type
        existing.metadata_json = reality
        db.add(existing)

    def _refresh_pool_metrics(self, db: Session, item: ProcurementPoolItem) -> None:
        supplier_items = list(db.scalars(select(ProcurementSupplierItem).where(ProcurementSupplierItem.pool_item_id == item.id)).all())
        prices = [float(row.price or 0) for row in supplier_items if float(row.price or 0) > 0]
        item.supplier_count = len(supplier_items)
        item.min_price = round(min(prices), 2) if prices else 0.0
        item.max_price = round(max(prices), 2) if prices else 0.0
        item.avg_price = round(mean(prices), 2) if prices else 0.0
        item.estimated_profit = round(max(0.0, item.avg_price * 0.75), 2) if item.avg_price else 0.0
        db.add(item)

    def _serialize_pool_item(self, db: Session, item: ProcurementPoolItem, *, include_suppliers: bool = False, include_analysis: bool = False) -> dict:
        suppliers = list(
            db.scalars(
                select(ProcurementSupplierItem)
                .where(ProcurementSupplierItem.pool_item_id == item.id)
                .order_by(ProcurementSupplierItem.supplier_truth_score.desc(), ProcurementSupplierItem.price.asc())
            ).all()
        )
        best_supplier_score = max((float(row.supplier_truth_score or row.supplier_score or 0) for row in suppliers), default=0.0)
        best_risk_score = min((float(row.risk_score or 100) for row in suppliers), default=100.0)
        risk_level = "low" if best_risk_score < 35 else "medium" if best_risk_score < 65 else "high"
        analysis = procurement_analysis_engine.latest_for_pool_item(db, pool_item_id=item.id) if include_analysis else None
        payload = {
            "id": item.id,
            "keyword": item.keyword,
            "category": item.category,
            "title": item.title,
            "image": item.image,
            "description": item.description,
            "source_platform": item.source_platform,
            "source_url": item.source_url,
            "supplier_count": item.supplier_count,
            "min_price": round(float(item.min_price or 0), 2),
            "max_price": round(float(item.max_price or 0), 2),
            "avg_price": round(float(item.avg_price or 0), 2),
            "estimated_profit": round(float(item.estimated_profit or 0), 2),
            "market_score": round(float(item.market_score or 0), 2),
            "status": item.status,
            "supplier_score": round(best_supplier_score, 2),
            "risk_level": risk_level,
            "created_at": item.created_at.isoformat() if item.created_at else "",
        }
        if include_suppliers:
            payload["suppliers"] = [
                {
                    "id": row.id,
                    "supplier_id": row.supplier_id,
                    "supplier_name": row.supplier_name,
                    "price": round(float(row.price or 0), 2),
                    "moq": row.moq,
                    "delivery_time": row.delivery_time,
                    "supplier_score": round(float(row.supplier_score or 0), 2),
                    "risk_score": round(float(row.risk_score or 0), 2),
                    "supplier_truth_score": round(float(row.supplier_truth_score or 0), 2),
                    "source_type": row.source_type,
                }
                for row in suppliers
            ]
        if analysis:
            payload["analysis"] = analysis.snapshot
        return payload

    def _apply_filters(
        self,
        items: list[dict],
        *,
        price_range: tuple[float | None, float | None] | None,
        profit_range: tuple[float | None, float | None] | None,
        supplier_score: float | None,
        risk_level: str | None,
    ) -> list[dict]:
        filtered = items
        if price_range:
            min_price, max_price = price_range
            if min_price is not None:
                filtered = [item for item in filtered if float(item.get("min_price") or 0) >= min_price]
            if max_price is not None:
                filtered = [item for item in filtered if float(item.get("max_price") or 0) <= max_price]
        if profit_range:
            min_profit, max_profit = profit_range
            if min_profit is not None:
                filtered = [item for item in filtered if float(item.get("estimated_profit") or 0) >= min_profit]
            if max_profit is not None:
                filtered = [item for item in filtered if float(item.get("estimated_profit") or 0) <= max_profit]
        if supplier_score is not None:
            filtered = [item for item in filtered if float(item.get("supplier_score") or 0) >= supplier_score]
        if risk_level:
            filtered = [item for item in filtered if str(item.get("risk_level") or "").lower() == risk_level.lower()]
        return filtered

    def _sort_items(self, items: list[dict], *, sort: str) -> list[dict]:
        normalized = str(sort or "latest").lower()
        if normalized == "lowest_price":
            return sorted(items, key=lambda item: float(item.get("min_price") or 999999))
        if normalized == "highest_profit":
            return sorted(items, key=lambda item: -float(item.get("estimated_profit") or 0))
        if normalized == "highest_score":
            return sorted(items, key=lambda item: -float(item.get("supplier_score") or 0))
        if normalized == "lowest_risk":
            return sorted(items, key=lambda item: {"low": 0, "medium": 1, "high": 2}.get(str(item.get("risk_level") or "high").lower(), 3))
        return sorted(items, key=lambda item: str(item.get("created_at") or ""), reverse=True)

    def _product_mid_price(self, product: SupplierProduct | None, supplier: Supplier) -> float:
        if product and (float(product.price_min or 0) > 0 or float(product.price_max or 0) > 0):
            values = [float(product.price_min or 0), float(product.price_max or 0)]
            values = [value for value in values if value > 0]
            return round(sum(values) / len(values), 2) if values else 0.0
        price_range = supplier.price_range or {}
        values = [float(price_range.get("min") or 0), float(price_range.get("max") or 0)]
        values = [value for value in values if value > 0]
        return round(sum(values) / len(values), 2) if values else 0.0

    def _description_from_product(self, product: SupplierProduct | None) -> str | None:
        if not product or not isinstance(product.raw_snapshot, dict):
            return None
        return str(product.raw_snapshot.get("description") or product.raw_snapshot.get("metadata", {}).get("description") or "").strip() or None

    def _normalize_source_type(self, source_type: str | None) -> str:
        value = str(source_type or "").strip().lower()
        if value == "browser_extension":
            return "1688_EXTENSION"
        if value in {"manual_input", "merchant_authorized"}:
            return "USER_IMPORT"
        return "LOCAL_DATABASE"

    def _extract_mid_price(self, raw: str) -> float:
        numbers = []
        current = ""
        for char in raw:
            if char.isdigit() or char == ".":
                current += char
            elif current:
                numbers.append(float(current))
                current = ""
        if current:
            numbers.append(float(current))
        if not numbers:
            return 0.0
        if len(numbers) == 1:
            return round(numbers[0], 2)
        return round(sum(numbers[:2]) / 2, 2)

    def _extract_moq(self, raw: str) -> int:
        digits = "".join(char if char.isdigit() else " " for char in str(raw or "")).split()
        return int(digits[0]) if digits else 0

    def _extract_delivery_time(self, metadata: dict) -> int | None:
        digits = "".join(char if char.isdigit() else " " for char in str(metadata.get("delivery_time") or "")).split()
        return int(digits[0]) if digits else None


procurement_pool_service = ProcurementPoolService()

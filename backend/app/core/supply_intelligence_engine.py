from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from statistics import mean

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.supply.alibaba_1688_adapter import AlibabaQuery
from app.adapters.supply.pinduoduo_supply_adapter import PinduoduoSupplyAdapter
from app.adapters.supply.source_manager import source_manager
from app.core.supplier_scoring_engine import supplier_scoring_engine
from app.core.supply_monitor import supply_monitor
from app.models.supplier import Supplier, SupplierProduct, SupplyAnalysisHistory, SupplySupplierHistory
from app.services.supply_cost_engine import supply_cost_engine


class SupplyQuery(BaseModel):
    keyword: str
    category: str | None = None
    target_market: str
    expected_price: float | None = None
    quantity: int = 100


class SupplyIntelligenceEngine:
    def analyze(self, db: Session, query: SupplyQuery) -> dict:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.analyze_async(db, query))
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(self.analyze_async(db, query))).result()

    async def analyze_async(self, db: Session, query: SupplyQuery) -> dict:
        source_payloads, pdd_payload = await asyncio.gather(
            source_manager.collect(
                db,
                query=AlibabaQuery(
                    keyword=query.keyword,
                    category=query.category,
                    target_price=query.expected_price,
                    region=query.target_market or "CN",
                ),
            ),
            PinduoduoSupplyAdapter().fetch(
                keyword=query.keyword,
                target_market=query.target_market,
                category=query.category,
                expected_price=query.expected_price,
                quantity=query.quantity,
            ),
        )

        source_payloads["pinduoduo"] = pdd_payload
        raw_suppliers: list[dict] = []
        for source_name, payload in source_payloads.items():
            for item in list(payload.get("data", {}).get("suppliers", [])):
                raw_suppliers.append(self._normalize_supplier(item=item, source_name=source_name, query=query))

        suppliers = self._score_suppliers(db, raw_suppliers=raw_suppliers, query=query)
        suppliers = sorted(
            suppliers,
            key=lambda item: (
                bool(item.get("is_mock")),
                -float(item.get("supplier_score") or 0),
                -float(item.get("supplier_confidence") or 0),
                float(item.get("price_mid") or 999999),
                int(item.get("min_order_quantity") or 999999),
            ),
        )[:10]

        selected_supplier = suppliers[0] if suppliers else None
        is_mock = not selected_supplier or bool(selected_supplier.get("is_mock"))
        cost_estimate = self._build_cost_estimate(selected_supplier=selected_supplier, query=query)
        profit_preview = self._build_profit_preview(cost_estimate=cost_estimate, selected_supplier=selected_supplier)
        risk_flags = self._collect_risk_flags(suppliers)
        confidence = self._compute_confidence(source_payloads=source_payloads, suppliers=suppliers)
        procurement_advice = self._procurement_advice(
            selected_supplier=selected_supplier,
            profit_preview=profit_preview,
            confidence=confidence,
        )

        payload = {
            "keyword": query.keyword,
            "category": query.category,
            "target_market": query.target_market,
            "quantity": query.quantity,
            "suppliers": suppliers,
            "selected_supplier": selected_supplier,
            "supplier_score": float(selected_supplier.get("supplier_score") or 0) if selected_supplier else 0.0,
            "supplier_quality": str(selected_supplier.get("supplier_level") or "D") if selected_supplier else "D",
            "supplier_confidence": float(selected_supplier.get("supplier_confidence") or 0) if selected_supplier else 0.0,
            "supplier_risk": list(selected_supplier.get("risk_flags") or []) if selected_supplier else ["supplier_unverified"],
            "cost_estimate": cost_estimate,
            "profit_preview": profit_preview,
            "confidence": confidence,
            "risk_flags": risk_flags,
            "procurement_recommendation": procurement_advice,
            "data_sources": source_payloads,
            "data_source": selected_supplier.get("source_type") if selected_supplier else "mock",
            "is_mock": is_mock,
        }
        self._persist(db, query=query, payload=payload)
        return payload

    def _normalize_supplier(self, *, item: dict, source_name: str, query: SupplyQuery) -> dict:
        price_range = item.get("price_range") or {}
        price_min = float(item.get("price_min") or price_range.get("min") or 0)
        price_max = float(item.get("price_max") or price_range.get("max") or price_min or 0)
        currency = str(item.get("currency") or price_range.get("currency") or "CNY")
        product_title = str(item.get("product_title") or item.get("title") or query.keyword)
        supplier_name = str(item.get("supplier_name") or item.get("name") or "未命名供应商")
        return {
            "name": supplier_name,
            "platform": "1688" if "1688" in source_name or source_name != "pinduoduo" else "pinduoduo",
            "supplier_type": str(item.get("supplier_type") or ("factory" if item.get("factory_level") else "trader")),
            "location": item.get("supplier_location") or item.get("location"),
            "product_category": query.category,
            "product_title": product_title,
            "product_image": (item.get("images") or [None])[0],
            "images": list(item.get("images") or []),
            "product_url": item.get("product_url") or item.get("url") or item.get("search_url"),
            "price_min": price_min,
            "price_max": price_max,
            "currency": currency,
            "min_order_quantity": int(item.get("min_order_quantity") or item.get("moq") or 0),
            "transaction_score": float(item.get("transaction_score") or 0),
            "factory_score": float(item.get("factory_score") or 0),
            "trust_score": float(item.get("trust_score") or 0),
            "factory_info": str(item.get("factory_level") or item.get("factory_info") or ""),
            "transaction_info": str(item.get("transaction_info") or ""),
            "data_source": str(item.get("data_source") or item.get("source_type") or source_name),
            "source_type": str(item.get("source_type") or source_name),
            "confidence_score": float(item.get("confidence_score") or 0),
            "certification": str(item.get("certification") or ""),
            "delivery_time": item.get("delivery_time"),
            "feedback_status": item.get("feedback_status"),
            "feedback_score": float(item.get("feedback_score") or 0),
            "availability": str(item.get("availability") or ("mock" if item.get("is_mock") else "available")),
            "is_mock": bool(item.get("is_mock", False)),
            "risk_flags": list(item.get("risk_flags") or []),
            "search_url": item.get("search_url") or item.get("product_url"),
            "last_verified_time": item.get("last_verified_time"),
        }

    def _score_suppliers(self, db: Session, *, raw_suppliers: list[dict], query: SupplyQuery) -> list[dict]:
        scored: list[dict] = []
        for item in raw_suppliers:
            price_min = float(item.get("price_min") or 0)
            price_max = float(item.get("price_max") or price_min)
            price_mid = round((price_min + price_max) / 2, 2) if (price_min or price_max) else 0.0
            market_match = self._market_match_score(item=item, query=query)
            stability_score = supplier_scoring_engine.stability_score(
                factory_score=float(item.get("factory_score") or 0),
                transaction_history=float(item.get("transaction_score") or 0),
                source_confidence=float(item.get("confidence_score") or 0),
            )
            score_meta = supplier_scoring_engine.score(
                stability_score=stability_score,
                price_competitiveness=supplier_scoring_engine.price_competitiveness(
                    price_mid=price_mid,
                    expected_price=query.expected_price,
                ),
                moq_reasonableness=supplier_scoring_engine.moq_reasonableness(
                    moq=int(item.get("min_order_quantity") or 0),
                    quantity=query.quantity,
                ),
                delivery_score=supplier_scoring_engine.delivery_score(
                    delivery_time_days=self._delivery_days(item.get("delivery_time")),
                ),
                certification_score=supplier_scoring_engine.certification_score(
                    certification=item.get("certification"),
                ),
                feedback_score=supplier_scoring_engine.feedback_score(
                    trust_score=float(item.get("trust_score") or 0),
                    feedback_status=item.get("feedback_status"),
                ),
            )
            risk_flags = list(item.get("risk_flags") or [])
            if int(item.get("min_order_quantity") or 0) > query.quantity and query.quantity > 0:
                risk_flags.append("high_moq")
            if float(item.get("confidence_score") or 0) < 0.6:
                risk_flags.append("supplier_unverified")
            if not str(item.get("certification") or "").strip():
                risk_flags.append("missing_certification")
            if item.get("is_mock"):
                risk_flags.append("mock_data_used")
            monitor_result = supply_monitor.inspect(
                db,
                supplier_name=str(item.get("name") or ""),
                platform=str(item.get("platform") or ""),
                keyword=query.keyword,
                product_title=str(item.get("product_title") or ""),
            )
            risk_flags.extend(monitor_result.get("risk_alert", []))
            scored.append(
                {
                    **item,
                    "price_mid": price_mid,
                    "market_match": market_match,
                    "supplier_score": score_meta["score"],
                    "supplier_level": score_meta["level"],
                    "supplier_confidence": round(float(item.get("confidence_score") or 0), 4),
                    "recommendation": score_meta["recommendation"],
                    "score_reasons": score_meta["reason"],
                    "estimated_profit": round(max(0.0, float(query.expected_price or 0) - price_mid), 2) if query.expected_price else 0.0,
                    "price_change": monitor_result.get("price_change", 0.0),
                    "stock_change": monitor_result.get("stock_change", "unknown"),
                    "risk_flags": sorted(set(risk_flags)),
                }
            )
        return scored

    def _market_match_score(self, *, item: dict, query: SupplyQuery) -> float:
        keyword = query.keyword.strip().lower()
        title = str(item.get("product_title") or "").lower()
        category = str(query.category or "").lower()
        score = 35.0
        if keyword and keyword in title:
            score += 40.0
        if category and category in str(item.get("product_category") or "").lower():
            score += 10.0
        if item.get("certification"):
            score += 5.0
        if float(item.get("confidence_score") or 0) >= 0.8:
            score += 10.0
        return round(min(100.0, score), 2)

    def _delivery_days(self, raw_value) -> int | None:
        if raw_value in (None, "", 0):
            return None
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            text = str(raw_value)
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else None

    def _build_cost_estimate(self, *, selected_supplier: dict | None, query: SupplyQuery) -> dict:
        product_cost = float(selected_supplier.get("price_mid") or 0) if selected_supplier else 0.0
        shipping_estimate = round(max(6.5, product_cost * 0.18 + (0.02 * query.quantity)), 2) if selected_supplier else 0.0
        reference_price = float(query.expected_price or (product_cost * 2.2 if product_cost else 0))
        platform_fee = round(reference_price * 0.12, 2)
        marketing_cost = round(reference_price * 0.08, 2)
        return supply_cost_engine.calculate(
            product_cost=product_cost,
            shipping_estimate=shipping_estimate,
            platform_fee=platform_fee,
            marketing_cost=marketing_cost,
            expected_price=query.expected_price,
        )

    def _build_profit_preview(self, *, cost_estimate: dict, selected_supplier: dict | None) -> dict:
        suggested_price = float(cost_estimate.get("suggested_price") or 0)
        purchase_cost = float(cost_estimate.get("product_cost") or 0)
        shipping_cost = float(cost_estimate.get("shipping_estimate") or 0)
        platform_cost = float(cost_estimate.get("platform_fee") or 0)
        ad_cost = float(cost_estimate.get("marketing_cost") or 0)
        gross_profit = round(suggested_price - purchase_cost, 2)
        net_profit = round(gross_profit - shipping_cost - platform_cost - ad_cost, 2)
        margin_rate = round(net_profit / suggested_price, 4) if suggested_price > 0 else 0.0
        confidence = round(float(selected_supplier.get("supplier_confidence") or 0), 4) if selected_supplier else 0.0
        return {
            "purchase_cost": purchase_cost,
            "shipping_cost": shipping_cost,
            "platform_cost": platform_cost,
            "ad_cost": ad_cost,
            "gross_profit": gross_profit,
            "net_profit": net_profit,
            "margin_rate": margin_rate,
            "confidence": confidence,
            "suggested_price": suggested_price,
            "landed_cost": float(cost_estimate.get("landed_cost") or 0),
        }

    def _collect_risk_flags(self, suppliers: list[dict]) -> list[str]:
        flags: list[str] = []
        for item in suppliers[:5]:
            flags.extend(list(item.get("risk_flags") or []))
        return sorted(set(flags))

    def _compute_confidence(self, *, source_payloads: dict[str, dict], suppliers: list[dict]) -> float:
        source_confidences = [float(payload.get("confidence") or 0) for payload in source_payloads.values()]
        base = mean(source_confidences) if source_confidences else 0.0
        supplier_confidence = mean([float(item.get("supplier_confidence") or 0) for item in suppliers[:3]]) if suppliers else 0.0
        return round(max(0.0, min(1.0, base * 0.55 + supplier_confidence * 0.45)), 4)

    def _procurement_advice(self, *, selected_supplier: dict | None, profit_preview: dict, confidence: float) -> dict:
        if not selected_supplier:
            return {
                "decision": "不建议采购",
                "reason": "当前没有可用供应商",
            }
        score = float(selected_supplier.get("supplier_score") or 0)
        margin = float(profit_preview.get("margin_rate") or 0)
        if score >= 80 and margin >= 0.3 and confidence >= 0.7:
            return {"decision": "建议采购", "reason": "供应评分、利润率、可信度都达标。"}
        if score >= 65 and margin >= 0.15 and confidence >= 0.5:
            return {"decision": "建议小批量测试", "reason": "可以先小批量验证，不建议直接放量。"}
        return {"decision": "暂不建议采购", "reason": "供应链可信度或利润空间不足。"}

    def _persist(self, db: Session, *, query: SupplyQuery, payload: dict) -> None:
        selected = payload.get("selected_supplier")
        if selected:
            supplier = self._upsert_supplier(db, selected, query=query)
            self._upsert_supplier_product(db, supplier_id=supplier.id, item=selected, keyword=query.keyword)
            self._append_supplier_history(db, item=selected, keyword=query.keyword, payload=payload)
        db.add(
            SupplyAnalysisHistory(
                keyword=query.keyword,
                category=query.category,
                target_market=query.target_market,
                quantity=query.quantity,
                supplier_score=float(payload.get("supplier_score") or 0),
                confidence=float(payload.get("confidence") or 0),
                is_mock=bool(payload.get("is_mock")),
                source=",".join(sorted(payload.get("data_sources", {}).keys())),
                snapshot=payload,
            )
        )
        db.commit()

    def _upsert_supplier(self, db: Session, item: dict, *, query: SupplyQuery) -> Supplier:
        record = db.scalar(
            select(Supplier)
            .where(Supplier.name == str(item.get("name") or ""))
            .where(Supplier.platform == str(item.get("platform") or ""))
        )
        if not record:
            record = Supplier(
                name=str(item.get("name") or ""),
                platform=str(item.get("platform") or ""),
                supplier_type=str(item.get("supplier_type") or "trader"),
                location=item.get("location"),
                product_category=query.category,
                min_order_quantity=int(item.get("min_order_quantity") or 0),
                price_range={"min": float(item.get("price_min") or 0), "max": float(item.get("price_max") or 0)},
                transaction_score=float(item.get("transaction_score") or 0),
                factory_score=float(item.get("factory_score") or 0),
                trust_score=float(item.get("supplier_score") or 0),
                certification=str(item.get("certification") or ""),
                delivery_time_days=self._delivery_days(item.get("delivery_time")),
                source_type=str(item.get("source_type") or "cache_database"),
                confidence_score=float(item.get("supplier_confidence") or item.get("confidence_score") or 0),
                is_authorized=str(item.get("source_type") or "") in {"merchant_authorized", "browser_extension"},
                last_feedback=" | ".join(item.get("score_reasons") or []),
                last_verified_time=datetime.now(UTC),
            )
            db.add(record)
            db.flush()
            return record

        record.supplier_type = str(item.get("supplier_type") or record.supplier_type)
        record.location = item.get("location")
        record.product_category = query.category
        record.min_order_quantity = int(item.get("min_order_quantity") or 0)
        record.price_range = {"min": float(item.get("price_min") or 0), "max": float(item.get("price_max") or 0)}
        record.transaction_score = float(item.get("transaction_score") or 0)
        record.factory_score = float(item.get("factory_score") or 0)
        record.trust_score = float(item.get("supplier_score") or 0)
        record.certification = str(item.get("certification") or record.certification or "")
        record.delivery_time_days = self._delivery_days(item.get("delivery_time")) or record.delivery_time_days
        record.source_type = str(item.get("source_type") or record.source_type)
        record.confidence_score = float(item.get("supplier_confidence") or item.get("confidence_score") or record.confidence_score or 0)
        record.is_authorized = record.source_type in {"merchant_authorized", "browser_extension"}
        record.last_feedback = " | ".join(item.get("score_reasons") or []) or record.last_feedback
        record.last_verified_time = datetime.now(UTC)
        db.add(record)
        db.flush()
        return record

    def _upsert_supplier_product(self, db: Session, *, supplier_id: int, item: dict, keyword: str) -> None:
        record = db.scalar(
            select(SupplierProduct)
            .where(SupplierProduct.supplier_id == supplier_id)
            .where(SupplierProduct.keyword == keyword)
            .where(SupplierProduct.product_title == str(item.get("product_title") or ""))
        )
        if not record:
            record = SupplierProduct(
                supplier_id=supplier_id,
                keyword=keyword,
                product_title=str(item.get("product_title") or ""),
                product_image=item.get("product_image"),
                product_url=item.get("product_url") or item.get("search_url"),
                price_min=float(item.get("price_min") or 0),
                price_max=float(item.get("price_max") or 0),
                currency=item.get("currency") or "CNY",
                images=list(item.get("images") or []),
                source_type=str(item.get("source_type") or "cache_database"),
                confidence_score=float(item.get("supplier_confidence") or item.get("confidence_score") or 0),
                factory_info=item.get("factory_info"),
                transaction_info=item.get("transaction_info"),
                raw_snapshot=item,
            )
            db.add(record)
            return
        record.product_image = item.get("product_image")
        record.product_url = item.get("product_url") or item.get("search_url")
        record.price_min = float(item.get("price_min") or 0)
        record.price_max = float(item.get("price_max") or 0)
        record.currency = item.get("currency") or "CNY"
        record.images = list(item.get("images") or [])
        record.source_type = str(item.get("source_type") or record.source_type)
        record.confidence_score = float(item.get("supplier_confidence") or item.get("confidence_score") or record.confidence_score or 0)
        record.factory_info = item.get("factory_info")
        record.transaction_info = item.get("transaction_info")
        record.raw_snapshot = item
        db.add(record)

    def _append_supplier_history(self, db: Session, *, item: dict, keyword: str, payload: dict) -> None:
        profit_preview = payload.get("profit_preview") or {}
        db.add(
            SupplySupplierHistory(
                supplier_name=str(item.get("name") or ""),
                platform=str(item.get("platform") or ""),
                keyword=keyword,
                product_title=str(item.get("product_title") or ""),
                product_url=item.get("product_url") or item.get("search_url"),
                source_type=str(item.get("source_type") or "cache_database"),
                price_min=float(item.get("price_min") or 0),
                price_max=float(item.get("price_max") or 0),
                currency=item.get("currency") or "CNY",
                min_order_quantity=int(item.get("min_order_quantity") or 0),
                gross_profit=float(profit_preview.get("gross_profit") or 0),
                net_profit=float(profit_preview.get("net_profit") or 0),
                margin_rate=float(profit_preview.get("margin_rate") or 0),
                stock_change=str(item.get("stock_change") or "unknown"),
                feedback_status=str(item.get("feedback_status") or ""),
                snapshot=item,
            )
        )


supply_intelligence_engine = SupplyIntelligenceEngine()

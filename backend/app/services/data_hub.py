from __future__ import annotations

from statistics import mean

from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.core.schemas import CostModelSchema, DecisionResultSchema, MarketSignalSchema, SupplierOfferSchema
from app.decision import DecisionPolicy, policy_engine, provider_router
from app.governance import data_quality_engine, data_source_registry, data_traceability_system, lineage_writer
from app.pipeline import cost_sync_pipeline, market_sync_pipeline, supplier_sync_pipeline
from app.repositories.data_governance import (
    data_lineage_repository,
    data_quality_history_repository,
    data_source_registry_repository,
)
from app.repositories.product import product_repository


class DataHub:
    def __init__(self) -> None:
        self.task_context_store: dict[int, dict] = {}

    def get_market_data(
        self,
        db: Session,
        *,
        keyword: str,
        category: str | None = None,
        task_input: dict | None = None,
    ) -> list[MarketSignalSchema]:
        policy = policy_engine.build(task_input) if task_input else None
        router = provider_router.build(policy)
        raw = self.get_raw_data(db, data_type="market", keyword=keyword, category=category, policy=policy)
        self._attach_task_context(raw, task_input)
        self._attach_router_metadata(raw, router.routing_metadata)
        self.persist_raw_data(db, raw)
        clean = self.get_clean_data(raw)
        trusted = self.get_trusted_data(clean)
        self.persist_trusted_data(db, trusted)
        return trusted

    def get_task_ready_data(self, task_id: int) -> dict | None:
        return self.task_context_store.get(task_id)

    def attach_task_context(self, *, task_id: int, context: dict) -> None:
        existing = self.task_context_store.get(task_id, {})
        self.task_context_store[task_id] = {**existing, **context}

    def persist_task_context(self, db: Session | None, *, task_id: int, context: dict) -> None:
        del db
        existing = self.task_context_store.get(task_id, {})
        self.task_context_store[task_id] = {**existing, **context}

    def get_supplier_data(self, db: Session, *, keyword: str, task_input: dict | None = None) -> list[SupplierOfferSchema]:
        policy = policy_engine.build(task_input) if task_input else None
        router = provider_router.build(policy)
        raw = self.get_raw_data(db, data_type="supplier", keyword=keyword, policy=policy)
        self._attach_task_context(raw, task_input)
        self._attach_router_metadata(raw, router.routing_metadata)
        self.persist_raw_data(db, raw)
        clean = self.get_clean_data(raw)
        trusted = self.get_trusted_data(clean)
        self.persist_trusted_data(db, trusted)
        return trusted

    def get_cost_data(
        self,
        *,
        db: Session | None = None,
        selling_price: float,
        currency: str,
        suppliers: list[SupplierOfferSchema],
        package_weight_kg: float = 0.45,
        task_input: dict | None = None,
    ) -> CostModelSchema:
        policy = policy_engine.build(task_input) if task_input else None
        router = provider_router.build(policy)
        raw = cost_sync_pipeline.sync_cost(
            selling_price=selling_price,
            currency=currency,
            suppliers=suppliers,
            package_weight_kg=package_weight_kg,
            policy=policy,
        )
        self._attach_task_context([raw], task_input)
        self._attach_router_metadata([raw], router.routing_metadata)
        self.persist_raw_data(db, [raw])
        trusted = self.get_trusted_data([raw])[0]
        self.persist_trusted_data(db, [trusted])
        return trusted

    def get_decision_data(
        self,
        db: Session,
        *,
        product_id: int,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
        intelligence_score: float,
        product_profit_score: float,
        product_risk_score: float,
        task_input: dict | None = None,
    ) -> DecisionResultSchema:
        trusted_market = self.get_trusted_data(market_signals)
        trusted_supplier = self.get_trusted_data(supplier_offers)
        trusted_cost = self.get_trusted_data([cost_model])[0]
        return self.get_decision_ready_data(
            db,
            product_id=product_id,
            market_signals=trusted_market,
            supplier_offers=trusted_supplier,
            cost_model=trusted_cost,
            intelligence_score=intelligence_score,
            product_profit_score=product_profit_score,
            product_risk_score=product_risk_score,
            task_input=task_input,
        )

    def get_raw_data(
        self,
        db: Session,
        *,
        data_type: str,
        keyword: str | None = None,
        category: str | None = None,
        policy: DecisionPolicy | None = None,
    ):
        if data_type == "market":
            if category:
                return market_sync_pipeline.sync_category(db, category)
            return market_sync_pipeline.sync_keyword_with_policy(db, keyword or "", policy)
        if data_type == "supplier":
            return supplier_sync_pipeline.sync_keyword_with_policy(db, keyword or "", policy)
        return []

    def get_clean_data(self, items):
        cleaned = []
        for item in items:
            if getattr(item, "lineage_chain", None) is None:
                item.lineage_chain = []
            cleaned.append(item)
        return cleaned

    def persist_raw_data(self, db: Session | None, items) -> None:
        if db is None:
            return
        for item in items:
            data_source_registry_repository.create(
                db,
                workspace_id=getattr(item, "workspace_id", None),
                source_type=str(getattr(item, "source_type", "mock")),
                provider_name=str(getattr(item, "provider_name", getattr(item, "source_platform", "unknown_provider"))),
                status="pending",
            )

    def get_trusted_data(self, items):
        trusted = []
        for item in items:
            source_type = getattr(item, "source_type", "mock")
            provider_name = getattr(item, "provider_name", None) or getattr(item, "source_platform", None) or "unknown_provider"
            source_id = getattr(item, "source_id", None) or getattr(item, "id", None) or provider_name
            quality = data_quality_engine.evaluate(
                source_type=source_type,
                timestamp=getattr(item, "timestamp", None),
            )
            trace = data_traceability_system.build_trace(
                source_id=str(source_id),
                source_type=source_type,
                provider_name=str(provider_name),
                transform_steps=["provider_fetch", "pipeline_transform", "governance_quality_check", "data_hub_gate"],
                lineage_chain=list(getattr(item, "lineage_chain", []) or []),
            )
            data_source_registry.register_source(
                source_id=str(source_id),
                source_type=source_type,
                provider_name=str(provider_name),
                status=getattr(item, "sync_status", "success"),
            )
            item.source_id = str(source_id)
            item.provider_name = str(provider_name)
            item.truth_level = quality["truth_level"]
            item.confidence_score = quality["confidence_score"]
            item.freshness_score = quality["freshness_score"]
            item.sync_status = getattr(item, "sync_status", "success")
            item.last_verified_at = trace["last_verified_at"]
            item.fetch_timestamp = trace["fetch_timestamp"]
            item.transform_steps = trace["transform_steps"]
            item.lineage_chain = trace["lineage_chain"]
            trusted.append(item)
        return trusted

    def persist_trusted_data(self, db: Session | None, items) -> None:
        if db is None:
            return
        for item in items:
            self.persist_lineage(db, item)
            self.persist_quality_metrics(db, item)
            data_source_registry_repository.create(
                db,
                workspace_id=getattr(item, "workspace_id", None),
                source_type=str(getattr(item, "source_type", "mock")),
                provider_name=str(getattr(item, "provider_name", "unknown_provider")),
                status=str(getattr(item, "sync_status", "success")),
            )

    def persist_lineage(self, db: Session, item) -> None:
        source_id = str(getattr(item, "source_id", getattr(item, "id", "unknown")))
        provider_name = str(getattr(item, "provider_name", "unknown_provider"))
        lineage_chain = list(getattr(item, "lineage_chain", []) or [])
        transform_steps = list(getattr(item, "transform_steps", []) or [])
        payload = {
            "source_id": source_id,
            "provider_name": provider_name,
            "source_type": str(getattr(item, "source_type", "mock")),
            "truth_level": str(getattr(item, "truth_level", "simulated")),
            "confidence_score": float(getattr(item, "confidence_score", 0.0)),
            "freshness_score": float(getattr(item, "freshness_score", 0.0)),
            "lineage_chain": lineage_chain,
            "transform_steps": transform_steps,
            "workspace_id": getattr(item, "workspace_id", None),
            "user_id": getattr(item, "user_id", None),
            "api_key_id": getattr(item, "api_key_id", None),
        }
        task_id = getattr(item, "task_id", None)
        pipeline_step = f"datahub:{provider_name}:{source_id}"
        lineage_writer.write_event_if_not_exists(
            db,
            event_type="lineage",
            event_stage="data_hub_lineage_persist",
            pipeline_step=pipeline_step,
            task_id=task_id,
            workspace_id=getattr(item, "workspace_id", None),
            user_id=getattr(item, "user_id", None),
            api_key_id=getattr(item, "api_key_id", None),
            source_id=source_id,
            node_type="legacy",
            payload_json=payload,
            lineage_chain=lineage_chain,
            transform_steps=transform_steps,
        )

    def persist_quality_metrics(self, db: Session, item) -> None:
        data_quality_history_repository.create(
            db,
            workspace_id=getattr(item, "workspace_id", None),
            data_id=str(getattr(item, "source_id", getattr(item, "id", "unknown"))),
            truth_level=str(getattr(item, "truth_level", "simulated")),
            confidence_score=float(getattr(item, "confidence_score", 0.0)),
            freshness_score=float(getattr(item, "freshness_score", 0.0)),
            reliability_score=float(getattr(item, "reliability_score", getattr(item, "confidence_score", 0.0))),
        )

    def get_decision_ready_data(
        self,
        db: Session,
        *,
        product_id: int,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
        intelligence_score: float,
        product_profit_score: float,
        product_risk_score: float,
        task_input: dict | None = None,
    ) -> DecisionResultSchema:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise AppError("PRODUCT_NOT_FOUND", "商品不存在", "db", 404)

        policy = policy_engine.build(task_input) if task_input else None
        weights = (policy.scoring_weights if policy else {"price": 0.4, "rating": 0.4, "speed": 0.2})
        router = provider_router.build(policy)

        market_fit_score = self._market_fit_score(market_signals)
        supplier_fit_score = self._supplier_fit_score(supplier_offers, weights=weights)
        profit_score = self._profit_score(
            selling_price=float(product.current_price or 0),
            total_cost=float(cost_model.total_cost),
            product_profit_score=product_profit_score,
        )
        risk_score = self._risk_score(product_risk_score, market_fit_score, supplier_fit_score)
        confidence_score = self._confidence_score(market_signals, supplier_offers, cost_model)
        reliability_score = self._reliability_score(market_signals, supplier_offers, cost_model)
        final_score = self._final_score(
            intelligence_score=intelligence_score,
            market_fit_score=market_fit_score,
            supplier_fit_score=supplier_fit_score,
            profit_score=profit_score,
            risk_score=risk_score,
        )
        decision = self._decision(final_score)
        return DecisionResultSchema(
            product_id=product_id,
            decision=decision,
            confidence_score=round(confidence_score, 4),
            profit_range=self._profit_range(float(product.current_price or 0), float(cost_model.total_cost)),
            risk_level=self._risk_level(risk_score),
            reasoning=self._reasoning(
                product_title=product.title,
                market_fit_score=market_fit_score,
                supplier_fit_score=supplier_fit_score,
                profit_score=profit_score,
                risk_score=risk_score,
                confidence_score=confidence_score,
                decision=decision,
            ),
            market_fit_score=round(market_fit_score, 2),
            supplier_fit_score=round(supplier_fit_score, 2),
            profit_score=round(profit_score, 2),
            risk_score=round(risk_score, 2),
            reliability_score=round(reliability_score, 4),
            final_score=round(final_score, 2),
            source_type="estimated",
            truth_level=self._truth_level(market_signals, supplier_offers, cost_model),
            sync_status="success",
            source_id=f"decision:{product_id}",
            provider_name="data_hub_v2",
            freshness_score=round(self._decision_freshness(market_signals, supplier_offers, cost_model), 4),
            last_verified_at=cost_model.last_verified_at,
            lineage_chain=[
                "providers",
                "pipelines",
                "governance",
                "data_hub_v2",
                "decision_engine",
                router.market_provider,
                router.supplier_provider,
                router.cost_provider,
            ],
            transform_steps=[
                "trusted_data_filter",
                "decision_ready_aggregation",
                "provider_router_attach",
                f"policy:{policy.decision_mode}" if policy else "policy:default",
            ],
        )

    def _attach_router_metadata(self, items, routing_metadata: dict[str, str]) -> None:
        route_markers = [f"{key}:{value}" for key, value in routing_metadata.items()]
        for item in items:
            item.lineage_chain = [*list(getattr(item, "lineage_chain", []) or []), *route_markers]
            item.transform_steps = [*list(getattr(item, "transform_steps", []) or []), "data_hub_router_attach"]

    def _attach_task_context(self, items, task_input: dict | None) -> None:
        payload = task_input or {}
        for item in items:
            item.workspace_id = payload.get("workspace_id")
            item.user_id = payload.get("user_id")
            item.api_key_id = payload.get("api_key_id")

    def _market_fit_score(self, market_signals: list[MarketSignalSchema]) -> float:
        if not market_signals:
            return 0.0
        return max(
            0.0,
            min(
                100.0,
                mean(
                    (
                        signal.trend_score * 0.35
                        + signal.demand_level * 0.35
                        + (100 - signal.competition_index) * 0.15
                        + signal.confidence_score * 0.15
                    )
                    for signal in market_signals
                ),
            ),
        )

    def _supplier_fit_score(self, supplier_offers: list[SupplierOfferSchema], *, weights: dict[str, float] | None = None) -> float:
        if not supplier_offers:
            return 0.0
        weights = weights or {"price": 0.4, "rating": 0.4, "speed": 0.2}
        scored = []
        for item in supplier_offers[:3]:
            price_score = 100 - float(item.price or 100) if item.price is not None else 0.0
            rating_score = float(item.rating or 0.0) * 20
            match_score = float(item.match_score)
            blended = price_score * weights.get("price", 0.4) + rating_score * weights.get("rating", 0.4) + match_score * weights.get("speed", 0.2)
            scored.append(blended)
        return max(0.0, min(100.0, mean(scored)))

    def _profit_score(self, *, selling_price: float, total_cost: float, product_profit_score: float) -> float:
        if selling_price <= 0:
            return max(0.0, min(100.0, product_profit_score * 0.7))
        margin_score = max(0.0, min(((selling_price - total_cost) / selling_price) * 100, 100.0))
        return max(0.0, min(100.0, margin_score * 0.55 + product_profit_score * 0.45))

    def _risk_score(self, product_risk_score: float, market_fit_score: float, supplier_fit_score: float) -> float:
        score = product_risk_score * 0.6 + (100 - market_fit_score) * 0.2 + (100 - supplier_fit_score) * 0.2
        return max(0.0, min(100.0, score))

    def _confidence_score(
        self,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
    ) -> float:
        market_conf = mean(signal.confidence_score for signal in market_signals) if market_signals else 0.0
        supplier_conf = 65.0 if supplier_offers else 0.0
        cost_conf = 45.0 if cost_model.truth_level == "simulated" else 70.0
        score = market_conf * 0.45 + supplier_conf * 0.30 + cost_conf * 0.25
        return max(0.0, min(1.0, score / 100))

    def _reliability_score(
        self,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
    ) -> float:
        market_rel = mean(signal.confidence_score for signal in market_signals) if market_signals else 0.0
        supplier_rel = mean(min(item.match_score / 100, 1.0) for item in supplier_offers[:3]) if supplier_offers else 0.0
        cost_rel = cost_model.confidence_score
        return max(0.0, min(1.0, market_rel * 0.45 + supplier_rel * 0.30 + cost_rel * 0.25))

    def _final_score(
        self,
        *,
        intelligence_score: float,
        market_fit_score: float,
        supplier_fit_score: float,
        profit_score: float,
        risk_score: float,
    ) -> float:
        score = (
            intelligence_score * 0.28
            + market_fit_score * 0.24
            + supplier_fit_score * 0.18
            + profit_score * 0.20
            + (100 - risk_score) * 0.10
        )
        return max(0.0, min(100.0, score))

    def _decision(self, final_score: float) -> str:
        normalized = final_score / 100
        if normalized > 0.75:
            return "RECOMMEND"
        if normalized >= 0.5:
            return "WATCH"
        return "REJECT"

    def _risk_level(self, risk_score: float) -> str:
        if risk_score >= 70:
            return "HIGH"
        if risk_score >= 45:
            return "MEDIUM"
        return "LOW"

    def _profit_range(self, selling_price: float, total_cost: float) -> dict:
        base_profit = round(selling_price - total_cost, 2)
        return {
            "min": round(base_profit * 0.85, 2),
            "mid": round(base_profit, 2),
            "max": round(base_profit * 1.15, 2),
        }

    def _truth_level(
        self,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
    ) -> str:
        levels = [signal.truth_level for signal in market_signals] + [item.truth_level for item in supplier_offers] + [cost_model.truth_level]
        if levels and all(level == "real" for level in levels):
            return "real"
        if any(level == "semi_real" for level in levels):
            return "semi_real"
        return "simulated"

    def _decision_freshness(
        self,
        market_signals: list[MarketSignalSchema],
        supplier_offers: list[SupplierOfferSchema],
        cost_model: CostModelSchema,
    ) -> float:
        scores = [signal.freshness_score for signal in market_signals] + [item.freshness_score for item in supplier_offers[:3]] + [cost_model.freshness_score]
        if not scores:
            return 0.0
        return mean(scores)

    def _reasoning(
        self,
        *,
        product_title: str,
        market_fit_score: float,
        supplier_fit_score: float,
        profit_score: float,
        risk_score: float,
        confidence_score: float,
        decision: str,
    ) -> list[str]:
        return [
            f"商品 {product_title[:40]} 的市场匹配分约为 {market_fit_score:.1f}，说明需求与趋势基础{'较强' if market_fit_score >= 70 else '一般' if market_fit_score >= 50 else '偏弱'}。",
            f"供应适配分约为 {supplier_fit_score:.1f}，当前供应候选的可用性{'较好' if supplier_fit_score >= 70 else '一般' if supplier_fit_score >= 50 else '偏弱'}。",
            f"利润分约为 {profit_score:.1f}，风险分约为 {risk_score:.1f}，利润与风险已经一起参与决策。",
            f"当前决策可信度约为 {confidence_score * 100:.1f}% ，数据结构已经统一经过 DataHub 聚合。",
            f"最终标准化决策结果为 {decision}。",
        ]


data_hub = DataHub()

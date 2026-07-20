from __future__ import annotations

from sqlalchemy.orm import Session

from app.decision import policy_engine, provider_router
from app.governance import lineage_writer
from app.repositories.data_governance import sync_job_repository
from app.repositories.decision_repository import decision_repository
from app.services.data_hub import data_hub
from app.services.decision_explain_service import decision_explain_service
from app.services.decision_engine import decision_engine
from app.services.decision_truth_wrapper import decision_truth_wrapper
from app.services.market_intelligence_engine import market_intelligence_engine
from app.services.supplier_matching_engine import supplier_matching_engine
from app.core.analysis_orchestrator import analysis_orchestrator


class ExecutionBridge:
    def execute(self, db: Session, *, task_id: int, job_type: str, payload: dict) -> dict:
        policy = policy_engine.build(payload)
        router = provider_router.build(policy)
        if job_type == "market":
            report_type = str(payload.get("report_type") or "market_intelligence").strip().lower()
            if report_type == "market_commercial_reality":
                result = market_intelligence_engine.commercial_reality_report(
                    db=db,
                    keyword=payload["keyword"],
                    region=payload.get("region", payload.get("market", "global")),
                )
            elif report_type == "market_reality":
                result = market_intelligence_engine.reality_report(
                    keyword=payload["keyword"],
                    region=payload.get("region", payload.get("market", "global")),
                    category=payload.get("category"),
                )
            else:
                result = market_intelligence_engine.analyze_keyword(
                    db,
                    payload["keyword"],
                    region=payload.get("region", payload.get("market", "global")),
                    category=payload.get("category"),
                    user_id=payload.get("user_id"),
                )
        elif job_type == "supplier":
            result = supplier_matching_engine.match(db, payload["keyword"])
        elif job_type == "decision":
            result = self._run_decision_flow(db, task_id=task_id, product_id=payload["product_id"], task_input=payload, policy=policy, router=router)
        else:
            raise ValueError(f"unsupported job type: {job_type}")

        sync_job_repository.update_status(
            db,
            task_id,
            status="success",
            result_payload=result,
        )
        return result

    def _run_decision_flow(self, db: Session, *, task_id: int, product_id: int, task_input: dict, policy, router) -> dict:
        data_hub.attach_task_context(
            task_id=task_id,
            context={"product_id": product_id, "job_type": "decision", "policy": policy.__dict__, "router": router.routing_metadata, "task_input": task_input},
        )

        decision_result = decision_engine.recommend(db, product_id, task_id=task_id, task_input=task_input)
        decision_repository.persist_decision_result(
            db,
            task_id=task_id,
            product_id=product_id,
            payload=decision_result,
        )
        truth_result = None
        explain_result = None

        if policy.pipeline_depth == "full":
            truth_result = decision_truth_wrapper.recommend(db, product_id, task_id=task_id, task_input=task_input)
            decision_repository.persist_business_truth_result(
                db,
                task_id=task_id,
                product_id=product_id,
                payload=truth_result,
            )
            explain_result = decision_explain_service.explain(
                db,
                product_id=product_id,
                task_id=task_id,
                task_input=task_input,
                decision_payload=decision_result,
                truth_payload=truth_result,
            )
        else:
            explain_result = {
                "product_id": product_id,
                "task_id": task_id,
                "market_signals_used": [],
                "supplier_sources": [],
                "cost_breakdown": {},
                "provider_routing": router.routing_metadata,
                "cost_provider": router.cost_provider,
                "supplier_provider": router.supplier_provider,
                "market_provider": router.market_provider,
                "risk_factors": {},
                "confidence_score": decision_result.get("confidence_score"),
                "why_this_recommendation": decision_result.get("reasons", []),
                "data_lineage": decision_result.get("lineage_chain", []),
            }

        task_context = {
            "task_id": task_id,
            "product_id": product_id,
            "policy": policy.__dict__,
            "router": router.routing_metadata,
            "decision_result": decision_result,
            "truth_result": truth_result,
            "explain_result": explain_result,
            "governance_trace": {
                "event_id": f"{task_id}:trace:trace_result_persist",
                "event_key": f"{task_id}:trace:trace_result_persist",
                "event_stage": "trace_result_persist",
                "task_id": task_id,
                "workspace_id": task_input.get("workspace_id"),
                "user_id": task_input.get("user_id"),
                "api_key_id": task_input.get("api_key_id"),
                "source_id": decision_result.get("source_id"),
                "truth_level": decision_result.get("truth_level"),
                "lineage_chain": decision_result.get("lineage_chain", []),
                "confidence_score": decision_result.get("confidence_score"),
                "freshness_score": decision_result.get("freshness_score"),
                "api_key_id": task_input.get("api_key_id"),
                "provider_routing": router.routing_metadata,
            },
        }
        lineage_writer.write_from_trace(
            db,
            task_context["governance_trace"],
            task_id=task_id,
            workspace_id=task_input.get("workspace_id"),
            user_id=task_input.get("user_id"),
            source_id=decision_result.get("source_id"),
        )
        data_hub.persist_task_context(db, task_id=task_id, context=task_context)
        return task_context


execution_bridge = ExecutionBridge()

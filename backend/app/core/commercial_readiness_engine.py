from __future__ import annotations

from app.core.config import settings
from app.core.config_center import config_center
from app.core.data_trust_layer import data_trust_layer
from app.core.execution_insight_layer import execution_insight_layer
from app.core.feedback_loop_v2 import feedback_loop_v2
from app.core.launch_checklist_engine import launch_checklist_engine
from app.core.product_mode import product_mode_resolver
from app.core.product_state_layer import ProductState
from app.core.commercial_guardrail import commercial_guardrail


class CommercialReadinessEngine:
    def evaluate(self) -> dict:
        insight = execution_insight_layer.summarize()
        growth = feedback_loop_v2.metrics()
        checklist = launch_checklist_engine.evaluate()
        payment = config_center.payment()
        smtp = config_center.smtp()
        flags = config_center.feature_flags()

        sample_trust = data_trust_layer.evaluate(
            data={},
            source_type="mock" if flags.get("mock_ai_enabled") or flags.get("mock_crawler_enabled") else "estimated",
            freshness_score=1.0,
            confidence_score=max(float(growth.get("ai_decision_accuracy") or 0.0), 0.3),
        )

        system_maturity_score = round(
            (
                float(growth.get("execution_success_rate") or 0) * 0.35
                + float(growth.get("ai_decision_accuracy") or 0) * 0.35
                + float(sample_trust.trust_level) * 0.30
            ) * 100,
            2,
        )
        profit_reliability_score = round(float(growth.get("ai_decision_accuracy") or 0) * 100, 2)
        execution_stability_score = round(float(growth.get("execution_success_rate") or 0) * 100, 2)

        billing_safe = bool(payment.get("wechat_pay_app_id") and payment.get("wechat_pay_mch_id") and payment.get("wechat_pay_api_v3_key") and payment.get("wechat_pay_private_key"))
        email_ready = bool(smtp.get("host") and smtp.get("user") and smtp.get("password") and smtp.get("port"))
        commercial_ready = checklist["launch_allowed"] and billing_safe and email_ready and system_maturity_score >= 75
        scale_ready = commercial_ready and execution_stability_score >= 80 and profit_reliability_score >= 80

        if sample_trust.is_mock or not checklist["launch_allowed"]:
            risk_level = "high"
        elif system_maturity_score < 75:
            risk_level = "medium"
        else:
            risk_level = "low"

        product_mode = product_mode_resolver.resolve(commercial_ready=commercial_ready, scale_ready=scale_ready)
        guardrail = commercial_guardrail.evaluate(
            product_mode=product_mode,
            risk_level=risk_level,
            is_mock=sample_trust.is_mock,
            launch_allowed=checklist["launch_allowed"],
            production_lock=(product_mode == "production_mode"),
        )

        state = ProductState(
            system_stage="commercial_validation" if product_mode != "production_mode" else "production_ready",
            commercial_ready=commercial_ready,
            billing_ready=billing_safe,
            execution_ready=execution_stability_score >= 70,
            data_maturity="mock" if sample_trust.is_mock else "estimated" if sample_trust.source_type == "estimated" else "real",
            risk_status=risk_level,
        )

        blocking_factors = list(dict.fromkeys([
            *checklist["blocking_factors"],
            *(guardrail["blocking_factors"] or []),
            *(["支付还没有达到真实可收费状态"] if not billing_safe else []),
            *(["邮箱系统还没有达到稳定可用状态"] if not email_ready else []),
            *(["执行成功率还不足以支持规模化"] if execution_stability_score < 80 else []),
            *(["利润预测准确率还不足以支撑商业收费"] if profit_reliability_score < 80 else []),
        ]))

        return {
            "ready_to_launch": commercial_ready and guardrail["allowed"],
            "billing_safe": billing_safe,
            "scale_ready": scale_ready,
            "risk_level": risk_level,
            "blocking_factors": blocking_factors,
            "system_maturity_score": system_maturity_score,
            "profit_reliability_score": profit_reliability_score,
            "execution_stability_score": execution_stability_score,
            "product_mode": product_mode,
            "product_state": state.model_dump(mode="json"),
            "launch_allowed": checklist["launch_allowed"] and guardrail["allowed"],
            "launch_checklist": checklist,
            "guardrail": guardrail,
            "platform_integration_status": {
                "frontend_url": settings.frontend_url or settings.frontend_origin,
                "backend_url": settings.backend_url,
                "execution_adapter_ready": True,
                "public_api_ready": bool(settings.next_public_api_base_url and not settings.has_local_address(settings.next_public_api_base_url)),
            },
            "commercial_readiness_score": system_maturity_score,
            "scale_recommendation": "现在只能做小范围演示 / beta 验证" if not scale_ready else "可以谨慎进入规模化阶段",
        }


commercial_readiness_engine = CommercialReadinessEngine()

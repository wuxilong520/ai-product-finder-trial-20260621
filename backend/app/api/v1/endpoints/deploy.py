from __future__ import annotations

from fastapi import APIRouter

from app.core.production_bootstrap_layer import production_bootstrap_layer


router = APIRouter()


@router.post("/deploy/production/check")
def deploy_production_check():
    status = production_bootstrap_layer.status()
    return {
        "ready_status": status["production_ready"],
        "blocking_items": status["blocking_items"],
        "recommendation": "先把 blocking_items 全部清掉，再切 production_mode" if status["blocking_items"] else "可以切换到 production_mode",
        "product_mode": status["product_mode"],
        "system_bootstrap_status": status["system_bootstrap_status"],
    }

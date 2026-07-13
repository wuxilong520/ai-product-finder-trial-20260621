import asyncio

from fastapi import APIRouter, Depends, status
from fastapi import Query
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.market import MarketAnalyzeRequest, MarketAnalyzeResponse, MarketConnectRequest
from app.services.sync_runtime_service import sync_runtime_service
from app.services.task_controller import task_controller
from app.sync.execution_bridge import execution_bridge


router = APIRouter()


@router.post("/market/analyze", response_model=MarketAnalyzeResponse)
def analyze_market_keyword(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        task = task_controller.submit_task(
            db,
            job_type="market",
            job_key=f"market:{payload.keyword.strip()}",
            payload={"keyword": payload.keyword, "region": payload.region, "category": payload.category},
            auth_context=auth_context,
            runner_factory=lambda task_id, task_db: lambda: execution_bridge.execute(
                task_db,
                task_id=task_id,
                job_type="market",
                payload={
                    "keyword": payload.keyword,
                    "region": payload.region,
                    "category": payload.category,
                    "workspace_id": auth_context.workspace_id,
                    "user_id": auth_context.user_id,
                },
            ),
        )
        result_wrapper = sync_runtime_service.get_task_result(task["task_id"])
        if not result_wrapper:
            result_wrapper = asyncio.run(sync_runtime_service.wait_for_result(task["task_id"], timeout=15))
        if not result_wrapper or result_wrapper.get("status") != "success":
            return error_response("MARKET_ANALYZE_PENDING", "市场分析任务仍在执行，请稍后重试。", "market", status.HTTP_202_ACCEPTED)
        result = result_wrapper["result"]
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_ANALYZE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)


@router.post("/market/intelligence", response_model=MarketAnalyzeResponse)
def market_intelligence(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.analyze_keyword(
            db,
            payload.keyword,
            region=payload.region,
            category=payload.category,
            user_id=auth_context.user_id,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_INTELLIGENCE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)


@router.post("/market/radar", response_model=MarketAnalyzeResponse)
def market_radar(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.analyze_keyword(
            db,
            payload.keyword,
            region=payload.region,
            category=payload.category,
            user_id=auth_context.user_id,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_RADAR_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return MarketAnalyzeResponse(**result)


@router.get("/market/reality/report")
def market_reality_report(
    keyword: str = Query(..., min_length=1),
    region: str = Query(default="global"),
    category: str | None = Query(default=None),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del db, auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.reality_report(
            keyword=keyword,
            region=region,
            category=category,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_REALITY_REPORT_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


@router.get("/market/radar/status")
def market_radar_status(
    keyword: str = Query(..., min_length=1),
    region: str = Query(default="US"),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.reality_report(
            keyword=keyword,
            region=region,
            category=None,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_RADAR_STATUS_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


@router.post("/market/v3/analyze")
def market_v3_analyze(
    payload: MarketAnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        result = market_intelligence_engine.analyze_v3(
            db,
            payload.keyword,
            region=payload.region,
            category=payload.category,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_V3_ANALYZE_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


@router.get("/market/connections")
def market_connections(
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        from app.core.commercial_data_connection_engine import commercial_data_connection_engine

        return commercial_data_connection_engine.list_connections(db, user_id=auth_context.user_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_CONNECTIONS_FAILED", str(exc), "market_connection", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/market/connect/shopify")
def connect_shopify_market(
    payload: MarketConnectRequest,
    auth_context=Depends(get_request_context),
):
    try:
        from app.core.commercial_data_connection_engine import commercial_data_connection_engine

        return commercial_data_connection_engine.start_shopify_connection(
            user_id=auth_context.user_id,
            workspace_id=auth_context.workspace_id,
            shop_domain=payload.shop_domain,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SHOPIFY_CONNECT_START_FAILED", str(exc), "oauth", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/market/connect/shopify/callback")
async def connect_shopify_market_callback(
    code: str = Query(..., min_length=1),
    shop: str = Query(..., min_length=3),
    state: str = Query(..., min_length=8),
    hmac: str | None = Query(default=None),
    db: Session = Depends(db_session),
):
    try:
        from app.core.commercial_data_connection_engine import commercial_data_connection_engine

        return await commercial_data_connection_engine.complete_shopify_connection(
            db,
            code=code,
            shop=shop,
            state=state,
            hmac_value=hmac,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SHOPIFY_CONNECT_CALLBACK_FAILED", str(exc), "oauth", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/market/commercial-report")
def market_commercial_report(
    keyword: str = Query(..., min_length=1),
    region: str = Query(default="US"),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        from app.core.commercial_data_connection_engine import commercial_data_connection_engine

        return commercial_data_connection_engine.commercial_report(
            db,
            user_id=auth_context.user_id,
            keyword=keyword,
            region=region,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_COMMERCIAL_REPORT_FAILED", str(exc), "market_connection", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/market/commercial-reality/report")
def market_commercial_reality_report(
    keyword: str = Query(..., min_length=1),
    region: str = Query(default="US"),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        from app.services.market_intelligence_engine import market_intelligence_engine

        return market_intelligence_engine.commercial_reality_report(
            db=db,
            keyword=keyword,
            region=region,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_COMMERCIAL_REALITY_REPORT_FAILED", str(exc), "market", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/market/connections/{platform}")
def delete_market_connection(
    platform: str,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        from app.core.commercial_data_connection_engine import commercial_data_connection_engine

        return commercial_data_connection_engine.revoke_connection(db, user_id=auth_context.user_id, platform=platform)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("MARKET_CONNECTION_DELETE_FAILED", str(exc), "market_connection", status.HTTP_500_INTERNAL_SERVER_ERROR)

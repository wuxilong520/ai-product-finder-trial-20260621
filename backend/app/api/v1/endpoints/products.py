from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.product import (
    AnalyzeRequest,
    AnalyzeResponse,
    CrawlRequest,
    CrawlResponse,
    ProductIntelligenceEngineResponse,
    ProductBatchDeleteRequest,
    ProductBatchDeleteResponse,
    PublicProductExtractBlocked,
    PublicProductExtractRequest,
    PublicProductExtractResponse,
    ProductListResponse,
    ProductRead,
)
from app.services.product_intelligence_engine import product_intelligence_engine
from app.services.product import product_service
from app.services.product_extractor import extract_public_product_page
from app.services.task_status import task_status_service


router = APIRouter()


def _accepted_task_response(*, task_id: int, message: str):
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "success": True,
            "status": "pending",
            "task_id": task_id,
            "message": message,
        },
    )


@router.post(
    "/extract",
    response_model=PublicProductExtractResponse | PublicProductExtractBlocked,
)
async def extract_public_product(payload: PublicProductExtractRequest):
    try:
        result = await extract_public_product_page(payload.url)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PUBLIC_EXTRACT_FAILED", str(exc), "scrape", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_product(
    payload: CrawlRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = await product_service.crawl_and_save(db, payload.url, auth_context.user_id, workspace_id=auth_context.workspace_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("REAL_SCRAPE_FAILED", str(exc), "scrape", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return CrawlResponse(**result.model_dump())


@router.post("/analyze")
def analyze_product(
    payload: AnalyzeRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        task = product_service.submit_analyze_task(
            db=db,
            payload=payload,
            auth_context=auth_context,
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PRODUCT_ANALYZE_SUBMIT_FAILED", str(exc), "task", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return _accepted_task_response(task_id=task["task_id"], message="商品分析正在后台执行，请稍后查看任务结果。")


@router.get("", response_model=ProductListResponse)
def list_products(
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    items, total = product_service.list_products(db, search, skip, limit, workspace_id=auth_context.workspace_id)
    return ProductListResponse(items=[ProductRead.model_validate(item) for item in items], total=total)


@router.delete("/batch-delete", response_model=ProductBatchDeleteResponse)
def batch_delete_products(
    payload: ProductBatchDeleteRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    deleted_ids = product_service.batch_delete_products(db, payload.product_ids, workspace_id=auth_context.workspace_id)
    if not deleted_ids:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return ProductBatchDeleteResponse(ok=True, deleted_ids=deleted_ids)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    product = product_service.get_product(db, product_id, workspace_id=auth_context.workspace_id)
    if not product:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return ProductRead.model_validate(product)


@router.get("/{product_id}/intelligence", response_model=ProductIntelligenceEngineResponse)
def get_product_intelligence(
    product_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        product = product_service.get_product(db, product_id, workspace_id=auth_context.workspace_id)
        if not product:
            return error_response("PRODUCT_NOT_FOUND", "商品不存在或不属于当前工作区", "db", status.HTTP_404_NOT_FOUND)
        payload = product_intelligence_engine.get_or_create_intelligence(db, product_id, workspace_id=auth_context.workspace_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PRODUCT_INTELLIGENCE_FAILED", "商品情报生成失败，请稍后重试", "intelligence", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return ProductIntelligenceEngineResponse(**payload)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    ok = product_service.delete_product(db, product_id, workspace_id=auth_context.workspace_id)
    if not ok:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return {"ok": True}

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
import asyncio

from app.api.deps import db_session, get_current_user
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
    current_user=Depends(get_current_user),
):
    try:
        result = await product_service.crawl_and_save(db, payload.url, current_user.id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("REAL_SCRAPE_FAILED", str(exc), "scrape", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return CrawlResponse(**result.model_dump())


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_product(
    payload: AnalyzeRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    asyncio.run(task_status_service.update("analyze", "pending", "分析任务已创建", {"product_id": payload.product_id, "title": payload.title}))
    asyncio.run(task_status_service.update("analyze", "running", "正在调用 AI 分析", {"product_id": payload.product_id, "title": payload.title}))
    try:
        product, analysis, intelligence = product_service.analyze_product(db, payload, current_user.id)
    except AppError as exc:
        asyncio.run(
            task_status_service.update(
                "analyze",
                "error",
                "分析失败",
                {"product_id": payload.product_id, "title": payload.title, "stage": exc.stage},
                exc.message,
            )
        )
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        asyncio.run(
            task_status_service.update(
                "analyze",
                "error",
                "分析失败",
                {"product_id": payload.product_id, "title": payload.title},
                str(exc),
            )
        )
        return error_response("AI_CALL_FAILED", str(exc), "ai", status.HTTP_502_BAD_GATEWAY)
    asyncio.run(
        task_status_service.update(
            "analyze",
            "success",
            "分析完成",
            {"product_id": product.id, "title": product.title},
        )
    )
    return AnalyzeResponse(product=ProductRead.model_validate(product), analysis=analysis, intelligence=intelligence)


@router.get("", response_model=ProductListResponse)
def list_products(
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    items, total = product_service.list_products(db, search, skip, limit)
    return ProductListResponse(items=[ProductRead.model_validate(item) for item in items], total=total)


@router.delete("/batch-delete", response_model=ProductBatchDeleteResponse)
def batch_delete_products(
    payload: ProductBatchDeleteRequest,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    deleted_ids = product_service.batch_delete_products(db, payload.product_ids)
    if not deleted_ids:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return ProductBatchDeleteResponse(ok=True, deleted_ids=deleted_ids)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    product = product_service.get_product(db, product_id)
    if not product:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return ProductRead.model_validate(product)


@router.get("/{product_id}/intelligence", response_model=ProductIntelligenceEngineResponse)
def get_product_intelligence(
    product_id: int,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    try:
        payload = product_intelligence_engine.get_or_create_intelligence(db, product_id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("PRODUCT_INTELLIGENCE_FAILED", str(exc), "intelligence", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return ProductIntelligenceEngineResponse(**payload)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    ok = product_service.delete_product(db, product_id)
    if not ok:
        return error_response("PRODUCT_NOT_FOUND", "商品不存在", "db", status.HTTP_404_NOT_FOUND)
    return {"ok": True}

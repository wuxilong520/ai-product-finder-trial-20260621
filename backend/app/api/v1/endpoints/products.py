from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError, error_response
from app.schemas.product import (
    AnalyzeRequest,
    AnalyzeResponse,
    CrawlRequest,
    CrawlResponse,
    PublicProductExtractBlocked,
    PublicProductExtractRequest,
    PublicProductExtractResponse,
    ProductListResponse,
    ProductRead,
)
from app.services.product import product_service
from app.services.product_extractor import extract_public_product_page


router = APIRouter()


@router.post(
    "/extract",
    response_model=PublicProductExtractResponse | PublicProductExtractBlocked,
)
async def extract_public_product(payload: PublicProductExtractRequest):
    result = await extract_public_product_page(payload.url)
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
    try:
        product, analysis, intelligence = product_service.analyze_product(db, payload, current_user.id)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("AI_CALL_FAILED", str(exc), "ai", status.HTTP_502_BAD_GATEWAY)
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


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return ProductRead.model_validate(product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(db_session),
    current_user=Depends(get_current_user),
):
    ok = product_service.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return {"ok": True}

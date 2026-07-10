from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.core.supply_intelligence_engine import SupplyQuery, supply_intelligence_engine
from app.schemas.supplier import SupplierMatchRequest, SupplierMatchResponse
from app.services.browser_import_service import BrowserImportPayload, browser_import_service
from app.services.supply_import_service import supply_import_service


router = APIRouter()


@router.post("/supply/intelligence", response_model=SupplierMatchResponse)
def supply_intelligence(
    payload: SupplierMatchRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        result = supply_intelligence_engine.analyze(
            db,
            SupplyQuery(
                keyword=payload.keyword,
                category=payload.category,
                target_market=payload.target_market,
                expected_price=payload.expected_price,
                quantity=payload.quantity,
            ),
        )
        suppliers = [
            {
                "supplier_name": item.get("name"),
                "platform": item.get("platform"),
                "supplier_title": item.get("product_title"),
                "supplier_url": item.get("product_url") or item.get("search_url") or "",
                "supplier_price": item.get("price_mid"),
                "currency": item.get("currency"),
                "match_score": item.get("market_match", 0),
                "availability": "available" if not item.get("is_mock") else "mock",
                "moq": item.get("min_order_quantity"),
                "supplier_score": item.get("supplier_score"),
                "supplier_level": item.get("supplier_level"),
                "supplier_confidence": item.get("supplier_confidence"),
                "profit_estimate": item.get("estimated_profit"),
                "risk_flags": item.get("risk_flags", []),
                "data_source": item.get("data_source"),
                "source_type": item.get("source_type"),
                "risk_level": "high" if "high_moq" in item.get("risk_flags", []) or "supplier_unverified" in item.get("risk_flags", []) else "medium" if item.get("risk_flags") else "low",
                "supplier_type": item.get("supplier_type"),
                "location": item.get("location"),
                "certification": item.get("certification"),
                "delivery_time": item.get("delivery_time"),
                "price_change": item.get("price_change"),
                "stock_change": item.get("stock_change"),
                "procurement_recommendation": result.get("procurement_recommendation", {}).get("decision"),
            }
            for item in result.get("suppliers", [])
        ]
        return SupplierMatchResponse(
            suppliers=suppliers,
            supplier_score=result.get("supplier_score"),
            supplier_confidence=result.get("supplier_confidence"),
            confidence=result.get("confidence"),
            source_type=result.get("data_source"),
            risk_level="high" if any(flag in {"high_moq", "supplier_unverified", "missing_certification"} for flag in result.get("risk_flags", [])) else "medium" if result.get("risk_flags") else "low",
            risk_flags=result.get("risk_flags", []),
            cost_estimate=result.get("cost_estimate"),
            profit_preview=result.get("profit_preview"),
            procurement_recommendation=result.get("procurement_recommendation"),
            is_mock=result.get("is_mock"),
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_INTELLIGENCE_FAILED", str(exc), "supply", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/supply/browser/import")
def browser_import_supply(
    payload: BrowserImportPayload,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        return browser_import_service.import_record(db, payload)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_BROWSER_IMPORT_FAILED", str(exc), "supply_import", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/supply/import")
async def import_supply_file(
    request: Request,
    file: UploadFile | None = File(default=None),
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    del auth_context
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
            records = body.get("records") if isinstance(body, dict) else body
            if not isinstance(records, list):
                return error_response("SUPPLY_IMPORT_INVALID", "JSON 导入必须传 records 数组。", "supply_import", status.HTTP_400_BAD_REQUEST)
            source_type = str((body or {}).get("source_type") or "manual_input")
            return supply_import_service.import_records(db, records=records, source_type=source_type)

        if not file:
            return error_response("SUPPLY_IMPORT_MISSING_FILE", "没有收到导入文件。", "supply_import", status.HTTP_400_BAD_REQUEST)
        raw = await file.read()
        records = supply_import_service.parse_upload(filename=file.filename or "upload.csv", content=raw)
        source_type = "csv_import"
        lower_name = (file.filename or "").lower()
        if lower_name.endswith(".json"):
            source_type = "manual_input"
        elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
            source_type = "csv_import"
        return supply_import_service.import_records(db, records=records, source_type=source_type)
    except ValueError as exc:
        return error_response("SUPPLY_IMPORT_INVALID", str(exc), "supply_import", status.HTTP_400_BAD_REQUEST)
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("SUPPLY_IMPORT_FAILED", str(exc), "supply_import", status.HTTP_500_INTERNAL_SERVER_ERROR)

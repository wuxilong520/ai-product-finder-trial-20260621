from fastapi import APIRouter

from app.schemas.skeleton_v1 import ApiEnvelope, ListingV1Request
from app.services.listing_service import listing_service


router = APIRouter()


@router.post("/listing", response_model=ApiEnvelope)
def create_listing(payload: ListingV1Request):
    result = listing_service.build_listing(
        keyword=payload.keyword,
        market=payload.market,
        channel=payload.channel,
    )
    return ApiEnvelope(
        data=result,
        meta={
            "version": "shanghang-ai-v1",
            "ai_engine": "mock_ai_engine",
            "channel": payload.channel,
        },
    )

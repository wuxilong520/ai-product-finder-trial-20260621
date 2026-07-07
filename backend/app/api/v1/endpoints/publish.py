from fastapi import APIRouter

from app.schemas.skeleton_v1 import ApiEnvelope, PublishV1Request
from app.services.publish_service import publish_service


router = APIRouter()


@router.post("/publish", response_model=ApiEnvelope)
def publish_listing(payload: PublishV1Request):
    result = publish_service.publish(
        keyword=payload.keyword,
        market=payload.market,
        channel=payload.channel,
        shop_domain=payload.shop_domain,
        oauth_code=payload.oauth_code,
    )
    return ApiEnvelope(
        data=result,
        meta={
            "version": "shanghang-ai-v1",
            "channel": payload.channel,
            "oauth_connected": bool(result.get("oauth", {}).get("connected")),
        },
    )

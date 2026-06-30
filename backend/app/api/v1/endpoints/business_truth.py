from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_request_context
from app.core.runtime import AppError, error_response
from app.schemas.business_truth import BusinessTruthRecommendRequest, BusinessTruthRecommendResponse
from app.services.decision_truth_wrapper import decision_truth_wrapper


router = APIRouter()


@router.post("/business-truth/recommend", response_model=BusinessTruthRecommendResponse)
def recommend_business_truth(
    payload: BusinessTruthRecommendRequest,
    db: Session = Depends(db_session),
    auth_context=Depends(get_request_context),
):
    try:
        result = decision_truth_wrapper.recommend(
            db,
            payload.product_id,
            task_input={
                "user_id": auth_context.user_id,
                "workspace_id": auth_context.workspace_id,
                "api_key_id": auth_context.api_key_id,
            },
        )
    except AppError as exc:
        return error_response(exc.error_code, exc.message, exc.stage, exc.status_code)
    except Exception as exc:
        return error_response("BUSINESS_TRUTH_FAILED", str(exc), "truth", status.HTTP_500_INTERNAL_SERVER_ERROR)
    return BusinessTruthRecommendResponse(**result)

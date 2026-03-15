from fastapi import APIRouter, Depends

from app.api.schemas import RetentionStatusResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.billing_retention import build_retention_status
from app.services.subscription_plans import get_effective_subscription_plan

router = APIRouter(prefix="/api/v1/me/retention", tags=["Billing"])


@router.get(
    "/status",
    summary="Get retention status and suggested actions",
    description="Returns churn-risk category and recommended retention actions for current user.",
    response_model=RetentionStatusResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def get_retention_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> RetentionStatusResponse:
    plan = get_effective_subscription_plan(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        role=current_user.role,
    )
    return build_retention_status(subscription_plan=plan)

from fastapi import APIRouter, Depends

from app.api.schemas import DataExportJobResponse, DataExportRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.data_export import start_data_export_job

router = APIRouter(prefix="/api/v1/me/data-export", tags=["Settings"])


@router.post(
    "",
    summary="Request user data export",
    description="Starts asynchronous export job for current user data.",
    response_model=DataExportJobResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
    },
)
async def request_data_export(
    payload: DataExportRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DataExportJobResponse:
    return start_data_export_job(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        export_format=payload.format,
    )

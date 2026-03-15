from fastapi import APIRouter, Depends

from app.api.schemas import DataExportJobResponse, DataExportJobStatusResponse, DataExportRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.data_export import get_data_export_job_for_user, start_data_export_job

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


@router.get(
    "/{job_id}",
    summary="Get export job status",
    description="Returns export job status for the authenticated user.",
    response_model=DataExportJobStatusResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        404: {"description": "Export job not found."},
    },
)
async def get_data_export_status(
    job_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DataExportJobStatusResponse:
    job = get_data_export_job_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        job_id=job_id,
    )
    if job is None:
        raise AppError(
            status_code=404,
            code="memory.not_found",
            message="Export job not found.",
        )
    return job

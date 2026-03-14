from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status

from app.api.schemas import AttachmentResponse
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.attachments import (
    ALLOWED_ATTACHMENT_CONTENT_TYPES,
    create_attachment,
)

router = APIRouter(prefix="/api/v1", tags=["Attachments"])


@router.post(
    "/attachments",
    summary="Upload receipt photo attachment",
    description="Uploads receipt image, runs OCR extraction, and returns memory proposal plus signed URL.",
    response_model=AttachmentResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Unsupported attachment type or validation error."},
    },
)
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AttachmentResponse:
    if file.content_type not in ALLOWED_ATTACHMENT_CONTENT_TYPES:
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="storage.unsupported_file_type",
            message="Only receipt photo images are supported.",
            details={"allowed_content_types": sorted(ALLOWED_ATTACHMENT_CONTENT_TYPES)},
        )
    content = await file.read()
    record = create_attachment(
        file_name=file.filename or "receipt.jpg",
        file_type=file.content_type or "image/jpeg",
        content=content,
        user=current_user,
    )
    return AttachmentResponse(
        id=record.id,
        file_url=record.signed_url,
        file_type=record.file_type,
        status=record.status,  # type: ignore[arg-type]
        ocr_status=record.ocr_status,  # type: ignore[arg-type]
        ocr_text_preview=record.ocr_text_preview,
        error_code=record.error_code,
        memory_proposal=record.memory_proposal,
    )

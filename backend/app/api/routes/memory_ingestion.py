from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from starlette import status

from app.api.schemas import MemoryProposalResponse, MemoryRecordResponse, SaveMemoryRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.api.routes.memories import _MEMORY_FIXTURES
from app.services.memory_ingestion import (
    extract_memory_proposal,
    missing_required_fields,
)
from app.services.semantic_cache import invalidate_user_cache

router = APIRouter(prefix="/api/v1", tags=["Voice", "Memory"])


@router.post(
    "/voice/memory",
    summary="Upload voice memory",
    description="Uploads an audio payload and returns extracted proposal plus clarification if required.",
    response_model=MemoryProposalResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def upload_voice_memory(
    audio: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MemoryProposalResponse:
    _ = current_user
    payload = await audio.read()
    transcript = payload.decode("utf-8", errors="ignore").strip()
    if not transcript:
        transcript = audio.filename or "voice memory"

    proposal = extract_memory_proposal(transcript)
    ai_state = "ready_to_confirm" if proposal.needs_confirmation else "needs_clarification"
    return MemoryProposalResponse(
        transcript=proposal.transcript,
        memory_type=proposal.memory_type,  # type: ignore[arg-type]
        structured_data=proposal.structured_data,
        clarification_questions=proposal.clarification_questions,
        missing_required_fields=proposal.missing_required_fields,
        needs_confirmation=proposal.needs_confirmation,
        ai_state=ai_state,  # type: ignore[arg-type]
        source_context="voice",
        confirmation_actions=["Confirm", "Modify", "Cancel"],
        editable_datetime=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


@router.post(
    "/memory",
    summary="Save confirmed memory",
    description="Persists memory only after explicit confirmation and required-field validation.",
    response_model=MemoryRecordResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error. Confirmation required or missing required fields."},
    },
)
async def save_memory(
    payload: SaveMemoryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MemoryRecordResponse:
    if not payload.confirmed:
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="memory.confirmation_required",
            message="Explicit confirmation is required before persistence.",
        )

    missing_fields = missing_required_fields(payload.memory_type, payload.structured_data)
    if missing_fields:
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="memory.missing_required_fields",
            message="Memory payload misses required fields.",
            details={"missing_required_fields": missing_fields},
        )

    record = {
        "id": str(uuid4()),
        "tenant_id": current_user.tenant_id,
        "user_id": current_user.user_id,
        "memory_type": payload.memory_type,
        "raw_text": payload.raw_text,
        "structured_data": payload.structured_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _MEMORY_FIXTURES.append(record)
    invalidate_user_cache(current_user.tenant_id, current_user.user_id)
    return MemoryRecordResponse(
        id=record["id"],
        memory_type=record["memory_type"],
        raw_text=record["raw_text"],
        structured_data=record["structured_data"],
        created_at=record["created_at"],
    )

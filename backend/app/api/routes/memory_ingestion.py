from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Request, UploadFile
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
from app.services.attachments import mark_attachment_persisted, validate_signed_attachment_url
from app.core.llmops import estimate_tokens_and_cost, plan_for_role, record_ai_usage
from app.services.ai_safety import enforce_input_safety

router = APIRouter(prefix="/api/v1", tags=["Voice", "Memory"])


@router.post(
    "/voice/memory",
    summary="Upload voice memory",
    description="Uploads an audio payload and returns extracted proposal plus clarification if required.",
    response_model=MemoryProposalResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def upload_voice_memory(
    request: Request,
    audio: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MemoryProposalResponse:
    _ = current_user
    payload = await audio.read()
    transcript = payload.decode("utf-8", errors="ignore").strip()
    if not transcript:
        transcript = audio.filename or "voice memory"
    session_id = request.headers.get("x-session-id", "voice-memory")
    transcript = enforce_input_safety(
        text=transcript,
        path="/api/v1/voice/memory",
        session_id=session_id,
    )

    proposal = extract_memory_proposal(transcript)
    output_text = (
        proposal.memory_type
        + "|"
        + str(proposal.structured_data)
        + "|"
        + "|".join(proposal.clarification_questions)
    )
    token_in, token_out, estimated_cost = estimate_tokens_and_cost(
        input_text=proposal.transcript,
        output_text=output_text,
    )
    record_ai_usage(
        use_case="memory_extraction",
        provider="openai",
        model_id="gpt-4o-mini",
        model_version="mvp-v1",
        prompt_version="memory_extraction_v1",
        user_plan=plan_for_role(current_user.role),
        user_id=current_user.user_id,
        token_in=token_in,
        token_out=token_out,
        estimated_cost=estimated_cost,
    )

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
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MemoryRecordResponse:
    session_id = request.headers.get("x-session-id", "save-memory")
    payload.raw_text = enforce_input_safety(
        text=payload.raw_text,
        path="/api/v1/memory",
        session_id=session_id,
    )
    _ = enforce_input_safety(
        text=str(payload.structured_data),
        path="/api/v1/memory",
        session_id=session_id,
    )
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

    attachment_url = payload.structured_data.get("attachment_url")
    if attachment_url is not None:
        if not isinstance(attachment_url, str):
            raise AppError(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="memory.validation_failed",
                message="attachment_url must be a string.",
            )
        record = validate_signed_attachment_url(attachment_url, current_user)
        if record is None:
            raise AppError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="auth.forbidden",
                message="Attachment signed URL is not authorized for this user.",
            )
        try:
            mark_attachment_persisted(record)
        except ValueError:
            raise AppError(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="attachment.not_ready_for_persistence",
                message="Attachment is not in a persistable lifecycle state.",
            ) from None
        payload.structured_data["attachment_id"] = record.id

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

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Request, UploadFile
from starlette import status

from app.api.schemas import MemoryProposalResponse, MemoryRecordResponse, SaveMemoryRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.core.settings import get_settings
from app.repositories.memory_repository import insert_memory_record
from app.services.memory_ingestion import (
    extract_memory_proposal,
    missing_required_fields,
)
from app.services.semantic_cache import invalidate_user_cache
from app.services.attachments import mark_attachment_persisted, validate_signed_attachment_url
from app.services.time_normalization import normalize_relative_when_value
from app.core.llmops import estimate_tokens_and_cost, plan_for_role, record_ai_usage
from app.core.idempotency import (
    build_payload_hash,
    get_idempotency_record,
    save_idempotency_record,
)
from app.services.ai_safety import enforce_input_safety
from app.services.audio_upload import read_and_validate_audio_upload
from app.services.embedding_generation import generate_and_store_embedding_for_memory
from app.services.ai_execution_mode import resolve_transcription_execution_mode
from app.services.prompts.memory_extraction_prompt import MEMORY_EXTRACTION_PROMPT_VERSION
from app.services.whisper_transcription import transcribe_audio_with_whisper_by_mode

router = APIRouter(prefix="/api/v1", tags=["Voice", "Memory"])


def _read_clarification_turn(raw_value: str | None) -> int:
    if raw_value is None:
        return 1
    try:
        parsed = int(raw_value.strip())
    except ValueError:
        return 1
    if parsed <= 0:
        return 1
    return parsed


@router.post(
    "/voice/memory",
    summary="Upload voice memory",
    description="Uploads an audio payload and returns extracted proposal plus clarification if required.",
    response_model=MemoryProposalResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Unsupported audio type, empty payload, or invalid upload payload."},
        503: {"description": "Transcription provider unavailable after retry attempts."},
    },
)
async def upload_voice_memory(
    request: Request,
    audio: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MemoryProposalResponse:
    _ = current_user
    settings = get_settings()
    payload = await read_and_validate_audio_upload(audio)
    extraction_start = perf_counter()
    execution_mode = resolve_transcription_execution_mode(
        payload_size_bytes=len(payload),
        forced_mode=request.headers.get("x-ai-execution-mode"),
        background_min_bytes=settings.voice_memory_background_min_bytes,
    )
    transcript = await transcribe_audio_with_whisper_by_mode(
        payload=payload,
        file_name=audio.filename,
        content_type=audio.content_type,
        execution_mode=execution_mode,
    )
    session_id = request.headers.get("x-session-id", "voice-memory")
    transcript = enforce_input_safety(
        text=transcript,
        path="/api/v1/voice/memory",
        session_id=session_id,
    )
    clarification_turn = _read_clarification_turn(request.headers.get("x-clarification-turn"))

    proposal = extract_memory_proposal(
        transcript,
        clarification_turn=clarification_turn,
        max_clarification_turns=settings.memory_clarification_max_turns,
    )
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
        prompt_version=MEMORY_EXTRACTION_PROMPT_VERSION,
        user_plan=plan_for_role(current_user.role),
        user_id=current_user.user_id,
        token_in=token_in,
        token_out=token_out,
        estimated_cost=estimated_cost,
        latency_ms=max((perf_counter() - extraction_start) * 1000, 0.001),
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
    idempotency_key = request.headers.get("Idempotency-Key", "").strip()
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
    when_value = payload.structured_data.get("when")
    if isinstance(when_value, str):
        normalized_when = normalize_relative_when_value(when_value)
        if normalized_when is not None:
            payload.structured_data["when"] = normalized_when
    payload_hash = build_payload_hash(payload.model_dump())
    if idempotency_key:
        existing = get_idempotency_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            path="/api/v1/memory",
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            if existing.payload_hash != payload_hash:
                raise AppError(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    code="memory.validation_failed",
                    message="Idempotency-Key reused with different payload.",
                )
            return MemoryRecordResponse(**existing.response_payload)

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
        "structured_data_schema_version": payload.structured_data_schema_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    insert_memory_record(record)
    generate_and_store_embedding_for_memory(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        memory_id=record["id"],
        raw_text=record["raw_text"],
        structured_data=record["structured_data"],
    )
    invalidate_user_cache(current_user.tenant_id, current_user.user_id)
    response_payload = {
        "id": record["id"],
        "memory_type": record["memory_type"],
        "raw_text": record["raw_text"],
        "structured_data": record["structured_data"],
        "structured_data_schema_version": record["structured_data_schema_version"],
        "created_at": record["created_at"],
    }
    if idempotency_key:
        save_idempotency_record(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            path="/api/v1/memory",
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            response_payload=response_payload,
        )
    return MemoryRecordResponse(
        id=response_payload["id"],
        memory_type=response_payload["memory_type"],
        raw_text=response_payload["raw_text"],
        structured_data=response_payload["structured_data"],
        structured_data_schema_version=response_payload["structured_data_schema_version"],
        created_at=response_payload["created_at"],
    )

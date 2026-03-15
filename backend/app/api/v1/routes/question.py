import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import StreamingResponse
from time import perf_counter
from starlette import status

from app.api.schemas import QuestionResponse, TextQuestionRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.repositories.memory_repository import list_memories_for_user
from app.services.question_engine import (
    compute_structured_result,
    format_answer_from_structured_result,
)
from app.services.semantic_cache import (
    extract_filter_context,
    get_cached_answer,
    put_cached_answer,
)
from app.services.user_preferences import get_preferred_language
from app.core.llmops import estimate_tokens_and_cost, plan_for_role, record_ai_usage
from app.services.ai_safety import enforce_input_safety, enforce_output_safety
from app.services.audio_upload import read_and_validate_audio_upload
from app.services.whisper_transcription import transcribe_audio_with_whisper

router = APIRouter(prefix="/api/v1", tags=["Voice"])


def _answer_question_from_text(
    *,
    question_text: str,
    path: str,
    session_id: str,
    current_user: AuthenticatedUser,
) -> QuestionResponse:
    question_text = enforce_input_safety(
        text=question_text,
        path=path,
        session_id=session_id,
    )
    scoped_memories = list_memories_for_user(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
    structured = compute_structured_result(question_text, scoped_memories)
    if structured.kind == "ambiguous_intent":
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="query.ambiguous_intent",
            message=structured.clarification_question or "Question is ambiguous.",
        )

    preferred_language = get_preferred_language(current_user.tenant_id, current_user.user_id)
    filter_context = extract_filter_context(question_text)
    context_signature = f"{structured.kind}|{','.join(sorted(structured.source_memory_ids))}"
    cached = None
    if structured.confidence in {"high", "medium"}:
        cached = get_cached_answer(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            question=question_text,
            language=preferred_language,
            filter_context=filter_context,
            context_signature=context_signature,
        )
    if cached is not None:
        return QuestionResponse(
            answer=cached.answer,
            confidence=cached.confidence,  # type: ignore[arg-type]
            source_memory_ids=cached.source_memory_ids,
        )

    answer_generation_start = perf_counter()
    answer = format_answer_from_structured_result(structured, preferred_language)
    enforce_output_safety(
        text=answer,
        path=path,
        session_id=session_id,
    )
    token_in, token_out, estimated_cost = estimate_tokens_and_cost(
        input_text=question_text,
        output_text=answer,
    )
    record_ai_usage(
        use_case="answer_generation",
        provider="openai",
        model_id="gpt-4o-mini",
        model_version="mvp-v1",
        prompt_version="answer_generation_v1",
        user_plan=plan_for_role(current_user.role),
        user_id=current_user.user_id,
        token_in=token_in,
        token_out=token_out,
        estimated_cost=estimated_cost,
        latency_ms=max((perf_counter() - answer_generation_start) * 1000, 0.001),
    )
    if structured.confidence in {"high", "medium"}:
        put_cached_answer(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            question=question_text,
            language=preferred_language,
            filter_context=filter_context,
            answer=answer,
            confidence=structured.confidence,
            source_memory_ids=structured.source_memory_ids,
            context_signature=context_signature,
        )
    return QuestionResponse(
        answer=answer,
        confidence=structured.confidence,  # type: ignore[arg-type]
        source_memory_ids=structured.source_memory_ids,
    )


def _sse_event(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=True)}\n\n"


def _iter_sse_answer(answer: QuestionResponse) -> Iterator[str]:
    words = answer.answer.split()
    if not words:
        yield _sse_event("chunk", {"text": ""})
    else:
        for index, token in enumerate(words):
            suffix = " " if index < len(words) - 1 else ""
            yield _sse_event("chunk", {"text": f"{token}{suffix}"})
    yield _sse_event(
        "done",
        {
            "confidence": answer.confidence,
            "source_memory_ids": answer.source_memory_ids,
        },
    )


@router.post(
    "/voice/question",
    summary="Upload voice question",
    description="Uploads a voice payload, transcribes it, and returns a database-first answer from stored memories.",
    response_model=QuestionResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Unsupported audio type, empty payload, or invalid upload payload."},
        503: {"description": "Transcription provider unavailable after retry attempts."},
    },
)
async def ask_voice_question(
    request: Request,
    audio: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> QuestionResponse:
    payload = await read_and_validate_audio_upload(audio)
    question_text = transcribe_audio_with_whisper(
        payload=payload,
        file_name=audio.filename,
        content_type=audio.content_type,
    )
    session_id = request.headers.get("x-session-id", "voice-question")
    return _answer_question_from_text(
        question_text=question_text,
        path="/api/v1/voice/question",
        session_id=session_id,
        current_user=current_user,
    )


@router.post(
    "/question",
    summary="Ask text question",
    description="Uses database-first deterministic aggregation and applies natural-language phrasing on top.",
    response_model=QuestionResponse,
    responses={401: {"description": "Unauthorized. Missing or invalid bearer token."}},
)
async def ask_text_question(
    payload: TextQuestionRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> QuestionResponse:
    session_id = request.headers.get("x-session-id", "question")
    return _answer_question_from_text(
        question_text=payload.question,
        path="/api/v1/question",
        session_id=session_id,
        current_user=current_user,
    )


@router.post(
    "/question/stream",
    summary="Ask text question with streaming response",
    description="Streams answer chunks and final metadata event over SSE.",
    responses={
        200: {
            "description": "SSE stream with chunk/done events.",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        },
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
        503: {"description": "Streaming unavailable. Client should fallback to /api/v1/question."},
    },
)
async def ask_text_question_stream(
    payload: TextQuestionRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    if request.headers.get("x-stream-disabled", "").strip().lower() in {"1", "true", "yes"}:
        raise AppError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="ai.provider_unavailable",
            message="Streaming unavailable. Fallback to /api/v1/question.",
            retryable=True,
        )
    session_id = request.headers.get("x-session-id", "question-stream")
    answer = _answer_question_from_text(
        question_text=payload.question,
        path="/api/v1/question/stream",
        session_id=session_id,
        current_user=current_user,
    )
    return StreamingResponse(
        _iter_sse_answer(answer),
        media_type="text/event-stream",
    )

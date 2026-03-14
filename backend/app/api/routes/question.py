from fastapi import APIRouter, Depends, Request
from starlette import status

from app.api.routes.memories import _MEMORY_FIXTURES
from app.api.schemas import QuestionResponse, TextQuestionRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
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

router = APIRouter(prefix="/api/v1", tags=["Voice"])


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
    payload.question = enforce_input_safety(
        text=payload.question,
        path="/api/v1/question",
        session_id=session_id,
    )
    scoped_memories = [
        item
        for item in _MEMORY_FIXTURES
        if item["user_id"] == current_user.user_id and item["tenant_id"] == current_user.tenant_id
    ]
    structured = compute_structured_result(payload.question, scoped_memories)
    if structured.kind == "ambiguous_intent":
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="query.ambiguous_intent",
            message=structured.clarification_question or "Question is ambiguous.",
        )

    preferred_language = get_preferred_language(current_user.tenant_id, current_user.user_id)
    filter_context = extract_filter_context(payload.question)
    context_signature = f"{structured.kind}|{','.join(sorted(structured.source_memory_ids))}"
    cached = None
    if structured.confidence in {"high", "medium"}:
        cached = get_cached_answer(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            question=payload.question,
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

    answer = format_answer_from_structured_result(structured, preferred_language)
    enforce_output_safety(
        text=answer,
        path="/api/v1/question",
        session_id=session_id,
    )
    token_in, token_out, estimated_cost = estimate_tokens_and_cost(
        input_text=payload.question,
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
    )
    if structured.confidence in {"high", "medium"}:
        put_cached_answer(
            tenant_id=current_user.tenant_id,
            user_id=current_user.user_id,
            question=payload.question,
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

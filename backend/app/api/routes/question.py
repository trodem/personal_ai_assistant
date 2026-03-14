from fastapi import APIRouter, Depends
from starlette import status

from app.api.routes.memories import _MEMORY_FIXTURES
from app.api.schemas import QuestionResponse, TextQuestionRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import AppError
from app.services.question_engine import (
    compute_structured_result,
    format_answer_from_structured_result,
)
from app.services.user_preferences import get_preferred_language

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
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> QuestionResponse:
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
    answer = format_answer_from_structured_result(structured, preferred_language)
    return QuestionResponse(
        answer=answer,
        confidence=structured.confidence,  # type: ignore[arg-type]
        source_memory_ids=structured.source_memory_ids,
    )

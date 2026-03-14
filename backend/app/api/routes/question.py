from fastapi import APIRouter, Depends

from app.api.routes.memories import _MEMORY_FIXTURES
from app.api.schemas import QuestionResponse, TextQuestionRequest
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.question_engine import (
    compute_structured_result,
    format_answer_from_structured_result,
)

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
    answer = format_answer_from_structured_result(structured)
    return QuestionResponse(
        answer=answer,
        confidence=structured.confidence,  # type: ignore[arg-type]
        source_memory_ids=structured.source_memory_ids,
    )

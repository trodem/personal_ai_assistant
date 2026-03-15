from fastapi import APIRouter, Depends, Request

from app.api.schemas import AcceptedResponse, AnswerFeedbackRequest
from app.core.analytics import emit_operational_event
from app.core.auth import AuthenticatedUser, get_current_user
from app.services.answer_feedback import submit_answer_feedback

router = APIRouter(prefix="/api/v1", tags=["Feedback"])


@router.post(
    "/feedback/answers",
    summary="Submit feedback for AI answer",
    description="Captures user feedback (`like` or `dislike`) for a generated answer.",
    response_model=AcceptedResponse,
    responses={
        401: {"description": "Unauthorized. Missing or invalid bearer token."},
        422: {"description": "Validation error."},
    },
)
async def submit_feedback_for_answer(
    payload: AnswerFeedbackRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AcceptedResponse:
    _ = submit_answer_feedback(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        answer_id=payload.answer_id,
        sentiment=payload.sentiment,
        reason=payload.reason,
        comment=payload.comment,
    )
    session_id = request.headers.get("x-session-id", "feedback-answer")
    emit_operational_event(
        event_name="answer_feedback_submitted",
        session_id=session_id,
        status_code=200,
        path="/api/v1/feedback/answers",
    )
    return AcceptedResponse(accepted=True)

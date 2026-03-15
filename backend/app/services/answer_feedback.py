from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class AnswerFeedbackRecord:
    id: str
    tenant_id: str
    user_id: str
    answer_id: str
    sentiment: str
    reason: str | None
    comment: str | None
    created_at: str


_FEEDBACK_LOCK = Lock()
_ANSWER_FEEDBACK_STORE: list[AnswerFeedbackRecord] = []


def submit_answer_feedback(
    *,
    tenant_id: str,
    user_id: str,
    answer_id: str,
    sentiment: str,
    reason: str | None,
    comment: str | None,
) -> AnswerFeedbackRecord:
    record = AnswerFeedbackRecord(
        id=str(uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        answer_id=answer_id,
        sentiment=sentiment,
        reason=reason,
        comment=comment,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    with _FEEDBACK_LOCK:
        _ANSWER_FEEDBACK_STORE.append(record)
    return record

from dataclasses import dataclass
import re

from starlette import status

from app.core.analytics import emit_operational_event
from app.core.errors import AppError

BLOCK_KEYWORDS = (
    "how to build a bomb",
    "make a bomb",
    "kill myself",
    "suicide method",
    "how to hack",
    "create malware",
)

REVIEW_KEYWORDS = (
    "passport number",
    "social security number",
    "ssn:",
)

WARN_KEYWORDS = (
    "idiot",
    "stupid",
    "hate you",
)

REDACTION_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "phone": re.compile(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b"),
    "national_id": re.compile(r"\b(?:[A-Z]{2}\d{6,}|[A-Z0-9]{9,12})\b"),
    "address": re.compile(
        r"\b\d{1,5}\s+[A-Za-z0-9.\- ]+\s(?:street|st|road|rd|avenue|ave|lane|ln|via|platz)\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class ModerationResult:
    decision: str
    reason: str


@dataclass(frozen=True)
class SanitizationResult:
    text: str
    changed: bool
    redactions: dict[str, int]


def moderate_text(text: str) -> ModerationResult:
    lowered = text.lower()
    for token in BLOCK_KEYWORDS:
        if token in lowered:
            return ModerationResult(decision="block", reason=f"blocked:{token}")
    for token in REVIEW_KEYWORDS:
        if token in lowered:
            return ModerationResult(decision="review", reason=f"review:{token}")
    for token in WARN_KEYWORDS:
        if token in lowered:
            return ModerationResult(decision="warn", reason=f"warn:{token}")
    return ModerationResult(decision="allow", reason="allow:clean")


def sanitize_text(text: str) -> SanitizationResult:
    output = text
    redactions: dict[str, int] = {}

    for key, pattern in REDACTION_PATTERNS.items():
        counter = 0

        def _replace(_: re.Match[str]) -> str:
            nonlocal counter
            counter += 1
            return f"[REDACTED_{key.upper()}_{counter}]"

        output = pattern.sub(_replace, output)
        if counter > 0:
            redactions[key] = counter

    return SanitizationResult(text=output, changed=output != text, redactions=redactions)


def enforce_input_safety(*, text: str, path: str, session_id: str) -> str:
    moderation = moderate_text(text)
    if moderation.decision == "block":
        emit_operational_event(
            event_name="moderation_blocked",
            session_id=session_id,
            status_code=status.HTTP_403_FORBIDDEN,
            path=path,
        )
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="moderation.blocked_content",
            message="Request cannot be processed due to safety policy.",
            details={"reason": moderation.reason},
        )
    if moderation.decision == "review":
        emit_operational_event(
            event_name="moderation_review_flagged",
            session_id=session_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            path=path,
        )
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="moderation.review_required",
            message="Request requires manual safety review.",
            details={"reason": moderation.reason},
        )
    if moderation.decision == "warn":
        emit_operational_event(
            event_name="moderation_warned",
            session_id=session_id,
            status_code=status.HTTP_200_OK,
            path=path,
        )

    sanitized = sanitize_text(text)
    if sanitized.changed:
        emit_operational_event(
            event_name="prompt_sanitized",
            session_id=session_id,
            status_code=status.HTTP_200_OK,
            path=path,
        )
        emit_operational_event(
            event_name="privacy_redaction_applied",
            session_id=session_id,
            status_code=status.HTTP_200_OK,
            path=path,
        )
    return sanitized.text


def enforce_output_safety(*, text: str, path: str, session_id: str) -> None:
    moderation = moderate_text(text)
    if moderation.decision == "block":
        emit_operational_event(
            event_name="moderation_blocked",
            session_id=session_id,
            status_code=status.HTTP_403_FORBIDDEN,
            path=path,
        )
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="moderation.blocked_content",
            message="Response blocked by safety policy.",
            details={"reason": moderation.reason},
        )
    if moderation.decision == "review":
        emit_operational_event(
            event_name="moderation_review_flagged",
            session_id=session_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            path=path,
        )
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="moderation.review_required",
            message="Response requires manual safety review.",
            details={"reason": moderation.reason},
        )
    if moderation.decision == "warn":
        emit_operational_event(
            event_name="moderation_warned",
            session_id=session_id,
            status_code=status.HTTP_200_OK,
            path=path,
        )

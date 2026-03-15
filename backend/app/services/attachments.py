import base64
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.core.auth import AuthenticatedUser
from app.core.llmops import estimate_tokens_and_cost, plan_for_role, record_ai_usage
from app.core.settings import get_settings
from app.services.ai_safety import enforce_input_safety
from app.services.memory_ingestion import extract_memory_proposal

ALLOWED_ATTACHMENT_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
}


@dataclass
class AttachmentRecord:
    id: str
    tenant_id: str
    user_id: str
    file_type: str
    file_name: str
    status: str
    ocr_status: str
    ocr_text_preview: str
    signed_url: str
    error_code: str | None
    lifecycle_states: list[str]
    memory_proposal: dict[str, Any]


_ATTACHMENTS_BY_ID: dict[str, AttachmentRecord] = {}


def _secret() -> str:
    return get_settings().app_dev_jwt_secret


def _sign(value: str) -> str:
    digest = hmac.new(_secret().encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def build_signed_attachment_url(attachment_id: str, user: AuthenticatedUser, ttl_seconds: int = 900) -> str:
    expires = int(time.time()) + ttl_seconds
    payload = f"{attachment_id}:{user.user_id}:{user.tenant_id}:{expires}"
    signature = _sign(payload)
    return f"signed://attachment/{attachment_id}?expires={expires}&sig={signature}"


def _parse_signed_attachment_url(url: str) -> tuple[str, int, str]:
    if not url.startswith("signed://attachment/"):
        raise ValueError("Unsupported signed URL format.")
    path_part, query = url.split("?", maxsplit=1)
    attachment_id = path_part.rsplit("/", maxsplit=1)[1]
    parts = dict(part.split("=", maxsplit=1) for part in query.split("&") if "=" in part)
    expires = int(parts.get("expires", "0"))
    signature = parts.get("sig", "")
    return attachment_id, expires, signature


def validate_signed_attachment_url(url: str, user: AuthenticatedUser) -> AttachmentRecord | None:
    try:
        attachment_id, expires, signature = _parse_signed_attachment_url(url)
    except (ValueError, KeyError):
        return None
    if expires <= int(time.time()):
        return None
    payload = f"{attachment_id}:{user.user_id}:{user.tenant_id}:{expires}"
    expected = _sign(payload)
    if not hmac.compare_digest(signature, expected):
        return None
    record = _ATTACHMENTS_BY_ID.get(attachment_id)
    if record is None:
        return None
    if record.user_id != user.user_id or record.tenant_id != user.tenant_id:
        return None
    return record


def _fake_ocr_preview(file_name: str, content: bytes) -> str:
    extracted = content.decode("utf-8", errors="ignore").strip()
    if extracted:
        return extracted
    lowered_name = file_name.lower()
    if "bread" in lowered_name:
        return "I bought bread for 3 chf"
    return "Receipt total 12 CHF"


def create_attachment(
    *,
    file_name: str,
    file_type: str,
    content: bytes,
    user: AuthenticatedUser,
) -> AttachmentRecord:
    attachment_id = str(uuid4())
    lifecycle_states = ["uploaded", "ocr_processing"]
    status = "ocr_processing"
    ocr_status = "processing"

    fail_ocr = "fail-ocr" in file_name.lower() or b"FORCE_OCR_FAIL" in content
    if fail_ocr:
        status = "failed"
        ocr_status = "failed"
        lifecycle_states.append("failed")
        signed_url = build_signed_attachment_url(attachment_id, user)
        record = AttachmentRecord(
            id=attachment_id,
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            file_type=file_type,
            file_name=file_name,
            status=status,
            ocr_status=ocr_status,
            ocr_text_preview="",
            signed_url=signed_url,
            error_code="ocr.processing_failed",
            lifecycle_states=lifecycle_states,
            memory_proposal={},
        )
        _ATTACHMENTS_BY_ID[attachment_id] = record
        return record

    ocr_text_preview = _fake_ocr_preview(file_name, content)
    extraction_start = time.perf_counter()
    sanitized_preview = enforce_input_safety(
        text=ocr_text_preview,
        path="/api/v1/attachments",
        session_id=f"attachment-{user.user_id}",
    )
    proposal = extract_memory_proposal(sanitized_preview)
    output_text = (
        proposal.memory_type
        + "|"
        + str(proposal.structured_data)
        + "|"
        + "|".join(proposal.clarification_questions)
    )
    token_in, token_out, estimated_cost = estimate_tokens_and_cost(
        input_text=sanitized_preview,
        output_text=output_text,
    )
    record_ai_usage(
        use_case="receipt_ocr_extraction",
        provider="openai",
        model_id="gpt-4o-mini",
        model_version="mvp-v1",
        prompt_version="receipt_extraction_v1",
        user_plan=plan_for_role(user.role),
        user_id=user.user_id,
        token_in=token_in,
        token_out=token_out,
        estimated_cost=estimated_cost,
        latency_ms=max((time.perf_counter() - extraction_start) * 1000, 0.001),
    )
    status = "proposal_ready"
    ocr_status = "completed"
    lifecycle_states.append("proposal_ready")

    signed_url = build_signed_attachment_url(attachment_id, user)
    record = AttachmentRecord(
        id=attachment_id,
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        file_type=file_type,
        file_name=file_name,
        status=status,
        ocr_status=ocr_status,
        ocr_text_preview=ocr_text_preview,
        signed_url=signed_url,
        error_code=None,
        lifecycle_states=lifecycle_states,
        memory_proposal={
            "transcript": proposal.transcript,
            "memory_type": proposal.memory_type,
            "structured_data": proposal.structured_data,
            "clarification_questions": proposal.clarification_questions,
            "missing_required_fields": proposal.missing_required_fields,
            "needs_confirmation": proposal.needs_confirmation,
        },
    )
    _ATTACHMENTS_BY_ID[attachment_id] = record
    return record


def mark_attachment_persisted(record: AttachmentRecord) -> None:
    if record.status == "failed":
        raise ValueError("Attachment is in failed state.")
    if record.status != "proposal_ready":
        raise ValueError("Attachment is not ready for persistence.")
    record.status = "confirmed"
    record.lifecycle_states.append("confirmed")
    record.status = "persisted"
    record.lifecycle_states.append("persisted")


def get_attachment(attachment_id: str) -> AttachmentRecord | None:
    return _ATTACHMENTS_BY_ID.get(attachment_id)

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthStatusResponse(BaseModel):
    status: str


class MemoryRecordResponse(BaseModel):
    id: str
    memory_type: str
    raw_text: str
    structured_data: dict[str, Any]
    structured_data_schema_version: int = Field(default=1, ge=1)
    created_at: str
    ai_state: Literal["saved"] = "saved"

    model_config = ConfigDict(extra="forbid")


class MemoryListResponse(BaseModel):
    items: list[MemoryRecordResponse]


class DeleteMemoryResponse(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")


class MemoryProposalResponse(BaseModel):
    transcript: str
    memory_type: Literal["expense_event", "inventory_event", "loan_event", "note", "document"]
    structured_data: dict[str, Any]
    clarification_questions: list[str] = []
    missing_required_fields: list[str] = []
    needs_confirmation: bool
    ai_state: Literal["needs_clarification", "ready_to_confirm"]
    source_context: Literal["voice", "text", "receipt_ocr"] = "voice"
    confirmation_actions: list[Literal["Confirm", "Modify", "Cancel"]] = ["Confirm", "Modify", "Cancel"]
    editable_datetime: str

    model_config = ConfigDict(extra="forbid")


class SaveMemoryRequest(BaseModel):
    memory_type: Literal["expense_event", "inventory_event", "loan_event", "note", "document"]
    raw_text: str
    structured_data: dict[str, Any]
    structured_data_schema_version: int = Field(default=1, ge=1)
    confirmed: bool

    model_config = ConfigDict(extra="forbid")


class TextQuestionRequest(BaseModel):
    question: str

    model_config = ConfigDict(extra="forbid")


class QuestionResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    source_memory_ids: list[str]

    model_config = ConfigDict(extra="forbid")


class AnswerFeedbackRequest(BaseModel):
    answer_id: str
    sentiment: Literal["like", "dislike"]
    reason: str | None = None
    comment: str | None = None

    model_config = ConfigDict(extra="forbid")


class AcceptedResponse(BaseModel):
    accepted: bool

    model_config = ConfigDict(extra="forbid")


class AttachmentResponse(BaseModel):
    id: str
    file_url: str
    file_type: str
    status: Literal["uploaded", "ocr_processing", "proposal_ready", "confirmed", "persisted", "failed"]
    ocr_status: Literal["pending", "processing", "completed", "failed"]
    ocr_text_preview: str | None = None
    error_code: str | None = None
    memory_proposal: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class DashboardLatestMemoryResponse(BaseModel):
    id: str
    memory_type: str
    raw_text: str
    created_at: str

    model_config = ConfigDict(extra="forbid")


class DashboardResponse(BaseModel):
    total_memories: int
    memories_by_type: dict[str, int]
    latest_memory_events: list[DashboardLatestMemoryResponse]

    model_config = ConfigDict(extra="allow")


class AdminUserResponse(BaseModel):
    id: str
    role: str

    model_config = ConfigDict(extra="forbid")


class AdminUsersListResponse(BaseModel):
    items: list[AdminUserResponse]


class UpdateProfileRequest(BaseModel):
    preferred_language: Literal["en", "it", "de"]

    model_config = ConfigDict(extra="forbid")


class UserSettingsResponse(BaseModel):
    user_id: str
    email: str
    preferred_language: Literal["en", "it", "de"]
    auth_provider: Literal["password", "google", "apple", "mixed"]
    role: Literal["user", "admin", "author"]
    status: Literal["active", "suspended", "canceled"]
    mfa_enabled: bool
    subscription_plan: Literal["free", "premium"]
    billing_exempt: bool
    payment_methods_enabled: bool
    default_payment_method: dict[str, Any] | None = None
    notification_preferences: dict[str, bool]

    model_config = ConfigDict(extra="forbid")

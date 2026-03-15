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


class AuthorDashboardResponse(BaseModel):
    total_users: int
    users_by_role: dict[str, int]
    users_by_status: dict[str, int]
    users_by_plan: dict[str, int]
    active_authors: int

    model_config = ConfigDict(extra="allow")


class AdminUserResponse(BaseModel):
    id: str
    email: str
    role: Literal["user", "admin", "author"]
    status: Literal["active", "suspended", "canceled"]
    subscription_plan: Literal["free", "premium"]
    billing_exempt: bool

    model_config = ConfigDict(extra="forbid")


class AdminUsersListResponse(BaseModel):
    items: list[AdminUserResponse]


class UpdateUserStatusRequest(BaseModel):
    status: Literal["active", "suspended", "canceled"]

    model_config = ConfigDict(extra="forbid")


class UpdateUserRoleRequest(BaseModel):
    role: Literal["user", "admin"]

    model_config = ConfigDict(extra="forbid")


class UpdateProfileRequest(BaseModel):
    preferred_language: Literal["en", "it", "de"]

    model_config = ConfigDict(extra="forbid")


class UpdateSecurityRequest(BaseModel):
    action: Literal["change_email", "change_password", "enable_2fa", "disable_2fa", "verify_2fa"]
    email: str | None = None
    password: str | None = None
    totp_code: str | None = None

    model_config = ConfigDict(extra="forbid")


class NotificationPreferences(BaseModel):
    in_app: bool
    push: bool
    email: bool

    model_config = ConfigDict(extra="forbid")


class UpdateNotificationPreferencesRequest(BaseModel):
    preferences: NotificationPreferences

    model_config = ConfigDict(extra="forbid")


class InAppNotificationRecord(BaseModel):
    id: str
    event_type: Literal["security_event", "billing_event", "system_event"]
    title: str
    body: str
    read: bool
    created_at: str

    model_config = ConfigDict(extra="forbid")


class InAppNotificationsListResponse(BaseModel):
    items: list[InAppNotificationRecord]

    model_config = ConfigDict(extra="forbid")


class PaymentMethodRecord(BaseModel):
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool

    model_config = ConfigDict(extra="forbid")


class PaymentMethodsListResponse(BaseModel):
    items: list[PaymentMethodRecord]

    model_config = ConfigDict(extra="forbid")


class PaymentMethodSetupIntentResponse(BaseModel):
    client_secret: str

    model_config = ConfigDict(extra="forbid")


class UpdatedResponse(BaseModel):
    updated: bool

    model_config = ConfigDict(extra="forbid")


class ChangePlanRequest(BaseModel):
    plan: Literal["free", "premium"]

    model_config = ConfigDict(extra="forbid")


class CancelPreviewRequest(BaseModel):
    reason: Literal[
        "too_expensive",
        "low_value",
        "too_many_errors",
        "not_using_enough",
        "switched_alternative",
        "other",
    ]

    model_config = ConfigDict(extra="forbid")


class CancelPreviewResponse(BaseModel):
    can_pause: bool
    can_downgrade: bool
    suggested_offer: str
    impact_summary: str

    model_config = ConfigDict(extra="forbid")


class CancelSubscriptionRequest(BaseModel):
    reason: Literal[
        "too_expensive",
        "low_value",
        "too_many_errors",
        "not_using_enough",
        "switched_alternative",
        "other",
    ]
    comment: str | None = None

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
    notification_preferences: NotificationPreferences

    model_config = ConfigDict(extra="forbid")

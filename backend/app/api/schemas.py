from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class HealthStatusResponse(BaseModel):
    status: str


class MemoryRecordResponse(BaseModel):
    id: str
    memory_type: str
    raw_text: str
    structured_data: dict[str, Any]
    created_at: str

    model_config = ConfigDict(extra="forbid")


class MemoryListResponse(BaseModel):
    items: list[MemoryRecordResponse]


class MemoryProposalResponse(BaseModel):
    transcript: str
    memory_type: Literal["expense_event", "inventory_event", "loan_event", "note", "document"]
    structured_data: dict[str, Any]
    clarification_questions: list[str] = []
    missing_required_fields: list[str] = []
    needs_confirmation: bool

    model_config = ConfigDict(extra="forbid")


class SaveMemoryRequest(BaseModel):
    memory_type: Literal["expense_event", "inventory_event", "loan_event", "note", "document"]
    raw_text: str
    structured_data: dict[str, Any]
    confirmed: bool

    model_config = ConfigDict(extra="forbid")


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

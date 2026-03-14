from typing import Any

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


class AdminUserResponse(BaseModel):
    id: str
    role: str

    model_config = ConfigDict(extra="forbid")


class AdminUsersListResponse(BaseModel):
    items: list[AdminUserResponse]

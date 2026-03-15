from collections import Counter
from datetime import datetime
from typing import Any

from app.api.schemas import DashboardLatestMemoryResponse, DashboardResponse


def _parse_created_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def build_dashboard_response(scoped_memories: list[dict[str, Any]]) -> DashboardResponse:
    type_counter: Counter[str] = Counter()
    for item in scoped_memories:
        memory_type = str(item.get("memory_type", "unknown"))
        type_counter[memory_type] += 1

    latest_items = sorted(
        scoped_memories,
        key=lambda item: _parse_created_at(str(item["created_at"])),
        reverse=True,
    )[:5]

    return DashboardResponse(
        total_memories=len(scoped_memories),
        memories_by_type=dict(type_counter),
        latest_memory_events=[
            DashboardLatestMemoryResponse(
                id=str(item["id"]),
                memory_type=str(item["memory_type"]),
                raw_text=str(item["raw_text"]),
                created_at=str(item["created_at"]),
            )
            for item in latest_items
        ],
    )

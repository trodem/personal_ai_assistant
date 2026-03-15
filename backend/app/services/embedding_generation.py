import hashlib
from typing import Any

from app.repositories.embedding_repository import insert_embedding_record


def generate_and_store_embedding_for_memory(
    *,
    tenant_id: str,
    user_id: str,
    memory_id: str,
    raw_text: str,
    structured_data: dict[str, Any],
) -> None:
    embedding_input = f"{raw_text.strip()}|{structured_data}"
    vector = _deterministic_embedding_vector(embedding_input)
    insert_embedding_record(
        {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "memory_id": memory_id,
            "embedding": vector,
            "provider": "openai",
            "model_id": "text-embedding-3-small",
        }
    )


def _deterministic_embedding_vector(text: str, dimensions: int = 16) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    output: list[float] = []
    for idx in range(dimensions):
        source = digest[idx % len(digest)]
        normalized = (source / 255.0) * 2.0 - 1.0
        output.append(round(normalized, 6))
    return output

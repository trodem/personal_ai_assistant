import hashlib
import math
import re
from typing import Any


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "at",
    "is",
    "are",
    "was",
    "were",
    "did",
    "do",
    "i",
    "my",
    "you",
    "it",
    "where",
    "what",
    "how",
    "much",
}


def find_semantic_memory_match(
    *,
    question: str,
    memories: list[dict[str, Any]],
    embeddings: list[dict[str, Any]],
    min_score: float = 0.20,
) -> dict[str, Any] | None:
    if not memories:
        return None

    embedding_by_memory_id = {
        str(item.get("memory_id")): list(item.get("embedding", []))
        for item in embeddings
        if item.get("memory_id")
    }
    question_vector = _deterministic_embedding_vector(question)
    question_tokens = _tokenize(question)

    best: dict[str, Any] | None = None
    best_score = -1.0
    for memory in memories:
        memory_id = str(memory.get("id", ""))
        memory_text = _memory_semantic_text(memory)
        if not memory_id or not memory_text:
            continue

        lexical = _jaccard_similarity(question_tokens, _tokenize(memory_text))
        vector_score = _cosine_similarity(question_vector, embedding_by_memory_id.get(memory_id, []))
        normalized_vector = (vector_score + 1.0) / 2.0  # [-1,1] -> [0,1]
        combined = (0.65 * lexical) + (0.35 * normalized_vector)
        if combined > best_score:
            best_score = combined
            best = {
                "memory_id": memory_id,
                "score": round(combined, 4),
                "raw_text": str(memory.get("raw_text", "")).strip(),
                "structured_data": memory.get("structured_data", {}),
            }

    if best is None or best_score < min_score:
        return None
    return best


def _memory_semantic_text(memory: dict[str, Any]) -> str:
    raw_text = str(memory.get("raw_text", "")).strip()
    structured = memory.get("structured_data", {})
    flat_structured = " ".join(str(value) for value in structured.values() if value is not None)
    return f"{raw_text} {flat_structured}".strip()


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]{3,}", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def _jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    if union == 0:
        return 0.0
    return intersection / union


def _deterministic_embedding_vector(text: str, dimensions: int = 16) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    output: list[float] = []
    for idx in range(dimensions):
        source = digest[idx % len(digest)]
        normalized = (source / 255.0) * 2.0 - 1.0
        output.append(round(normalized, 6))
    return output


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    length = min(len(left), len(right))
    if length == 0:
        return 0.0
    left_vec = left[:length]
    right_vec = right[:length]
    dot = sum(a * b for a, b in zip(left_vec, right_vec))
    left_norm = math.sqrt(sum(a * a for a in left_vec))
    right_norm = math.sqrt(sum(b * b for b in right_vec))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)

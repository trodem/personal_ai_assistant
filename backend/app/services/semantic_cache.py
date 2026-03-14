from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re


SEMANTIC_SIMILARITY_THRESHOLD = 0.90
DEFAULT_TTL_HOURS = 24
VOLATILE_TTL_HOURS = 1
MAX_ENTRIES_PER_USER = 100


@dataclass
class CachedQuestionAnswer:
    normalized_question: str
    language: str
    filter_context: str
    answer: str
    confidence: str
    source_memory_ids: list[str]
    context_signature: str
    created_at: datetime
    ttl_hours: int


_CACHE_BY_USER: dict[tuple[str, str], list[CachedQuestionAnswer]] = {}


def _user_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def normalize_question(question: str) -> str:
    lowered = question.lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return " ".join(cleaned.split())


def extract_filter_context(question: str) -> str:
    lowered = normalize_question(question)
    currency = "any"
    if " chf" in f" {lowered} ":
        currency = "CHF"
    elif " eur" in f" {lowered} ":
        currency = "EUR"
    elif " usd" in f" {lowered} ":
        currency = "USD"

    period = "default"
    for token in ("this month", "this week", "today", "last year", "last month"):
        if token in lowered:
            period = token
            break
    return f"currency={currency};period={period}"


def is_volatile_query(question: str) -> bool:
    lowered = normalize_question(question)
    return any(token in lowered for token in ("this month", "this week", "today"))


def _token_set(text: str) -> set[str]:
    return set(part for part in normalize_question(text).split(" ") if part)


def semantic_similarity(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens.intersection(right_tokens))
    union = len(left_tokens.union(right_tokens))
    if union == 0:
        return 0.0
    return intersection / union


def _is_not_expired(entry: CachedQuestionAnswer, now: datetime) -> bool:
    return entry.created_at + timedelta(hours=entry.ttl_hours) > now


def get_cached_answer(
    *,
    tenant_id: str,
    user_id: str,
    question: str,
    language: str,
    filter_context: str,
    context_signature: str,
) -> CachedQuestionAnswer | None:
    key = _user_key(tenant_id, user_id)
    entries = _CACHE_BY_USER.get(key, [])
    now = datetime.now(timezone.utc)

    best_match: CachedQuestionAnswer | None = None
    best_score = 0.0
    for entry in entries:
        if entry.language != language:
            continue
        if entry.filter_context != filter_context:
            continue
        if entry.context_signature != context_signature:
            continue
        if not _is_not_expired(entry, now):
            continue
        score = semantic_similarity(entry.normalized_question, question)
        if score >= SEMANTIC_SIMILARITY_THRESHOLD and score > best_score:
            best_score = score
            best_match = entry
    return best_match


def put_cached_answer(
    *,
    tenant_id: str,
    user_id: str,
    question: str,
    language: str,
    filter_context: str,
    answer: str,
    confidence: str,
    source_memory_ids: list[str],
    context_signature: str,
) -> None:
    key = _user_key(tenant_id, user_id)
    entries = _CACHE_BY_USER.setdefault(key, [])
    ttl_hours = VOLATILE_TTL_HOURS if is_volatile_query(question) else DEFAULT_TTL_HOURS
    entries.append(
        CachedQuestionAnswer(
            normalized_question=normalize_question(question),
            language=language,
            filter_context=filter_context,
            answer=answer,
            confidence=confidence,
            source_memory_ids=source_memory_ids,
            context_signature=context_signature,
            created_at=datetime.now(timezone.utc),
            ttl_hours=ttl_hours,
        )
    )
    if len(entries) > MAX_ENTRIES_PER_USER:
        entries.sort(key=lambda entry: entry.created_at, reverse=True)
        _CACHE_BY_USER[key] = entries[:MAX_ENTRIES_PER_USER]


def invalidate_user_cache(tenant_id: str, user_id: str) -> None:
    _CACHE_BY_USER.pop(_user_key(tenant_id, user_id), None)


def get_user_cache_size(tenant_id: str, user_id: str) -> int:
    return len(_CACHE_BY_USER.get(_user_key(tenant_id, user_id), []))

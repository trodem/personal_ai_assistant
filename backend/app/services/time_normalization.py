from datetime import datetime, timedelta, timezone
import re


_RELATIVE_PATTERNS: tuple[tuple[str, int], ...] = (
    (r"\btoday\b", 0),
    (r"\byesterday\b", -1),
    (r"\btomorrow\b", 1),
    (r"\blast week\b", -7),
    (r"\bnext week\b", 7),
)


def normalize_relative_when_value(value: str, reference: datetime | None = None) -> str | None:
    normalized_reference = _normalized_reference(reference)
    lowered = value.strip().lower()
    for pattern, day_offset in _RELATIVE_PATTERNS:
        if re.fullmatch(pattern, lowered):
            return (normalized_reference + timedelta(days=day_offset)).isoformat()
    return None


def normalize_relative_when_from_text(text: str, reference: datetime | None = None) -> str | None:
    normalized_reference = _normalized_reference(reference)
    lowered = text.lower()
    for pattern, day_offset in _RELATIVE_PATTERNS:
        if re.search(pattern, lowered):
            return (normalized_reference + timedelta(days=day_offset)).isoformat()
    return None


def _normalized_reference(reference: datetime | None) -> datetime:
    if reference is None:
        return datetime.now(timezone.utc)
    if reference.tzinfo is None:
        return reference.replace(tzinfo=timezone.utc)
    return reference.astimezone(timezone.utc)

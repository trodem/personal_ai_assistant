SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "it", "de")
DEFAULT_LANGUAGE = "en"


def normalize_preferred_language(value: str | None) -> str:
    if not value:
        return DEFAULT_LANGUAGE
    lowered = value.strip().lower()
    if lowered in SUPPORTED_LANGUAGES:
        return lowered
    return DEFAULT_LANGUAGE

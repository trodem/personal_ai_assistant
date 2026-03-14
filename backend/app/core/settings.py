import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal, cast


_VALID_APP_ENVS = {"dev", "staging", "prod"}
_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _read_str(name: str, default: str | None = None) -> str:
    raw = os.getenv(name)
    if raw is None:
        if default is not None:
            return default
        raise ValueError(f"Missing required environment variable: {name}")
    value = raw.strip()
    if not value:
        raise ValueError(f"Environment variable {name} cannot be empty")
    return value


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"Environment variable {name} must be > 0")
    return value


def _read_cors_origins(name: str) -> tuple[str, ...]:
    raw = _read_str(
        name,
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    )
    values = tuple(item.strip() for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError(f"Environment variable {name} must contain at least one origin")
    return values


@dataclass(frozen=True)
class AppSettings:
    app_env: Literal["dev", "staging", "prod"]
    app_version: str
    api_port: int
    log_level: str
    app_cors_allow_origins: tuple[str, ...]
    app_dev_jwt_secret: str
    supabase_url: str
    ai_token_budget_free: int
    ai_token_budget_premium: int


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    app_env_raw = _read_str("APP_ENV", "dev").lower()
    if app_env_raw not in _VALID_APP_ENVS:
        raise ValueError(f"APP_ENV must be one of: {sorted(_VALID_APP_ENVS)}")

    log_level = _read_str("LOG_LEVEL", "INFO").upper()
    if log_level not in _VALID_LOG_LEVELS:
        raise ValueError(f"LOG_LEVEL must be one of: {sorted(_VALID_LOG_LEVELS)}")

    return AppSettings(
        app_env=cast(Literal["dev", "staging", "prod"], app_env_raw),
        app_version=_read_str("APP_VERSION", "dev"),
        api_port=_read_int("API_PORT", 8000),
        log_level=log_level,
        app_cors_allow_origins=_read_cors_origins("APP_CORS_ALLOW_ORIGINS"),
        app_dev_jwt_secret=_read_str("APP_DEV_JWT_SECRET", "dev_jwt_secret"),
        supabase_url=os.getenv("SUPABASE_URL", "").rstrip("/"),
        ai_token_budget_free=_read_int("AI_TOKEN_BUDGET_FREE", 200000),
        ai_token_budget_premium=_read_int("AI_TOKEN_BUDGET_PREMIUM", 2000000),
    )

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from fastapi import Header
from starlette import status

from app.core.errors import AppError
from app.core.request_context import tenant_id_ctx_var, user_id_ctx_var


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    tenant_id: str


def _urlsafe_b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(payload_b64: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return _urlsafe_b64encode(digest)


def build_dev_token(user_id: str, *, tenant_id: str = "tenant-default", ttl_seconds: int = 3600) -> str:
    secret = os.getenv("SUPABASE_JWT_SECRET", "dev_jwt_secret")
    payload = {"sub": user_id, "tenant_id": tenant_id, "exp": int(time.time()) + ttl_seconds}
    payload_b64 = _urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64, secret)}"


def _decode_token(token: str) -> dict[str, object]:
    try:
        payload_b64, signature = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Invalid token format.",
        ) from exc

    secret = os.getenv("SUPABASE_JWT_SECRET", "dev_jwt_secret")
    expected_signature = _sign(payload_b64, secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Invalid token signature.",
        )

    try:
        payload = json.loads(_urlsafe_b64decode(payload_b64).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token payload is invalid.",
        ) from exc

    exp = int(payload.get("exp", 0))
    if exp <= int(time.time()):
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token is expired.",
        )

    if not payload.get("sub"):
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token subject is missing.",
        )
    return payload


def get_current_user(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> AuthenticatedUser:
    if not authorization:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.missing_token",
            message="Missing bearer token.",
        )
    if not authorization.lower().startswith("bearer "):
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Authorization header must use Bearer scheme.",
        )

    token = authorization.split(" ", maxsplit=1)[1].strip()
    payload = _decode_token(token)
    user_id = str(payload["sub"])
    token_tenant_id = str(payload.get("tenant_id", "")).strip()
    if not x_tenant_id or not token_tenant_id:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Tenant context is required.",
        )
    if x_tenant_id != token_tenant_id:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Cross-tenant access is forbidden.",
        )

    user_id_ctx_var.set(user_id)
    tenant_id_ctx_var.set(token_tenant_id)
    return AuthenticatedUser(user_id=user_id, tenant_id=token_tenant_id)

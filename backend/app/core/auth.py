import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from app.core.errors import AppError
from app.core.request_context import tenant_id_ctx_var, user_id_ctx_var
from app.repositories.admin_user_repository import upsert_admin_user
from app.services.mfa_security import get_effective_mfa_enabled
from app.core.settings import get_settings


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    tenant_id: str
    role: str
    mfa_enabled: bool
    status: str


bearer_scheme = HTTPBearer(auto_error=False)
USER_ID_CLAIM_CANDIDATES = ("sub", "user_id", "uid")


def _dev_hs256_secret() -> str:
    return get_settings().app_dev_jwt_secret


def _urlsafe_b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(payload_b64: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return _urlsafe_b64encode(digest)


def _encode_jwt(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"
    signature = _sign(signing_input, secret)
    return f"{signing_input}.{signature}"


def build_dev_token(
    user_id: str,
    *,
    tenant_id: str | None = "tenant-default",
    role: str = "user",
    mfa_enabled: bool = False,
    status: str = "active",
    ttl_seconds: int = 3600,
) -> str:
    secret = _dev_hs256_secret()
    payload: dict[str, object] = {
        "sub": user_id,
        "role": role,
        "mfa_enabled": mfa_enabled,
        "status": status,
        "exp": int(time.time()) + ttl_seconds,
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id
    return _encode_jwt(payload, secret)


def _decode_token(token: str) -> dict[str, object]:
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Invalid token format.",
        ) from exc

    try:
        header = json.loads(_urlsafe_b64decode(header_b64).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token header is invalid.",
        ) from exc
    alg = str(header.get("alg", ""))
    if alg == "HS256":
        secret = _dev_hs256_secret()
        expected_signature = _sign(f"{header_b64}.{payload_b64}", secret)
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
    elif alg in {"ES256", "RS256"}:
        payload = _decode_with_jwks(token, alg)
    else:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Unsupported token algorithm.",
        )

    exp = int(payload.get("exp", 0))
    if exp <= int(time.time()):
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token is expired.",
        )

    _ = resolve_internal_user_id(payload)
    return payload


def resolve_internal_user_id(payload: dict[str, object]) -> str:
    for claim_name in USER_ID_CLAIM_CANDIDATES:
        claim_value = payload.get(claim_name)
        if claim_value is None:
            continue
        user_id = str(claim_value).strip()
        if user_id:
            return user_id
    raise AppError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="auth.invalid_token",
        message="Token user identifier claim is missing.",
    )


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    supabase_url = get_settings().supabase_url
    if not supabase_url:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="SUPABASE_URL is required for JWT verification.",
        )
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    return jwt.PyJWKClient(jwks_url)


def _decode_with_jwks(token: str, algorithm: str) -> dict[str, object]:
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[algorithm],
            options={"verify_aud": False},
        )
        return dict(payload)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token signature verification failed.",
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    x_tenant_id: str | None = Header(default=None),
) -> AuthenticatedUser:
    if credentials is None:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.missing_token",
            message="Missing bearer token.",
        )
    if credentials.scheme.lower() != "bearer":
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Authorization header must use Bearer scheme.",
        )

    token = credentials.credentials.strip()
    payload = _decode_token(token)
    user_id = resolve_internal_user_id(payload)
    role = str(payload.get("role", "user"))
    token_mfa_enabled = bool(payload.get("mfa_enabled", False))
    account_status = str(payload.get("status", "active")).lower()
    if account_status not in {"active", "suspended", "canceled"}:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="auth.invalid_token",
            message="Token account status is invalid.",
        )
    if account_status in {"suspended", "canceled"}:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Account is not active.",
        )
    normalized_header_tenant = (x_tenant_id or "").strip()
    token_tenant_id = str(payload.get("tenant_id", "")).strip()
    if token_tenant_id:
        if not normalized_header_tenant:
            raise AppError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="auth.forbidden",
                message="Tenant context is required.",
            )
        if normalized_header_tenant != token_tenant_id:
            raise AppError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="auth.forbidden",
                message="Cross-tenant access is forbidden.",
            )
        effective_tenant = token_tenant_id
    else:
        if normalized_header_tenant and normalized_header_tenant != "tenant-default":
            raise AppError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="auth.forbidden",
                message="Cross-tenant access is forbidden.",
            )
        # Single-tenant fallback for personal mode tokens.
        effective_tenant = "tenant-default"

    if not effective_tenant:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.forbidden",
            message="Tenant context is required.",
        )
    mfa_enabled = get_effective_mfa_enabled(
        tenant_id=effective_tenant,
        user_id=user_id,
        token_mfa_enabled=token_mfa_enabled,
    )

    upsert_admin_user(
        tenant_id=effective_tenant,
        user_id=user_id,
        role=role,
        status=account_status,
        email=str(payload.get("email", "") or ""),
    )

    user_id_ctx_var.set(user_id)
    tenant_id_ctx_var.set(effective_tenant)
    return AuthenticatedUser(
        user_id=user_id,
        tenant_id=effective_tenant,
        role=role,
        mfa_enabled=mfa_enabled,
        status=account_status,
    )


def enforce_mfa_policy_for_role(user: AuthenticatedUser) -> None:
    if user.role in {"admin", "author"} and not user.mfa_enabled:
        raise AppError(
            status_code=status.HTTP_403_FORBIDDEN,
            code="auth.mfa_required",
            message="MFA is required for this role.",
        )

from dataclasses import asdict, dataclass
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.request_context import request_id_ctx_var


HTTP_STATUS_TO_ERROR_CODE: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "memory.validation_failed",
    status.HTTP_401_UNAUTHORIZED: "auth.invalid_token",
    status.HTTP_403_FORBIDDEN: "auth.forbidden",
    status.HTTP_404_NOT_FOUND: "memory.not_found",
    status.HTTP_409_CONFLICT: "memory.version_conflict",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "memory.missing_required_fields",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate.limit_exceeded",
    status.HTTP_502_BAD_GATEWAY: "ai.provider_unavailable",
    status.HTTP_503_SERVICE_UNAVAILABLE: "ai.provider_unavailable",
}


@dataclass
class ErrorPayload:
    code: str
    message: str
    details: dict[str, Any]
    request_id: str
    retryable: bool


def build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    retryable: bool = False,
) -> JSONResponse:
    payload = ErrorPayload(
        code=code,
        message=message,
        details=details or {},
        request_id=request_id_ctx_var.get(),
        retryable=retryable,
    )
    return JSONResponse(status_code=status_code, content={"error": asdict(payload)})


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        retryable: bool = False,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)


def map_http_error_code(status_code: int) -> str:
    return HTTP_STATUS_TO_ERROR_CODE.get(status_code, "internal.unexpected_error")


def is_retryable_http_status(status_code: int) -> bool:
    return status_code in {
        status.HTTP_429_TOO_MANY_REQUESTS,
        status.HTTP_502_BAD_GATEWAY,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    }


def app_error_to_response(error: AppError) -> JSONResponse:
    return build_error_response(
        status_code=error.status_code,
        code=error.code,
        message=error.message,
        details=error.details,
        retryable=error.retryable,
    )


def validation_error_to_response(exc: Exception) -> JSONResponse:
    details = getattr(exc, "errors", lambda: [])()
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="memory.missing_required_fields",
        message="Request validation failed.",
        details={"errors": details},
        retryable=False,
    )


def http_error_to_response(status_code: int, request: Request) -> JSONResponse:
    return build_error_response(
        status_code=status_code,
        code=map_http_error_code(status_code),
        message=f"Request failed for path {request.url.path}.",
        details={},
        retryable=is_retryable_http_status(status_code),
    )


def unexpected_error_to_response() -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal.unexpected_error",
        message="Unexpected internal server error.",
        details={},
        retryable=False,
    )

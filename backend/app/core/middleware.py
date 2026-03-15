import logging
import time
import uuid

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.analytics import emit_operational_event
from app.core.errors import (
    AppError,
    app_error_to_response,
    build_error_response,
    http_error_to_response,
    unexpected_error_to_response,
    validation_error_to_response,
)
from app.core.metrics import metrics_registry
from app.core.request_context import request_id_ctx_var, tenant_id_ctx_var, trace_id_ctx_var, user_id_ctx_var


logger = logging.getLogger(__name__)


class MandatoryAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Enforce bearer auth on every API v1 route by default.
        if request.method.upper() == "OPTIONS":
            return await call_next(request)
        if not request.url.path.startswith("/api/v1"):
            return await call_next(request)

        authorization = request.headers.get("Authorization", "").strip()
        if not authorization:
            return build_error_response(
                status_code=401,
                code="auth.missing_token",
                message="Missing bearer token.",
            )
        if not authorization.lower().startswith("bearer "):
            return build_error_response(
                status_code=401,
                code="auth.invalid_token",
                message="Authorization header must use Bearer scheme.",
            )
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except AppError as exc:
            logger.warning("app_error", extra={"error_code": exc.code, "status_code": exc.status_code})
            return app_error_to_response(exc)
        except RequestValidationError as exc:
            logger.warning("request_validation_error", extra={"error_code": "memory.missing_required_fields"})
            return validation_error_to_response(exc)
        except StarletteHTTPException as exc:
            logger.warning(
                "http_exception",
                extra={"error_code": "http.exception", "status_code": exc.status_code},
            )
            return http_error_to_response(exc.status_code, request)
        except Exception:
            logger.exception("unhandled_exception", extra={"error_code": "internal.unexpected_error"})
            return unexpected_error_to_response()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        trace_id = request.headers.get("x-trace-id", request_id)
        user_id = "-"
        session_id = request.headers.get("x-session-id", request_id)

        token_request = request_id_ctx_var.set(request_id)
        token_trace = trace_id_ctx_var.set(trace_id)
        token_user = user_id_ctx_var.set(user_id)
        token_tenant = tenant_id_ctx_var.set("-")

        start = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            response.headers["x-request-id"] = request_id
            response.headers["x-trace-id"] = trace_id

            metrics_registry.record_request(request.method, request.url.path, response.status_code)
            logger.info(
                "request_processed",
                extra={
                    "http_method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

            if 400 <= response.status_code < 500:
                emit_operational_event(
                    event_name="api_error_4xx",
                    session_id=session_id,
                    status_code=response.status_code,
                    path=request.url.path,
                )
            elif response.status_code >= 500:
                emit_operational_event(
                    event_name="api_error_5xx",
                    session_id=session_id,
                    status_code=response.status_code,
                    path=request.url.path,
                )
            return response
        finally:
            request_id_ctx_var.reset(token_request)
            trace_id_ctx_var.reset(token_trace)
            user_id_ctx_var.reset(token_user)
            tenant_id_ctx_var.reset(token_tenant)

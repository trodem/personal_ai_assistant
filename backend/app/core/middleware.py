import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.analytics import emit_operational_event
from app.core.metrics import metrics_registry
from app.core.request_context import request_id_ctx_var, trace_id_ctx_var, user_id_ctx_var


logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        trace_id = request.headers.get("x-trace-id", request_id)
        user_id = request.headers.get("x-user-id", "-")
        session_id = request.headers.get("x-session-id", request_id)

        token_request = request_id_ctx_var.set(request_id)
        token_trace = trace_id_ctx_var.set(trace_id)
        token_user = user_id_ctx_var.set(user_id)

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

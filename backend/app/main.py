import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.core.errors import (
    AppError,
    app_error_to_response,
    http_error_to_response,
    unexpected_error_to_response,
    validation_error_to_response,
)
from app.core.logging_config import configure_logging
from app.core.middleware import RequestContextMiddleware


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal AI Assistant Backend", version="0.1.0")
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
app.include_router(metrics_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "personal-ai-assistant-backend"}


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    logger.warning("app_error", extra={"error_code": exc.code, "status_code": exc.status_code})
    return app_error_to_response(exc)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("request_validation_error", extra={"error_code": "request.validation_failed"})
    return validation_error_to_response(exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning(
        "http_exception",
        extra={"error_code": "http.exception", "status_code": exc.status_code},
    )
    return http_error_to_response(exc.status_code, request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", extra={"error_code": "internal.unexpected_error"})
    return unexpected_error_to_response()

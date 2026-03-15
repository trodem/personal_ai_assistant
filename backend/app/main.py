import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.author import router as author_router
from app.api.v1.routes.attachments import router as attachments_router
from app.api.v1.routes.billing import router as billing_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.feedback import router as feedback_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.memory_ingestion import router as memory_ingestion_router
from app.api.v1.routes.memories import router as memories_router
from app.api.v1.routes.metrics import router as metrics_router
from app.api.v1.routes.notifications import router as notifications_router
from app.api.v1.routes.question import router as question_router
from app.api.v1.routes.settings import router as settings_router
from app.core.errors import http_error_to_response, validation_error_to_response
from app.core.logging_config import configure_logging
from app.core.middleware import ErrorHandlingMiddleware, RequestContextMiddleware
from app.core.settings import get_settings


configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI(
    title="Personal AI Assistant Backend",
    version="0.1.0",
    description="MVP backend APIs for health, metrics, authenticated memory access, and admin controls.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.app_cors_allow_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-request-id", "x-trace-id"],
)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(memories_router)
app.include_router(memory_ingestion_router)
app.include_router(attachments_router)
app.include_router(question_router)
app.include_router(feedback_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(author_router)
app.include_router(settings_router)
app.include_router(notifications_router)
app.include_router(billing_router)


@app.get("/", summary="Service metadata", tags=["Health"])
async def root() -> dict[str, str]:
    return {"service": "personal-ai-assistant-backend"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return http_error_to_response(exc.status_code, request)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return validation_error_to_response(exc)

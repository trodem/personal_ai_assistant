import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.author import router as author_router
from app.api.v1.routes.attachments import router as attachments_router
from app.api.v1.routes.billing import router as billing_router
from app.api.v1.routes.coupons import router as coupons_router
from app.api.v1.routes.data_export import router as data_export_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.feedback import router as feedback_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.memory_ingestion import router as memory_ingestion_router
from app.api.v1.routes.memories import router as memories_router
from app.api.v1.routes.metrics import router as metrics_router
from app.api.v1.routes.notifications import router as notifications_router
from app.api.v1.routes.question import router as question_router
from app.api.v1.routes.retention import router as retention_router
from app.api.v1.routes.settings import router as settings_router
from app.core.errors import http_error_to_response, validation_error_to_response
from app.core.logging_config import configure_logging
from app.core.middleware import ErrorHandlingMiddleware, MandatoryAuthMiddleware, RequestContextMiddleware
from app.core.settings import get_settings


configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

ERROR_STATUS_CODES = {"400", "401", "403", "404", "409", "422", "429", "500", "502", "503"}
ERROR_CONTENT_SCHEMA_REF = {"$ref": "#/components/schemas/ErrorEnvelope"}


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
app.add_middleware(MandatoryAuthMiddleware)
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
app.include_router(retention_router)
app.include_router(coupons_router)
app.include_router(data_export_router)


def _inject_standard_error_responses(schema: dict) -> None:
    paths = schema.get("paths", {})
    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            responses = operation.get("responses", {})
            if not isinstance(responses, dict):
                continue
            for code, response in responses.items():
                if code not in ERROR_STATUS_CODES:
                    continue
                if not isinstance(response, dict):
                    continue
                content = response.setdefault("content", {})
                if "application/json" in content:
                    continue
                content["application/json"] = {"schema": ERROR_CONTENT_SCHEMA_REF}


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    components = schema.setdefault("components", {})
    component_schemas = components.setdefault("schemas", {})
    component_schemas["ErrorDetails"] = {
        "type": "object",
        "additionalProperties": True,
        "title": "ErrorDetails",
    }
    component_schemas["ErrorObject"] = {
        "type": "object",
        "title": "ErrorObject",
        "required": ["code", "message", "details", "request_id", "retryable"],
        "properties": {
            "code": {"type": "string", "title": "Code"},
            "message": {"type": "string", "title": "Message"},
            "details": {"$ref": "#/components/schemas/ErrorDetails"},
            "request_id": {"type": "string", "title": "Request Id"},
            "retryable": {"type": "boolean", "title": "Retryable"},
        },
        "additionalProperties": False,
    }
    component_schemas["ErrorEnvelope"] = {
        "type": "object",
        "title": "ErrorEnvelope",
        "required": ["error"],
        "properties": {"error": {"$ref": "#/components/schemas/ErrorObject"}},
        "additionalProperties": False,
    }
    _inject_standard_error_responses(schema)
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", summary="Service metadata", tags=["Health"])
async def root() -> dict[str, str]:
    return {"service": "personal-ai-assistant-backend"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return http_error_to_response(exc.status_code, request)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return validation_error_to_response(exc)

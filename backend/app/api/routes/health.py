from fastapi import APIRouter

from app.api.schemas import HealthStatusResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/live",
    summary="Liveness probe",
    description="Returns service liveness status for container/platform health checks.",
    response_model=HealthStatusResponse,
)
async def live() -> HealthStatusResponse:
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns readiness status to indicate the API can serve requests.",
    response_model=HealthStatusResponse,
)
async def ready() -> HealthStatusResponse:
    return {"status": "ready"}

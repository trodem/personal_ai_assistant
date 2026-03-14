from fastapi import APIRouter, Response

from app.core.llmops import render_llmops_prometheus
from app.core.metrics import metrics_registry

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics() -> Response:
    payload = metrics_registry.as_prometheus() + render_llmops_prometheus()
    return Response(content=payload, media_type="text/plain")

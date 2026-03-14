from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from app.core.llmops import render_llmops_prometheus
from app.core.metrics import metrics_registry

router = APIRouter(tags=["Metrics"])


@router.get(
    "/metrics",
    summary="Runtime and LLMOps metrics",
    description="Exposes Prometheus-compatible metrics for API runtime and LLMOps monitoring.",
    response_class=PlainTextResponse,
)
async def metrics() -> Response:
    payload = metrics_registry.as_prometheus() + render_llmops_prometheus()
    return Response(content=payload, media_type="text/plain")

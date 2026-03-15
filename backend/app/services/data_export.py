from uuid import uuid4

from app.api.schemas import DataExportJobResponse

_EXPORT_JOBS: dict[tuple[str, str], dict[str, str]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def start_data_export_job(*, tenant_id: str, user_id: str, export_format: str) -> DataExportJobResponse:
    _ = export_format
    key = _settings_key(tenant_id, user_id)
    jobs = dict(_EXPORT_JOBS.get(key, {}))
    job_id = str(uuid4())
    jobs[job_id] = "queued"
    _EXPORT_JOBS[key] = jobs
    return DataExportJobResponse(job_id=job_id, status="queued")

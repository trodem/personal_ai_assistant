from uuid import UUID, uuid4

from app.api.schemas import DataExportJobResponse, DataExportJobStatusResponse

_EXPORT_JOBS: dict[tuple[str, str], dict[str, str]] = {}


def _settings_key(tenant_id: str, user_id: str) -> tuple[str, str]:
    return (tenant_id, user_id)


def start_data_export_job(*, tenant_id: str, user_id: str, export_format: str) -> DataExportJobResponse:
    _ = export_format
    key = _settings_key(tenant_id, user_id)
    jobs = dict(_EXPORT_JOBS.get(key, {}))
    job_id = uuid4()
    jobs[str(job_id)] = "queued"
    _EXPORT_JOBS[key] = jobs
    return DataExportJobResponse(job_id=job_id, status="queued")


def get_data_export_job_for_user(
    *,
    tenant_id: str,
    user_id: str,
    job_id: UUID,
) -> DataExportJobStatusResponse | None:
    jobs = _EXPORT_JOBS.get(_settings_key(tenant_id, user_id), {})
    job_key = str(job_id)
    status = jobs.get(job_key)
    if status is None:
        return None
    return DataExportJobStatusResponse(job_id=job_key, status=status)

from app.domain.async_job_boundary import ExecutionMode


def resolve_transcription_execution_mode(
    *,
    payload_size_bytes: int,
    forced_mode: str | None,
    background_min_bytes: int,
) -> ExecutionMode:
    normalized_forced = (forced_mode or "").strip().lower()
    if normalized_forced == "background_worker":
        return "background_worker"
    if normalized_forced == "request_path":
        return "request_path"
    if payload_size_bytes >= background_min_bytes:
        return "background_worker"
    return "request_path"

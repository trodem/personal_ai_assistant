from dataclasses import dataclass
from typing import Literal


ExecutionMode = Literal["request_path", "background_worker"]


@dataclass(frozen=True)
class JobBoundary:
    job_name: str
    execution_mode: ExecutionMode
    rationale: str


# MVP baseline boundary:
# - request_path: executed inside HTTP request/response lifecycle.
# - background_worker: queued/asynchronous worker execution path.
JOB_BOUNDARIES: tuple[JobBoundary, ...] = (
    JobBoundary(
        job_name="memory_extraction",
        execution_mode="request_path",
        rationale="MVP keeps extraction inline to preserve confirmation UX in one request cycle.",
    ),
    JobBoundary(
        job_name="answer_generation",
        execution_mode="request_path",
        rationale="Question response remains synchronous for current API contract.",
    ),
    JobBoundary(
        job_name="attachment_ocr_extraction",
        execution_mode="request_path",
        rationale="Current attachment flow returns proposal immediately in MVP baseline.",
    ),
    JobBoundary(
        job_name="data_export_generation",
        execution_mode="background_worker",
        rationale="Export is asynchronous by contract (`/api/v1/me/data-export`).",
    ),
    JobBoundary(
        job_name="orphan_attachment_cleanup",
        execution_mode="background_worker",
        rationale="Cleanup is scheduled maintenance, not user-request blocking path.",
    ),
    JobBoundary(
        job_name="account_data_lifecycle_deletion",
        execution_mode="background_worker",
        rationale="Retention/deletion workflow is asynchronous and retry-oriented.",
    ),
    JobBoundary(
        job_name="embedding_generation",
        execution_mode="background_worker",
        rationale="Potentially expensive processing should be offloaded when enabled.",
    ),
)


def execution_mode_for(job_name: str) -> ExecutionMode:
    for boundary in JOB_BOUNDARIES:
        if boundary.job_name == job_name:
            return boundary.execution_mode
    raise KeyError(f"Unknown job boundary: {job_name}")

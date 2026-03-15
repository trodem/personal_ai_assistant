from __future__ import annotations

from fastapi import UploadFile
from starlette import status

from app.core.errors import AppError


MAX_AUDIO_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_AUDIO_CONTENT_TYPES: set[str] = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
    "audio/webm",
    "audio/ogg",
}


async def read_and_validate_audio_upload(audio: UploadFile) -> bytes:
    content_type = (audio.content_type or "").strip().lower()
    if content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="storage.unsupported_file_type",
            message="Unsupported audio content type.",
            details={"allowed_content_types": sorted(ALLOWED_AUDIO_CONTENT_TYPES)},
        )

    chunks: list[bytes] = []
    total_bytes = 0
    while True:
        chunk = await audio.read(1024 * 1024)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > MAX_AUDIO_UPLOAD_BYTES:
            raise AppError(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="memory.validation_failed",
                message="Audio payload exceeds size limit.",
                details={"max_bytes": MAX_AUDIO_UPLOAD_BYTES},
            )
        chunks.append(chunk)

    payload = b"".join(chunks)
    if not payload:
        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="memory.validation_failed",
            message="Audio payload is empty.",
            details={},
        )
    return payload

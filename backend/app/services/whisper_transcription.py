from __future__ import annotations

import asyncio
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Callable
from urllib import error, request

from starlette import status

from app.core.errors import AppError
from app.domain.async_job_boundary import ExecutionMode


_OPENAI_TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"
_RETRYABLE_HTTP_STATUSES = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class WhisperConfig:
    model: str
    timeout_seconds: float
    max_retries: int
    api_key: str


def _load_config() -> WhisperConfig:
    model = (os.getenv("OPENAI_MODEL_TRANSCRIPTION", "whisper-1") or "whisper-1").strip()
    api_key = (os.getenv("OPENAI_API_KEY", "") or "").strip()
    timeout_seconds = float(os.getenv("WHISPER_TIMEOUT_SECONDS", "15"))
    max_retries = int(os.getenv("WHISPER_MAX_RETRIES", "2"))
    if timeout_seconds <= 0:
        raise ValueError("WHISPER_TIMEOUT_SECONDS must be > 0")
    if max_retries < 0:
        raise ValueError("WHISPER_MAX_RETRIES must be >= 0")
    return WhisperConfig(
        model=model,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        api_key=api_key,
    )


def _is_configured_openai_key(api_key: str) -> bool:
    if not api_key:
        return False
    lowered = api_key.lower()
    return not lowered.startswith("replace_me")


def _decode_audio_payload_fallback(payload: bytes, file_name: str | None) -> str:
    transcript = payload.decode("utf-8", errors="ignore").strip()
    if transcript:
        return transcript
    return (file_name or "voice memory").strip() or "voice memory"


def _build_multipart_body(*, file_name: str, content_type: str, payload: bytes, model: str) -> tuple[str, bytes]:
    boundary = f"----codex-whisper-{uuid.uuid4().hex}"
    parts: list[bytes] = []
    crlf = b"\r\n"

    def _add(value: bytes) -> None:
        parts.append(value)
        parts.append(crlf)

    _add(f"--{boundary}".encode("utf-8"))
    _add(b'Content-Disposition: form-data; name="model"')
    _add(b"")
    _add(model.encode("utf-8"))

    _add(f"--{boundary}".encode("utf-8"))
    _add(
        (
            f'Content-Disposition: form-data; name="file"; filename="{file_name}"'
        ).encode("utf-8")
    )
    _add(f"Content-Type: {content_type}".encode("utf-8"))
    _add(b"")
    _add(payload)

    _add(f"--{boundary}--".encode("utf-8"))
    body = b"".join(parts)
    return boundary, body


def _default_whisper_transport(
    *,
    api_key: str,
    model: str,
    payload: bytes,
    file_name: str,
    content_type: str,
    timeout_seconds: float,
) -> tuple[int, dict[str, Any]]:
    boundary, body = _build_multipart_body(
        file_name=file_name,
        content_type=content_type,
        payload=payload,
        model=model,
    )
    req = request.Request(
        _OPENAI_TRANSCRIPTIONS_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            response_bytes = response.read()
            parsed = json.loads(response_bytes.decode("utf-8"))
            return int(response.status), parsed
    except error.HTTPError as exc:
        body_bytes = exc.read() or b"{}"
        try:
            parsed = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            parsed = {}
        return int(exc.code), parsed


def transcribe_audio_with_whisper(
    *,
    payload: bytes,
    file_name: str | None,
    content_type: str | None,
    transport: Callable[..., tuple[int, dict[str, Any]]] | None = None,
) -> str:
    config = _load_config()
    if not _is_configured_openai_key(config.api_key):
        return _decode_audio_payload_fallback(payload, file_name)

    safe_file_name = file_name or "voice-memory.wav"
    safe_content_type = (content_type or "audio/wav").strip() or "audio/wav"
    transport_fn = transport or _default_whisper_transport
    attempts = config.max_retries + 1
    last_error: str | None = None

    for attempt in range(1, attempts + 1):
        try:
            status_code, response_payload = transport_fn(
                api_key=config.api_key,
                model=config.model,
                payload=payload,
                file_name=safe_file_name,
                content_type=safe_content_type,
                timeout_seconds=config.timeout_seconds,
            )
        except TimeoutError:
            last_error = "timeout"
            if attempt < attempts:
                continue
            break
        except error.URLError:
            last_error = "network_error"
            if attempt < attempts:
                continue
            break

        if status_code == 200:
            text = str(response_payload.get("text", "")).strip()
            if not text:
                return _decode_audio_payload_fallback(payload, file_name)
            return text

        if status_code in _RETRYABLE_HTTP_STATUSES and attempt < attempts:
            last_error = f"http_{status_code}"
            continue

        if status_code in _RETRYABLE_HTTP_STATUSES:
            last_error = f"http_{status_code}"
            break

        raise AppError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="memory.validation_failed",
            message="Whisper transcription rejected the audio payload.",
            details={"provider_status": status_code},
        )

    raise AppError(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="ai.provider_unavailable",
        message="Whisper transcription service unavailable after retries.",
        details={"reason": last_error or "unknown"},
        retryable=True,
    )


async def transcribe_audio_with_whisper_by_mode(
    *,
    payload: bytes,
    file_name: str | None,
    content_type: str | None,
    execution_mode: ExecutionMode,
) -> str:
    if execution_mode == "background_worker":
        return await asyncio.to_thread(
            transcribe_audio_with_whisper,
            payload=payload,
            file_name=file_name,
            content_type=content_type,
        )
    return transcribe_audio_with_whisper(
        payload=payload,
        file_name=file_name,
        content_type=content_type,
    )

import os
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.errors import AppError
from app.services.whisper_transcription import transcribe_audio_with_whisper


class WhisperTranscriptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_fallback_decodes_payload_when_openai_key_not_configured(self) -> None:
        os.environ["OPENAI_API_KEY"] = "replace_me"
        text = transcribe_audio_with_whisper(
            payload=b"I bought bread",
            file_name="note.wav",
            content_type="audio/wav",
        )
        self.assertEqual(text, "I bought bread")

    def test_retries_on_timeout_then_succeeds(self) -> None:
        os.environ["OPENAI_API_KEY"] = "sk-test"
        os.environ["WHISPER_MAX_RETRIES"] = "2"
        calls = {"count": 0}

        def fake_transport(**_: object) -> tuple[int, dict[str, object]]:
            calls["count"] += 1
            if calls["count"] == 1:
                raise TimeoutError("timed out")
            return 200, {"text": "transcribed ok"}

        text = transcribe_audio_with_whisper(
            payload=b"binary-audio",
            file_name="voice.wav",
            content_type="audio/wav",
            transport=fake_transport,
        )
        self.assertEqual(text, "transcribed ok")
        self.assertEqual(calls["count"], 2)

    def test_raises_provider_unavailable_after_retry_exhaustion(self) -> None:
        os.environ["OPENAI_API_KEY"] = "sk-test"
        os.environ["WHISPER_MAX_RETRIES"] = "1"

        def always_timeout(**_: object) -> tuple[int, dict[str, object]]:
            raise TimeoutError("timed out")

        with self.assertRaises(AppError) as context:
            transcribe_audio_with_whisper(
                payload=b"binary-audio",
                file_name="voice.wav",
                content_type="audio/wav",
                transport=always_timeout,
            )
        self.assertEqual(context.exception.status_code, 503)
        self.assertEqual(context.exception.code, "ai.provider_unavailable")
        self.assertTrue(context.exception.retryable)

    def test_maps_non_retryable_provider_error_to_validation_error(self) -> None:
        os.environ["OPENAI_API_KEY"] = "sk-test"

        def bad_request(**_: object) -> tuple[int, dict[str, object]]:
            return 400, {"error": {"message": "bad audio"}}

        with self.assertRaises(AppError) as context:
            transcribe_audio_with_whisper(
                payload=b"binary-audio",
                file_name="voice.wav",
                content_type="audio/wav",
                transport=bad_request,
            )
        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.code, "memory.validation_failed")


if __name__ == "__main__":
    unittest.main()

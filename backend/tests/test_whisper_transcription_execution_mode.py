import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.whisper_transcription import transcribe_audio_with_whisper_by_mode


class WhisperExecutionModeTests(unittest.IsolatedAsyncioTestCase):
    async def test_background_worker_uses_asyncio_to_thread(self) -> None:
        async def _fake_to_thread(func, *args, **kwargs):  # type: ignore[no-untyped-def]
            return "from-thread"

        with patch("app.services.whisper_transcription.asyncio.to_thread", _fake_to_thread):
            value = await transcribe_audio_with_whisper_by_mode(
                payload=b"audio",
                file_name="memory.wav",
                content_type="audio/wav",
                execution_mode="background_worker",
            )
        self.assertEqual(value, "from-thread")

    async def test_request_path_uses_inline_transcription(self) -> None:
        with patch(
            "app.services.whisper_transcription.transcribe_audio_with_whisper",
            return_value="inline-transcript",
        ):
            value = await transcribe_audio_with_whisper_by_mode(
                payload=b"audio",
                file_name="memory.wav",
                content_type="audio/wav",
                execution_mode="request_path",
            )
        self.assertEqual(value, "inline-transcript")


if __name__ == "__main__":
    unittest.main()

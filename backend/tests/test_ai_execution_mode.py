import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.ai_execution_mode import resolve_transcription_execution_mode


class AiExecutionModeTests(unittest.TestCase):
    def test_forced_background_worker_takes_precedence(self) -> None:
        mode = resolve_transcription_execution_mode(
            payload_size_bytes=10,
            forced_mode="background_worker",
            background_min_bytes=1024,
        )
        self.assertEqual(mode, "background_worker")

    def test_forced_request_path_takes_precedence(self) -> None:
        mode = resolve_transcription_execution_mode(
            payload_size_bytes=999999,
            forced_mode="request_path",
            background_min_bytes=1024,
        )
        self.assertEqual(mode, "request_path")

    def test_large_payload_uses_background_worker(self) -> None:
        mode = resolve_transcription_execution_mode(
            payload_size_bytes=2048,
            forced_mode=None,
            background_min_bytes=1024,
        )
        self.assertEqual(mode, "background_worker")

    def test_small_payload_uses_request_path(self) -> None:
        mode = resolve_transcription_execution_mode(
            payload_size_bytes=100,
            forced_mode=None,
            background_min_bytes=1024,
        )
        self.assertEqual(mode, "request_path")


if __name__ == "__main__":
    unittest.main()

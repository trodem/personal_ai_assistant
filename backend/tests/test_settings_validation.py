import os
import unittest
from unittest.mock import patch

from app.core.settings import get_settings


class SettingsValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()

    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_valid_settings_are_typed(self) -> None:
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "staging",
                "APP_VERSION": "0.2.0",
                "API_PORT": "9000",
                "LOG_LEVEL": "warning",
                "APP_CORS_ALLOW_ORIGINS": "http://localhost:3000,http://localhost:5173",
                "APP_DEV_JWT_SECRET": "secret_value",
                "AI_TOKEN_BUDGET_FREE": "100",
                "AI_TOKEN_BUDGET_PREMIUM": "200",
                "MEMORY_CLARIFICATION_MAX_TURNS": "4",
                "VOICE_MEMORY_BACKGROUND_MIN_BYTES": "2048",
            },
            clear=False,
        ):
            settings = get_settings()
            self.assertEqual(settings.app_env, "staging")
            self.assertEqual(settings.app_version, "0.2.0")
            self.assertEqual(settings.api_port, 9000)
            self.assertEqual(settings.log_level, "WARNING")
            self.assertEqual(settings.app_cors_allow_origins, ("http://localhost:3000", "http://localhost:5173"))
            self.assertEqual(settings.ai_token_budget_free, 100)
            self.assertEqual(settings.ai_token_budget_premium, 200)
            self.assertEqual(settings.memory_clarification_max_turns, 4)
            self.assertEqual(settings.voice_memory_background_min_bytes, 2048)

    def test_invalid_app_env_raises(self) -> None:
        with patch.dict(os.environ, {"APP_ENV": "qa"}, clear=False):
            with self.assertRaisesRegex(ValueError, "APP_ENV must be one of"):
                get_settings()

    def test_invalid_log_level_raises(self) -> None:
        with patch.dict(os.environ, {"LOG_LEVEL": "TRACE"}, clear=False):
            with self.assertRaisesRegex(ValueError, "LOG_LEVEL must be one of"):
                get_settings()

    def test_invalid_budget_raises(self) -> None:
        with patch.dict(os.environ, {"AI_TOKEN_BUDGET_FREE": "zero"}, clear=False):
            with self.assertRaisesRegex(ValueError, "AI_TOKEN_BUDGET_FREE must be an integer"):
                get_settings()

    def test_invalid_memory_clarification_max_turns_raises(self) -> None:
        with patch.dict(os.environ, {"MEMORY_CLARIFICATION_MAX_TURNS": "0"}, clear=False):
            with self.assertRaisesRegex(ValueError, "MEMORY_CLARIFICATION_MAX_TURNS must be > 0"):
                get_settings()

    def test_invalid_voice_memory_background_min_bytes_raises(self) -> None:
        with patch.dict(os.environ, {"VOICE_MEMORY_BACKGROUND_MIN_BYTES": "-1"}, clear=False):
            with self.assertRaisesRegex(ValueError, "VOICE_MEMORY_BACKGROUND_MIN_BYTES must be > 0"):
                get_settings()

    def test_empty_cors_origins_raises(self) -> None:
        with patch.dict(os.environ, {"APP_CORS_ALLOW_ORIGINS": "   "}, clear=False):
            with self.assertRaisesRegex(ValueError, "cannot be empty"):
                get_settings()


if __name__ == "__main__":
    unittest.main()

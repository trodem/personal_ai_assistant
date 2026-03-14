import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.analytics import (
    REQUIRED_COMMON_FIELDS,
    build_event,
    validate_event_schema,
)


class ProductAnalyticsContractTests(unittest.TestCase):
    def test_event_contains_required_common_fields(self) -> None:
        event = build_event(
            event_name="api_error_4xx",
            session_id="session-1",
            user_id=None,
        )
        for field in REQUIRED_COMMON_FIELDS:
            self.assertIn(field, event)

    def test_event_name_must_be_snake_case(self) -> None:
        with self.assertRaises(ValueError):
            build_event(
                event_name="ApiError4xx",
                session_id="session-1",
                user_id=None,
            )

    def test_validate_event_schema_accepts_valid_event(self) -> None:
        event = build_event(
            event_name="api_error_5xx",
            session_id="session-2",
            user_id="user-1",
        )
        self.assertTrue(validate_event_schema(event))


if __name__ == "__main__":
    unittest.main()

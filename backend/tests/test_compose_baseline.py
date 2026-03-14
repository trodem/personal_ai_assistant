import pathlib
import unittest


class ComposeBaselineTests(unittest.TestCase):
    def test_compose_has_required_services_and_healthchecks(self) -> None:
        compose_path = pathlib.Path(__file__).resolve().parents[2] / "docker-compose.yml"
        content = compose_path.read_text(encoding="utf-8")

        self.assertIn("services:", content)
        self.assertIn("backend:", content)
        self.assertIn("postgres:", content)
        self.assertIn("healthcheck:", content)
        self.assertIn("/health/live", content)


if __name__ == "__main__":
    unittest.main()

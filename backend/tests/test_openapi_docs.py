import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app


class OpenApiDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_openapi_includes_implemented_paths(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()

        self.assertIn("/health/live", schema["paths"])
        self.assertIn("/health/ready", schema["paths"])
        self.assertIn("/metrics", schema["paths"])
        self.assertIn("/api/v1/memories", schema["paths"])
        self.assertIn("/api/v1/admin/users", schema["paths"])

    def test_protected_paths_have_bearer_security(self) -> None:
        schema = self.client.get("/openapi.json").json()
        security_schemes = schema["components"]["securitySchemes"]
        self.assertIn("HTTPBearer", security_schemes)
        self.assertEqual(security_schemes["HTTPBearer"]["type"], "http")
        self.assertEqual(security_schemes["HTTPBearer"]["scheme"], "bearer")

        memories_get = schema["paths"]["/api/v1/memories"]["get"]
        admin_users_get = schema["paths"]["/api/v1/admin/users"]["get"]
        self.assertTrue(memories_get.get("security"))
        self.assertTrue(admin_users_get.get("security"))

    def test_operations_have_summary_and_responses(self) -> None:
        schema = self.client.get("/openapi.json").json()

        live_get = schema["paths"]["/health/live"]["get"]
        self.assertEqual(live_get["summary"], "Liveness probe")
        self.assertIn("200", live_get["responses"])

        memories_get = schema["paths"]["/api/v1/memories"]["get"]
        self.assertEqual(memories_get["summary"], "List user memories")
        self.assertIn("401", memories_get["responses"])
        self.assertIn("403", memories_get["responses"])


if __name__ == "__main__":
    unittest.main()

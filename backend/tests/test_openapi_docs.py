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
        self.assertIn("/api/v1/dashboard", schema["paths"])
        self.assertIn("/api/v1/admin/users", schema["paths"])
        self.assertIn("/api/v1/admin/users/{id}/status", schema["paths"])
        self.assertIn("/api/v1/author/users/{id}/role", schema["paths"])
        self.assertIn("/api/v1/author/dashboard", schema["paths"])
        self.assertIn("/api/v1/me/settings/security", schema["paths"])
        self.assertIn("/api/v1/me/settings/notifications", schema["paths"])
        self.assertIn("/api/v1/me/settings/payment-methods", schema["paths"])
        self.assertIn("/api/v1/me/settings/payment-methods/setup-intent", schema["paths"])
        self.assertIn("/api/v1/me/settings/payment-methods/{id}/default", schema["paths"])
        self.assertIn("/api/v1/me/settings/payment-methods/{id}", schema["paths"])

    def test_protected_paths_have_bearer_security(self) -> None:
        schema = self.client.get("/openapi.json").json()
        security_schemes = schema["components"]["securitySchemes"]
        self.assertIn("HTTPBearer", security_schemes)
        self.assertEqual(security_schemes["HTTPBearer"]["type"], "http")
        self.assertEqual(security_schemes["HTTPBearer"]["scheme"], "bearer")

        memories_get = schema["paths"]["/api/v1/memories"]["get"]
        dashboard_get = schema["paths"]["/api/v1/dashboard"]["get"]
        admin_users_get = schema["paths"]["/api/v1/admin/users"]["get"]
        self.assertTrue(memories_get.get("security"))
        self.assertTrue(dashboard_get.get("security"))
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

        dashboard_get = schema["paths"]["/api/v1/dashboard"]["get"]
        self.assertEqual(dashboard_get["summary"], "Dashboard statistics")
        self.assertIn("401", dashboard_get["responses"])

        voice_memory_post = schema["paths"]["/api/v1/voice/memory"]["post"]
        self.assertEqual(voice_memory_post["summary"], "Upload voice memory")
        self.assertIn("422", voice_memory_post["responses"])

        voice_question_post = schema["paths"]["/api/v1/voice/question"]["post"]
        self.assertEqual(voice_question_post["summary"], "Upload voice question")
        self.assertIn("422", voice_question_post["responses"])

        stream_post = schema["paths"]["/api/v1/question/stream"]["post"]
        self.assertEqual(stream_post["summary"], "Ask text question with streaming response")
        self.assertIn("503", stream_post["responses"])

        feedback_post = schema["paths"]["/api/v1/feedback/answers"]["post"]
        self.assertEqual(feedback_post["summary"], "Submit feedback for AI answer")
        self.assertIn("422", feedback_post["responses"])

        delete_memory = schema["paths"]["/api/v1/memory/{id}"]["delete"]
        self.assertEqual(delete_memory["summary"], "Delete memory")
        self.assertIn("404", delete_memory["responses"])

        admin_update_status = schema["paths"]["/api/v1/admin/users/{id}/status"]["patch"]
        self.assertEqual(admin_update_status["summary"], "Update user status (admin/author)")
        self.assertIn("422", admin_update_status["responses"])

        author_update_role = schema["paths"]["/api/v1/author/users/{id}/role"]["patch"]
        self.assertEqual(author_update_role["summary"], "Update user role (author only)")
        self.assertIn("422", author_update_role["responses"])

        author_dashboard_get = schema["paths"]["/api/v1/author/dashboard"]["get"]
        self.assertEqual(author_dashboard_get["summary"], "Global supervision dashboard (author only)")
        self.assertIn("403", author_dashboard_get["responses"])

        settings_security_patch = schema["paths"]["/api/v1/me/settings/security"]["patch"]
        self.assertEqual(settings_security_patch["summary"], "Trigger security-sensitive settings change")
        self.assertIn("422", settings_security_patch["responses"])

        settings_notifications_patch = schema["paths"]["/api/v1/me/settings/notifications"]["patch"]
        self.assertEqual(settings_notifications_patch["summary"], "Update notification preferences")
        self.assertIn("422", settings_notifications_patch["responses"])

        settings_payment_methods_get = schema["paths"]["/api/v1/me/settings/payment-methods"]["get"]
        self.assertEqual(settings_payment_methods_get["summary"], "List user payment methods")
        self.assertIn("403", settings_payment_methods_get["responses"])

        settings_payment_methods_setup = schema["paths"]["/api/v1/me/settings/payment-methods/setup-intent"]["post"]
        self.assertEqual(settings_payment_methods_setup["summary"], "Create setup intent for payment method")
        self.assertIn("403", settings_payment_methods_setup["responses"])

        settings_payment_methods_default = schema["paths"]["/api/v1/me/settings/payment-methods/{id}/default"]["post"]
        self.assertEqual(settings_payment_methods_default["summary"], "Set default payment method")
        self.assertIn("404", settings_payment_methods_default["responses"])

        settings_payment_methods_delete = schema["paths"]["/api/v1/me/settings/payment-methods/{id}"]["delete"]
        self.assertEqual(settings_payment_methods_delete["summary"], "Remove payment method")
        self.assertIn("404", settings_payment_methods_delete["responses"])


if __name__ == "__main__":
    unittest.main()

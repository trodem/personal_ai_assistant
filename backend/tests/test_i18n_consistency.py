import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import build_dev_token
from app.core.i18n import SUPPORTED_LANGUAGES
from app.main import app


class I18nConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}", "x-tenant-id": "tenant-a"}

    def test_settings_default_language_falls_back_to_en(self) -> None:
        token = build_dev_token("user-i18n-default", tenant_id="tenant-a")
        response = self.client.get("/api/v1/me/settings", headers=self._headers(token))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["preferred_language"], "en")

    def test_profile_language_update_supports_it_and_persists(self) -> None:
        token = build_dev_token("user-i18n-it", tenant_id="tenant-a")
        response = self.client.patch(
            "/api/v1/me/settings/profile",
            headers=self._headers(token),
            json={"preferred_language": "it"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["preferred_language"], "it")

        get_response = self.client.get("/api/v1/me/settings", headers=self._headers(token))
        self.assertEqual(get_response.status_code, 200)
        persisted_payload = get_response.json()
        self.assertEqual(persisted_payload["preferred_language"], "it")

    def test_profile_language_rejects_unsupported_locale(self) -> None:
        token = build_dev_token("user-i18n-invalid", tenant_id="tenant-a")
        response = self.client.patch(
            "/api/v1/me/settings/profile",
            headers=self._headers(token),
            json={"preferred_language": "fr"},
        )
        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "memory.missing_required_fields")

    def test_profile_language_accepts_supabase_authenticated_role_claim(self) -> None:
        token = build_dev_token("user-i18n-authenticated-role", tenant_id="tenant-a", role="authenticated")
        response = self.client.patch(
            "/api/v1/me/settings/profile",
            headers=self._headers(token),
            json={"preferred_language": "de"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["preferred_language"], "de")
        self.assertEqual(payload["role"], "user")

    def test_flutter_arb_languages_match_backend_supported_languages(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        arb_dir = project_root / "mobile" / "lib" / "l10n"
        expected_keys = {
            "settingsLanguageTitle",
            "settingsLanguageEnglish",
            "settingsLanguageItalian",
            "settingsLanguageGerman",
        }

        discovered_locales: set[str] = set()
        for locale in SUPPORTED_LANGUAGES:
            arb_path = arb_dir / f"app_{locale}.arb"
            self.assertTrue(arb_path.exists(), f"Missing ARB file for locale: {locale}")
            payload = json.loads(arb_path.read_text(encoding="utf-8"))
            discovered_locales.add(payload["@@locale"])
            self.assertTrue(expected_keys.issubset(payload.keys()))

        self.assertEqual(discovered_locales, set(SUPPORTED_LANGUAGES))


if __name__ == "__main__":
    unittest.main()

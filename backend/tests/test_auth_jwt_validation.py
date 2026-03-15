import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.auth import _decode_token, _jwks_client, build_dev_token, get_current_user
from app.core.errors import AppError


def _fake_jwt(alg: str, payload_b64: str = "e30") -> str:
    # header payload is not verified in tests that patch JWKS decode path.
    headers = {
        "RS256": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
        "ES256": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9",
    }
    return f"{headers[alg]}.{payload_b64}.signature"


class SupabaseJwtValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        _jwks_client.cache_clear()

    def tearDown(self) -> None:
        _jwks_client.cache_clear()

    def test_rs256_token_enforces_exp_and_sub_after_jwks_decode(self) -> None:
        token = _fake_jwt("RS256")
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={"sub": "user-1", "exp": 4_102_444_800, "role": "user"},
        ):
            payload = _decode_token(token)
        self.assertEqual(payload["sub"], "user-1")

    def test_rs256_token_missing_subject_is_rejected(self) -> None:
        token = _fake_jwt("RS256")
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={"exp": 4_102_444_800, "role": "user"},
        ):
            with self.assertRaises(AppError) as exc:
                _decode_token(token)
        self.assertEqual(exc.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(exc.exception.code, "auth.invalid_token")

    def test_rs256_token_accepts_user_id_claim_as_internal_identifier(self) -> None:
        token = _fake_jwt("RS256")
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={"user_id": "internal-user-123", "exp": 4_102_444_800, "role": "user"},
        ):
            payload = _decode_token(token)
        self.assertEqual(payload["user_id"], "internal-user-123")

    def test_rs256_token_expired_is_rejected(self) -> None:
        token = _fake_jwt("RS256")
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={"sub": "user-1", "exp": 1, "role": "user"},
        ):
            with self.assertRaises(AppError) as exc:
                _decode_token(token)
        self.assertEqual(exc.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(exc.exception.code, "auth.invalid_token")

    def test_missing_supabase_url_raises_invalid_token_error(self) -> None:
        with patch("app.core.auth.get_settings") as mocked_settings:
            mocked_settings.return_value.supabase_url = ""
            with self.assertRaises(AppError) as exc:
                _jwks_client()
        self.assertEqual(exc.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(exc.exception.code, "auth.invalid_token")

    def test_get_current_user_accepts_rs256_payload_from_jwks_path(self) -> None:
        token = _fake_jwt("RS256")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={
                "sub": "user-rs256",
                "role": "user",
                "mfa_enabled": False,
                "status": "active",
                "tenant_id": "tenant-rs",
                "exp": 4_102_444_800,
            },
        ):
            user = get_current_user(credentials=credentials, x_tenant_id="tenant-rs")
        self.assertEqual(user.user_id, "user-rs256")
        self.assertEqual(user.tenant_id, "tenant-rs")

    def test_get_current_user_maps_uid_claim_to_internal_user_id(self) -> None:
        token = _fake_jwt("RS256")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch(
            "app.core.auth._decode_with_jwks",
            return_value={
                "uid": "uid-claim-user-1",
                "role": "user",
                "mfa_enabled": False,
                "status": "active",
                "tenant_id": "tenant-uid",
                "exp": 4_102_444_800,
            },
        ):
            user = get_current_user(credentials=credentials, x_tenant_id="tenant-uid")
        self.assertEqual(user.user_id, "uid-claim-user-1")
        self.assertEqual(user.tenant_id, "tenant-uid")

    def test_get_current_user_rejects_custom_tenant_header_when_token_has_no_tenant_claim(self) -> None:
        token = build_dev_token("user-single-tenant", tenant_id=None)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with self.assertRaises(AppError) as exc:
            get_current_user(credentials=credentials, x_tenant_id="tenant-b2b")
        self.assertEqual(exc.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(exc.exception.code, "auth.forbidden")


if __name__ == "__main__":
    unittest.main()

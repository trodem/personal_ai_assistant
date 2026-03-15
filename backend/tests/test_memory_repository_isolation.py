import unittest

from backend.app.repositories.memory_repository import insert_memory_record, list_memories_for_user


class MemoryRepositoryIsolationTests(unittest.TestCase):
    def test_list_requires_scope(self) -> None:
        with self.assertRaisesRegex(ValueError, "tenant_id is required"):
            list_memories_for_user(tenant_id="", user_id="user-alpha")
        with self.assertRaisesRegex(ValueError, "user_id is required"):
            list_memories_for_user(tenant_id="tenant-a", user_id="")

    def test_list_is_scoped_by_tenant_and_user(self) -> None:
        tenant_a_user_alpha = list_memories_for_user(tenant_id="tenant-a", user_id="user-alpha")
        self.assertTrue(tenant_a_user_alpha)
        self.assertTrue(all(item["tenant_id"] == "tenant-a" for item in tenant_a_user_alpha))
        self.assertTrue(all(item["user_id"] == "user-alpha" for item in tenant_a_user_alpha))

        tenant_b_user_alpha = list_memories_for_user(tenant_id="tenant-b", user_id="user-alpha")
        self.assertTrue(tenant_b_user_alpha)
        self.assertTrue(all(item["tenant_id"] == "tenant-b" for item in tenant_b_user_alpha))
        self.assertTrue(all(item["user_id"] == "user-alpha" for item in tenant_b_user_alpha))

    def test_insert_requires_scope(self) -> None:
        with self.assertRaisesRegex(ValueError, "tenant_id is required"):
            insert_memory_record(
                {
                    "id": "test-id",
                    "tenant_id": "",
                    "user_id": "user-alpha",
                    "memory_type": "note",
                    "raw_text": "test",
                    "structured_data": {},
                    "created_at": "2026-03-15T00:00:00+00:00",
                }
            )


if __name__ == "__main__":
    unittest.main()

import unittest

from backend.app.domain.async_job_boundary import JOB_BOUNDARIES, execution_mode_for


class AsyncJobBoundaryTests(unittest.TestCase):
    def test_job_names_are_unique(self) -> None:
        names = [item.job_name for item in JOB_BOUNDARIES]
        self.assertEqual(len(names), len(set(names)))

    def test_expected_execution_modes(self) -> None:
        self.assertEqual(execution_mode_for("memory_extraction"), "request_path")
        self.assertEqual(execution_mode_for("answer_generation"), "request_path")
        self.assertEqual(execution_mode_for("data_export_generation"), "background_worker")
        self.assertEqual(execution_mode_for("embedding_generation"), "background_worker")

    def test_unknown_job_raises(self) -> None:
        with self.assertRaises(KeyError):
            execution_mode_for("unknown-job")


if __name__ == "__main__":
    unittest.main()

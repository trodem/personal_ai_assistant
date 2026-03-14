import unittest
from importlib import import_module
from pathlib import Path


class BackendStructureTests(unittest.TestCase):
    def test_backend_app_has_required_modular_packages(self) -> None:
        app_root = Path(__file__).resolve().parents[1] / "app"

        required_packages = ("api", "services", "repositories", "domain")
        for package in required_packages:
            package_dir = app_root / package
            self.assertTrue(package_dir.is_dir(), f"Missing package directory: {package_dir}")
            self.assertTrue((package_dir / "__init__.py").is_file(), f"Missing __init__.py for {package}")

    def test_new_packages_are_importable(self) -> None:
        import_module("backend.app.repositories")
        import_module("backend.app.domain")


if __name__ == "__main__":
    unittest.main()

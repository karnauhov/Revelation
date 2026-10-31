from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import atomic_json
from local_release.hooks import shared_service_startup, unregister_startup
from local_release.service import identity, PRODUCT


class SharedStartupTest(unittest.TestCase):
    def test_registered_healthy_service_is_reused_without_modifying_other_projects(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            registry, queue = root / "registry.json", root / "catalogue/project-queue.json"
            atomic_json(queue, {"repo": str(root / "repo")})
            atomic_json(registry, {"projects": {"project": {"repo": str(root / "repo"), "catalogue": str(queue.parent)}}})
            def response():
                return BytesIO(json.dumps({"product": PRODUCT, "registry": identity(registry)}).encode())
            with patch("local_release.agent.registry_path", return_value=registry), \
                    patch("urllib.request.urlopen", side_effect=lambda *a, **k: response()):
                result = shared_service_startup("project", queue)
                self.assertEqual(result["kind"], "shared-service")
                self.assertIsNone(shared_service_startup("another-project", queue))
            with patch("local_release.hooks.capture") as command:
                unregister_startup(result)
                command.assert_not_called()

    def test_foreign_service_or_repository_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            registry, queue = root / "registry.json", root / "project-queue.json"
            atomic_json(queue, {"repo": str(root / "repo")})
            atomic_json(registry, {"projects": {"project": {"repo": str(root / "repo"), "catalogue": str(root)}}})
            with patch("local_release.agent.registry_path", return_value=registry), \
                    patch("urllib.request.urlopen", side_effect=lambda *a, **k: BytesIO(b'{"product":"foreign"}')):
                self.assertIsNone(shared_service_startup("project", queue))
            atomic_json(queue, {"repo": str(root / "different-repo")})
            with patch("local_release.agent.registry_path", return_value=registry), patch("urllib.request.urlopen") as request:
                self.assertIsNone(shared_service_startup("project", queue))
                request.assert_not_called()

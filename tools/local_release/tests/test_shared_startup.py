from io import BytesIO
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import atomic_json, capture, read_json
from local_release.hooks import shared_service_startup, unregister_startup
from local_release.service import identity, PRODUCT
from local_release import service


class SharedStartupTest(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'native Windows Startup shortcut')
    def test_shell_startup_shortcut_launches_hidden_logged_server_and_reuses_it(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            registry = root / 'state/registry.json'
            atomic_json(registry, {'schema': 1, 'projects': {}})
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', 0))
                port = probe.getsockname()[1]
            appdata = root / 'roaming'
            (appdata / 'Microsoft/Windows/Start Menu/Programs/Startup').mkdir(parents=True)
            with patch.dict(os.environ, APPDATA=str(appdata)):
                shortcut = service.install_startup(registry, port)
            startup = read_json(registry.parent / 'startup.json')
            self.assertIn('start-service', startup['arguments'])
            env = dict(os.environ, AI11_TEST_STARTUP=str(shortcut))
            try:
                capture(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                         'Start-Process -FilePath $env:AI11_TEST_STARTUP -WindowStyle Hidden'], env=env)
                deadline = time.monotonic() + 60
                while not (registry.parent / 'service.json').exists() and time.monotonic() < deadline:
                    time.sleep(.1)
                before = read_json(registry.parent / 'service.json')
                self.assertEqual(service.start(registry, port), f'http://127.0.0.1:{port}')
                self.assertEqual(before['pid'], read_json(registry.parent / 'service.json')['pid'])
                self.assertTrue((registry.parent / 'service.log').is_file())
            finally:
                service.stop(registry, port)
                # HTTP closes before the detached pythonw releases its log.
                # Wait on this fixture-owned file before TemporaryDirectory cleanup.
                deadline = time.monotonic() + 5
                while True:
                    try:
                        (registry.parent / 'service.log').unlink(missing_ok=True)
                        break
                    except PermissionError:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(.1)

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

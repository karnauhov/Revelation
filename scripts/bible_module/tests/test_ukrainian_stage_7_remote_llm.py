from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ROOT = ROOT / "scripts" / "bible_module"
REGISTRY_PATH = SCRIPT_ROOT / "stage7_remote_llm_models.json"
PILOT_CHECKPOINT_PATH = (
    SCRIPT_ROOT
    / "reports"
    / "ukrainian_stage_7_20260801"
    / "local_llm_remote_pilot_checkpoint.manifest.json"
)


class UkrainianStage7RemoteLlmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_is_pinned_licensed_and_fits_verified_host_storage(self) -> None:
        registry = self.registry
        self.assertEqual(registry["schema_version"], 1)
        self.assertEqual(registry["runtime"]["release"], "b10545")
        self.assertEqual(registry["runtime"]["license"], "MIT")
        model_ids = [row["model_id"] for row in registry["models"]]
        self.assertEqual(len(model_ids), len(set(model_ids)))
        total_bytes = 0
        for model in registry["models"]:
            self.assertEqual(model["license"], "Apache-2.0")
            self.assertRegex(model["commit"], r"^[0-9a-f]{40}$")
            self.assertEqual(model["reasoning"], "on")
            self.assertGreater(model["reasoning_budget"], 0)
            model_bytes = 0
            for item in model["files"]:
                self.assertIn(model["commit"], item["url"])
                self.assertRegex(item["sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(item["size_bytes"], 0)
                model_bytes += item["size_bytes"]
            self.assertLess(model_bytes, 11 * 1024**3)
            total_bytes += model_bytes
        self.assertLess(total_bytes, 40_000_000_000)

    def test_service_binds_only_verified_lan_address_and_disables_web_ui(self) -> None:
        task = (SCRIPT_ROOT / "stage7_remote_llm_task.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("target_host_contract.service_host_ipv4", task)
        self.assertNotIn("'--host', '0.0.0.0'", task)
        self.assertIn("'--no-webui'", task)
        self.assertIn("'--reasoning-format', 'deepseek'", task)
        self.assertIn("'-dev', 'CUDA0'", task)
        self.assertIn("'-ngl', '99'", task)
        host_service = (
            SCRIPT_ROOT / "stage7_remote_llm_host_service.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("$startupTimeoutMinutes = 15", host_service)
        self.assertIn("AddMinutes($startupTimeoutMinutes)", host_service)

    def test_setup_restricts_ports_and_uses_only_public_ssh_key(self) -> None:
        setup = (SCRIPT_ROOT / "setup_stage7_remote_llm_host.ps1").read_text(
            encoding="utf-8"
        )
        package = (SCRIPT_ROOT / "prepare_stage7_remote_llm_package.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("-RemoteAddress $OwnerLaptopAddress", setup)
        self.assertIn("-LocalPort 22", setup)
        self.assertIn("-LocalPort 8080", setup)
        self.assertIn("revelation_stage7_ed25519.pub", setup)
        self.assertNotRegex(
            package,
            re.compile(r"Get-Content[^\n]*\$PrivateKeyPath", re.IGNORECASE),
        )
        self.assertNotRegex(package, re.compile(r"Copy-Item[^\n]*PrivateKey", re.IGNORECASE))
        self.assertIn("contains_private_key = $false", package)

    def test_setup_captures_native_stderr_without_powershell_51_false_failure(self) -> None:
        setup = (SCRIPT_ROOT / "setup_stage7_remote_llm_host.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("function Invoke-NativeCapture", setup)
        self.assertIn("$ErrorActionPreference = 'Continue'", setup)
        self.assertIn("$nativeExitCode = $LASTEXITCODE", setup)
        self.assertIn("if ($nativeExitCode -ne 0)", setup)
        self.assertNotIn("(& $runtimePath '--version' 2>&1", setup)
        self.assertNotIn("(& $runtimePath '--list-devices' 2>&1", setup)

    def test_week_queue_is_fail_closed_until_reviewed_pilot_verdict(self) -> None:
        controller = (SCRIPT_ROOT / "manage_stage7_remote_llm.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("remote_pilot_verdict.json", controller)
        self.assertIn("$verdict.passed -ne $true", controller)
        self.assertIn("$verdict.model_id -ne $ModelId", controller)
        self.assertIn("finally", controller)
        self.assertIn("Stop-RemoteModel", controller)
        self.assertIn("[uint32]2147483649", controller)
        self.assertIn("[uint32]2147483648", controller)
        self.assertNotIn("SetThreadExecutionState(0x", controller)

    def test_remote_pilot_checkpoint_keeps_failed_models_candidate_only(self) -> None:
        checkpoint = json.loads(PILOT_CHECKPOINT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["schema_version"], 1)
        self.assertEqual(checkpoint["processed_count"], 3)
        self.assertEqual(checkpoint["error_count"], 2)
        self.assertEqual(
            checkpoint["status"],
            "complete_remote_gpu_pilot_all_models_candidate_only",
        )
        self.assertEqual(checkpoint["host"]["final_status"], "stopped")
        self.assertFalse(checkpoint["verdict"]["remote_pilot_verdict_created"])
        self.assertFalse(checkpoint["verdict"]["weekly_queue_authorized"])
        self.assertIsNone(checkpoint["verdict"]["gold_review_capable_model_id"])
        qwen9 = checkpoint["models"][0]
        self.assertEqual(qwen9["matching_decisions"], 12)
        self.assertEqual(qwen9["total_decisions"], 67)
        self.assertLess(qwen9["exact_link_null_agreement"], 0.8)

    def test_remote_workflow_has_no_stage8_or_sqlite_action(self) -> None:
        names = [
            "stage7_remote_llm_task.ps1",
            "stage7_remote_llm_host_service.ps1",
            "setup_stage7_remote_llm_host.ps1",
            "prepare_stage7_remote_llm_package.ps1",
            "manage_stage7_remote_llm.ps1",
        ]
        content = "\n".join(
            (SCRIPT_ROOT / name).read_text(encoding="utf-8").lower()
            for name in names
        )
        self.assertNotIn("stage_8", content)
        self.assertNotIn("sqlite", content)

    def test_operator_guide_documents_fail_closed_remote_sequence(self) -> None:
        guide = (
            ROOT
            / "docs"
            / "ru"
            / "content"
            / "ukrainian-bible-strongs-stage-7-remote-llm-operator-guide.ru.md"
        ).read_text(encoding="utf-8")
        required_commands = [
            "-Action TestSsh",
            "-Action Status",
            "-Action ListModels",
            "-Action BenchmarkAll",
            "-Action RunWeekQueue",
            "-Action Stop",
        ]
        for command in required_commands:
            self.assertIn(command, guide)
        self.assertLess(guide.index("-Action BenchmarkAll"), guide.index("-Action RunWeekQueue"))
        self.assertIn("remote_pilot_verdict.json", guide)
        self.assertIn("1 018 verse-runs", guide)
        self.assertIn("Копировать что-либо с компьютера Назара не требуется", guide)


if __name__ == "__main__":
    unittest.main()

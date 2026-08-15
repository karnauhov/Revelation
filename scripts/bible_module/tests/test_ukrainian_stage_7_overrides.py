"""CC0 fail-closed contracts for versioned Ukrainian stage-7 overrides."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.bible_module.ukrainian_stage_7_model import (
    override_is_current,
    validate_versioned_alignment_overrides,
)


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "ukrainian_stage_7"
    / "override_contract_cases.json"
)


class Stage7OverrideContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def _validate(
        self,
        rows: list[dict[str, object]],
        *,
        current: dict[str, object] | None = None,
    ):
        current = current or self.fixture["current"]
        return validate_versioned_alignment_overrides(
            rows,
            source_registry_sha256=current["source_registry"],
            stage6_text_sha256=current["stage6_text"],
            stage6_verse_sha256_by_target_token_id=current["verse_by_target_id"],
            legacy_snapshot_sha256=current["legacy_snapshot"],
            fingerprint_sha256=current["fingerprint"],
            fingerprint_selected_original_layer_sha256=current[
                "fingerprint_selected_original_layer"
            ],
            source_apparatus_sha256_by_original_token_id=current[
                "source_apparatus_by_original_id"
            ],
        )

    def test_valid_legacy_and_textual_records_use_independent_current_inputs(self) -> None:
        validated = self._validate(
            [deepcopy(self.fixture["legacy"]), deepcopy(self.fixture["textual"])]
        )
        self.assertEqual(
            set(validated), {"fixture-legacy-v1", "fixture-textual-v1"}
        )

    def test_tampered_digest_and_extra_or_missing_digest_fail_closed(self) -> None:
        for mutation in ("tampered", "missing", "extra"):
            with self.subTest(mutation=mutation):
                row = deepcopy(self.fixture["legacy"])
                if mutation == "tampered":
                    row["input_digests"]["stage6_text"] = "0" * 64
                elif mutation == "missing":
                    del row["input_digests"]["legacy_snapshot"]
                else:
                    row["input_digests"]["self_asserted"] = "8" * 64
                with self.assertRaisesRegex(ValueError, "stale or tampered"):
                    self._validate([row])

    def test_tampered_source_registry_and_source_apparatus_fail_closed(self) -> None:
        changed_registry = deepcopy(self.fixture["current"])
        changed_registry["source_registry"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or tampered"):
            self._validate(
                [deepcopy(self.fixture["textual"])], current=changed_registry
            )

        missing_apparatus = deepcopy(self.fixture["current"])
        del missing_apparatus["source_apparatus_by_original_id"][
            "orig:alternative"
        ]
        with self.assertRaisesRegex(ValueError, "source apparatus"):
            self._validate(
                [deepcopy(self.fixture["textual"])], current=missing_apparatus
            )

    def test_dangling_target_or_tampered_verse_fail_closed(self) -> None:
        dangling = deepcopy(self.fixture["legacy"])
        dangling["stable_oh1988_token_ids"] = ["uk7:AAA:001:9:13"]
        with self.assertRaisesRegex(ValueError, "stage6 verse"):
            self._validate([dangling])

        tampered = deepcopy(self.fixture["legacy"])
        tampered["input_digests"]["verse"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or tampered"):
            self._validate([tampered])

        changed_verse = deepcopy(self.fixture["current"])
        changed_verse["verse_by_target_id"]["uk7:AAA:001:0:4"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale or tampered"):
            self._validate(
                [deepcopy(self.fixture["legacy"])], current=changed_verse
            )

    def test_fingerprint_selected_layer_and_legacy_snapshot_are_current_locked(self) -> None:
        cases = (
            ("legacy", "legacy_snapshot"),
            ("textual", "fingerprint"),
            ("textual", "fingerprint_selected_original_layer"),
        )
        for row_name, current_key in cases:
            with self.subTest(input=current_key):
                current = deepcopy(self.fixture["current"])
                current[current_key] = "0" * 64
                with self.assertRaisesRegex(ValueError, "stale or tampered"):
                    self._validate(
                        [deepcopy(self.fixture[row_name])], current=current
                    )

    def test_explicit_or_missing_stale_flag_fails_closed(self) -> None:
        for value in (True, None):
            with self.subTest(stale=value):
                row = deepcopy(self.fixture["legacy"])
                if value is None:
                    del row["stale"]
                else:
                    row["stale"] = value
                with self.assertRaisesRegex(ValueError, "stale"):
                    self._validate([row])

    def test_duplicate_ids_cycle_and_missing_superseded_id_fail_closed(self) -> None:
        duplicate = [
            deepcopy(self.fixture["legacy"]),
            deepcopy(self.fixture["legacy"]),
        ]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self._validate(duplicate)

        left = deepcopy(self.fixture["legacy"])
        right = deepcopy(self.fixture["legacy"])
        left["override_id"] = "fixture-left"
        right["override_id"] = "fixture-right"
        left["supersedes"] = "fixture-right"
        right["supersedes"] = "fixture-left"
        with self.assertRaisesRegex(ValueError, "cycle"):
            self._validate([left, right])

        missing = deepcopy(self.fixture["legacy"])
        missing["supersedes"] = "fixture-not-present"
        with self.assertRaisesRegex(ValueError, "missing ID"):
            self._validate([missing])

    def test_valid_supersedes_chain_returns_only_active_records(self) -> None:
        old = deepcopy(self.fixture["legacy"])
        current = deepcopy(self.fixture["legacy"])
        old["override_id"] = "fixture-legacy-v0"
        current["override_id"] = "fixture-legacy-v1"
        current["supersedes"] = old["override_id"]
        validated = self._validate([old, current])
        self.assertEqual(set(validated), {"fixture-legacy-v1"})

    def test_generic_current_check_requires_exact_digest_key_set(self) -> None:
        digest = "a" * 64
        override = {"stale": False, "input_digests": {"stage6_text": digest}}
        self.assertFalse(
            override_is_current(
                override,
                {"stage6_text": digest, "source_registry": "b" * 64},
            )
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

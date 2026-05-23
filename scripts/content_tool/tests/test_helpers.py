from __future__ import annotations

import unittest

from scripts.content_tool.helpers import GREEK_DESC_GROUP_RANGES


class GreekDescGroupRangesTest(unittest.TestCase):
    def test_extended_ranges_cover_only_attested_na28_lxx_keys(self) -> None:
        extended_ranges = [
            (start_id, end_id)
            for start_id, end_id in GREEK_DESC_GROUP_RANGES
            if start_id > 5624
        ]

        extended_count = sum(
            end_id - start_id + 1 for start_id, end_id in extended_ranges
        )

        self.assertEqual(extended_count, 88)
        self.assertIn((6000, 6003), extended_ranges)
        self.assertIn((20833, 20833), extended_ranges)
        self.assertFalse(
            any(start_id <= 21502 <= end_id for start_id, end_id in extended_ranges)
        )


if __name__ == "__main__":
    unittest.main()

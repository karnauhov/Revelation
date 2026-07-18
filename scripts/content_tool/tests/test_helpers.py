from __future__ import annotations

import unittest

from scripts.content_tool.helpers import GREEK_DESC_GROUP_RANGES


class GreekDescGroupRangesTest(unittest.TestCase):
    def test_ranges_stop_at_classic_greek_strong_boundary(self) -> None:
        self.assertEqual(GREEK_DESC_GROUP_RANGES[-1], (5506, 5624))
        self.assertFalse(
            any(start_id > 5624 for start_id, _ in GREEK_DESC_GROUP_RANGES)
        )
        self.assertFalse(
            any(end_id > 5624 for _, end_id in GREEK_DESC_GROUP_RANGES)
        )


if __name__ == "__main__":
    unittest.main()

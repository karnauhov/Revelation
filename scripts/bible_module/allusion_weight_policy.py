"""Editable Greek Strong weights used by the LXX/TR index publisher."""
from __future__ import annotations

from collections import defaultdict
import json
import math
from pathlib import Path

POLICY_FILE = Path(__file__).resolve().parent / "data/greek_strong_weights.json"


def expand_policy(policy: dict) -> list[float]:
    """Expand the default and disjoint exceptions to a G-number-indexed array."""
    last = policy["last_strong_number"]
    if type(last) is not int or not 1 <= last <= 65535:
        raise ValueError("Invalid Greek Strong number range")

    def checked_weight(value):
        value = float(value)
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Invalid semantic weight {value}")
        return value

    default = checked_weight(policy["default_weight"])
    weights = [0.0] + [default] * last
    seen = set()
    for key, numbers in policy["exceptions_by_weight"].items():
        weight = checked_weight(key)
        for number in numbers:
            if type(number) is not int or not 1 <= number <= last or number in seen:
                raise ValueError(f"Invalid or duplicate exception G{number}")
            seen.add(number)
            weights[number] = weight
    return weights


def read_policy(path: Path = POLICY_FILE) -> tuple[int, list[float]]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    version = policy["policy_version"]
    if type(version) is not int or version < 1:
        raise ValueError("Invalid semantic policy version")
    return version, expand_policy(policy)


def compact_policy(entries, version):
    groups = defaultdict(list)
    for number in range(1, len(entries) + 1):
        weight = entries[f"G{number}"]["weight"]
        if weight != 1.0:
            groups[weight].append(number)
    return {
        "policy_version": version,
        "last_strong_number": len(entries),
        "default_weight": 1.0,
        "exceptions_by_weight": {str(k): groups[k] for k in sorted(groups)},
    }

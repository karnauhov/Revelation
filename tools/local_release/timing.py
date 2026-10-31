"""Stage timing, including retries, without double-counting nested stages."""

import math
import time


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def latest_seconds(row, *, running=False, session=None, now=None, monotonic=None):
    if row.get("status") == "running":
        if not running:
            return None
        started = row.get("monotonic_started")
        if row.get("session_id") == session and session and number(started):
            elapsed = (time.monotonic() if monotonic is None else monotonic) - started
            return elapsed if number(elapsed) else None
        end = time.time() if now is None else now
    elif number(row.get("duration_seconds")):
        return row["duration_seconds"]
    else:
        end = row.get("finished")
    started = row.get("started")
    if isinstance(started, (int, float)) and isinstance(end, (int, float)):
        elapsed = end - started
        return elapsed if number(elapsed) else None
    return None


def cumulative_seconds(row, **clock):
    if row.get("status") != "running" and number(row.get("total_duration_seconds")):
        return row["total_duration_seconds"]
    latest = latest_seconds(row, **clock)
    return row.get("prior_duration_seconds", 0) + latest if latest is not None else None


def summarize(result, *, running=False, now=None, monotonic=None):
    steps = {**result.get("timing_totals", {}), **result.get("steps", {})}
    roots = []
    for name, row in steps.items():
        parent = row.get("parent_step")
        if parent:
            continue
        # Old results predate explicit parent links. Integration file stages
        # already belong to their aggregate integration-<platform> timer.
        if "parent_step" not in row and name.startswith("integration-"):
            parent = next((key for key in steps if key.count("-") == 1 and name.startswith(key + "-")), None)
            if parent:
                continue
        roots.append(row)
    clock = {"running": running, "session": result.get("session_id"), "now": now, "monotonic": monotonic}
    values = [cumulative_seconds(row, **clock) for row in roots]
    latest = latest_seconds(steps.get(result.get("current_step"), {}), **clock)
    return {"seconds": sum(value for value in values if value is not None),
        "available": any(value is not None for value in values),
        "partial": any(value is None for value in values) or any(row.get("timing_partial", False) for row in roots),
        "estimated": any(not row.get("timing_exact", False) for row in roots),
        "current_seconds": latest if running else None,
        "steps_measured": sum(value is not None for value in values), "steps_total": len(roots)}

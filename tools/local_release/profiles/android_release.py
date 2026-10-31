"""Keep Android's generated plugin paths on the physical builder drive."""

import json
from pathlib import Path

from ..core import ReleaseError, atomic_json


def plugin_paths_valid(ctx):
    index = ctx.workspace / ".flutter-plugins-dependencies"
    try:
        plugins = json.loads(index.read_text(encoding="utf-8"))["plugins"]["android"]
        if not plugins:
            return False
        for plugin in plugins:
            path = Path(plugin["path"])
            if not path.is_absolute() or not path.is_dir():
                return False
            # Local overrides must use the physical checkout, never its
            # temporary MSBuild SUBST alias (which is removed after a run).
            local = ctx.workspace / "third_party" / plugin["name"]
            if local.exists() and path.resolve() != local.resolve():
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def dependencies(ctx, *, force=False):
    if force or not plugin_paths_valid(ctx):
        ctx.command(["flutter", "pub", "get"], cwd=ctx.workspace)
    if not plugin_paths_valid(ctx):
        raise ReleaseError("Android plugin paths are missing or still reference a temporary workspace alias")


def recover_cache(ctx):
    """Repair stale paths, then evaluate Gradle without deleting valid builds."""
    evidence = ctx.directory / "results/windows-android-cache-recovery.json"
    previous = dict(ctx.result["steps"].get("android-cache-recovery", {}))

    def action():
        dependencies(ctx, force=True)
        wrapper = ctx.workspace / "android/gradlew.bat"
        ctx.command([wrapper, "help", "--offline"], cwd=ctx.workspace / "android")
        atomic_json(evidence, {"schema": 1, "sha": ctx.job["sha"],
            "cause": "Generated Android plugin paths referenced a detached temporary SUBST drive",
            "physical_workspace": str(ctx.workspace), "plugin_paths_valid": True,
            "gradle_configuration": "passed", "previous_attempt": previous})

    ctx.stage("android-cache-recovery", action,
              ["results/windows-android-cache-recovery.json"])

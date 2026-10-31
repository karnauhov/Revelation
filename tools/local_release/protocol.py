"""Versioned, source-preserving exchange contract for independent OS builders."""

from pathlib import Path

from .core import ReleaseError, digest, inside

VERSION = 2
SOURCE_FIELDS = ("project", "repository", "run_id", "sha", "version", "build", "tag",
                 "source_bundle_sha256", "compile_defines_sha256", "profile", "artifacts", "architectures")


def same_source(old, new):
    return all(old.get(key) == new.get(key) for key in SOURCE_FIELDS)


def validate_upgrade(old, new):
    if not same_source(old, new):
        raise ReleaseError("Runtime update changes immutable release source identity")
    if new.get("protocol_version", 1) > VERSION:
        raise ReleaseError("Update this computer's bootstrap for the newer exchange protocol")
    if new.get("preparation_revision", 1) <= old.get("preparation_revision", 1):
        raise ReleaseError("Runtime update is not newer than the installed revision")
    for host, gates in old["required_steps"].items():
        if not set(gates) <= set(new["required_steps"].get(host, [])):
            raise ReleaseError("Runtime update removes required release gates")


def draft_packages(ctx):
    """A structurally checked package can be backed up before the whole run passes."""
    records = {}
    specifications = ctx.job.get("artifact_specs")
    if not specifications:
        # Old jobs keep their original all-host gate until explicitly upgraded.
        if not all(ctx.result["steps"].get(s, {}).get("status") == "passed"
                   for s in ctx.job["required_steps"][ctx.host]):
            return records
        specifications = {name: {"host": ctx.host, "gates": []} for name in ctx.job["artifacts"]}
    for name, specification in specifications.items():
        if specification["host"] != ctx.host:
            continue
        path = inside(ctx.output, name)
        expected = next((step.get("outputs", {}).get("packages/" + name)
                         for step in ctx.result["steps"].values()
                         if step.get("status") == "passed" and "packages/" + name in step.get("outputs", {})), None)
        if path.is_file() and expected and digest(path) == expected:
            inspected = all(ctx.result["steps"].get(s, {}).get("status") == "passed" for s in specification["gates"])
            records[name] = {"sha256": expected, "verification": "structure_verified" if inspected else "built_unverified",
                             "gates": specification["gates"]}
    return records

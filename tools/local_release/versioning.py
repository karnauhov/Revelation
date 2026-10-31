"""One commit-msg version increment, using the project's existing helper."""

import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

from .core import ReleaseError, atomic_json, git, inside, read_json, hidden_flags
from .hooks import hook_directory

MARKER = "# AI11 synchronized build number v1"


def commit(repo, profile, message):
    if "[skip ci]" in message.read_text(encoding="utf-8"):
        pending = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "ai11-version-pending.json"))
        if pending.exists():
            from .core import digest
            plan = read_json(pending)
            if plan["base_head"] == git(repo, "rev-parse", "HEAD") and plan.get("before"):
                if any(digest(inside(repo, name)) != expected for name, expected in plan["after"].items()):
                    raise ReleaseError("Pending version files were edited; preserve and reconcile them before retry")
                for name, value in plan["before"].items():
                    inside(repo, name).write_bytes(bytes.fromhex(value))
                git(repo, "add", "--", *plan["files"])
                plan["after"] = {name: digest(inside(repo, name)) for name in plan["files"]}
                atomic_json(pending, plan)
        return
    settings = read_json(profile)["versioning"]
    pending_path = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "ai11-version-pending.json"))
    pending_plan = read_json(pending_path) if pending_path.exists() else None
    files = settings["files"]
    paths = [inside(repo, name) for name in files]
    if git(repo, "diff", "--name-only", "--", *files):
        raise ReleaseError("Version files have unstaged changes; stage them explicitly before committing")
    before = {path: path.read_bytes() for path in paths}
    helper = inside(repo, settings["helper"])
    head = git(repo, "show", "HEAD:pubspec.yaml")
    current = (repo / "pubspec.yaml").read_text(encoding="utf-8")
    pattern = r"^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$"
    old, new = re.search(pattern, head, re.M), re.search(pattern, current, re.M)
    if not old or not new:
        raise ReleaseError("Cannot determine indexed release version")
    # A failed signing attempt leaves the already bumped version staged. Reuse
    # it on retry, and respect an explicit helper-managed version change.
    arguments = (["set-version", new[1], "--build", new[2]] if int(new[2]) > int(old[2]) or new[1] != old[1] else ["inc-build"])
    try:
        process = subprocess.run([sys.executable, str(helper), "--repo-root", str(repo), *arguments],
                                 capture_output=True, text=True, check=False, creationflags=hidden_flags())
        if process.returncode:
            raise ReleaseError("Project version helper failed; version files restored")
        git(repo, "add", "--", *files)
        from .core import digest
        original = (pending_plan["before"] if pending_plan and pending_plan["base_head"] == git(repo, "rev-parse", "HEAD")
                    else {name: before[inside(repo, name)].hex() for name in files})
        atomic_json(pending_path,
                    {"base_head": git(repo, "rev-parse", "HEAD"), "files": files,
                     "before": original,
                     "after": {name: digest(inside(repo, name)) for name in files}})
    except BaseException:
        for path, value in before.items():
            path.write_bytes(value)
        raise


def finalize(repo, profile):
    pending = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "ai11-version-pending.json"))
    if not pending.exists():
        return
    plan = read_json(pending)
    if git(repo, "rev-parse", "HEAD") == plan["base_head"]:
        return
    changed = git(repo, "diff", "--cached", "--name-only").splitlines()
    if not set(changed) <= set(plan["files"]):
        raise ReleaseError("Version finalization found unrelated staged changes; checkpoint preserved")
    if changed:
        # Git caches the tree before commit-msg. Fold only the four helper
        # outputs into the just-created commit, with all hooks disabled for
        # this internal amend. The visible history has one logical commit.
        empty = hook_directory(repo) / "ai11-version-no-hooks"
        empty.mkdir(exist_ok=True)
        command = ["-c", "core.hooksPath=" + str(empty), "commit", "--amend", "--no-edit", "--no-verify", "--allow-empty"]
        if "\ngpgsig " in "\n" + git(repo, "cat-file", "-p", "HEAD"):
            command.append("--gpg-sign")
        git(repo, *command)
    pending.unlink()


def install(repo, profile):
    directory = hook_directory(repo)
    directory.mkdir(parents=True, exist_ok=True)
    hook = directory / "commit-msg"
    if hook.exists() and MARKER in hook.read_text(encoding="utf-8"):
        return hook
    # Avoid layering a second counter over a legacy project-specific hook.
    for name in ("pre-commit", "prepare-commit-msg", "commit-msg", "post-commit"):
        path = directory / name
        if path.exists() and re.search(r"inc-build|bump-build|update_release_version|MyAppBuild|msix_version", path.read_text(encoding="utf-8"), re.I):
            raise ReleaseError("Existing version hook requires reconciliation before installing another counter: " + name)
    settings = read_json(profile).get("versioning")
    if not settings:
        raise ReleaseError("This project has no versioning helper profile")
    inside(repo, settings["helper"])
    backup = directory / "commit-msg.before-local-release-version"
    post = directory / "post-commit"
    old_post = directory / "post-commit.before-local-release-version"
    if backup.exists() or old_post.exists():
        raise ReleaseError("Previous version-hook backup exists; preserve and inspect it")
    if hook.exists():
        hook.rename(backup)
    command = " ".join(shlex.quote(str(value).replace("\\", "/")) for value in (
        sys.executable, Path(__file__).with_name("cli.py").resolve(), "version-commit", "--repo", repo.resolve(),
        "--profile", profile.resolve(), "--message"))
    previous = shlex.quote(backup.as_posix())
    hook.write_text("#!/bin/sh\n" + MARKER + "\n" +
                    f"if [ -x {previous} ]; then {previous} \"$@\" || exit $?; fi\n" +
                    command + ' "$1"\n', encoding="utf-8", newline="\n")
    os.chmod(hook, 0o755)
    if post.exists():
        post.rename(old_post)
    final_command = " ".join(shlex.quote(str(value).replace("\\", "/")) for value in (
        sys.executable, Path(__file__).with_name("cli.py").resolve(), "version-finalize", "--repo", repo.resolve(), "--profile", profile.resolve()))
    post.write_text("#!/bin/sh\n" + MARKER + "\n" + final_command + " || exit $?\n" +
                    f"if [ -x {shlex.quote(old_post.as_posix())} ]; then {shlex.quote(old_post.as_posix())} \"$@\"; fi\n", encoding="utf-8", newline="\n")
    os.chmod(post, 0o755)
    return hook


def remove(repo):
    hook = hook_directory(repo) / "commit-msg"
    if not hook.exists() or MARKER not in hook.read_text(encoding="utf-8"):
        raise ReleaseError("Version hook differs; preserve it for inspection")
    hook.unlink()
    backup = hook.with_name("commit-msg.before-local-release-version")
    if backup.exists():
        backup.rename(hook)
    post = hook_directory(repo) / "post-commit"
    if post.exists() and MARKER in post.read_text(encoding="utf-8"):
        post.unlink()
        backup = post.with_name("post-commit.before-local-release-version")
        if backup.exists():
            backup.rename(post)

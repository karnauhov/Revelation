---
name: revelation
description: Use for Revelation project release/version updates: increment build, set semantic version, and keep pubspec.yaml, setup.iss, snap/snapcraft.yaml, and snap/gui/revelation-x.desktop in sync. It also recalculates msix_version with rule third segment = patch + build.
---

# Revelation

Project-specific workflow for release version maintenance.

## When to use

Use this skill when the user asks to:
- increment build number
- set a new semantic version (`X.Y.Z`)
- synchronize release/version fields across project files

## Source of truth and rules

- Semantic version and build: `pubspec.yaml` (`version: X.Y.Z+BUILD`)
- MSIX version: `pubspec.yaml` (`msix_version: X.Y.(Z + BUILD).0`)
- Inno Setup values: `setup.iss` (`MyAppVersion`, `MyAppBuild`)
- Snap version: `snap/snapcraft.yaml` (`version: 'X.Y.Z.BUILD'`)
- Desktop entry version: `snap/gui/revelation-x.desktop` (`Version=X.Y.Z.BUILD`)

Rule:
- `msix_version` third segment is always `patch + build`

## Preferred command

Run the bundled script from repo root:

```bash
python .agents/skills/revelation/scripts/update_release_version.py <command>
```

Commands:

1. Increment build (keeps semantic version unchanged)

```bash
python .agents/skills/revelation/scripts/update_release_version.py inc-build
```

2. Set semantic version (keeps build unchanged by default)

```bash
python .agents/skills/revelation/scripts/update_release_version.py set-version 1.0.6
```

Optional build override:

```bash
python .agents/skills/revelation/scripts/update_release_version.py set-version 1.0.6 --build 140
```

## After update

- Verify modified files and values.
- Optionally run:

```bash
flutter analyze
```

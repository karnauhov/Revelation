---
name: revelation
description: Use for Revelation project release/version updates when asked to increment build number or sync release versions (e.g. "increase build number", "bump build", "увеличь билд номер", "подними билд"). Keeps pubspec.yaml, setup.iss, snap/snapcraft.yaml, and snap/gui/revelation-x.desktop in sync and recalculates msix_version with rule third segment = patch + build.
---

# Revelation

Project-specific workflow for release version maintenance.

## When to use

Use this skill when the user asks to:
- increment build number
- set a new semantic version (`X.Y.Z`)
- synchronize release/version fields across project files
- commands in Russian like: `увеличь билд номер`, `подними билд`, `инкремент билда`

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

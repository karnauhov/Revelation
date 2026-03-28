# Testing Strategy (EN)

Doc-Version: `2.0.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Purpose

Define the current testing baseline for Revelation.

## Test Layers

- Unit tests live in `test/` and cover cubits, services, repositories, router contracts, and shared helpers.
- Widget tests cover screen and widget behavior. Tagged widget runs are available when isolating that layer.
- Smoke integration tests live in `integration_test/smoke/`.
- Shared test helpers live in [`test/test_harness/README.md`](../../../test/test_harness/README.md).

## Usual Local Checks

```bash
dart format .
flutter analyze
flutter test
flutter test --tags widget
dart run scripts/check_forbidden_patterns.dart
dart run scripts/check_docs_sync.dart
```

Run `dart run scripts/check_docs_sync.dart` when a synchronized RU/EN doc pair changes.

## Automation

- `.github/workflows/flutter_build.yml` repeats format, analysis, tests, coverage filtering, and forbidden-pattern checks.
- `.github/workflows/integration_smoke.yml` runs the smoke suite on Android on schedule or on demand.

## Quality Rules

- New behavior or bug fixes should land with the nearest relevant unit or widget test.
- Tests should use deterministic fakes/stubs and should not depend on external network access.
- High-risk state flows should cover:
  - stale async race (`latest request wins`)
  - lifecycle safety (`close before async completes`)
  - rapid switching in primary source image-preview flows

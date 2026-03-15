# Testing Strategy (EN)

Doc-Version: `1.0.2`  
Last-Updated: `2026-03-15`  
Source-Commit: `working-tree`

## 1. Purpose
Define the required testing strategy for the current Revelation architecture.

## 2. Test Suites
- Unit: `test/` (cubit, router args, async guards, domain/service logic).
- Widget: `test/widget/` with `@Tags(['widget'])`.
- Integration smoke: `integration_test/smoke/` (manual workflow run).
- Harness: `test/test_harness/` with `fake_env`, `fake_logger`, `fake_remote`.

## 3. Mandatory Local Checks
```bash
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
flutter test --coverage
dart run scripts/coverage_baseline.dart --min-all=90.0
dart run scripts/check_forbidden_patterns.dart
```

## 4. CI Gates
- `.github/workflows/flutter_build.yml`:
  - format check
  - analyze
  - unit tests
  - widget tests
  - coverage + thresholds
  - forbidden patterns
- `.github/workflows/integration_smoke.yml`:
  - runs only via `workflow_dispatch`
  - executes `flutter test integration_test/smoke` on an Android emulator.

## 5. Test Quality Rules
- Changes in cubit/repository/router code must include relevant unit or widget tests.
- Bug fixes require regression tests.
- Tests must not depend on external network or unstable runtime conditions.
- UI scenarios should use deterministic fake/stub dependencies.
- For state-management changes in high-risk flows, regression scenarios are required:
  - stale async race (`latest request wins`);
  - lifecycle safety (`close before async completes`);
  - detail image-preview rapid-switch behavior (stale geometry and side-effect call-count).

## 6. Done Criteria
- All mandatory checks from sections 3 and 4 pass.
- For RU/EN docs changes, `dart run scripts/check_docs_sync.dart` is executed.

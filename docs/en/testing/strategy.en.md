# Testing Strategy (EN)

Doc-Version: `0.4.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define a verifiable testing strategy to support safe architectural refactoring.

## 2. Current Baseline
- Unit tests: minimal baseline (existing smoke/unit set).
- Widget tests: minimal smoke baseline exists and runs as a separate mandatory CI gate.
- Integration smoke tests: dedicated suite in `integration_test/smoke` with manual workflow execution.
- Build quality gates (pre-build): `format + analyze + unit + widget + forbidden patterns` in `.github/workflows/flutter_build.yml`.

## 3. Target Test Pyramid
- Unit tests: 60-70%.
- Widget tests: 25-35%.
- Integration smoke: 5-10% (selective).

## 4. Mandatory Gates
- Format check: `dart format --output=none --set-exit-if-changed .`
- Static analysis: `flutter analyze`
- Unit tests: `flutter test --exclude-tags widget`
- Widget tests: `flutter test --tags widget`
- Fast architectural grep checks for forbidden patterns.

## 5. Test Harness Baseline
- Fake logger: validate side effects and error paths without real Talker.
- Fake env: provide deterministic environment values (for example SUPABASE defines).
- Fake remote: emulate DB/file downloads without external network.

## 6. Regression Policy
- Any P0 task is considered complete only after analyze/tests pass.
- New architectural restrictions are enforced with a baseline allowlist first, preventing new violations without breaking legacy immediately.
- The allowlist must shrink as migration progresses.
- Integration smoke runs only manually via `workflow_dispatch`.
- CI execution of integration smoke runs in a dedicated workflow on Android emulator runner.

## 7. Execution Commands
```bash
dart format .
flutter analyze
flutter test --exclude-tags widget
flutter test --tags widget
flutter test integration_test/smoke
flutter test
dart run scripts/check_forbidden_patterns.dart
```

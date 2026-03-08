# Testing Strategy (EN)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-08`  
Source-Commit: `working-tree`

## 1. Purpose
Define a verifiable testing strategy to support safe architectural refactoring.

## 2. Current Baseline
- Unit tests: minimal baseline (existing smoke/unit set).
- Widget tests: not established as a mandatory layer.
- Integration tests: not part of the regular cycle yet.
- PR quality gates: before Phase 0 there was no complete `format + analyze + test` gate.

## 3. Target Test Pyramid
- Unit tests: 60-70%.
- Widget tests: 25-35%.
- Integration smoke: 5-10% (selective).

## 4. Phase 0 Mandatory Gates
- Format check: `dart format --output=none --set-exit-if-changed .`
- Static analysis: `flutter analyze`
- Tests: `flutter test`
- Fast architectural grep checks for forbidden patterns.

## 5. Test Harness Baseline
- Fake logger: validate side effects and error paths without real Talker.
- Fake env: provide deterministic environment values (for example SUPABASE defines).
- Fake remote: emulate DB/file downloads without external network.

## 6. Regression Policy
- Any P0 task is considered complete only after analyze/tests pass.
- New architectural restrictions are enforced with a baseline allowlist first, preventing new violations without breaking legacy immediately.
- The allowlist must shrink as migration progresses.

## 7. Execution Commands
```bash
dart format .
flutter analyze
flutter test
dart run scripts/check_forbidden_patterns.dart
```

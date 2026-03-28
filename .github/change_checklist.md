## Change Checklist
- [ ] Code follows module boundaries (`app/core/infra/shared/features`).
- [ ] No new `provider`/`ChangeNotifier`/`notifyListeners` usage in runtime code.
- [ ] `dart format .` executed.
- [ ] `flutter analyze` executed.
- [ ] `flutter test` executed (or targeted suite with rationale).
- [ ] `dart run scripts/check_forbidden_patterns.dart` executed.
- [ ] RU/EN docs pairs are synchronized where required by `AGENTS.md`.
- [ ] If dependencies changed in `pubspec.yaml`, `assets/data/about_libraries.xml` is synchronized.
- [ ] If integration smoke is needed, run `.github/workflows/integration_smoke.yml` manually (`workflow_dispatch`).

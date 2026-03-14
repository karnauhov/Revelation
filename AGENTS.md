# AGENTS.md

## Project Overview
- Revelation is a Flutter app for studying the Book of Revelation.
- The repository includes targets for web, Android, iOS, Windows, Linux, and macOS.
- The application entry point is `lib/main.dart`.

## Current Stack
- Dart SDK: `^3.9.0`
- Flutter with `flutter generate: true`
- Navigation: `go_router`
- State management target (mandatory): `BLoC/Cubit` (`flutter_bloc`)
- Dependency lookup: `get_it`
- Local persistence: `shared_preferences`
- Local database: `drift`, `drift_flutter`
- Remote downloads/storage: `supabase_flutter`
- Logging and route tracing: `talker_flutter`
- Desktop window handling: native platform runners (`windows/runner`, `linux/runner`)
- Localization: `flutter_localizations`, `intl`

## Repository Layout
- `lib/app/`: app bootstrap, DI, router, composition root
- `lib/core/`: cross-cutting contracts (`errors`, `async`, `platform`, `logging`, `audio`, diagnostics)
- `lib/infra/`: DB/remote/storage implementations (`db`, `remote`, `storage`)
- `lib/shared/`: reusable UI, config, localization helpers, navigation helpers, shared models/utils
- `lib/features/`: feature-first modules (`about`, `download`, `primary_sources`, `settings`, `topics`)
- `lib/l10n/`: ARB files and generated localization files
- `assets/data/`, `assets/images/`, `assets/sounds/`: app content and assets
- `web/db/`: localized SQLite files used by the web build
- `scripts/`: project tools for content/database work
- `.agents/skills/revelation/scripts/`: release/version sync tooling

## Working Rules
- Keep changes aligned with the current folder responsibilities in the repository layout above.
- State management policy is strict:
  - New or modified stateful presentation logic must use `BLoC/Cubit`.
  - Do not introduce new `provider`/`ChangeNotifier` usages.
  - When touching legacy `ChangeNotifier` flows, migrate the touched scope to `Cubit`/`Bloc` instead of extending legacy patterns.
- Any state-management contract change must be synchronized in:
  - `docs/ru/architecture/revelation_architecture_refactor_roadmap_ru.md`
  - `docs/ru/architecture/revelation_refactor_work_roadmap_ru.md`
  - `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md` and `docs/en/architecture/state_migration_matrix_phase_3_7.en.md`
  - `docs/ru/architecture/overview.ru.md` and `docs/en/architecture/overview.en.md`
  - `docs/ru/architecture/module-boundaries.ru.md` and `docs/en/architecture/module-boundaries.en.md`
- RU/EN docs sync policy is mandatory for approved pairs:
  - `docs/ru/architecture/overview.ru.md` <-> `docs/en/architecture/overview.en.md`
  - `docs/ru/architecture/module-boundaries.ru.md` <-> `docs/en/architecture/module-boundaries.en.md`
  - `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md` <-> `docs/en/architecture/state_migration_matrix_phase_3_7.en.md`
  - `docs/ru/testing/strategy.ru.md` <-> `docs/en/testing/strategy.en.md`
  - `docs/ru/architecture/residual_debt_backlog.ru.md` <-> `docs/en/architecture/residual_debt_backlog.en.md`
  - Policy source: `docs/ru/architecture/docs_sync_policy.ru.md` and `docs/en/architecture/docs_sync_policy.en.md`
  - Instruction workflow: `docs/ru/architecture/docs_sync_instruction_workflow.ru.md` and `.en.md`
- Keep package metadata synchronized between `pubspec.yaml` and `assets/data/about_libraries.xml`: when adding/removing a package in `dependencies` or `dev_dependencies`, add/remove the corresponding `@Package` entry in `about_libraries.xml` in the same change, and take license name plus links from the package page.
- Use change checklist from `.github/change_checklist.md` for every change set (code + tests + docs RU/EN).
- Keep localization in sync for supported locales: `en`, `es`, `uk`, `ru`.
- Do not commit secrets. `api-keys.json` is gitignored.
- `ServerManager` expects compile-time defines `SUPABASE_URL` and `SUPABASE_KEY`.
- The Snap packaging flow uses `--dart-define-from-file=api-keys.json`.
- If you change database content or language loading behavior, check both `lib/infra/db/` and `web/db/`.

## Generated Files
- Do not manually edit generated Drift files such as `lib/infra/db/**/*.g.dart`.
- Do not manually edit generated localization files such as `lib/l10n/app_localizations*.dart`.
- Treat generated platform plugin registrant files under platform folders as generated unless there is a clear reason to touch them.

## Common Commands
- Install dependencies: `flutter pub get`
- Format code: `dart format .`
- Static analysis: `flutter analyze`
- Tests: `flutter test`
- Docs sync check: `dart run scripts/check_docs_sync.dart`
- Generate Drift code: `dart run build_runner build --delete-conflicting-outputs`
- Watch Drift codegen: `dart run build_runner watch --delete-conflicting-outputs`
- Generate localization files: `flutter gen-l10n`

## Validation
- Run `dart format .` before finishing non-trivial code changes.
- Run `flutter analyze` before finishing non-trivial code changes.
- Run `flutter test` before finishing non-trivial code changes.
- When docs from approved RU/EN pairs are changed, run `dart run scripts/check_docs_sync.dart`.
- For state-architecture changes, run `rg "package:provider|ChangeNotifier|notifyListeners" lib test` and treat new matches as migration regressions.
- `flutter analyze` and `flutter test` pass in the repository state verified on March 7, 2026.

## Release Versioning
- Version values are synchronized across:
  - `pubspec.yaml`
  - `setup.iss`
  - `snap/snapcraft.yaml`
  - `snap/gui/revelation-x.desktop`
- Prefer the existing helper script instead of editing those files manually:
  - `python .agents/skills/revelation/scripts/update_release_version.py inc-build`
  - `python .agents/skills/revelation/scripts/update_release_version.py set-version X.Y.Z`
- The script keeps `pubspec.yaml` build metadata, `msix_version`, Inno Setup values, Snap version, and desktop entry version in sync.

## Release Checklist
- Update version information in the versioned project files listed above.
- Update `CHANGELOG.md`.
- Build the Snap package with `snapcraft_build.sh`, install it locally, and verify it.
- Commit the release changes for auto build.
- Deploy the website content in the separate `Revelation.website` repository.
- Deploy release artifacts to Snapcraft and GitHub Releases.
- Deploy mobile and store releases to Google Play and Microsoft Store.

## Database Update Checklist
- Upload the new DB file to the Supabase storage bucket used by the project.
- Copy the DB file into `web/db/`.
- Deploy the website content in the separate `Revelation.website` repository.

## References
- `README.md`: project overview and platform links
- `DEV_INFO.md`: release and DB deployment notes


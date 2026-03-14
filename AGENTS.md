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
  - Do not introduce `provider`/`ChangeNotifier`/`notifyListeners` in runtime or test code.
  - When touching non-cubit stateful flows, migrate the touched scope to `Cubit`/`Bloc`.
  - In `lib/features/**/presentation`, use only `bloc/`, `screens/`, and `widgets/` as target architecture folders; do not add `controllers/` or `coordinators/`.
  - In feature code, keep a single source of truth for each state slice; do not maintain parallel cubits/states for the same UI data.
  - Do not pass `BuildContext` into `application/**` services or `presentation/bloc/**`; localization and UI context-dependent work must stay in presentation UI layer.
  - For architecture moves/renames, update barrel exports, imports, related tests, and RU/EN architecture docs in the same change set.
  - Do not run business or cross-slice side effects from `build`; place them in cubit/listener/lifecycle hooks with idempotent guards.
  - For async cubit flows, after each `await` protect state application with `isClosed` and/or stale-request guards (`LatestRequestGuard` or equivalent).
  - Keep state/value contracts comparable: implement consistent value equality (`==/hashCode` or `Equatable`) for state-driven classes.
  - Do not add duplicate visibility flags in state (for example `imageShown`/`showDescription`) when visibility is derivable from existing data and UI modes.
  - In presentation, avoid direct repository/orchestrator construction where DI factories exist; use `AppDi` provisioning/factories.
  - For high-risk state-management fixes, add regression tests for stale async race, close-before-complete lifecycle, and side-effect call-count/rapid-switch behavior.
- Any state-management contract change must be synchronized in:
  - `docs/ru/architecture/state_management_matrix.ru.md` and `docs/en/architecture/state_management_matrix.en.md`
  - `docs/ru/architecture/overview.ru.md` and `docs/en/architecture/overview.en.md`
  - `docs/ru/architecture/module-boundaries.ru.md` and `docs/en/architecture/module-boundaries.en.md`
- RU/EN docs sync rules are mandatory for approved pairs:
  - `docs/ru/architecture/overview.ru.md` <-> `docs/en/architecture/overview.en.md`
  - `docs/ru/architecture/module-boundaries.ru.md` <-> `docs/en/architecture/module-boundaries.en.md`
  - `docs/ru/architecture/state_management_matrix.ru.md` <-> `docs/en/architecture/state_management_matrix.en.md`
  - `docs/ru/testing/strategy.ru.md` <-> `docs/en/testing/strategy.en.md`
- Sync rules:
  - Any semantic change in an RU document must include the EN twin update in the same change set.
  - Any semantic change in an EN document must include the RU twin update in the same change set.
  - For each RU/EN pair, `Doc-Version`, `Last-Updated`, and `Source-Commit` must match.
- Documentation navigation rule:
  - Every documentation file must be reachable either by a direct link from `README.md` or by links from another document when it is a 2nd+ level nested document.
  - When adding, renaming, or deleting docs, update navigation links in `README.md` and in related parent docs in the same change set.
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
- For state-architecture changes, run `rg "package:provider|ChangeNotifier|notifyListeners" lib test` and treat new matches as architecture regressions.
- For state-architecture changes, run `rg "BuildContext" lib/features --glob "**/application/**/*.dart" --glob "**/presentation/bloc/**/*.dart"` and treat matches as architecture regressions (except explicitly approved transitional adapters).
- For state-management changes in high-risk flows, ensure regression tests cover:
  - stale async race (`latest request wins`)
  - lifecycle safety (`close before async completes`)
  - side-effect call-count and rapid-switch UI scenarios (for example detail image-preview flows)
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

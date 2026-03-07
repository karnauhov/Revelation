# AGENTS.md

## Project Overview
- Revelation is a Flutter app for studying the Book of Revelation.
- The repository includes targets for web, Android, iOS, Windows, Linux, and macOS.
- The application entry point is `lib/main.dart`.

## Current Stack
- Dart SDK: `^3.9.0`
- Flutter with `flutter generate: true`
- Navigation: `go_router`
- State management: `provider` with `ChangeNotifier`
- Dependency lookup: `get_it`
- Local persistence: `shared_preferences`
- Local database: `drift`, `drift_flutter`
- Remote downloads/storage: `supabase_flutter`
- Logging and route tracing: `talker_flutter`
- Desktop window handling: `window_manager`
- Localization: `flutter_localizations`, `intl`

## Repository Layout
- `lib/screens/`: UI screens
- `lib/viewmodels/`: `ChangeNotifier` view models
- `lib/repositories/`: persistence and data access
- `lib/managers/`: app-wide managers such as DB and server initialization
- `lib/services/`: domain/content helpers
- `lib/db/`: Drift schema and generated database code
- `lib/l10n/`: ARB files and generated localization files
- `assets/data/`, `assets/images/`, `assets/sounds/`: app content and assets
- `web/db/`: localized SQLite files used by the web build
- `scripts/`: project tools for content/database work
- `.agents/skills/revelation/scripts/`: release/version sync tooling

## Working Rules
- Keep changes aligned with the current folder responsibilities in the repository layout above.
- Keep localization in sync for supported locales: `en`, `es`, `uk`, `ru`.
- Do not commit secrets. `api-keys.json` is gitignored.
- `ServerManager` expects compile-time defines `SUPABASE_URL` and `SUPABASE_KEY`.
- The Snap packaging flow uses `--dart-define-from-file=api-keys.json`.
- If you change database content or language loading behavior, check both `lib/db/` and `web/db/`.

## Generated Files
- Do not manually edit generated Drift files such as `lib/db/*.g.dart`.
- Do not manually edit generated localization files such as `lib/l10n/app_localizations*.dart`.
- Treat generated platform plugin registrant files under platform folders as generated unless there is a clear reason to touch them.

## Common Commands
- Install dependencies: `flutter pub get`
- Format code: `dart format .`
- Static analysis: `flutter analyze`
- Tests: `flutter test`
- Generate Drift code: `dart run build_runner build --delete-conflicting-outputs`
- Watch Drift codegen: `dart run build_runner watch --delete-conflicting-outputs`
- Generate localization files: `flutter gen-l10n`

## Validation
- Run `dart format .` before finishing non-trivial code changes.
- Run `flutter analyze` before finishing non-trivial code changes.
- Run `flutter test` before finishing non-trivial code changes.
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

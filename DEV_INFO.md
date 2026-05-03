# Operational Notes

This file contains short practical notes for local development, release work, and content maintenance.

## Environment

- The app expects compile-time defines `SUPABASE_URL` and `SUPABASE_KEY`.
- Sentry is enabled only when `SENTRY_DSN` is provided. Release builds should also provide `SENTRY_ENVIRONMENT=production`; `SENTRY_TRACES_SAMPLE_RATE` can lower the manual session transaction sample rate if the free quota needs protection.
- Debug symbol/source-map upload uses the Sentry Dart plugin and requires `SENTRY_AUTH_TOKEN` in CI or local release environments.
- Snap packaging uses `--dart-define-from-file=api-keys.json`.
- Working database files are edited in `%Documents%/revelation/db`.
- Web builds consume SQLite files from `web/db/`.
- Web DB version checks prefer `web/db/manifest.json`; the content tool button `Сохранить в проект` compares DB size/date between working DBs and `web/db`, rewrites only changed files, increments `data_version` only for rewritten DBs, and then refreshes `manifest.json`.
- Content tool release-publish config is stored locally in `env/content_tool_release_publish.env` (the `env/` folder is gitignored).

## Sentry Debug Artifacts

- CI uploads Sentry debug symbols/source maps from `.github/workflows/flutter_build.yml`.
- GitHub Actions must have the repository secret `SENTRY_AUTH_TOKEN`; the runtime DSN stays in `SENTRY_DSN`.
- `pubspec.yaml` keeps `upload_sources: true` for Sentry source context in Flutter web and Drift worker events; `commits: false` avoids requiring commit association permissions.
- Flutter web must be built with `--source-maps` before running `dart run sentry_dart_plugin`.
- After Sentry upload, remove generated web `*.map` files before publishing a public web archive.

Local release upload examples:

```powershell
$env:SENTRY_AUTH_TOKEN = "sntrys_your_token_here"
flutter build windows --release --no-tree-shake-icons --dart-define-from-file=api-keys.json
dart run sentry_dart_plugin --sentry-define=upload_source_maps=false
```

```powershell
$env:SENTRY_AUTH_TOKEN = "sntrys_your_token_here"
flutter build web --release --source-maps --dart-define-from-file=api-keys.json
dart run sentry_dart_plugin --sentry-define=upload_debug_symbols=false
$workspacePath = (Resolve-Path ".").Path
$webBuildPath = (Resolve-Path "build/web").Path
if (-not $webBuildPath.StartsWith($workspacePath)) { throw "Unexpected web build path: $webBuildPath" }
Get-ChildItem -LiteralPath $webBuildPath -Recurse -Filter "*.map" | Remove-Item -Force
```

## Release Versioning

Use the helper script instead of editing release files by hand:

```bash
python .agents/skills/revelation/scripts/update_release_version.py inc-build
python .agents/skills/revelation/scripts/update_release_version.py set-version X.Y.Z
```

The script keeps these files synchronized:

- `pubspec.yaml`
- `setup.iss`
- `snap/snapcraft.yaml`
- `snap/gui/revelation-x.desktop`

## Release Notes

- Update `CHANGELOG.md` only for notable user-visible changes.
- Build and verify the platforms that are part of the release.
- Publish updated website content in the separate `Revelation.website` repository when web assets or web DB files change.
- Publish release artifacts to the required stores and distribution channels for that release.

## Database Workflow

- Each working DB file (`revelation.sqlite`, `revelation_<lang>.sqlite`) must contain `db_metadata`.
- Required metadata keys are `schema_version`, `data_version`, and `date`.
- Schema changes must keep these values synchronized:
  - Drift `schemaVersion`
  - SQLite `PRAGMA user_version`
  - `db_metadata.schema_version`
  - distributed DB files in `%Documents%/revelation/db` and `web/db/`
- Every DB schema change must also review the content tool DB comparison/publish logic in `scripts/content_tool/mixins/core_db.py`. Update that logic and `scripts/content_tool/tests/test_core_db_metadata.py` whenever the schema change affects how DB differences should be detected or summarized (for example new tables to ignore, virtual/shadow tables, metadata-only tables, or changed publish semantics).
- After DB content updates, upload the new DB files to the Supabase storage bucket and copy the same files into `web/db/`; when you use the content tool publish button, `web/db/manifest.json` is refreshed automatically in the same step.
- Before using the content tool button `Опубликовать`, local working DB files, `web/db/`, and local `web/db/manifest.json` must already be synchronized via `Сохранить в проект`.

## Primary Sources Content

- The content tool lives in `scripts/content_tool/`.
- Run it with `python -m scripts.content_tool`.
- Preview images are stored as `common_resources` records in `revelation.sqlite`.
- Localized metadata and localized link titles are stored in `revelation_<lang>.sqlite`.
- Page images are expected under `%Documents%/revelation/primary_sources/...` with the same relative path as `page.image`.
- After changing primary source content, publish the updated DB files to Supabase, copy them to `web/db/`, and deploy the website content if needed.

## Deploy

- Deploy on [revelation.website](https://github.com/karnauhov/Revelation.website)
- Deploy on [Snapcraft](https://snapcraft.io/revelation-x/listing) and [GitHub Releases](https://github.com/karnauhov/Revelation/releases). See [commands for deploy](https://dashboard.snapcraft.io/snaps/revelation-x/upload/), then [move release to latest/stable](https://snapcraft.io/revelation-x/releases) and save
- Deploy on [Goole Play](https://play.google.com/console/u/1/developers/8693299089478158768/app/4975644827990074725/tracks/production)
- Deploy on [Microsoft Sore](https://partner.microsoft.com/ru-ru/dashboard/products/9NXHRR2P4087/overview)

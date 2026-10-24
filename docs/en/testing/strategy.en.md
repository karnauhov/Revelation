# Testing Strategy (EN)

Doc-Version: `2.1.2`
Last-Updated: `2026-10-24`
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

## Browser Database Opening Check

`integration_test/web_database_open_test.dart` checks 45 concurrent Drift worker requests, waiting for a shared lock, releasing it after a failure, and opening/reopening common and localized databases from `web/db/`. The connector's queue and Web Lock prevent overlapping OPFS probes as described in [Drift #3856](https://github.com/simolus3/drift/issues/3856).

Start a ChromeDriver compatible with the local Chrome on port 4444, then run locally:

```bash
flutter drive --release --driver=test_driver/integration_test.dart --target=integration_test/web_database_open_test.dart -d web-server --browser-name=chrome --headless --driver-port=4444 --web-port=8766
```

This uses a separate local origin without affecting the published site's data. On native devices this browser check is explicitly skipped and does not count as passed. Updated tabs on the same origin share a Web Lock; without Web Locks, the queue operates within one tab. Old open tabs do not participate in the new lock until they reload.

The first long press on a dictionary verse link is covered by `integration_test/strong_usage_preview_test.dart`. For Chrome, replace `--target` in the command above with this file; for Windows, run `flutter test integration_test/strong_usage_preview_test.dart -d windows`. The check verifies both a visible preview and copying the text exactly once.

## Local Bible Module Update Check

The native connector compares the SQLite file's own `schema_version` and `data_version` with the manifest even when file sizes match. Before replacement it validates integrity, size, and all advertised release metadata; a newer local release is preserved. A failed download is not reported as an update, and an old retained release is not reported as current. The manifest describes the expected release rather than proving installation.

`test/infra/db/connectors/local_database_sync_native_test.dart` covers same-size data/schema updates, reopening without another download, rejecting stale objects, network failure, corruption, and missing metadata. A shared queue serializes module discovery and local database updates; a regression with three parallel readers verifies a single download without overlapping temporary files. An `AboutScreen` widget test verifies the message for a retained stale release.

`integration_test/bible_module_update_test.dart` exercises the real path through local HTTP storage, download, the SQLite connector, repository, and reader screen. It checks visible text replacement, the installed version, no repeated download, and preserving a working copy when the manifest and object disagree. All files are synthetic and live in a temporary directory; working databases and Supabase are unaffected.

```bash
flutter test integration_test/bible_module_update_test.dart -d windows
```

On Web this native scenario is explicitly skipped and does not count as passed. Web uses a separate connector and a manifest token to reset storage on the next page launch; `web_db_version_sync_plan_test.dart` checks changed and unchanged tokens. Full version acceptance still requires a separate complete local run.

## Automation

- `.github/workflows/flutter_build.yml` repeats format, analysis, tests, coverage filtering, and forbidden-pattern checks.
- All integration tests, including smoke, run locally. The dedicated GitHub Actions workflow has been deleted and disabled; do not recreate or run it, including as a fallback for an unavailable local device.

## Acceptance for Every Version

- Prepare scenarios only for the version's new and changed functionality and directly affected interactions. Repeating full manual acceptance of the entire application is not required.
- Add or update integration tests for new and changed functionality, pages, windows, and dialogs in the same change set. Keep critical startup and navigation scenarios in `integration_test/smoke/`.
- Before acceptance and publication, run all integration tests locally, for example `flutter test integration_test -d <device-id>`, on applicable supported devices. Record an unavailable device or toolchain as a limitation, not a passing check; do not use GitHub Actions for this execution.
- For each manual scenario, record understandable preconditions, steps, expected and actual results, build, platform, language, and evidence. Codex performs available checks independently; owner participation is needed for domain decisions and actions unavailable to Codex.
- Maintain one current checklist and one complete current acceptance report per version. Repeat affected scenarios after fixes and retain material evidence.
- Publication and deployment are a separate version task after acceptance; verify the actual published builds and data.

## Quality Rules

- New behavior or bug fixes should land with the nearest relevant unit or widget test.
- Tests should use deterministic fakes/stubs and should not depend on external network access.
- High-risk state flows should cover:
  - stale async race (`latest request wins`)
  - lifecycle safety (`close before async completes`)
  - rapid switching in primary source image-preview flows

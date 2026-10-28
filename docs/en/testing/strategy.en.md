# Testing Strategy (EN)

Doc-Version: `2.4.3`
Last-Updated: `2026-10-28`
Source-Commit: `working-tree`

## Bible module information

Additional regressions check standalone language names (including the exact Russian nominative forms), absence of module code/ID even in expanded details, a constant 560-pixel dialog width with a narrow-screen cap, unchanged width after expansion/module changes, and actual multiline rendering of long titles and values. Local integration checks repeat language, hidden-ID and width assertions against installed files.

DB tests verify revision propagation and missing/invalid metadata; model tests verify version/date equality. Widget tests cover en/es/uk/ru at 420 and 1700 logical pixels, toolbar/overflow entry, switching to a module without metadata, stable revision dates, and preserved source/license text and links. Run `flutter test integration_test/bible_module_info_test.dart -d windows` locally to compare the dialog against the actual installed LXX/TR, KJV and OH1988 SQLite metadata in all four UI languages, expand the details and close the dialog. For Web, run the same target through local ChromeDriver and `flutter drive --release --driver=test_driver/integration_test.dart --target=integration_test/bible_module_info_test.dart -d web-server --browser-name=chrome --headless --driver-port=4444 --web-port=8770`. Installed candidates are required; native files are opened read-only, preferences are isolated, and no production download or publication occurs. This is targeted REV191 validation; full version acceptance remains REV236.

## Parallel reading and saved choices

`integration_test/smoke/bible_parallel_reading_smoke_test.dart` locally checks en/uk: two default panes, readable text, closing the translation through the toolbar/menu, reopening the saved single pane, following `bible:Мт17:5`, and an explicit `module` overriding the stored layout. Links do not overwrite preferences. It uses synthetic text, real routing/screens, and the SharedPreferences adapter with isolated test storage; production and user data are unchanged. Run `flutter test integration_test/smoke/bible_parallel_reading_smoke_test.dart -d windows`; for Web use local ChromeDriver and `flutter drive --release --driver=test_driver/integration_test.dart --target=integration_test/smoke/bible_parallel_reading_smoke_test.dart -d web-server --browser-name=chrome --headless --driver-port=4444 --web-port=8768`. This is targeted REV127 validation; full version acceptance remains REV236.

Widget tests exercise the same user flow at 420×900 and 1280×800, including toolbar overflow. Unit tests cover en/uk and missing es/ru translations, stored choices, reference priority, concurrent initial loads, closing while awaiting data, manual changes before automatic selection completes, stale module switches, and serialized rapid preference writes.

## First launch and reading recovery

`integration_test/first_reading_test.dart` exercises the real en/es/uk/ru language selector and settings persistence, a failed first module download, retrying on the same screen, reopening the installed copy offline, and installing a newer data version. Native runs use temporary Documents, synthetic SQLite, and loopback HTTP rather than working files or production Supabase. Run sequentially on local native devices: `flutter test integration_test/first_reading_test.dart -d <device-id>`. A Web skip of this suite is not a passing check. A separate `integration_test/smoke/bible_first_load_retry_smoke_test.dart` runs in Chrome using local `flutter drive --release` and ChromeDriver: after a controlled discovery failure, the real Web connector opens LXX/TR from local web/db. This checks UI recovery and actual reading rather than simulating browser network disconnection.

Unit regressions cover rapid retries, the original reference, stale responses, and close-before-complete; widget regressions cover the localized button and recovered verse in all four languages. Full bootstrap remains in startup smoke; full version acceptance is REV236. The [single current REV210 report](../../ru/testing/rev210-first-reading.ru.md) separates laboratory results, module availability, and the limits of existing analytics.

## Bible text modules and footnotes

OH1988 text-release coverage checks sealed input digests, full text/comment round trips, deterministic SQLite builds, failed replacement safety, and footnote binding. Content-tool Tk tests cover separate editing/filtering, transaction rollback, metadata increments and legacy compatibility. Flutter DB/model/repository/widget tests cover schema 3/4 without version changes, comment equality and propagation, exclusion from search/copy, and keyboard-accessible footnotes. Local Bible navigation smoke covers selecting OH1988, opening/closing a note, absence of an empty note action and existing Greek Strong navigation. Full version acceptance remains REV236; publication remains REV237.

## Local folder opening failures

`LocalFolderOpenException` preserves the resolved application folder path, original cause and stack when folder creation or launching fails. If path resolution itself fails, the About screen retains the generic localized message. Unit tests cover process exceptions, rejected desktop/mobile launches, creation failure, and unresolved paths; widget and localization contracts check exact paths with spaces and Unicode in all four languages.

Run `flutter test integration_test/about_local_folder_test.dart -d windows` locally to exercise the About screen's actual Tools action through native directory creation and a deliberately failing launcher boundary in en/es/uk/ru. The check uses temporary folders and never opens a file manager or changes working databases. On Web the native-only check is explicitly skipped, not counted as passed. Other native devices may run the same suite; record only devices actually tested.

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

## Android System Bars and Release Optimization

Android startup explicitly enables `SystemUiMode.edgeToEdge` before rendering. Unit tests check call order and leave other platforms unchanged. Splash widget tests cover portrait system bars and landscape cutouts. The local `integration_test/smoke/app_startup_smoke_test.dart` checks the splash, menu, and drawer against actual system insets; on Android it also requires nonzero status-bar insets and verifies landscape rotation. Run it locally with `flutter test integration_test/smoke/app_startup_smoke_test.dart -d <android-device-id>`. This native command runs in Debug and does not accept `--release`. Separately build and install a release APK, then check startup, the drawer, and reader navigation: R8 does not optimize debug builds. Run Flutter builds and tests sequentially because they share generated plugin registrants.

CI and local validation use Flutter 3.47.2 with its supported Android toolchain: AGP 9.1.0, Gradle 9.3.1, Kotlin Gradle Plugin 2.4.0, and Java 17. AGP 9 enables optimized resource shrinking by default; Flutter enables release minification, resource shrinking, and optimized default ProGuard rules. Keep Flutter/plugin consumer rules, including reflection-related rules. Kotlin uses `compilerOptions` rather than the removed `kotlinOptions` DSL. Retain `android.builtInKotlin=false` for unmigrated plugins and `android.newDsl=false` for Flutter's legacy DSL compatibility; these are temporary supported migration bridges. See [Android R8 guidance](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization) and [Flutter Kotlin migration](https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin).

Play Console recommendations describe the uploaded artifact, currently 1.0.7+172. Deprecated system-bar color calls can remain in Flutter/AndroidX for older Android versions; absence of application-owned calls does not prove the warning has disappeared. Do not patch SDK caches or suppress compatibility code to silence the scanner. Recheck recommendations after the separately accepted release is uploaded in REV237; a local successful build is not publication or a new Play measurement.

The stable Android WebView 1.1.3 package still requests a ProGuard default removed by AGP 9. The [licensed compatibility snapshot](../../../third_party/flutter_inappwebview_android/README.md) replaces just that default in both build types. The startup smoke also loads local HTML and evaluates JavaScript through the real Android WebView without external requests. For a release check, build `integration_test/webview_release_probe.dart` as the APK target and verify the visible `REV142 WebView release OK` marker; then rebuild the ordinary `lib/main.dart` target before checking normal startup and reader navigation. The probe must never be uploaded as a release artifact.

## Browser Database Opening Check

`integration_test/web_database_open_test.dart` checks 45 concurrent Drift worker requests, waiting for a shared lock, releasing it after a failure, and opening/reopening common and localized databases from `web/db/`. The connector's queue and Web Lock prevent overlapping OPFS probes as described in [Drift #3856](https://github.com/simolus3/drift/issues/3856).

Start a ChromeDriver compatible with the local Chrome on port 4444, then run locally:

```bash
flutter drive --release --driver=test_driver/integration_test.dart --target=integration_test/web_database_open_test.dart -d web-server --browser-name=chrome --headless --driver-port=4444 --web-port=8766
```

This uses a separate local origin without affecting the published site's data. On native devices this browser check is explicitly skipped and does not count as passed. Updated tabs on the same origin share a Web Lock; without Web Locks, the queue operates within one tab. Old open tabs do not participate in the new lock until they reload.

The first long press on a dictionary verse link is covered by `integration_test/strong_usage_preview_test.dart`. For Chrome, replace `--target` in the command above with this file; for Windows, run `flutter test integration_test/strong_usage_preview_test.dart -d windows`. The check verifies both a visible preview and copying the text exactly once.

## Local Bible Module Update Check

The [REVELATION-FLUTTER-H](https://ai11-link.sentry.io/issues/156728094/) regression checks failure to write the local `manifest.json`. Unit tests reproduce `FileSystemException` with OS codes 2 and 5, module discovery, background verification of all databases, same-size module replacement, rejection of a stale object, and subsequent cache recovery. A failed write retains the merged manifest in memory, preserving version, size and integrity checks. In the Windows integration check, a directory at the manifest file path causes a real write failure: the reader displays the new verse, and the next open restores the cache without another module download. Run `flutter test integration_test/bible_module_update_test.dart -d windows`. Data is temporary and the server uses loopback; production is unchanged. The event belongs to 1.0.7+172; the old release alone does not prove that earlier serialization fixes this failure. The physical OneDrive failure on the original device is not reproduced.

Verified on 2026-10-28 with the local 1.0.8+173 candidate, Flutter 3.47.2 / Dart 3.13.2: `flutter analyze` found no issues; `flutter test --coverage` passed 1021 tests; `dart run scripts/coverage_baseline.dart --min-effective=90.0` reported 90.79%; `flutter test integration_test/bible_module_update_test.dart -d windows --reporter expanded` passed 1 test on Windows x64, Debug. All five new unit scenarios fail with a manifest write error before the fix and pass afterwards. Formatting, forbidden-pattern and RU/EN docs-sync checks passed. Debug still emits Drift's multiple-database-instance warning during repeated opens; the test passes and no warning suppression was added. Android/Linux/macOS/iOS were not run in this investigation; full version acceptance remains REV236. Validation preceded commit/push; no deployment was performed.

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

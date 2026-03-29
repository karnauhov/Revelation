# AGENTS.md

If any rule below conflicts with a direct owner request, owner request wins.

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

## Model and Reasoning Selection
- The assistant cannot switch the model in the current session on its own; model switching is performed by the user.
- Before each new task, the assistant must recommend a pair: `model + reasoning level`, with a short rationale.
- After the user switches the model, the assistant must continue the same task without losing context.
- If task complexity/risk increases during execution, escalate reasoning to `high` or `xhigh` and explain why.

### Model Selection Matrix
| Model | Use Cases |
| --- | --- |
| `GPT-5.4` | Architecture work, deep code review, complex bugs, system-level logic. |
| `GPT-5.3-Codex` | Main development, refactoring, tests, CI/CD, databases, API integrations. |
| `GPT-5.4-Mini` | Translations, UI/UX copy, changelog/release notes, simple JSON edits. |
| `GPT-5.2-Codex` | Boilerplate and minor local edits. |

### Reasoning Matrix
| Reasoning | When to Use |
| --- | --- |
| `low` | Very simple or template-based tasks. |
| `medium` | Most everyday implementation tasks. |
| `high` | Complex logic, non-trivial bugs, architectural decisions. |
| `xhigh` | Critical incidents, high uncertainty, high cost of error. |

### Default Recommendation
- If task type is unclear, recommend `GPT-5.3-Codex + high`.

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
- When moving or renaming runtime files under `lib/`, move or rename related tests under `test/` in the same change set.
- Any functional add/change/remove in runtime code must include relevant test updates in the same change set:
  - add or update unit tests for changed business logic, repositories, services, and shared contracts;
  - add or update widget tests for changed UI behavior and state-driven presentation;
  - remove or rewrite obsolete tests when functionality is removed.
- Any new screen, route, deep link, startup flow, or other critical end-to-end behavior must update relevant smoke coverage in `integration_test/smoke/` in the same change set.
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
- Preserve the current logging contract:
  - keep uncaught error logging wired through `runZonedGuarded`, `FlutterError.onError`, and `PlatformDispatcher.instance.onError`;
  - keep route tracing enabled through `TalkerRouteObserver`;
  - keep BLoC/Cubit lifecycle logging enabled through `AppBlocObserver`.
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
- Keep acknowledgements metadata synchronized with `assets/data/about_libraries.xml`:
  - before adding any new third-party package, SDK, native library, binary, or other dependency, verify that its license permits use and redistribution in this project's context: public, open-source, and non-commercial; treat unclear/custom/commercial/restricted/copyleft-sensitive licenses as requiring explicit owner confirmation before adoption;
  - when researching or recommending libraries, include a license compatibility check as part of the search/evaluation step, explicitly record the detected license, and reject options whose license is unknown, unclear, or incompatible with the project context above;
  - `about_libraries.xml` is for third-party dependencies and third-party redistributed components only; do not add first-party packages, internal workspace/path packages, or other dependencies authored inside this project repository;
  - when adding/removing a third-party package in `dependencies` or `dev_dependencies`, add/remove the corresponding `@Package` entry in `about_libraries.xml` in the same change;
  - for hosted pub packages, take the license name plus official/license links from the exact package page, not from the publisher, organization, or repository root;
  - for third-party local/path/git/workspace packages, record links for the exact package itself, not just the repository root: `officialSite` must point to the exact package source location and `licenseLink` must resolve to an existing license page/file for that exact package; if the package inherits a repo/root license, add a package-local license pointer/file or equivalent exact package license page and link that;
  - when adding/removing a third-party native library, SDK, redistributable, binary, or other non-pub dependency used directly from platform code, add/remove the corresponding entry in `about_libraries.xml` in the same change, and record the exact library/product page plus its exact license page, not just the vendor homepage;
  - do not add separate acknowledgement entries for operating-system or platform SDK APIs that are part of the target platform/toolchain and are not redistributed with the app (for example `XAudio2` from Windows).
- Use change checklist from `.github/change_checklist.md` for every change set (code + tests + docs RU/EN).
- Keep localization in sync for supported locales: `en`, `es`, `uk`, `ru`.
- Do not commit secrets. `api-keys.json` is gitignored.
- `ServerManager` expects compile-time defines `SUPABASE_URL` and `SUPABASE_KEY`.
- The Snap packaging flow uses `--dart-define-from-file=api-keys.json`.
- If you change database content or language loading behavior, check both `lib/infra/db/` and `web/db/`.
- Database schema version is stored inside each SQLite file in `db_metadata.schema_version` (`revelation.sqlite` and `revelation_<lang>.sqlite`).
- When changing a DB schema, update the Drift `schemaVersion`, the SQLite `PRAGMA user_version`, and `db_metadata.schema_version` in the working DB files under `%Documents%/revelation/db`, then publish/copy the updated DB files to `web/db/`.

## Generated Files
- Do not manually edit generated Drift files such as `lib/infra/db/**/*.g.dart`.
- Do not manually edit generated localization files such as `lib/l10n/app_localizations*.dart`.
- Treat generated platform plugin registrant files under platform folders as generated unless there is a clear reason to touch them.

## Common Commands
- Install dependencies: `flutter pub get`
- Format code: `dart format .`
- Static analysis: `flutter analyze`
- Tests: `flutter test`
- Coverage: `flutter test --coverage`
- Docs sync check: `dart run scripts/check_docs_sync.dart`
- Forbidden pattern checks: `dart run scripts/check_forbidden_patterns.dart`
- Smoke integration tests: `flutter test integration_test/smoke`
- Generate Drift code: `dart run build_runner build --delete-conflicting-outputs`
- Watch Drift codegen: `dart run build_runner watch --delete-conflicting-outputs`
- Generate localization files: `flutter gen-l10n`

## Validation
- Run `dart format .` before finishing non-trivial code changes.
- Run `flutter analyze` before finishing non-trivial code changes.
- Run `flutter test` before finishing non-trivial code changes.
- Run `dart run scripts/check_forbidden_patterns.dart` before finishing non-trivial code changes.
- When docs from approved RU/EN pairs are changed, run `dart run scripts/check_docs_sync.dart`.
- For startup, routing, deep-link, or other critical end-to-end flow changes, update relevant coverage in `integration_test/smoke/` and run `flutter test integration_test/smoke` when the environment supports it; otherwise trigger `.github/workflows/integration_smoke.yml`.
- For state-architecture changes, run `rg "package:provider|ChangeNotifier|notifyListeners" lib test` and treat new matches as architecture regressions.
- For state-architecture changes, run `rg "BuildContext" lib/features --glob "**/application/**/*.dart" --glob "**/presentation/bloc/**/*.dart"` and treat matches as architecture regressions (except explicitly approved transitional adapters).
- For state-management changes in high-risk flows, ensure regression tests cover:
  - stale async race (`latest request wins`)
  - lifecycle safety (`close before async completes`)
  - side-effect call-count and rapid-switch UI scenarios (for example detail image-preview flows)
- Coverage thresholds are enforced in CI through `dart run scripts/coverage_baseline.dart --min-effective=90.0`; run `flutter test --coverage` for broad or high-risk runtime changes and before release-oriented validation.
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
- Do not bypass the release-version synchronization helper unless explicitly requested by the owner.

## Release Checklist
- Update version information in the versioned project files listed above.
- Update `CHANGELOG.md` only when there are new user-visible and non-duplicated changes for the release.
- Build the Snap package with `snapcraft_build.sh`, install it locally, and verify it.
- Commit the release changes for auto build.
- Deploy the website content in the separate `Revelation.website` repository.
- Deploy release artifacts to Snapcraft and GitHub Releases.
- Deploy mobile and store releases to Google Play and Microsoft Store.

## Changelog Rules
- Keep changelog entries compact and user-facing; `CHANGELOG.md` is not a commit-by-commit technical log.
- Add a changelog bullet only for notable user-visible outcomes (feature, fix, UX/performance/reliability improvement) or release-critical changes users must know about.
- Do not add bullets for purely internal work with no user impact (refactors, folder moves, dependency bumps without visible effect, test-only updates, formatting, CI tweaks).
- Do not duplicate information: if a change is already covered by an existing bullet in the same unreleased version, update that bullet only if clarity improves; otherwise add nothing.
- Merge related internal commits into one short outcome-oriented bullet written in plain language.
- Prefer concise wording: one bullet = one clear user outcome; avoid deep implementation details and architecture/process jargon.
- If a release has no new notable user-facing changes beyond already documented items, skipping changelog edits is allowed.

## Database Update Checklist
- Edit/version working DB files in `%Documents%/revelation/db`.
- Keep `db_metadata` records in sync for every DB file: `schema_version`, `data_version`, `date`.
- If the DB schema changed, update both the code schema version and the schema version stored inside the DB files before publishing.
- Upload the new DB file to the Supabase storage bucket used by the project.
- Copy the DB file into `web/db/`.
- Deploy the website content in the separate `Revelation.website` repository.

## Cases Requiring Owner Confirmation
- Breaking public route or deep-link contract changes without a compatibility path.
- Legal, license, copyright, or other policy text changes that affect app content or published docs.
- Weakening or removing quality gates, smoke coverage expectations, or logging hooks.
- Changing the release/version synchronization flow or bypassing the helper script.

## References
- `README.md`: project overview and platform links
- `DEV_INFO.md`: release and DB deployment notes

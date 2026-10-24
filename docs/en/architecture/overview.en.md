# Architecture Overview (EN)

Doc-Version: `2.5.0`
Last-Updated: `2026-10-24`
Source-Commit: `working-tree`

## Bible text modules and footnotes

Bible modules support legacy schema 3 and schema 4 with a separate verse comment. The OH1988 text release uses sealed stage-6 text/footnotes and contains no Strong links. BibleModuleDB reads column capabilities and never migrates externally versioned native or web Bible files. Comments flow through the existing repository and reader state; a labelled keyboard-accessible action opens the full footnote separately. Search and verse copying use only canonical text.

## Strong Feature Notes

- `StrongUsagePreviewCubit` owns loading and copying the preview for one verse link; the UI shows the tooltip after its message updates.
- The app now supports `/strongs_dictionary` as a first-class route.
- `strongs_dictionary` owns Strong dictionary domain/data/presentation and its page/dialog/embedded UI.
- `strongs_dictionary` keeps a cached picker/search index for lookup by number, Greek word, and localized entry text.
- Shared markdown remains Strong-agnostic: no Strong-specific marker or inline syntax in `shared/ui/markdown`.

## Purpose

Describe the current Revelation runtime architecture.

## Runtime Shape

- `lib/main.dart` creates `Talker`, registers core services in `AppDi`, installs `AppBlocObserver`, launches `RevelationStartupHost`, and delegates progressive startup to `AppStartupCubit` plus `AppBootstrap`.
- `AppStartupCubit` owns the launch splash state, app/build metadata for the splash footer, startup progress, failure/retry flow, and the handoff to the ready app shell.
- `AppBootstrap` initializes Flutter bindings, global error handling, platform setup, settings, Supabase, local databases, and the default handlers for `word:` and Strong links while reporting startup progress.
- `RevelationApp` builds `MaterialApp.router`, applies locale/theme/font settings from `SettingsCubit`, and exposes `en`, `es`, `uk`, and `ru`.
- `AppRouter` uses `go_router` and routes to the main, topic, Bible reader, primary source list, primary source detail, Strong's dictionary page, settings, about, and download screens.
- `AppDi.appBlocProviders` wires the global app state: `SettingsCubit`, `TopicsCatalogCubit`, and `PrimarySourcesCubit`.
- `AppDi.registerCore` registers cross-cutting runtime services such as `Talker` and the shared `MarkdownImageLoader`.
- `PrimarySourceScreen` creates feature-scoped detail state with `session`, `image`, `page-settings`, `description`, `viewport`, and `orchestration` cubits. `PrimarySourceDetailCoordinator` is a screen helper, not the source of truth.
- `BibleScreen` creates feature-scoped Bible reader state with `BibleWorkspaceCubit` for open pane composition and `BibleReaderCubit` for each module pane.
- `strongs_dictionary` is a self-contained feature with its own domain/data/presentation layers, dialog/page UI, picker flow, and primary-source integration API.

## Data and Services

- App settings are persisted with `shared_preferences`.
- Local content is read from Drift-backed SQLite databases.
- Remote downloads use Supabase Storage through `ServerManager`.
- Shared markdown rendering is centralized in `shared/ui/markdown`: `RevelationMarkdownBody` plus `RevelationMarkdownImagesCubit` provide one project-wide markdown image policy with local-first loading, preload progress, and reusable image rendering across topics, primary source descriptions, dialogs, and about content.
- `MarkdownImageLoader` contracts live in `core/content/markdown_images`, while the default downloader/cache implementation lives in `infra/content/markdown_images`.
- Shared markdown no longer owns Strong-specific presentation tokens or inline syntax. Strong origin/source UI is rendered by `strongs_dictionary` widgets.
- `AboutCubit` reads database metadata from `db_metadata` and exposes app/build/database version information to the UI.
- `LatestRequestGuard` is used in async flows where stale responses must not overwrite newer state.

## Error Diagnostics

- `SentryAppAnalyticsReporter` preserves a non-empty supplied stack. For a blank trace, it recovers `Error.stackTrace` when available; otherwise the SDK attaches a capture-site snapshot, rather than claiming to recover the original throw site. `AppBootstrap` passes a missing Flutter error stack through as empty so this recovery remains possible, while keeping Talker logging intact. The `revelation.error.stack_trace_origin` context records `provided`, `error`, or `capture`. Stack attachment is explicitly enabled in `runWithSentry`.
- `integration_test/sentry_error_reporting_test.dart` checks serialized envelopes in a local browser/device with an in-memory transport, including original frames, recovered frames, marked snapshots, and user redaction. No test events are sent to production.
- A missing historical event is different from a missing stack at capture time. [Sentry retention](https://docs.sentry.io/security-legal-pii/security/data-retention-periods/) limits access to stored events; source maps and capture-site snapshots cannot restore expired data or an original stack that the runtime never supplied. Preserve available event evidence during triage.

## Architectural Invariants

- The runtime structure of `lib/` is `app`, `core`, `infra`, `shared`, `features`, `l10n`.
- Stateful presentation logic uses `Cubit`/`Bloc`.
- Presentation does not talk directly to low-level DB or remote managers.
- Global cross-feature policies belong in shared/core/infra layers, not inside a single feature module.
- Database schema changes must keep code-level schema versions and distributed SQLite files synchronized.

## Related Documents

- [Module Boundaries](./module-boundaries.en.md)
- [State Management Matrix](./state_management_matrix.en.md)
- [Testing Strategy](../testing/strategy.en.md)

# Module Boundaries (EN)

Doc-Version: `2.6.0`
Last-Updated: `2026-10-24`
Source-Commit: `working-tree`

## Parallel reading by default and from reference links

`BibleWorkspaceCubit` opens a new workspace with LXX/TR and an available translation in the app language, matching published module metadata. KJV (en) and OH1988 (uk) are currently available; missing es/ru translations or unreadable optional metadata leave the original module open. No unavailable modules are invented. An explicit link `module` takes priority; an unavailable module falls back to the normal original/first available module rather than the stored selection.

An ordinary `/bible` restores the saved panes, including a legacy single-module preference. `bible:` and `/bible` reference parameters open the requested book/chapter/verse with a translation independently of the saved layout, preserving existing route formats. Automatic opening and navigation do not write preferences. Only explicitly adding/closing a pane or successfully changing a module saves the complete ready layout. The workspace alone owns these writes; ReaderCubit no longer writes the shared single-module preference. Writes are serialized and incomplete layouts are not saved. Initial loads coalesce; closing the workspace or manually changing its layout prevents delayed automatic selection from applying. Linked navigation remains a setting of the current workspace. Translation selection runs once; after a slow load the new pane waits for the current synchronization and follows the latest primary reference.

## Retrying the first Bible load

`BibleReaderCubit.retryInitialLoad` retries only a failed initial load and preserves the original route arguments. Button availability derives from failure and the absence of verseMap; starting a retry synchronously moves the cubit to loading so rapid taps coalesce. The existing LatestRequestGuard protects against stale responses and completion after close. The workspace, repository, and reader state retain their existing data ownership; no parallel retry state is introduced.

## Bible text modules and footnotes

BibleModuleDB owns schema capability detection and returns an empty comment for legacy files. BibleVerseText and BibleChapterVerse carry text and comment as distinct comparable values. BibleRepository forwards comments into chapter data but excludes them from text search. BibleVerseCommentButton owns localized dialog presentation; it introduces no parallel state slice. Python content-tool editing saves text/comment atomically and discovers the column dynamically. Its existing table-content comparison includes comment changes; metadata-only differences remain excluded from content summaries.

## Strong Feature Notes

- Async verse-link preview state belongs to `strongs_dictionary/presentation/bloc/StrongUsagePreviewCubit`; localization and Tooltip presentation remain in the widget.
- `features/strongs_dictionary` owns Strong dictionary domain/data/presentation logic, including page/dialog/picker/embedded flows.
- `shared/ui/markdown` stays Strong-agnostic and must not contain Strong-specific markers or inline syntax handlers.

## Purpose

Define where code belongs and how layers depend on each other.

## Top-Level Structure

- `lib/app` - bootstrap, startup shell, DI, router, top-level composition
- `lib/core` - cross-cutting primitives such as errors, async guards, logging, audio, platform utilities, diagnostics
- `lib/infra` - database, remote, and storage implementations
- `lib/shared` - reusable UI, shared models, localization helpers, and common utilities
- `lib/features` - feature-first modules
- `lib/l10n` - ARB files and generated localization code

## Feature Layout

When a feature needs internal layering, use this structure:

- `presentation` - `bloc/`, `screens/`, `widgets/`
- `application` - orchestration and use-case services
- `data` - repositories, data models, and mapping

A smaller feature may omit layers that it does not need, but the dependency direction stays the same.

## Dependency Rules

- `presentation` may depend on feature services, repositories, and DI factories, but not on low-level infra managers directly.
- `app/startup` may depend on app bootstrap/composition code and shared localization/theme primitives, but it must not move feature-specific state ownership into the root shell.
- `presentation/bloc` and `application` must not receive `BuildContext`.
- `application` contains no widgets.
- `data` may use infra gateways and storage implementations.
- `infra` does not import feature presentation code.
- `shared` stays reusable and does not own feature-specific orchestration.
- `core` stays feature-agnostic.
- The global markdown image policy is split by layer: request/load contracts live in `core/content/markdown_images`, the default downloader/cache implementation lives in `infra/content/markdown_images`, and per-document UI state plus rendering live in `shared/ui/markdown`.
- Features do not own markdown image caching or preload policy; they only pass markdown content and feature-specific link handlers into the shared markdown widgets.
- `features/strongs_dictionary` owns Strong dictionary domain/data/presentation logic, including picker/dialog/page flows and the embedded primary-source dictionary entry UI.
- `shared/ui/markdown` must remain Strong-agnostic: no Strong-specific markers, syntax handlers, or feature tooltip renderers.
- `features/bible` owns Bible module discovery, local module preferences, per-pane reading state, and the Bible reader screen; shared link handling may route `bible:` links into this feature but must not own reader state.

## State Rules

- Stateful presentation uses `Cubit`/`Bloc` only.
- A single UI data slice has a single source of truth.
- Do not introduce duplicate cubits or duplicate visibility flags when state can be derived from existing values.
- Async cubits must guard post-`await` state application with `isClosed` and stale-request protection where needed.

## Usual Validation

- `dart run scripts/check_forbidden_patterns.dart`
- `flutter analyze`
- `flutter test`

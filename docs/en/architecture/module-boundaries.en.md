# Module Boundaries (EN)

Doc-Version: `2.6.12`
Last-Updated: `2026-11-27`
Source-Commit: `working-tree`

ImagePreview owns the decoded leaf, paints it beneath its annotations and reports when the geometry is ready. The orchestration cubit restores the saved transform once and flushes pending viewport changes to the outgoing leaf before navigation. The image loader reads the original dimensions from a bounded HTTP range. The image cubit applies the comparison only to the current request, independently of image display.

## Bible bookmark boundaries

The Bible feature owns the bookmark model and its versioned local preference. The store serializes read-modify-write operations and the workspace opens one bookmark Cubit for its panes and dialogs. The reader provides the canonical verse map and opens selected references through its existing navigation. The shared study dialog provides optional movement by its header and constrains the surface to the available viewport.

## Manuscript image tools

The primary source presentation/bloc layer owns tool drafts. Dialogs initialize from the current page and apply changes through the existing coordinator commands.

## Strong number availability in a module

`BibleModuleDB.readInfo` derives `BibleModuleInfo.hasStrongNumbers` from standalone G/H numeric tokens in the text of all verses. SQL selects candidates in bounded batches, then the shared reader token contract validates them; comments are excluded. The capability participates in value equality and is refreshed when module information is read, without SQLite schema changes or a persistent cache. Each pane derives Strong toolbar and overflow action availability from its own `selectedModule`, without another visibility flag in state. The display preference survives switching through a text-only module, and the standalone dictionary remains available.

## Bible module revision metadata

The DB adapter reads optional revision metadata from the same file as module information. `BibleModuleInfo` carries nullable scalar versions/date with value equality; the repository and ReaderCubit retain ownership of the selected module. Presentation alone maps known language/canon/numbering values to localized readable names, formats the revision calendar date without a device-timezone shift, and preserves unknown values and complete source/license details. Module code and ID remain internal data and are omitted from the information dialog. Database schema and content are unchanged.

## Parallel reading by default and from reference links

`BibleWorkspaceCubit` restores the ordered panes, their modules, selections and visible verses, and the linked navigation setting from a versioned local preference. A first visit uses the legacy module list or LXX/TR and the default translation. An internal Bible reference first opens a passage dialog. Its reader action and direct reference routes show the passage in all panes for this visit. If the specified module is missing, it temporarily replaces the first pane. Returning through the menu restores the ordinary reading session.

When the dictionary opens from the menu, `StrongsDictionaryCubit` restores the locally saved Strong number and article scroll position. Opening a full page with an explicit number saves that entry immediately at the top. Scrolling the article updates its saved position. Cross-references on the dictionary page select and save the new entry in place. The manuscript detail panel updates its own selection and highlights matching numbers on the leaf. Browsing that panel or a preview elsewhere preserves the last full-page visit. If the saved entry is unavailable, the dictionary opens the first available entry.

An ordinary `/bible` restores the saved panes, including a legacy single-module preference. `bible:` and `/bible` reference parameters open the requested book/chapter/verse with a translation independently of the saved layout, preserving existing route formats. Automatic opening and navigation do not write preferences. Only explicitly adding/closing a pane or successfully changing a module saves the complete ready layout. The workspace alone owns these writes; ReaderCubit no longer writes the shared single-module preference. Writes are serialized and incomplete layouts are not saved. Initial loads coalesce; closing the workspace or manually changing its layout prevents delayed automatic selection from applying. Linked navigation remains a setting of the current workspace. Translation selection runs once; after a slow load the new pane waits for the current synchronization and follows the latest primary reference.

## Catalog and default Bible module

The Bible word renderer reads the G/H identifiers supplied by each module. Only Greek identifiers shared with the original can be highlighted. Unmatched annotations remain dictionary links in passage dialogs. AllusionIndex supplies the same distinct Strong identifiers and corpus-adjusted weights to the source summary and to ranking. The original module supplies occurrence counts.

BibleLibraryRepository reads the website database manifest on Web and the storage manifest on native platforms. The content tool writes the module ID, language, role, canon, versification and revision. Compatible catalog entries become available in the same app build. The repository merges installed modules with the current manifest and persists the catalog for offline use. The settings screen shows the effective translation and refreshes discovery when its selection dialog opens.

The reader, passage dialog and search cards resolve the global preference through this repository. Explicit links retain their requested module. A passage preview passes the module actually displayed to the reader. The shared dictionary and passage dialogs use the same toolbar and text-export services.

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

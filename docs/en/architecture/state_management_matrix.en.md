# State Management Matrix (EN)

Doc-Version: `2.6.5`
Last-Updated: `2026-11-21`
Source-Commit: `working-tree`

## Manuscript image tools

BrightnessDraftCubit and ReplacementDraftCubit use Dart records with value equality. Closing a dialog disposes its cubit. After using the eyedropper, the next dialog reads the current viewport values.

## Strong number availability in a module

`BibleModuleDB.readInfo` derives `BibleModuleInfo.hasStrongNumbers` from standalone G/H numeric tokens in the text of all verses. SQL selects candidates in bounded batches, then the shared reader token contract validates them; comments are excluded. The capability participates in value equality and is refreshed when module information is read, without SQLite schema changes or a persistent cache. Each pane derives Strong toolbar and overflow action availability from its own `selectedModule`, without another visibility flag in state. The display preference survives switching through a text-only module, and the standalone dictionary remains available.

## Module information in reader state

`BibleReaderState.selectedModule` remains the sole selected-module snapshot in each pane. Its `BibleModuleInfo` value now includes optional data/schema versions and a revision date; equality and hashing include all three values. Initial loading and module switching bring the revision through the existing guarded asynchronous flow. Opening module information has no I/O or state-write side effect; the same dialog serves the toolbar and overflow menu.

## Parallel reading by default and from reference links

`BibleWorkspaceCubit` opens a new workspace with LXX/TR and the default translation. Reference links open with the resolved translation in the primary pane. An explicit module in the route takes precedence. The language of the interface drives automatic selection, with English as the fallback. KJV serves en/es/ru and OH1988 serves uk with the current catalog. A missing module can lead to a reader error with retry, without changing the saved preference.

An ordinary `/bible` restores the saved panes, including a legacy single-module preference. `bible:` and `/bible` reference parameters open the requested book/chapter/verse with a translation independently of the saved layout, preserving existing route formats. Automatic opening and navigation do not write preferences. Only explicitly adding/closing a pane or successfully changing a module saves the complete ready layout. The workspace alone owns these writes; ReaderCubit no longer writes the shared single-module preference. Writes are serialized and incomplete layouts are not saved. Initial loads coalesce; closing the workspace or manually changing its layout prevents delayed automatic selection from applying. Linked navigation remains a setting of the current workspace. Translation selection runs once; after a slow load the new pane waits for the current synchronization and follows the latest primary reference.

## Allusion search and Bible catalog state

The search state keeps annotated source and translation rows. A separate request guard protects the original passage across overlapping selections. The same immutable index supplies word weights, per-verse matches and ranking. The source word list expands independently of the passage text and result cards. Selecting a different passage collapses its word list.

SettingsCubit persists the default Bible module. BibleCatalogCubit first emits cached modules and then the refreshed catalog. AppDi supplies one AllusionSearchCubit per app session. It keeps the query, results, selected level and page across navigation and reloads previews when the translation changes. The canonical verse map is independent of index preparation. Background preparation and searches on the same visit share one index request. A new visit checks the installed revision again, and a failed preparation can be retried. A request guard protects against out-of-order results when the user changes the query, page or settings.

BiblePassagePreviewCubit owns the current verse range and both module previews. Previous and next shift the range using the verse map. Each side can show available text independently. Late completions after navigation or closing the dialog are discarded.

## Retrying the first Bible load

`BibleReaderCubit.retryInitialLoad` retries only a failed initial load and preserves the original route arguments. Button availability derives from failure and the absence of verseMap; starting a retry synchronously moves the cubit to loading so rapid taps coalesce. The existing LatestRequestGuard protects against stale responses and completion after close. The workspace, repository, and reader state retain their existing data ownership; no parallel retry state is introduced.

## Bible text modules and footnotes

BibleReaderCubit remains the single source of chapter verses, including their separate comments, in each workspace pane. Comment visibility derives from the loaded verse comment; there is no extra visibility flag or comment cubit. Verse value equality includes the comment so changed notes update the existing state-driven presentation. Opening/closing the footnote is an explicit UI dialog action with no repository side effect.

## Strong Feature Notes

- `StrongUsagePreviewCubit` is the sole source of preview text and presentation requests for one link; it coalesces rapid requests and discards results after closure when a link changes.
- `StrongsDictionaryCubit` is the source of truth for Strong dictionary selection/content/navigation and full-text filtering in page and dialog flows.
- `StrongNumberPickerCubit` owns input normalization and selected picker entry state for the Strong number picker.

## Purpose

Show which cubit owns each runtime state slice.

## Core Rules

- `Cubit` is the default state primitive in the app.
- State lives in cubits, not in mutable widget fields or feature models.
- State classes stay immutable and comparable.
- Errors are represented with `AppFailure`.
- When async work can race, newer requests must win.

## Ownership Matrix

| Scope | Owner | Responsibility |
|---|---|---|
| `app/startup` | `AppStartupCubit` | Launch splash progress, startup locale/version metadata, readiness/failure state, and handoff to the initialized app shell |
| `app/settings` | `SettingsCubit` | Current app settings, selected locale, theme, font size, loading and failure state |
| `about` | `AboutCubit` | App/build versions, database metadata, changelog section state, expandable about sections |
| `bible/workspace` | `BibleWorkspaceCubit` | Open Bible reader panes, linked navigation/scrolling mode, and persisted module pane set |
| `bible/reader` | `BibleReaderCubit` | Per-pane Bible module, selected reference, chapter verses, verse selection range, Strong display toggle, and loading/failure state |
| `shared/markdown/document` | `RevelationMarkdownImagesCubit` | Per-markdown-document remote image preload, local-first image state, progress counters, and stale-request protection shared across features |
| `topics/catalog` | `TopicsCatalogCubit` | Topic list, language-bound reloads, topic icons |
| `topics/content` | `TopicContentCubit` | Single topic markdown content, metadata fallback resolution, and loading/failure state |
| `primary_sources/list` | `PrimarySourcesCubit` | Full/significant/fragment source collections and loading/failure state |
| `primary_sources/list-ui` | `PrimarySourcesExpansionCubit` | Expanded cards on the list screen |
| `primary_source/detail/session` | `PrimarySourceSessionCubit` | Current source, selected page, image key, toolbar/menu session state |
| `primary_source/detail/image` | `PrimarySourceImageCubit` | Image bytes, local-page availability, loading state, texture limits |
| `primary_source/detail/page-settings` | `PrimarySourcePageSettingsCubit` | Image filters and overlay toggles |
| `primary_source/detail/description` | `PrimarySourceDescriptionCubit` | Verse/word selection, description content, Strong picker entries |
| `primary_source/detail/viewport` | `PrimarySourceViewportCubit` | Pan, zoom, selection area, color replacement state |
| `primary_source/detail/orchestration` | `PrimarySourceDetailOrchestrationCubit` | Safe coordination of page changes, image loading, and save/restore flows |
| `strongs_dictionary/content` | `StrongsDictionaryCubit` | Selected Strong number, cached picker/search list, full-text query, dictionary markdown content, and next/previous navigation |
| `strongs_dictionary/picker` | `StrongNumberPickerCubit` | Strong picker text input normalization, nearest allowed entry selection, and picker confirmation state |
| `strongs_dictionary/verse-preview` | `StrongUsagePreviewCubit` | Preview text/failure for one link, copying, and presentation request after the UI updates |
| `download` | Stateless screen | No persistent runtime state slice |

## Scope Notes

- `RevelationStartupHost` creates `AppStartupCubit` at the app root and mounts the global app providers only after startup is ready.
- Global providers are created by `AppDi.appBlocProviders`.
- Shared markdown widgets create `RevelationMarkdownImagesCubit` per rendered markdown document instead of storing markdown image preload state inside feature cubits.
- `StrongsDictionaryCubit` is the single source of truth for Strong dictionary selection state in page/dialog flows; `primary_sources` only delegates actions through the Strong feature API.
- `PrimarySourceScreen` creates the detail cubits with `MultiBlocProvider`.
- `PrimarySourceDetailCoordinator` adapts UI events to the detail cubits; it is not a state owner.
- `BibleWorkspaceCubit` owns only page-level reader pane composition; each pane keeps its own Bible text and selection state in `BibleReaderCubit`.

# State Management Matrix (EN)

Doc-Version: `2.6.0`
Last-Updated: `2026-10-24`
Source-Commit: `working-tree`

## Parallel reading by default and from reference links

`BibleWorkspaceCubit` opens a new workspace with LXX/TR and an available translation in the app language, matching published module metadata. KJV (en) and OH1988 (uk) are currently available; missing es/ru translations or unreadable optional metadata leave the original module open. No unavailable modules are invented. An explicit link `module` takes priority; an unavailable module falls back to the normal original/first available module rather than the stored selection.

An ordinary `/bible` restores the saved panes, including a legacy single-module preference. `bible:` and `/bible` reference parameters open the requested book/chapter/verse with a translation independently of the saved layout, preserving existing route formats. Automatic opening and navigation do not write preferences. Only explicitly adding/closing a pane or successfully changing a module saves the complete ready layout. The workspace alone owns these writes; ReaderCubit no longer writes the shared single-module preference. Writes are serialized and incomplete layouts are not saved. Initial loads coalesce; closing the workspace or manually changing its layout prevents delayed automatic selection from applying. Linked navigation remains a setting of the current workspace. Translation selection runs once; after a slow load the new pane waits for the current synchronization and follows the latest primary reference.

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

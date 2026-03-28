# State Management Matrix (EN)

Doc-Version: `2.0.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

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
| `app/settings` | `SettingsCubit` | Current app settings, selected locale, theme, font size, loading and failure state |
| `about` | `AboutCubit` | App/build versions, database metadata, changelog section state, expandable about sections |
| `topics/catalog` | `TopicsCatalogCubit` | Topic list, language-bound reloads, topic icons |
| `topics/content` | `TopicContentCubit` | Single topic markdown content and loading/failure state |
| `primary_sources/list` | `PrimarySourcesCubit` | Full/significant/fragment source collections and loading/failure state |
| `primary_sources/list-ui` | `PrimarySourcesExpansionCubit` | Expanded cards on the list screen |
| `primary_source/detail/session` | `PrimarySourceSessionCubit` | Current source, selected page, image key, toolbar/menu session state |
| `primary_source/detail/image` | `PrimarySourceImageCubit` | Image bytes, local-page availability, loading state, texture limits |
| `primary_source/detail/page-settings` | `PrimarySourcePageSettingsCubit` | Image filters and overlay toggles |
| `primary_source/detail/description` | `PrimarySourceDescriptionCubit` | Verse/word selection, description content, Strong picker entries |
| `primary_source/detail/viewport` | `PrimarySourceViewportCubit` | Pan, zoom, selection area, color replacement state |
| `primary_source/detail/orchestration` | `PrimarySourceDetailOrchestrationCubit` | Safe coordination of page changes, image loading, and save/restore flows |
| `download` | Stateless screen | No persistent runtime state slice |

## Scope Notes

- Global providers are created by `AppDi.appBlocProviders`.
- `PrimarySourceScreen` creates the detail cubits with `MultiBlocProvider`.
- `PrimarySourceDetailCoordinator` adapts UI events to the detail cubits; it is not a state owner.

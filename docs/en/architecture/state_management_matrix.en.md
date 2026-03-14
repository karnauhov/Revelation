# State Management Matrix (EN)

Doc-Version: `1.1.5`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define the current runtime state ownership model in Revelation.

## 2. Mandatory Contracts
- Stateful presentation logic is implemented with `Cubit`/`Bloc`.
- Default pattern: `Cubit`; `Bloc` is used only for event orchestration across multiple state slices.
- State classes remain immutable and evolve through `copyWith`.
- Collections in state (`List`/`Map`) are stored as unmodifiable copies.
- Errors in state contracts are represented by `AppFailure`.

## 3. Ownership Matrix

| Scope | Owner | State contract (summary) |
|---|---|---|
| `app/settings` | `SettingsCubit` | `SettingsState { AppSettings settings; bool isLoading; AppFailure? failure; }` |
| `about` | `AboutCubit` | `AboutState { String appVersion; String buildNumber; String changelog; bool isLoading; bool isChangelogExpanded; bool isAcknowledgementsExpanded; bool isRecommendedExpanded; AppFailure? failure; }` |
| `topics/catalog` | `TopicsCatalogCubit` | `TopicsCatalogState { String language; List<TopicInfo> topics; Map<String, TopicResource?> iconByKey; bool isLoading; AppFailure? failure; }` |
| `topics/content` | `TopicContentCubit` | `TopicContentState { String route; String language; String name; String description; String markdown; bool isLoading; AppFailure? failure; }` |
| `primary_sources/list` | `PrimarySourcesCubit` | `PrimarySourcesState { List<PrimarySource> full; List<PrimarySource> significant; List<PrimarySource> fragments; bool isLoading; AppFailure? failure; }` |
| `primary_sources/list-expansion` | `PrimarySourcesExpansionCubit` | `PrimarySourcesExpansionState { Set<String> expandedSourceIds; }` |
| `primary_source/detail/session` | `PrimarySourceSessionCubit` | `PrimarySourceSessionState { PrimarySource source; model.Page? selectedPage; String imageName; bool isMenuOpen; }` |
| `primary_source/detail/image` | `PrimarySourceImageCubit` | `PrimarySourceImageState { Uint8List? imageData; bool isLoading; bool refreshError; Map<String, bool?> localPageLoaded; int maxTextureSize; }` |
| `primary_source/detail/page-settings` | `PrimarySourcePageSettingsCubit` | `PrimarySourcePageSettingsState { String rawSettings; bool isNegative; bool isMonochrome; double brightness; double contrast; bool showWordSeparators; bool showStrongNumbers; bool showVerseNumbers; }` |
| `primary_source/detail/description` | `PrimarySourceDescriptionCubit` | `PrimarySourceDescriptionState { String? content; DescriptionKind currentType; int? currentNumber; List<GreekStrongPickerEntry> pickerEntries; }` |
| `primary_source/detail/viewport` | `PrimarySourceViewportCubit` | `PrimarySourceViewportState { double dx; double dy; double scale; double savedX; double savedY; double savedScale; bool scaleAndPositionRestored; ZoomStatus zoomStatus; Rect? selectedArea; Color colorToReplace; Color newColor; double tolerance; bool pipetteMode; bool selectAreaMode; bool isColorToReplace; }` |
| `primary_source/detail/orchestration` | `PrimarySourceDetailOrchestrationCubit` | `PrimarySourceDetailOrchestrationState {}` (coordinates `loadImage`, `changeSelectedPage`, and debounced save/restore over detail cubits) |
| `download` | stateless screen | `N/A` |

## 4. Provider Scope
- Global cubit providers are wired in `AppDi.appBlocProviders`: `SettingsCubit`, `TopicsCatalogCubit`, `PrimarySourcesCubit`.
- Feature-scoped detail state in `PrimarySourceScreen` is created with `MultiBlocProvider`.

## 5. Notes
- `PrimarySourceDetailCoordinator` delegates image/page/save/restore flow to `PrimarySourceDetailOrchestrationCubit` and is not the source of truth for state contracts.
- Selection (`currentType/currentNumber`) on the primary source detail screen is stored in `PrimarySourceDescriptionState`; there is no separate selection cubit.
- Any state ownership change must be mirrored in both RU and EN versions of this document.

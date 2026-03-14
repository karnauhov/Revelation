# Phase 3.7 — State Migration Matrix (EN)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define and approve the Phase 3.7 migration matrix: `feature -> cubit/bloc set -> owner state contracts`.

## 2. Approval Rules
- Default pattern: `Cubit` for state-driven flows.
- `Bloc` is allowed only for complex event orchestration across multiple cubit slices.
- All state contracts are immutable DTOs.
- After Phase 3.7, no `provider`/`ChangeNotifier` remains in runtime code.

## 3. Approved Matrix

| Scope | Current owner | Target Cubit/Bloc set | Owner state contracts |
|---|---|---|---|
| `app_shell/settings` | `SettingsViewModel` (global) | `SettingsCubit` | `SettingsState { AppSettings settings; bool isLoading; AppFailure? failure; }` |
| `about` | `AboutViewModel` (screen-local) | `AboutCubit` | `AboutState { String appVersion; String buildNumber; String changelog; bool isLoading; bool isChangelogExpanded; bool isAcknowledgementsExpanded; bool isRecommendedExpanded; AppFailure? failure; }` |
| `topics/catalog` (`MainScreen`, `TopicList`, icons) | `MainViewModel` + local `FutureBuilder` state | `TopicsCatalogCubit` | `TopicsCatalogState { String language; List<TopicInfo> topics; Map<String, CommonResource?> iconByKey; bool isLoading; AppFailure? failure; }` |
| `topics/content` (`TopicScreen`) | local `FutureBuilder` state | `TopicContentCubit` | `TopicContentState { String route; String language; String name; String description; String markdown; bool isLoading; AppFailure? failure; }` |
| `primary_sources/list` | `PrimarySourcesCubit` | `PrimarySourcesCubit` | `PrimarySourcesState { List<PrimarySource> full; List<PrimarySource> significant; List<PrimarySource> fragments; bool isLoading; AppFailure? failure; }` |
| `primary_source/detail/session` | `PrimarySourceViewModel` (state subset) | `PrimarySourceSessionCubit` | `PrimarySourceSessionState { PrimarySource source; model.Page? selectedPage; String imageName; bool isMenuOpen; }` |
| `primary_source/detail/image` | `PrimarySourceViewModel` + image orchestrator | `PrimarySourceImageCubit` | `PrimarySourceImageState { Uint8List? imageData; bool isLoading; bool imageShown; bool refreshError; Map<String, bool?> localPageLoaded; int maxTextureSize; }` |
| `primary_source/detail/page-settings` | `PrimarySourceViewModel` + page-settings orchestrator | `PrimarySourcePageSettingsCubit` | `PrimarySourcePageSettingsState { String rawSettings; bool isNegative; bool isMonochrome; double brightness; double contrast; bool showWordSeparators; bool showStrongNumbers; bool showVerseNumbers; }` |
| `primary_source/detail/selection` | `PrimarySourceViewModel` | `PrimarySourceSelectionCubit` | `PrimarySourceSelectionState { Rect? selectedArea; bool pipetteMode; bool selectAreaMode; Color colorToReplace; Color newColor; double tolerance; }` |
| `primary_source/detail/viewport` | `PrimarySourceViewModel` + `ImagePreviewController` | `PrimarySourceViewportCubit` | `PrimarySourceViewportState { double dx; double dy; double scale; double savedX; double savedY; double savedScale; bool scaleAndPositionRestored; ZoomStatus zoomStatus; }` |
| `primary_source/detail/description` | `PrimarySourceViewModel` + description orchestrator | `PrimarySourceDescriptionCubit` | `PrimarySourceDescriptionState { bool showDescription; String? content; DescriptionKind currentType; int? currentNumber; List<GreekStrongPickerEntry> pickerEntries; }` |
| `primary_source/detail/cross-slice orchestration` | inside one `PrimarySourceViewModel` | `PrimarySourceCoordinatorBloc` (optional, if needed) | `PrimarySourceCoordinatorState { bool initialized; AppFailure? failure; }` |
| `download` | stateless screen (no state-holder) | `No Cubit/Bloc in Phase 3.7` | `N/A` |
| `app/di + app/root provider wiring` | `AppDi.appBlocProviders` + `MultiBlocProvider` | `AppDi.appBlocProviders` + `MultiBlocProvider` | `AppStateScopeContract { global providers map; feature-scoped providers per route; }` |

## 4. Notes
- In the current scope, `download` stays stateless and does not require a dedicated state-holder.
- `PrimarySourceCoordinatorBloc` should be introduced only if cross-cubit orchestration is actually required.
- Target state-layer filename convention: `*_cubit.dart`, `*_state.dart`, `*_bloc.dart` (bloc only when needed).

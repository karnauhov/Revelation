# State Management Matrix (RU)

Doc-Version: `1.0.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать актуальное распределение runtime state в проекте Revelation.

## 2. Mandatory Contracts
- Stateful presentation-логика реализуется через `Cubit`/`Bloc`.
- Базовый паттерн: `Cubit`; `Bloc` используется только для event-orchestration между несколькими state-срезами.
- State-классы остаются immutable и обновляются через `copyWith`.
- Ошибки в state-контрактах передаются через `AppFailure`.

## 3. Ownership Matrix

| Scope | Owner | State contract (summary) |
|---|---|---|
| `app/settings` | `SettingsCubit` | `SettingsState { AppSettings settings; bool isLoading; AppFailure? failure; }` |
| `about` | `AboutCubit` | `AboutState { String appVersion; String buildNumber; String changelog; bool isLoading; bool isChangelogExpanded; bool isAcknowledgementsExpanded; bool isRecommendedExpanded; AppFailure? failure; }` |
| `topics/catalog` | `TopicsCatalogCubit` | `TopicsCatalogState { String language; List<TopicInfo> topics; Map<String, CommonResource?> iconByKey; bool isLoading; AppFailure? failure; }` |
| `topics/content` | `TopicContentCubit` | `TopicContentState { String route; String language; String name; String description; String markdown; bool isLoading; AppFailure? failure; }` |
| `primary_sources/list` | `PrimarySourcesCubit` | `PrimarySourcesState { List<PrimarySource> full; List<PrimarySource> significant; List<PrimarySource> fragments; bool isLoading; AppFailure? failure; }` |
| `primary_source/detail/session` | `PrimarySourceSessionCubit` | `PrimarySourceSessionState { PrimarySource source; model.Page? selectedPage; String imageName; bool isMenuOpen; }` |
| `primary_source/detail/image` | `PrimarySourceImageCubit` | `PrimarySourceImageState { Uint8List? imageData; bool isLoading; bool imageShown; bool refreshError; Map<String, bool?> localPageLoaded; int maxTextureSize; }` |
| `primary_source/detail/page-settings` | `PrimarySourcePageSettingsCubit` | `PrimarySourcePageSettingsState { String rawSettings; bool isNegative; bool isMonochrome; double brightness; double contrast; bool showWordSeparators; bool showStrongNumbers; bool showVerseNumbers; }` |
| `primary_source/detail/selection` | `PrimarySourceSelectionCubit` | `PrimarySourceSelectionState { DescriptionKind currentType; int? currentNumber; }` |
| `primary_source/detail/description` | `PrimarySourceDescriptionCubit` | `PrimarySourceDescriptionState { bool showDescription; String? content; DescriptionKind currentType; int? currentNumber; List<GreekStrongPickerEntry> pickerEntries; }` |
| `primary_source/detail/viewport` | `PrimarySourceViewportCubit` | `PrimarySourceViewportState { double dx; double dy; double scale; double savedX; double savedY; double savedScale; bool scaleAndPositionRestored; ZoomStatus zoomStatus; Rect? selectedArea; Color colorToReplace; Color newColor; double tolerance; bool pipetteMode; bool selectAreaMode; bool isColorToReplace; }` |
| `download` | stateless screen | `N/A` |

## 4. Provider Scope
- Глобальные cubit-провайдеры в `AppDi.appBlocProviders`: `SettingsCubit`, `TopicsCatalogCubit`, `PrimarySourcesCubit`.
- Feature-scoped detail state в `PrimarySourceScreen` создается через `MultiBlocProvider`.

## 5. Notes
- `PrimarySourceDetailCoordinator` и `PrimarySourceViewModel` являются orchestration-слоем поверх cubit-срезов и не являются source-of-truth для state-контрактов.
- Изменение state ownership требует синхронного обновления RU/EN версии этого документа.

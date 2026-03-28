# Матрица управления состоянием (RU)

Doc-Version: `2.0.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Назначение

Показать, какой cubit владеет каждым runtime state-срезом.

## Базовые правила

- `Cubit` является основным state-примитивом приложения.
- Состояние хранится в cubit-ах, а не в mutable-полях виджетов или feature-моделей.
- State-классы остаются immutable и comparable.
- Ошибки представляются через `AppFailure`.
- Если async-запросы могут гоняться между собой, побеждает самый новый запрос.

## Матрица владения

| Scope | Owner | Responsibility |
|---|---|---|
| `app/settings` | `SettingsCubit` | Текущие настройки приложения, выбранные locale/theme/font size, loading и failure state |
| `about` | `AboutCubit` | Версии приложения и сборки, метаданные БД, состояние changelog-блока и раскрываемых секций about-экрана |
| `topics/catalog` | `TopicsCatalogCubit` | Список тем, reload при смене языка, иконки тем |
| `topics/content` | `TopicContentCubit` | Markdown-контент одной темы и ее loading/failure state |
| `primary_sources/list` | `PrimarySourcesCubit` | Коллекции full/significant/fragments и loading/failure state |
| `primary_sources/list-ui` | `PrimarySourcesExpansionCubit` | Раскрытые карточки на экране списка |
| `primary_source/detail/session` | `PrimarySourceSessionCubit` | Текущий первоисточник, выбранная страница, image key, состояние toolbar/menu |
| `primary_source/detail/image` | `PrimarySourceImageCubit` | Байты изображения, доступность локальных страниц, loading state, ограничения texture size |
| `primary_source/detail/page-settings` | `PrimarySourcePageSettingsCubit` | Фильтры изображения и overlay-переключатели |
| `primary_source/detail/description` | `PrimarySourceDescriptionCubit` | Выбор стиха/слова, контент описания, элементы Strong picker |
| `primary_source/detail/viewport` | `PrimarySourceViewportCubit` | Pan, zoom, область выделения, состояние замены цвета |
| `primary_source/detail/orchestration` | `PrimarySourceDetailOrchestrationCubit` | Безопасная координация смены страниц, загрузки изображений и save/restore flow |
| `download` | Stateless screen | Постоянный runtime state-срез отсутствует |

## Примечания по scope

- Глобальные провайдеры создаются в `AppDi.appBlocProviders`.
- `PrimarySourceScreen` поднимает detail cubit-ы через `MultiBlocProvider`.
- `PrimarySourceDetailCoordinator` адаптирует UI-события к detail cubit-ам и не владеет состоянием.

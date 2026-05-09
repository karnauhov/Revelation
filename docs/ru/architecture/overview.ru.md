# Обзор архитектуры (RU)

Doc-Version: `2.3.0`  
Last-Updated: `2026-05-09`  
Source-Commit: `working-tree`

## Strong Feature Notes

- Приложение поддерживает `/strongs_dictionary` как полноценный маршрут.
- `strongs_dictionary` владеет domain/data/presentation-логикой словаря Стронга, а также UI страницы, диалога и встроенного отображения статьи.
- `strongs_dictionary` хранит кэшированный список/поисковый индекс для поиска по номеру, греческому слову и локализованному тексту статьи.
- Общий markdown остаётся независимым от Strong: в `shared/ui/markdown` нет Strong-специфичных маркеров или inline-синтаксиса.

## Назначение

Зафиксировать текущее runtime-устройство Revelation.

## Общая схема

- `lib/main.dart` создаёт `Talker`, регистрирует core-сервисы в `AppDi`, подключает `AppBlocObserver`, запускает `RevelationStartupHost` и делегирует поэтапный старт связке `AppStartupCubit` и `AppBootstrap`.
- `AppStartupCubit` владеет состоянием стартового splash-экрана, метаданными версии/сборки для нижнего блока splash, прогрессом запуска, failure/retry-потоком и переключением в готовую оболочку приложения.
- `AppBootstrap` инициализирует Flutter bindings, глобальную обработку ошибок, платформенную среду, настройки, Supabase, локальные базы данных и дефолтные обработчики `word:` и Strong-ссылок, параллельно публикуя прогресс запуска.
- `RevelationApp` собирает `MaterialApp.router`, применяет locale/theme/font из `SettingsCubit` и поддерживает `en`, `es`, `uk`, `ru`.
- `AppRouter` использует `go_router` и обслуживает экраны main, topic, список первоисточников, detail первоисточника, страницу словаря Стронга, settings, about и download.
- `AppDi.appBlocProviders` подключает глобальный app-state: `SettingsCubit`, `TopicsCatalogCubit`, `PrimarySourcesCubit`.
- `AppDi.registerCore` регистрирует кросс-срезные runtime-сервисы, включая `Talker` и общий `MarkdownImageLoader`.
- `PrimarySourceScreen` создаёт feature-scoped detail-state через cubit-срезы `session`, `image`, `page-settings`, `description`, `viewport`, `orchestration`. `PrimarySourceDetailCoordinator` выступает экранным адаптером, но не хранит source of truth.
- `strongs_dictionary` является самостоятельной feature со своими domain/data/presentation-слоями, UI страницы/диалога, picker-flow и API интеграции с первоисточниками.

## Данные и сервисы

- Настройки приложения сохраняются через `shared_preferences`.
- Локальный контент читается из SQLite через Drift.
- Удалённые загрузки идут через Supabase Storage и `ServerManager`.
- Общий markdown-низ вынесен в `shared/ui/markdown`: `RevelationMarkdownBody` и `RevelationMarkdownImagesCubit` обеспечивают единую project-wide политику изображений с local-first загрузкой, прогрессом предзагрузки и общим рендерингом для topic-ов, описаний первоисточников, dialog-ов и about-контента.
- Контракты `MarkdownImageLoader` живут в `core/content/markdown_images`, а дефолтная downloader/cache-реализация живёт в `infra/content/markdown_images`.
- Общий markdown больше не владеет Strong-специфичными presentation-токенами или inline-синтаксисом. UI происхождения/источника Strong рендерится виджетами `strongs_dictionary`.
- `AboutCubit` читает метаданные БД из `db_metadata` и отдаёт в UI версии приложения, сборки и баз данных.
- `LatestRequestGuard` используется в async-потоках, где устаревший ответ не должен перезаписывать более новое состояние.

## Инварианты

- Рабочая структура `lib/`: `app`, `core`, `infra`, `shared`, `features`, `l10n`.
- Stateful presentation-логика строится на `Cubit`/`Bloc`.
- Presentation-слой не обращается напрямую к низкоуровневым DB/remote manager-классам.
- Глобальные cross-feature политики живут в shared/core/infra слоях, а не внутри одной feature.
- Изменения схемы БД требуют синхронизации версий в коде и в распространяемых SQLite-файлах.

## Связанные документы

- [Границы модулей](./module-boundaries.ru.md)
- [Матрица управления состоянием](./state_management_matrix.ru.md)
- [Стратегия тестирования](../testing/strategy.ru.md)

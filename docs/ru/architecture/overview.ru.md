# Обзор архитектуры (RU)

Doc-Version: `2.2.0`  
Last-Updated: `2026-03-30`  
Source-Commit: `working-tree`

## Назначение

Зафиксировать текущее runtime-устройство Revelation.

## Общая схема

- `lib/main.dart` создаёт `Talker`, регистрирует core-сервисы в `AppDi`, подключает `AppBlocObserver`, запускает `RevelationStartupHost` и делегирует поэтапный старт связке `AppStartupCubit` и `AppBootstrap`.
- `AppStartupCubit` владеет состоянием стартового splash-экрана, метаданными версии/сборки для нижнего блока splash, прогрессом запуска, failure/retry-потоком и переключением в готовую оболочку приложения.
- `AppBootstrap` инициализирует Flutter bindings, глобальную обработку ошибок, платформенную среду, настройки, Supabase, локальные базы данных и дефолтные обработчики `word:` и Strong-ссылок, параллельно публикуя прогресс запуска.
- `RevelationApp` собирает `MaterialApp.router`, применяет locale/theme/font из `SettingsCubit` и поддерживает `en`, `es`, `uk`, `ru`.
- `AppRouter` использует `go_router` и обслуживает экраны main, topic, список первоисточников, detail первоисточника, settings, about и download.
- `AppDi.appBlocProviders` подключает глобальный app-state: `SettingsCubit`, `TopicsCatalogCubit`, `PrimarySourcesCubit`.
- `AppDi.registerCore` регистрирует кросс-срезные runtime-сервисы, включая `Talker` и общий `MarkdownImageLoader`.
- `PrimarySourceScreen` создаёт feature-scoped detail-state через cubit-срезы `session`, `image`, `page-settings`, `description`, `viewport`, `orchestration`. `PrimarySourceDetailCoordinator` выступает экранным адаптером, но не хранит source of truth.

## Данные и сервисы

- Настройки приложения сохраняются через `shared_preferences`.
- Локальный контент читается из SQLite через Drift.
- Удалённые загрузки идут через Supabase Storage и `ServerManager`.
- Общий markdown-низ вынесен в `shared/ui/markdown`: `RevelationMarkdownBody` и `RevelationMarkdownImagesCubit` обеспечивают единую project-wide политику изображений с local-first загрузкой, прогрессом предзагрузки и общим рендерингом для topic-ов, описаний первоисточников, dialog-ов и about-контента.
- Контракты `MarkdownImageLoader` живут в `core/content/markdown_images`, а дефолтная downloader/cache-реализация живёт в `infra/content/markdown_images`.
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

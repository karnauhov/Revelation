# Architecture Overview (RU)

Doc-Version: `1.1.2`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать текущее архитектурное устройство Revelation.

## 2. Runtime Architecture Snapshot
- Точка входа: `lib/main.dart` настраивает `Talker`, регистрирует core-зависимости, подключает `AppBlocObserver`, инициализирует `AppBootstrap` и запускает `MaterialApp.router`.
- Bootstrap: `AppBootstrap` выполняет `WidgetsFlutterBinding.ensureInitialized`, глобальные error hooks, инициализацию платформы, загрузку настроек, инициализацию Supabase и локальных БД.
- Навигация: `go_router` в `AppRouter`, для критичных переходов используются typed route args (`TopicRouteArgs`, `PrimarySourceRouteArgs`).
- Обработка `word:`-ссылок: `shared/navigation` использует callback-контракты; дефолтный обработчик регистрируется на bootstrap-уровне (`AppBootstrap`).
- Глобальный state scope: `AppDi.appBlocProviders` предоставляет `SettingsCubit`, `TopicsCatalogCubit`, `PrimarySourcesCubit`.
- Detail state для primary source: в `PrimarySourceScreen` создается `MultiBlocProvider` с cubit-срезами `session/image/page-settings/description/viewport`; selection-поля (`currentType/currentNumber`) входят в `PrimarySourceDescriptionState`.
- Detail orchestration для primary source: `PrimarySourceDetailOrchestrationCubit` координирует `loadImage`, `changeSelectedPage` и debounce-логику save/restore между detail cubit-срезами.
- Поток данных: `presentation cubit -> feature repository -> data source -> infra gateway -> drift db`.
- Remote-слой: `ServerManager` работает с Supabase Storage для загрузки БД и файлов.
- Логирование и диагностика: `Talker`, `TalkerRouteObserver`, `AppBlocObserver`.
- Локализация: поддерживаются `en`, `es`, `uk`, `ru`.

## 3. Architectural Invariants
- В `lib/` используются только верхнеуровневые каталоги: `app`, `core`, `infra`, `shared`, `features`, `l10n`.
- Stateful presentation реализуется только на `BLoC/Cubit`.
- `provider`/`ChangeNotifier`/`notifyListeners` запрещены в runtime/test коде.
- Presentation-слой не обращается напрямую к `DBManager()`/`ServerManager()`.
- `core` и `shared` не содержат feature-specific orchestration/зависимостей на feature-модули.
- Изменения архитектурных документов в RU/EN выполняются синхронно.

## 4. Core Cross-Cutting Contracts
- Ошибки и результаты операций: `AppFailure` и `AppResult`.
- Защита от устаревших async-ответов: `LatestRequestGuard`.
- Платформенные различия инкапсулированы в `core/platform`.

## 5. Related Docs
- Границы модулей: `docs/ru/architecture/module-boundaries.ru.md` и EN twin.
- Контракты state ownership: `docs/ru/architecture/state_management_matrix.ru.md` и EN twin.
- Стратегия тестирования: `docs/ru/testing/strategy.ru.md` и EN twin.
- Правила RU/EN синхронизации зафиксированы в `AGENTS.md`.

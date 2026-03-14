**Короткий executive summary**
Проект уже production-ready по платформам и релизному процессу, но архитектурно упирается в концентрацию ответственности в нескольких “god”-модулях (`main.dart`, `DBManager`, `PrimarySourceViewModel`, `utils/common.dart`) и в непоследовательные границы слоёв (часть экранов работает напрямую с DB/сервисами). Рекомендация: **эволюционный deep-refactor без rewrite**, с переходом к **hybrid feature-first** структуре и целевым **полным переходом на BLoC/Cubit** (без остатка `Provider/ChangeNotifier` после завершения Phase 3.7), формализацией контрактов маршрутов/ошибок/данных, декомпозицией state/data orchestration, обязательными unit+widget тестами в CI и постоянной RU/EN документацией с policy синхронизации.

---

# Revelation — Architecture Audit & Deep Refactor Roadmap (2026-03-14)

## 1. Title
**Revelation Architecture Audit & Practically Actionable Deep Refactor Roadmap (No Rewrite, Evolutionary)**

## 2. Executive summary
- Текущая архитектура: **слойно-типовая (type-first/layer-ish)** с фактическим hybrid в коде.
- Главный долг: **размытые boundaries** между UI/state/data/infra.
- Главные точки риска:  
  [main.dart](C:/Users/karna/Projects/Revelation/lib/main.dart:75),  
  [db_manager.dart](C:/Users/karna/Projects/Revelation/lib/infra/db/runtime/db_manager.dart:53),  
  [primary_source_view_model.dart](C:/Users/karna/Projects/Revelation/lib/features/primary_sources/presentation/controllers/primary_source_view_model.dart:19),  
  [common.dart](C:/Users/karna/Projects/Revelation/lib/shared/utils/common.dart:1),  
  [app_router.dart](C:/Users/karna/Projects/Revelation/lib/app/router/app_router.dart:47).
- CI зрелый для билдов/релизов, но как quality gate неполный:  
  [flutter_build.yml](C:/Users/karna/Projects/Revelation/.github/workflows/flutter_build.yml:46) содержит `analyze`, но нет обязательных unit/widget тестов.
- Тестовый baseline минимальный: 1 test file (`test/utils/pronunciation_test.dart`), integration tests отсутствуют.
- Локализация по ключам синхронизирована (`en/es/uk/ru`), это сильная сторона.
- Рекомендуемый путь: **7 фаз (0..5 + 3.7)**, сначала safety net + границы + low-risk wins, затем data/state/navigation refactor, потом полный state migration на BLoC/Cubit, затем тесты и governance.
- State management политика: **полный переход на BLoC/Cubit с запретом Provider/ChangeNotifier в целевом состоянии**.

## 3. Project context
- Домен: Bible study app (Book of Revelation), multi-platform: Web/Android/Windows/Linux.
- Текущий стек подтвержден в [pubspec.yaml](C:/Users/karna/Projects/Revelation/pubspec.yaml:8).
- Текущий bootstrap/DI/router:  
  [main.dart](C:/Users/karna/Projects/Revelation/lib/main.dart:29),  
  [app_router.dart](C:/Users/karna/Projects/Revelation/lib/app/router/app_router.dart:16).
- DB layer: Drift common/localized DB + web/native connectors:  
  [db_common.dart](C:/Users/karna/Projects/Revelation/lib/infra/db/common/db_common.dart:129),  
  [db_localized.dart](C:/Users/karna/Projects/Revelation/lib/infra/db/localized/db_localized.dart:45),  
  [connect/native.dart](C:/Users/karna/Projects/Revelation/lib/infra/db/connectors/native.dart:21),  
  [connect/web.dart](C:/Users/karna/Projects/Revelation/lib/infra/db/connectors/web.dart:27).
- Supabase integration: [server_manager.dart](C:/Users/karna/Projects/Revelation/lib/infra/remote/supabase/server_manager.dart:15).
- Локальные skills изучены все; в roadmap используются: `flutter-architecture`, `flutter-testing`, `flutter-drift`, `flutter-internationalization`, `flutter-adaptive-ui`, `flutter-expert`, `revelation`.
- Baseline quality (проверено локально): `flutter analyze` — clean; `flutter test` — pass (1 файл).

## 4. Audit methodology
### Audit checklist
- [x] Инвентаризация структуры `lib/`, `test/`, `.github/workflows/`, `.agents/skills/`.
- [x] Анализ bootstrap/composition root.
- [x] Анализ DI/singleton usage.
- [x] Анализ routing/contracts.
- [x] Анализ state ownership/async orchestration.
- [x] Анализ data layer/Drift/Supabase.
- [x] Анализ l10n/theming/adaptive patterns.
- [x] Анализ тестовой пирамиды и CI gates.
- [x] Анализ документации и governance пробелов.
- [x] Baseline analyze/test прогон.

### Ограничения аудита
- Профилирование runtime perf (DevTools traces) не проводилось в этом проходе.
- Не проводились e2e прогонки на всех устройствах/магазинных build flavors.
- Фокус на архитектуре, а не на pixel/UI polishing.

## 5. Current architecture summary
- `main.dart` содержит одновременно: bootstrap, error handlers, window init, settings init, server init, db init, global handlers, provider wiring.
- `get_it` используется как глобальный locator ограниченно (Talker + cache manager), но это создает “скрытый global access”.
- `DBManager` — singleton + in-memory hub, хранит массивы таблиц и раздает их во все слои.
- `ServerManager` — singleton для Supabase init/download/info.
- State management:
  - Исторически: `Provider + ChangeNotifier` (`SettingsViewModel`, `PrimarySourcesViewModel`, `MainViewModel` и локальные VM).
  - Target: BLoC/Cubit-only, с миграцией и декомпозицией state в отдельной Phase 3.7.
- UI неоднороден:
  - Часть экранов идёт через VM.
  - Часть экранов работает напрямую с DB/service/link logic.
- Router:
  - `AppRouter` singleton.
  - Не typed contracts, `state.extra` часто `Map<String, dynamic>` и query fallback.
- Тестирование: один unit-test файл, widget/integration покрытие практически отсутствует.
- Документация архитектуры внутри репозитория отсутствует (нет `docs/`).

## 6. Current strengths worth preserving
- **Drift schema split (common/localized)** хорошо соответствует домену и i18n данным.
- **Web DB version sync strategy** в `connect/web.dart` зрелая и продуманная.
- **Talker + global error hooks** уже есть, не надо изобретать с нуля.
- **Локализации синхронизированы** по ключам для `en/es/uk/ru`.
- **Release version sync** уже автоматизирован через `revelation` skill/script.
- **Анализатор чистый** — хорошая дисциплина для безопасной миграции.
- **No giant framework churn needed**: текущий стек способен масштабироваться при корректных границах.

## 7. Main architectural problems and risks
### P0 (критично)
- Сильная концентрация ответственности в крупных файлах:
  - `PrimarySourceToolbar` ~1061 lines,
  - `ImagePreview` ~1034 lines,
  - `PrimarySourceScreen` ~794 lines,
  - `common.dart` ~767 lines,
  - `PrimarySourceViewModel` ~566 lines.
- `DBManager` как global data hub с `late` кэшами и cross-feature доступом.
- Непредсказуемость маршрутов через `Map<String, dynamic>` в `state.extra`.
- Нет обязательных unit/widget тестов в CI.
- Отсутствует архитектурная RU/EN документация и governance.

### P1 (важно)
- Непоследовательный state ownership: VM + прямые DB calls в UI.
- Async race risks в image loading/state updates.
- Отсутствие lifecycle cleanup (`dispose`) в некоторых state holders.
- `utils/common.dart` смешивает platform, link, dialog, markdown, parser, file sync, diagnostics.
- Историческое дублирование/размытые границы state setup (`MainViewModel` глобально и локально) как индикатор слабой формализации state contracts.

### P2 (желательно)
- Избыточные/неиспользуемые зависимости/регистрации (например, cache manager registration без фактического использования).
- Повторяющийся UI logic для desktop drag-scroll.
- Legacy поля в моделях (`link1/2/3`) рядом с новой link-структурой.

## 8. Target architecture recommendation
### Рекомендация
**Hybrid Feature-First Architecture**:
- `features/*` для бизнес-фич.
- `shared/*` для повторно используемых UI-компонентов.
- `core/*` для стабильных базовых абстракций (errors, logging, env, platform policy).
- `infra/*` для DB/remote/storage implementations.

### Почему не strict чистый Clean Architecture
- Для Revelation полный domain/use-case слой везде даст оверхед.
- Нужен **селективный application/domain слой** только для сложных сценариев (`primary_sources`, `topic content orchestration`, sync flows).

### Почему не giant rewrite
- Риск регрессий на production multi-platform.
- Уже есть рабочие подсистемы, которые лучше эволюционно укреплять.

### Насколько строгий feature-first подходит Revelation
- **Подходит частично (рекомендовано):** presentation/application/data внутри крупных фич.
- **Не нужен “тотальный strict feature-first”:** `l10n`, `db schema`, `app bootstrap`, `release scripts` логичнее оставить вне feature-tree.
- Итог: **hybrid > strict** для этого проекта.

## 9. Recommended state management direction
### Выбор
**Полный переход на BLoC/Cubit с финальным запретом Provider/ChangeNotifier в production-коде**.

### Обоснование
- Принято явное архитектурное решение: максимальная предсказуемость, масштабируемость и формализованные state transitions важнее migration cost.
- После завершения folder/module migration (`Phase 3.5`) кодовая база готова к контролируемой миграции state-слоя без big-bang rewrite.
- `PrimarySource` требует гранулярного разрезания состояния; BLoC/Cubit дает ясную FSM-модель и точечный контроль rebuild-поведения.

### Практический target pattern
- `FeatureState` как immutable DTO (предпочтительно с `equatable`).
- `FeatureCubit` для state-driven сценариев, `FeatureBloc` для event-heavy сценариев.
- `BlocSelector` / `buildWhen` для гранулярных перерисовок.
- `PrimarySource` разбивается на несколько cubit-срезов (image/page settings/selection/description/viewport/session).
- Вынесение тяжёлой orchestration в application services/use-cases; UI не ходит напрямую в `DBManager/ServerManager`.

### Альтернативы и trade-offs
- Сохранение Provider/ChangeNotifier: +ниже краткосрочная стоимость, -слабее формализация переходов, хуже масштабирование сложных экранов (`primary_sources`).
- Riverpod migration: +DI/testability ergonomics, -дополнительный paradigm churn при уже принятом решении на BLoC/Cubit.
- Гибрид Provider + Cubit в долгую: запрещено как целевое состояние; допускается только как краткоживущий transitional слой в рамках Phase 3.7.

## 10. Recommended folder/module structure
### Target structure (proposed)
```text
lib/
  app/
    bootstrap/
    di/
    router/
  core/
    errors/
    logging/
    env/
    platform/
    async/
  infra/
    db/
      common/
      localized/
      connectors/
    remote/
      supabase/
    storage/
      preferences/
      files/
  shared/
    ui/
      widgets/
      dialogs/
    utils/
  features/
    topics/
      presentation/
      application/
      data/
    primary_sources/
      presentation/
      application/
      data/
    settings/
      presentation/
      application/
      data/
    about/
      presentation/
      application/
      data/
    download/
      presentation/
  l10n/
```

### Folder migration map (current -> target)
| Current | Target | Priority | Note |
|---|---|---:|---|
| `lib/screens/main/*` | `lib/features/topics/presentation/*` | P0 | Topics list/cards + drawer related split |
| `lib/screens/topic/*` | `lib/features/topics/presentation/*` | P0 | Topic markdown/content screen |
| `lib/screens/primary_sources/*` | `lib/features/primary_sources/presentation/list/*` | P0 | Source list/item |
| `lib/screens/primary_source/*` | `lib/features/primary_sources/presentation/detail/*` | P0 | Decompose by widgets/controllers |
| `lib/features/*/presentation/viewmodels/*` | `lib/features/*/presentation/bloc/*` | P0 | Replace ChangeNotifier VM with Cubit/Bloc state holders |
| `lib/repositories/settings_repository.dart` | `lib/features/settings/data/*` | P1 | prefs adapter |
| `lib/repositories/pages_repository.dart` | `lib/features/primary_sources/data/*` | P1 | page state persistence |
| `lib/repositories/primary_sources_db_repository.dart` | `lib/features/primary_sources/data/*` | P0 | core data mapping |
| `lib/managers/db_manager.dart` | `lib/infra/db/*` + feature data sources | P0 | Break global hub |
| `lib/managers/server_manager.dart` | `lib/infra/remote/supabase/*` | P0 | Explicit interfaces |
| `lib/utils/common.dart` | `lib/core/*` + `lib/shared/utils/*` | P0 | Split by responsibility |
| `lib/common_widgets/*` | `lib/shared/ui/widgets/*` | P1 | Shared presentation |
| `lib/app_router.dart` | `lib/app/router/*` | P0 | typed route contracts |
| `lib/theme.dart` | `lib/core/theme/*` | P1 | keep logic, split files |
| `lib/controllers/audio_controller.dart` | `lib/core/audio/*` or `features/*` usage adapters | P1 | remove hidden singleton access |
| `lib/db/*` | `lib/infra/db/*` | P0 | drift schema/connectors stay but rehomed |

## 11. Architectural boundaries and rules
### Boundary rules
- `presentation` не импортирует `infra` напрямую.
- `presentation` общается с `application/controller`.
- `presentation` state holders реализуются через `Cubit/Bloc` (без `ChangeNotifier`).
- `data` слой единственный знает про Drift row/JSON raw.
- `infra` не зависит от feature presentation.
- `shared/ui` не содержит feature business logic.
- `core` не зависит от конкретных фич.

### Dependency rules
- Разрешенные направления:
  - `features/*/presentation -> features/*/application -> features/*/data -> infra`.
  - `features/* -> shared, core`.
- Запрещенные:
  - `screens/widgets -> DBManager()/ServerManager()`.
  - `router` contracts через untyped maps.
  - Новый runtime-код на `Provider/ChangeNotifier` после старта Phase 3.7 запрещен.
  - Глобальные mutable singletons в feature-логике.

### Route contract rules
- Ввести route args классы:
  - `TopicRouteArgs { route, name?, description? }`
  - `PrimarySourceRouteArgs { sourceId, pageName?, wordIndex? }`
- Навигация по `sourceId`, а не передача тяжелых mutable model objects через `extra`.

### Error model rules
- Ввести `AppError` hierarchy (`DataError`, `NetworkError`, `ValidationError`, `UnexpectedError`).
- Любой async command возвращает явно success/error state, не теряет исключения молча.

### Grep/search validation strategy (после каждого шага)
- `rg "DBManager\\(\\)" lib/screens lib/common_widgets`
- `rg "ServerManager\\(\\)" lib/screens lib/features/*/presentation`
- `rg "state\\.extra is Map<String, dynamic>" lib`
- `rg "GetIt\\.I<" lib/features`
- `rg "showCustomDialog\\(" lib/features/*/data`
- `rg "TODO|FIXME" lib`

## 12. Documentation strategy (RU + EN mandatory)
### Цель
Короткая, понятная, постоянно синхронизированная двуязычная документация.

### Proposed docs set
- `docs/architecture/overview.ru.md`
- `docs/architecture/overview.en.md`
- `docs/architecture/module-boundaries.ru.md`
- `docs/architecture/module-boundaries.en.md`
- `docs/testing/strategy.ru.md`
- `docs/testing/strategy.en.md`
- `docs/adr/ADR-001-...md` ... `ADR-006-...md`
- `docs/process/change-checklist.ru.md`
- `docs/process/change-checklist.en.md`

### Docs synchronization policy RU/EN
- Каждому RU документу соответствует EN twin с одинаковой структурой заголовков.
- В шапке каждого документа:
  - `Doc-Version`,
  - `Last-Updated`,
  - `Source-Commit`.
- Structural/code changes в PR **обязаны** обновлять RU+EN.
- Если изменен только один язык — CI warning/fail (поэтапно fail).

### Минимальный набор ADR
- ADR-001: Hybrid feature-first target architecture.
- ADR-002: State management policy on BLoC/Cubit (zero Provider/ChangeNotifier after Phase 3.7).
- ADR-003: Typed routing contracts.
- ADR-004: DBManager decomposition and data source boundaries.
- ADR-005: Testing pyramid + CI quality gates.
- ADR-006: RU/EN docs sync governance.

### Нужен ли новый skill
**Да, оправдано.**  
Предложение: `revelation-architecture-governance` (или `revelation-docs-sync`) для recurring work:
- RU/EN docs update checklist.
- ADR template generation.
- PR docs gate checklist.
- Commands for docs parity checks.

## 13. Testing strategy
### Current state
- Unit tests: минимально (1 файл).
- Widget tests: отсутствуют.
- Integration tests: отсутствуют.
- Architecture currently test-hostile из-за singleton/global access.

### Target testing pyramid (for Revelation)
- 60-70% unit tests.
- 25-35% widget tests.
- 5-10% selective integration smoke tests.

### Priority test coverage plan
- P0 unit:
  - `DescriptionContentService`
  - `PrimarySourceReferenceResolver`
  - `PagesSettings.pack/unpack`
  - route args parsing/validation
  - DB mapping adapters (in-memory drift)
- P1 widget:
  - `SettingsScreen` interactions
  - `TopicScreen` markdown link handling
  - `PrimarySourcesScreen` load/error/empty states
  - `PrimarySourceToolbar` enable/disable logic
- P2 integration:
  - app bootstrap smoke
  - navigation main -> topic -> primary source
  - language switch + DB localized content reload

### Test infrastructure
- In-memory Drift DB fixtures.
- Fake `ServerManager`/remote downloader.
- Fake logger/talker adapter.
- Test harness for router + bloc/cubit state holders.
- Optional golden tests for top screens after stabilization.

### Regression safety strategy
- Branch-by-abstraction migration.
- Compatibility adapters на переходный период.
- Baseline snapshot test list перед каждой фазой.
- “No behavior change” commits отдельно от structural moves.

## 14. CI / quality gates strategy
### Current gap
- CI workflow только на push в `main`, с `analyze`, без unit/widget gate.
- PR quality gates отсутствуют.

### CI rollout plan for tests
- Step 1 (P0): добавить PR workflow:
  - `dart format --output=none --set-exit-if-changed .`
  - `flutter analyze`
  - `flutter test --coverage`
- Step 2 (P1): разделить тесты по tags/suites:
  - `unit+widget` обязательно на PR.
  - integration smoke по label/manual/nightly.
- Step 3 (P2): добавить threshold policy:
  - стартовый coverage gate мягкий,
  - постепенное повышение.
- Step 4 (P2): добавить docs sync check:
  - RU/EN pair existence + header parity.
- Step 5 (P2): import-boundary checks (grep-based) как fast gate.

### Dependency review strategy
- Ежеквартальный audit `pubspec`:
  - remove unused deps,
  - classify deps by layer owner,
  - ban new deps без ADR/justification.
- Немедленный кандидат на пересмотр: `flutter_cache_manager` (зарегистрирован, но не используется).
- Добавить test-only deps: `mocktail` (или аналог), `integration_test`.

## 15. Skills enablement plan
### Skills to use in refactor execution
- `flutter-architecture`: target structure, migration sequencing, boundaries.
- `flutter-drift`: decomposition DB access/data contracts/migrations/tests.
- `flutter-testing`: unit/widget/integration infra and CI rollout.
- `flutter-internationalization`: RU/EN + l10n process checks.
- `flutter-adaptive-ui`: normalize responsive policies and platform branches.
- `flutter-expert`: widget decomposition/perf-sensitive refactors.
- `revelation`: release version sync (без ручного расхождения файлов).

### Suggested new skill (justified)
- `revelation-docs-sync`:
  - RU/EN docs twin enforcement,
  - ADR checklist,
  - mandatory docs update triggers,
  - PR checklist automation snippets.

## 16. Phased migration roadmap

### Phase 0 — Audit stabilization / safety net / baseline
- Цель: зафиксировать безопасную точку старта и измеримые baseline.
- Почему нужна: без baseline невозможно управлять регрессиями при глубоком рефакторинге.
- Concrete tasks:
  - [P0] Зафиксировать архитектурный baseline doc (RU/EN).
  - [P0] Добавить PR workflow с `format + analyze + test`.
  - [P0] Создать test harness skeleton (fake logger, fake env, fake remote).
  - [P1] Ввести initial grep checks для forbidden patterns.
- Affected files/modules/areas:
  - `.github/workflows/*`
  - `test/` infrastructure
  - `docs/` (new)
- Риски:
  - Ложноположительные CI падения на старте.
- Dependencies/prerequisites:
  - Нет.
- Relevant skills:
  - `flutter-testing`, `flutter-architecture`, `flutter-internationalization`.
- Test expectations:
  - Existing tests pass.
  - New CI run validates format/analyze/test.
- Docs update expectations (RU + EN):
  - `overview.ru/en` created.
  - `testing.strategy.ru/en` created.
- Quality gates:
  - analyze/test mandatory on PR.
- Criteria of done:
  - Baseline зафиксирован.
  - PR без этих checks не merge.

### Phase 1 — Quick wins / high-impact low-risk improvements
- Цель: убрать наиболее болезненные structural anti-patterns без изменения фич.
- Почему нужна: быстрое снижение риска до крупных миграций.
- Concrete tasks:
  - [P0] Убрать дублирование `MainViewModel` provider registration.
  - [P0] Выделить bootstrap/DI из `main.dart` в `app/bootstrap` и `app/di`.
  - [P0] Ввести typed route args wrappers (пока с backward-compatible adapters).
  - [P0] Добавить `dispose`/lifecycle cleanup в длинные state holders.
  - [P1] Разбить `utils/common.dart` на логические модули (links/dialogs/platform/markdown/file-sync).
  - [P1] Убрать или обосновать неиспользуемые DI регистрации/dependencies.
- Affected files/modules/areas:
  - `lib/main.dart`, `lib/app_router.dart`, `lib/utils/common.dart`,
  - `lib/viewmodels/primary_source_view_model.dart`,
  - `lib/screens/main/main_screen.dart`.
- Риски:
  - Скрытые зависимости на старые util-функции.
- Dependencies/prerequisites:
  - Phase 0 completed.
- Relevant skills:
  - `flutter-architecture`, `flutter-expert`, `flutter-testing`.
- Test expectations:
  - Добавить unit tests на route args adapters.
  - Widget smoke for app startup/navigation entry.
- Docs update expectations (RU + EN):
  - Обновить module boundaries и changelog архитектуры.
- Quality gates:
  - No new direct `DBManager/ServerManager` calls in UI.
- Criteria of done:
  - main/bootstrap чище.
  - route contracts безопаснее.
  - hot spots частично декомпозированы.

### Phase 2 — Architectural boundaries and folder/module migration
- Цель: перевести структуру на hybrid feature-first без функциональной ломки.
- Почему нужна: текущая type-first структура затрудняет масштабирование и онбординг.
- Concrete tasks:
  - [P0] Создать target folders `app/core/infra/shared/features`.
  - [P0] Мигрировать `settings` и `about` как pilot features.
  - [P1] Мигрировать `topics` presentation/data постепенно.
  - [P1] Ввести boundary import rules (lint/grep).
  - [P2] Добавить временные barrel exports для мягкого перехода import-путей.
- Affected files/modules/areas:
  - `lib/screens/*`, `lib/viewmodels/*`, `lib/repositories/*`, `lib/utils/*`, `lib/common_widgets/*`.
- Риски:
  - Большой объём move/rename конфликтов.
- Dependencies/prerequisites:
  - Phase 1 completed.
- Relevant skills:
  - `flutter-architecture`, `flutter-adaptive-ui`, `flutter-expert`.
- Test expectations:
  - Widget tests на migrated features.
  - Smoke tests imports/build.
- Docs update expectations (RU + EN):
  - folder map + boundaries docs updated.
- Quality gates:
  - Запрещены cross-feature imports в presentation.
- Criteria of done:
  - Минимум 2 фичи полностью migrated в target style.
  - Старые слои не расширяются новым кодом.

### Phase 3 — State/data/navigation refactors
- Цель: устранить ключевые системные долги в state/data/router contracts.
- Почему нужна: именно здесь сегодня максимальный architectural risk.
- Concrete tasks:
  - [P0] Декомпозировать `DBManager` на data sources/repositories/cache policy.
  - [P0] Перенести direct DB access из `TopicList/TopicCard/TopicScreen` в feature controllers/services.
  - [P0] Разделить `PrimarySourceViewModel` на orchestrators:
    - image loading,
    - page settings,
    - description panel.
  - [P0] Убрать untyped `Map extra` contracts для critical routes.
  - [P1] Ввести error/result model и user-facing fallback states.
  - [P1] Стандартизировать async patterns (request token/cancel/ignore stale result).
- Affected files/modules/areas:
  - `lib/infra/db/runtime/db_manager.dart`,
  - `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`,
  - `lib/features/topics/presentation/*`,
  - `lib/features/primary_sources/presentation/detail/*`,
  - `lib/features/primary_sources/presentation/controllers/primary_source_view_model.dart`,
  - `lib/app/router/app_router.dart`.
- Риски:
  - Поведенческие регрессии в primary source UX.
- Dependencies/prerequisites:
  - Phase 2 completed.
- Relevant skills:
  - `flutter-drift`, `flutter-architecture`, `flutter-expert`, `flutter-testing`.
- Test expectations:
  - Unit tests for new repositories/controllers.
  - Widget tests for primary source flows.
  - Integration smoke for route contracts.
- Docs update expectations (RU + EN):
  - ADR-003/ADR-004 finalized.
- Quality gates:
  - zero direct data access from presentation in migrated features.
- Criteria of done:
  - DBManager перестал быть global read hub.
  - Primary source flow предсказуем и покрыт тестами.

### Phase 3.7 — Full state migration to BLoC/Cubit + granular PrimarySource slicing
- Цель: полностью перенести управление состоянием на BLoC/Cubit и убрать legacy state frameworks.
- Почему нужна: без этого останется смешанная архитектура состояния и высокий риск повторной деградации в крупные state-monoliths.
- Concrete tasks:
  - [P0] Утвердить migration matrix `feature -> target cubit/bloc set -> owner state contracts`.
  - [P0] Добавить и настроить BLoC runtime слой (`flutter_bloc`, `BlocObserver`, единые правила ошибок/логирования переходов).
  - [P0] Перевести app composition root c provider wiring на `MultiBlocProvider`/feature-scoped `BlocProvider`.
  - [P0] Мигрировать `settings/about/topics/download` с `ChangeNotifier` на `Cubit/Bloc`.
  - [P0] Разрезать state `PrimarySource` на гранулярные cubit-срезы:
    - source/session context,
    - image loading/cache/local availability,
    - page settings persistence,
    - selection (word/verse/strong),
    - description panel content/navigation,
    - viewport/render controls (zoom/layers/colors/tool mode).
  - [P0] Удалить legacy state слой: `provider` imports, `ChangeNotifier`, `notifyListeners`, viewmodel-only contracts.
  - [P1] Ввести архитектурные guardrails (`rg`/script checks) на запрет нового `Provider/ChangeNotifier` кода в `lib/` и `test/` (кроме исторической документации).
  - [P1] Добавить unit/widget тесты на state transitions и regression-critical сценарии после миграции.
- Affected files/modules/areas:
  - `lib/main.dart`, `lib/app/di/*`, `lib/app/router/*`,
  - `lib/features/*/presentation/*`,
  - `lib/features/primary_sources/{presentation,application}/*`,
  - `scripts/check_forbidden_patterns.dart`,
  - `pubspec.yaml`, `pubspec.lock`.
- Риски:
  - Высокий churn в UI-state bindings и потенциальные behavioral regressions в `primary_sources`.
- Dependencies/prerequisites:
  - Phase 3 и Phase 3.5 completed.
- Relevant skills:
  - `flutter-architecture`, `flutter-expert`, `flutter-testing`.
- Test expectations:
  - Unit tests на все новые cubit/bloc state transitions.
  - Widget tests на критичные user flows с `BlocProvider`.
  - Regression smoke по navigation + primary source interactions.
- Docs update expectations (RU + EN):
  - Обновить `overview`, `module-boundaries`, `testing strategy`, `AGENTS.md`, ADR-002.
- Quality gates:
  - `rg "package:provider|ChangeNotifier|notifyListeners" lib test` не находит production/test code после завершения фазы.
- Criteria of done:
  - В runtime-коде нет `Provider/ChangeNotifier`.
  - Все feature state flows работают через `BLoC/Cubit`.
  - `PrimarySource` state декомпозирован на гранулярные cubit-срезы и покрыт тестами.

### Phase 4 — Testing hardening and CI enforcement
- Цель: сделать качество воспроизводимым и enforceable.
- Почему нужна: без этого архитектура деградирует обратно.
- Concrete tasks:
  - [P0] Обязательные unit+widget tests в PR CI.
  - [P0] Тестовые матрицы по critical feature modules.
  - [P1] Integration smoke tests (selective/nightly).
  - [P1] Coverage trend tracking.
  - [P2] Golden tests для наиболее стабильных экранов.
- Affected files/modules/areas:
  - `.github/workflows/*`, `test/`, `integration_test/`.
- Риски:
  - Увеличение CI времени.
- Dependencies/prerequisites:
  - Phase 3 + Phase 3.7 key refactors merged.
- Relevant skills:
  - `flutter-testing`, `flutter-expert`.
- Test expectations:
  - Unit/widget >= required baseline for all critical features.
- Docs update expectations (RU + EN):
  - testing strategy + CI policy finalized.
- Quality gates:
  - PR blocked if analyze/unit/widget fail.
- Criteria of done:
  - CI реально защищает архитектуру, не декоративно.

### Phase 5 — Docs hardening / final cleanup / governance
- Цель: закрепить архитектуру как процесс, а не разовый refactor.
- Почему нужна: долгосрочная поддержка и онбординг.
- Concrete tasks:
  - [P0] Утвердить RU/EN docs set и sync policy.
  - [P0] Внедрить PR checklist: code + tests + docs RU/EN.
  - [P1] Добавить `revelation-docs-sync` skill (или instruction workflow).
  - [P1] Удалить deprecated adapters и старые пути после стабилизации.
  - [P2] Финальный architecture review + residual debt backlog.
- Affected files/modules/areas:
  - `docs/`, `.agents/skills/*` (new optional), `AGENTS.md`, CI checks.
- Риски:
  - Governance fatigue, если чеклисты слишком тяжёлые.
- Dependencies/prerequisites:
  - Phase 4 completed.
- Relevant skills:
  - `flutter-architecture`, `flutter-internationalization`, `revelation`.
- Test expectations:
  - Regression suite remains green after cleanup.
- Docs update expectations (RU + EN):
  - full parity verified.
- Quality gates:
  - docs sync check enabled.
- Criteria of done:
  - архитектурные правила и docs обновляются по умолчанию при изменениях.

## 17. Risk register
| ID | Risk | Priority | Probability | Impact | Mitigation |
|---|---|---:|---:|---:|---|
| R1 | Регрессии в `primary_source` UX при декомпозиции | P0 | Medium | High | branch-by-abstraction + widget/integration smoke |
| R2 | Затяжная миграция структуры папок | P1 | High | Medium | пилотные feature migrations + import adapters |
| R3 | CI станет слишком долгим | P1 | Medium | Medium | split jobs, caching, selective integration |
| R4 | Команда продолжит писать в legacy folders | P0 | Medium | High | boundary gates + PR checklist |
| R5 | Доки RU/EN разойдутся | P0 | High | Medium | docs sync policy + CI check |
| R6 | Singleton coupling останется скрытым | P0 | Medium | High | centralized DI + banned patterns grep checks |
| R7 | Перегиб с абстракциями | P1 | Medium | Medium | add layers only for complex flows |
| R8 | Обновления DB/Supabase flow сломают web sync | P0 | Low | High | preserve existing connector logic + drift tests |

## 18. What should NOT be changed
- Не делать full rewrite.
- Не оставлять смешанную state-архитектуру (`Provider + BLoC`) после завершения Phase 3.7.
- Не ломать рабочий Drift schema/web-db deployment flow.
- Не убирать Talker/logging hooks без эквивалентной observability.
- Не трогать generated files вручную (`*.g.dart`, generated l10n).
- Не менять release version sync процесс вручную вместо `revelation` script.
- Не смешивать новые feature boundaries с новыми global singletons.

## 19. Recommended execution order
1. Phase 0 целиком.
2. Phase 1 P0 tasks.
3. Phase 2 pilot migrations (`settings`, `about`) + boundary checks.
4. Phase 3 P0 tasks (`DBManager` split, `primary_source` decomposition, typed routes).
5. Phase 3.7 full state migration to `BLoC/Cubit` + `PrimarySource` granular slicing.
6. Phase 4 CI enforcement for tests.
7. Phase 5 governance/docs hardening and cleanup.

## 20. Definition of Done
- Архитектура в hybrid feature-first форме для критичных фич.
- Нет прямого DB/remote access из presentation.
- Typed route contracts заменили map-based critical navigation.
- `primary_source` flow декомпозирован и покрыт тестами.
- В production/test коде отсутствуют `provider`/`ChangeNotifier` state patterns.
- State management унифицирован на `BLoC/Cubit` с гранулярными state slices в `primary_sources`.
- Unit+widget tests обязательны в CI на PR.
- Integration smoke для critical navigation/data flows есть и стабилен.
- RU/EN docs синхронизированы и обновляются при structural changes.
- ADR минимум из 6 ключевых решений зафиксирован.

## 21. Progress journal template
```markdown
# Architecture Refactor Journal

## Entry
- Date:
- Phase:
- Task ID:
- Priority: P0 / P1 / P2
- Owner:

## Change Summary
- What changed:
- Why changed:
- Scope (files/modules):

## Validation
- Analyze: pass/fail
- Unit tests: pass/fail
- Widget tests: pass/fail
- Integration smoke: pass/fail
- Grep boundary checks: pass/fail

## Docs
- RU updated: yes/no (file list)
- EN updated: yes/no (file list)
- ADR updated: yes/no

## Risks / Follow-ups
- New risks:
- Mitigations:
- Next task:
```

## 22. Top 10 highest-impact architectural improvements
1. **P0** Разделить `DBManager` на data sources/repositories с явными контрактами.
2. **P0** Убрать untyped `Map<String, dynamic>` route contracts для `topic/primary_source`.
3. **P0** Декомпозировать `PrimarySourceViewModel` и `primary_source` UI-монолиты.
4. **P0** Полностью мигрировать state слой на `BLoC/Cubit` и удалить `Provider/ChangeNotifier`.
5. **P0** Вынести bootstrap/DI/router composition из `main.dart` в `app/*`.
6. **P0** Сделать unit+widget tests обязательным PR gate в CI.
7. **P1** Разбить `utils/common.dart` на целевые модули и убрать cross-layer util-sink.
8. **P1** Перевести `topics`/`settings`/`about` в hybrid feature-first structure.
9. **P1** Ввести единый error/result model + user-facing fallback states.
10. **P1** Внедрить RU/EN docs sync policy с CI checks и ADR набором.

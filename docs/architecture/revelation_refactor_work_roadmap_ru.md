# Revelation — Рабочий Roadmap Миграции Архитектуры (RU)

Источник: раздел `16. Phased migration roadmap` и `21. Progress journal template` из  
[revelation_architecture_refactor_roadmap_ru.md](C:/Users/karna/Projects/Revelation/docs/architecture/revelation_architecture_refactor_roadmap_ru.md)

Статус: `Phase 0/1/2/3 завершены, Phase 3.5 в работе (P0 started), Phase 4 paused`  
Версия roadmap: `v1`  
Дата создания: `2026-03-08`

## 1. Глобальный чеклист по фазам (пустые чекбоксы)

### Phase 0 — Audit stabilization / safety net / baseline
- [x] Цель фазы зафиксирована: безопасная точка старта и baseline.
- [x] Обоснование фазы зафиксировано: без baseline нельзя управлять регрессиями.
- [x] Задача [P0]: зафиксировать baseline docs (RU/EN).
- [x] Подшаг [P0.1]: создать `overview.ru`.
- [x] Подшаг [P0.2]: создать `overview.en` (можно отложить контент до финала, но файл/план должны быть).
- [x] Подшаг [P0.3]: создать `testing.strategy.ru`.
- [x] Подшаг [P0.4]: создать `testing.strategy.en` (как минимум каркас).
- [x] Задача [P0]: добавить PR workflow c `format + analyze + test`.
- [x] Подшаг [P0.5]: включить `dart format --output=none --set-exit-if-changed .`.
- [x] Подшаг [P0.6]: включить `flutter analyze`.
- [x] Подшаг [P0.7]: включить `flutter test`.
- [x] Задача [P0]: создать test harness skeleton (fake logger, fake env, fake remote).
- [x] Подшаг [P0.8]: подготовить test utilities/fakes.
- [x] Задача [P1]: ввести initial grep checks для forbidden patterns.
- [x] Подшаг [P0.9]: добавить быстрые проверки на `DBManager()/ServerManager()` в UI.
- [x] Подшаг [P0.10]: добавить проверку на map-based route contracts в критичных местах.
- [x] Affected areas верифицированы: `.github/workflows/*`, `test/*`, `docs/*`.
- [x] Риски проверены и записаны.
- [x] Dependencies/prerequisites подтверждены (`нет`).
- [x] Relevant skills назначены.
- [x] Test expectations выполнены.
- [x] Docs update expectations выполнены (RU + EN plan).
- [x] Quality gates пройдены.
- [x] Criteria of done выполнен.

### Phase 1 — Quick wins / high-impact low-risk improvements
- [x] Цель фазы зафиксирована: убрать high-impact structural anti-patterns без функциональной ломки.
- [x] Обоснование фазы зафиксировано: быстрый и безопасный выигрыш перед большими миграциями.
- [x] Задача [P0]: убрать дублирование `MainViewModel` provider registration.
- [x] Задача [P0]: выделить bootstrap/DI из `main.dart` в `app/bootstrap` и `app/di`.
- [x] Подшаг [P1.1]: вынести bootstrap sequence.
- [x] Подшаг [P1.2]: вынести DI registration.
- [x] Задача [P0]: ввести typed route args wrappers (с временной backward-compatible адаптацией).
- [x] Задача [P0]: добавить `dispose`/lifecycle cleanup в длинные state holders.
- [x] Задача [P1]: разбить `utils/common.dart` на логические модули (links/dialogs/platform/markdown/file-sync).
- [x] Задача [P1]: убрать или обосновать неиспользуемые DI регистрации/dependencies.
- [x] Affected areas верифицированы: `lib/main.dart`, `lib/app_router.dart`, `lib/utils/common.dart`, `lib/viewmodels/primary_source_view_model.dart`, `lib/screens/main/main_screen.dart`.
- [x] Риски проверены и записаны.
- [x] Dependencies/prerequisites подтверждены (`Phase 0 completed`).
- [x] Relevant skills назначены.
- [x] Test expectations выполнены.
- [x] Docs update expectations выполнены.
- [x] Quality gates пройдены.
- [x] Criteria of done выполнен.

### Phase 2 — Architectural boundaries and folder/module migration
- [x] Цель фазы зафиксирована: перейти к hybrid feature-first структуре без массовой ломки.
- [x] Обоснование фазы зафиксировано: текущая структура мешает масштабированию/онбордингу.
- [x] Задача [P0]: создать target folders `app/core/infra/shared/features`.
- [x] Задача [P0]: мигрировать `settings` и `about` как pilot features.
- [x] Подшаг [P2.1]: миграция `settings`.
- [x] Подшаг [P2.2]: миграция `about`.
- [x] Задача [P1]: мигрировать `topics` presentation/data поэтапно.
- [x] Задача [P1]: ввести boundary import rules (lint/grep).
- [x] Задача [P2]: добавить временные barrel exports для мягкого перехода import-путей.
- [x] Affected areas верифицированы: `lib/screens/*`, `lib/viewmodels/*`, `lib/repositories/*`, `lib/utils/*`, `lib/common_widgets/*`.
- [x] Риски проверены и записаны.
- [x] Dependencies/prerequisites подтверждены (`Phase 1 completed`).
- [x] Relevant skills назначены.
- [x] Test expectations выполнены.
- [x] Docs update expectations выполнены.
- [x] Quality gates пройдены.
- [x] Criteria of done выполнен.

### Phase 3 — State/data/navigation refactors
- [x] Цель фазы зафиксирована: устранить ключевой долг в state/data/router.
- [x] Обоснование фазы зафиксировано: здесь максимальный architectural risk.
- [x] Задача [P0]: декомпозировать `DBManager` на data sources/repositories/cache policy.
- [x] Задача [P0]: перенести direct DB access из `TopicList/TopicCard/TopicScreen` в feature controllers/services.
- [x] Задача [P0]: разделить `PrimarySourceViewModel` на orchestrators.
- [x] Подшаг [P3.1]: image loading orchestration.
- [x] Подшаг [P3.2]: page settings orchestration.
- [x] Подшаг [P3.3]: description panel orchestration.
- [x] Задача [P0]: убрать untyped `Map extra` contracts для critical routes.
- [x] Задача [P1]: ввести error/result model и user-facing fallback states.
- [x] Задача [P1]: стандартизировать async patterns (request token/cancel/ignore stale result).
- [x] Affected areas верифицированы: `lib/managers/db_manager.dart`, `lib/repositories/primary_sources_db_repository.dart`, `lib/screens/topic/*`, `lib/screens/primary_source/*`, `lib/viewmodels/primary_source_view_model.dart`, `lib/app_router.dart`.
- [x] Риски проверены и записаны.
- [x] Dependencies/prerequisites подтверждены (`Phase 2 completed`).
- [x] Relevant skills назначены.
- [x] Test expectations выполнены.
- [x] Docs update expectations выполнены.
- [x] Quality gates пройдены.
- [x] Criteria of done выполнен.

### Phase 3.5 — Folder/module structure governance
- [x] Цель фазы зафиксирована: привести структуру каталогов к feature-first target и предотвратить разрастание legacy.
- [x] Обоснование фазы зафиксировано: расположение файлов является архитектурным контрактом, а не косметикой.
- [x] Задача [P0]: выполнить фактический аудит `lib/*` против `section 10` target-structure.
- [x] Задача [P0]: зафиксировать mandatory file placement rule как отдельное правило архитектуры.
- [x] Задача [P0]: добавить automated enforcement для запрета новых файлов в legacy-каталогах.
- [x] Задача [P0]: зафиксировать zero-legacy migration plan по всем legacy-каталогам.
- [ ] Задача [P1]: мигрировать `lib/screens/*` в `features/*/presentation/*` и `shared/ui/*`.
- [ ] Задача [P1]: мигрировать `lib/viewmodels/*` в `features/*/presentation/controllers/*` (или orchestrators).
- [ ] Задача [P1]: мигрировать `lib/repositories/*` в `features/*/data/repositories/*`.
- [ ] Задача [P1]: мигрировать `lib/services/*` в `features/*/application/*` или `infra/*`.
- [ ] Задача [P1]: мигрировать `lib/common_widgets/*` в `shared/ui/widgets/*`.
- [ ] Задача [P1]: мигрировать `lib/controllers/*` в `core/*` или `features/*/presentation/controllers/*`.
- [ ] Задача [P1]: мигрировать `lib/models/*` в `features/*/data/models/*` и `shared/*`.
- [ ] Задача [P1]: мигрировать `lib/db/*` в `infra/db/{common,localized,connectors}/*`.
- [ ] Задача [P1]: мигрировать `lib/managers/*` в `infra/*` adapters (legacy wrappers удалить).
- [ ] Задача [P1]: мигрировать `lib/utils/*` в `core/*`, `shared/utils/*`, `infra/*`.
- [ ] Задача [P0]: удалить пустые legacy-каталоги из `lib/` и ужесточить checks до `zero legacy`.
- [ ] Задача [P0]: сузить top-level `lib` до canonical набора (`app/core/infra/shared/features/l10n`).
- [x] Affected areas верифицированы: `lib/*`, `scripts/check_forbidden_patterns.dart`, `docs/architecture/*`.
- [x] Риски проверены и записаны.
- [x] Dependencies/prerequisites подтверждены (`Phase 3 completed`).
- [x] Relevant skills назначены.
- [x] Test expectations выполнены.
- [x] Docs update expectations выполнены.
- [x] Quality gates пройдены.
- [ ] Criteria of done выполнен.

### Phase 4 — Testing hardening and CI enforcement
- [x] Цель фазы зафиксирована: сделать качество воспроизводимым и enforceable.
- [x] Обоснование фазы зафиксировано: без этого архитектура деградирует обратно.
- [x] Задача [P0]: unit+widget tests обязательны в PR CI.
- [ ] Задача [P0]: тестовые матрицы по critical feature modules.
- [ ] Задача [P1]: selective integration smoke tests (nightly/manual/label-based).
- [ ] Задача [P1]: coverage trend tracking.
- [ ] Задача [P2]: golden tests для стабильных экранов.
- [ ] Affected areas верифицированы: `.github/workflows/*`, `test/*`, `integration_test/*`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 3 key refactors merged`).
- [x] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены.
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

### Phase 5 — Docs hardening / final cleanup / governance
- [ ] Цель фазы зафиксирована: закрепить архитектуру как процесс.
- [ ] Обоснование фазы зафиксировано: долгосрочная поддержка и онбординг.
- [ ] Задача [P0]: утвердить RU/EN docs set и sync policy.
- [ ] Задача [P0]: внедрить PR checklist `code + tests + docs RU/EN`.
- [ ] Задача [P1]: добавить `revelation-docs-sync` skill (или instruction workflow).
- [ ] Задача [P1]: удалить deprecated adapters и legacy paths после стабилизации.
- [ ] Задача [P2]: финальный architecture review + residual debt backlog.
- [ ] Affected areas верифицированы: `docs/*`, `.agents/skills/*`, `AGENTS.md`, CI checks.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 4 completed`).
- [ ] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены.
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

## 2. Рабочая структура каждой фазы (для исполнения)

### Шаблон исполнения фазы
- Цель:
- Почему эта фаза нужна:
- Конкретные задачи:
- Affected files/modules/areas:
- Риски:
- Dependencies/prerequisites:
- Relevant skills:
- Test expectations:
- Docs update expectations (RU + EN):
- Quality gates:
- Criteria of done:

## 3. Приоритеты (P0 / P1 / P2)

- `P0`: критично, блокирует дальнейшие фазы или несет высокий риск регрессии.
- `P1`: важно, дает высокий/средний эффект, но не блокирует старт следующих этапов.
- `P2`: желательные улучшения/полировка/укрепление после стабилизации.

## 4. Правила ведения этого рабочего roadmap

- Отмечать чекбоксы только после фактического выполнения и валидации.
- Любое завершение задачи фиксировать записью в логе ниже.
- Любой `P0` шаг без тестов/валидации не считается завершенным.
- Этот файл пока ведется на русском; перевод на английский делаем при закрытии миграции.

## 4.1 Zero-Legacy План Миграции Каталогов

### 4.1.1 Текущий legacy inventory (на 2026-03-08)

| Legacy каталог | Dart files | Target location |
|---|---:|---|
| `lib/screens` | 24 | `lib/features/*/presentation/*`, `lib/shared/ui/*` |
| `lib/viewmodels` | 5 | `lib/features/*/presentation/controllers/*` |
| `lib/repositories` | 3 | `lib/features/*/data/repositories/*` |
| `lib/services` | 2 | `lib/features/*/application/*`, `lib/infra/*` |
| `lib/common_widgets` | 5 | `lib/shared/ui/widgets/*` |
| `lib/controllers` | 2 | `lib/core/*`, `lib/features/*/presentation/controllers/*` |
| `lib/models` | 17 | `lib/features/*/data/models/*`, `lib/shared/*` |
| `lib/db` | 8 | `lib/infra/db/{common,localized,connectors}/*` |
| `lib/managers` | 2 | `lib/infra/*` (adapter implementations) |
| `lib/utils` | 22 | `lib/core/*`, `lib/shared/utils/*`, `lib/infra/*` |

### 4.1.2 Волны миграции (без legacy остатка)

1. `Wave A (P0)`: `primary_sources` вертикальный срез
   - `screens/primary_source/*`, `screens/primary_sources/*`, `viewmodels/primary_source*`, `repositories/pages_repository.dart`, `repositories/primary_sources_db_repository.dart`, `services/description_*`.
   - Target: `features/primary_sources/{presentation,application,data}` + `shared/ui/widgets`.
   - Exit: нет imports из `screens/viewmodels/repositories/services` в primary_sources feature.
2. `Wave B (P0)`: `topics + main + download`
   - `screens/main/*`, `screens/topic/*`, `screens/download/*`, `viewmodels/main_view_model.dart`.
   - Target: `features/topics/*`, `features/download/presentation/*`.
   - Exit: роуты используют только feature-пути.
3. `Wave C (P1)`: `about + settings` legacy cleanup
   - удалить оставшиеся adapters и imports на `screens/about/*`, `screens/settings/*`.
   - Target: `features/about/*`, `features/settings/*` already canonical.
   - Exit: `lib/screens/about` и `lib/screens/settings` удалены.
4. `Wave D (P1)`: shared UI и контроллеры
   - `common_widgets/*`, `controllers/*`.
   - Target: `shared/ui/widgets/*`, `core/*` или feature controllers.
   - Exit: `lib/common_widgets` и `lib/controllers` удалены.
5. `Wave E (P1)`: data contracts/models consolidation
   - `models/*`, `repositories/*`, `services/*` остатки.
   - Target: feature-local `data/models`, `data/repositories`, `application/*`, plus minimal `shared/*`.
   - Exit: `lib/models`, `lib/repositories`, `lib/services` удалены.
6. `Wave F (P0)`: infra finalization
   - `db/*`, `managers/*`, `utils/*` остатки.
   - Target: `infra/db/*`, `infra/remote/*`, `core/*`, `shared/utils/*`.
   - Exit: `lib/db`, `lib/managers`, `lib/utils` удалены.
7. `Wave G (P0)`: hard cleanup and policy lock
   - удалить legacy allowlist, ужесточить checks до запрета legacy каталогов как таковых.
   - итоговый top-level `lib`: только `app/core/infra/shared/features/l10n`.

### 4.1.3 Definition of Done (Zero Legacy)

- В `lib/` отсутствуют legacy-каталоги: `screens`, `viewmodels`, `repositories`, `services`, `common_widgets`, `controllers`, `models`, `db`, `managers`, `utils`.
- Все imports переведены на canonical target-пути.
- `scripts/check_forbidden_patterns.dart` падает при появлении любого legacy каталога/файла.
- После каждой волны обязательны: `dart run scripts/check_forbidden_patterns.dart`, `flutter analyze`, `flutter test`.

---

## 5. Лог миграции (на основе раздела 21 аудита)

### 5.1 Шаблон записи в лог

```markdown
### [YYYY-MM-DD HH:MM] Phase X / Task <ID> / <Короткое название>
- Статус: done / blocked / partial
- Priority: P0 / P1 / P2
- What changed:
- Why changed:
- Scope (files/modules):
- Validation:
  - Analyze: pass/fail
  - Unit tests: pass/fail
  - Widget tests: pass/fail
  - Integration smoke: pass/fail
  - Grep boundary checks: pass/fail
- Docs:
  - RU updated: yes/no (file list)
  - EN updated: yes/no (file list)
  - ADR updated: yes/no
- Risks / follow-ups:
  - New risks:
  - Mitigations:
  - Next task:
```

### 5.2 Журнал выполнения

#### [2026-03-08 00:00] Roadmap initialization
- Статус: done
- Priority: P0
- What changed: создан отдельный рабочий roadmap документ на основе разделов 16 и 21 аудита.
- Why changed: нужен управляемый чеклист исполнения миграции и единый рабочий журнал.
- Scope (files/modules): `docs/architecture/revelation_refactor_work_roadmap_ru.md`.
- Validation:
  - Analyze: n/a
  - Unit tests: n/a
  - Widget tests: n/a
  - Integration smoke: n/a
  - Grep boundary checks: n/a
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (запланировано на закрытие миграции)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: нет
  - Mitigations: n/a
  - Next task: старт миграции в отдельном чате (по решению владельца проекта).

#### [2026-03-08 15:49] Phase 0 / Task P0-P0.10 / Baseline docs + PR gates + harness + grep checks
- Статус: done
- Priority: P0/P1
- What changed:
  - Созданы baseline docs: `overview` и `testing strategy` в RU/EN.
  - Добавлен PR workflow `.github/workflows/pr_quality.yml` с `format + analyze + test`.
  - Добавлен test harness skeleton: fake logger/env/remote + базовый тест на harness.
  - Добавлен `scripts/check_forbidden_patterns.dart` с baseline-allowlist для legacy в UI/router.
- Why changed:
  - Phase 0 требует зафиксировать стартовый baseline, сделать quality gates воспроизводимыми и начать enforce архитектурных ограничений.
- Scope (files/modules):
  - `docs/architecture/overview.ru.md`
  - `docs/architecture/overview.en.md`
  - `docs/testing/strategy.ru.md`
  - `docs/testing/strategy.en.md`
  - `.github/workflows/pr_quality.yml`
  - `scripts/check_forbidden_patterns.dart`
  - `test/test_harness/*`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/overview.ru.md`, `docs/testing/strategy.ru.md`, `docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: yes (`docs/architecture/overview.en.md`, `docs/testing/strategy.en.md`)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: baseline allowlist фиксирует существующий legacy (`DBManager()` в части UI, map-based route contracts в `app_router`).
  - Mitigations: allowlist должен уменьшаться в следующих фазах; новые нарушения блокируются сразу.
  - Next task: Phase 1 / P0 — убрать дублирование `MainViewModel` provider registration.

#### [2026-03-08 15:52] Phase 1 / Task P0 / Remove duplicated MainViewModel provider registration
- Статус: done
- Priority: P0
- What changed:
  - Удален локальный `ChangeNotifierProvider<MainViewModel>` из `MainScreen`.
  - `MainScreen` теперь использует уже зарегистрированный глобальный `MainViewModel` из `main.dart`.
- Why changed:
  - Убрать дублированную регистрацию и избежать двух разных экземпляров одного view model в одном потоке UI.
- Scope (files/modules):
  - `lib/screens/main/main_screen.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: возможна смена жизненного цикла `MainViewModel` (теперь строго app-scoped).
  - Mitigations: следующий шаг Phase 1 проверяет bootstrap/DI и lifecycle cleanup централизованно.
  - Next task: Phase 1 / P0 — выделить bootstrap/DI из `main.dart` в `app/bootstrap` и `app/di`.

#### [2026-03-08 19:18] Phase 1 / Task P0 (P1.1 + P1.2) / Bootstrap and DI extracted from main.dart
- Статус: done
- Priority: P0
- What changed:
  - Добавлен `AppBootstrap` с startup sequence: error hooks, platform/window init, settings load, server/db init, strong handlers.
  - Добавлен `AppDi` с регистрацией core зависимостей (`Talker`, `BaseCacheManager`) и app-level provider wiring.
  - `main.dart` приведен к роли composition root: `runZonedGuarded` + bootstrap + `runApp`.
- Why changed:
  - Снизить связность `main.dart` и подготовить кодовую базу к дальнейшей миграции по слоям `app/bootstrap` и `app/di`.
- Scope (files/modules):
  - `lib/app/bootstrap/app_bootstrap.dart`
  - `lib/app/di/app_di.dart`
  - `lib/main.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `AppBootstrap` пока использует текущие singleton manager’ы (`DBManager`, `ServerManager`), их декомпозиция запланирована на Phase 3.
  - Mitigations: сохранить API менеджеров неизменным до фазы state/data refactors; покрывать шаги analyze/test.
  - Next task: Phase 1 / P0 — ввести typed route args wrappers с backward-compatible адаптацией.

#### [2026-03-08 19:22] Phase 1 / Task P0 / Typed route args wrappers with backward compatibility
- Статус: done
- Priority: P0
- What changed:
  - Добавлены typed route wrappers: `TopicRouteArgs`, `PrimarySourceRouteArgs`.
  - `app_router.dart` переведен на typed parsing с fallback к legacy форматам (`PrimarySource`, `Map<String, dynamic>`, query params).
  - Обновлены места навигации на typed `extra` (`TopicCard`, `SourceItemWidget`, word-link navigation, cross-source navigation).
  - Добавлены unit tests на parser/adapters route args.
- Why changed:
  - Уменьшить риск невалидных map-контрактов в router и подготовить переход к полностью типизированной навигации.
- Scope (files/modules):
  - `lib/app/router/route_args.dart`
  - `lib/app_router.dart`
  - `lib/screens/main/topic_card.dart`
  - `lib/screens/primary_sources/source_item.dart`
  - `lib/screens/primary_source/primary_source_screen.dart`
  - `lib/utils/app_link_handler.dart`
  - `test/app/router/route_args_test.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: в router сохранен legacy fallback для совместимости; полное удаление map-путей отложено до последующих фаз.
  - Mitigations: новые переходы использовать только typed args; legacy fallback удалять по мере миграции фич.
  - Next task: Phase 1 / P0 — добавить `dispose`/lifecycle cleanup в длинные state holders.

#### [2026-03-08 19:25] Phase 1 / Task P0 / Dispose and lifecycle cleanup for long-lived state holder
- Статус: done
- Priority: P0
- What changed:
  - В `PrimarySourceViewModel` добавлен явный lifecycle cleanup: отмена debounce timers, снятие listener’а, dispose внутренних notifier/controller.
  - Добавлена защита от уведомлений после dispose (`_isDisposed` guard + safe `notifyListeners`).
  - В `ImagePreviewController` добавлен `dispose` для `TransformationController`.
- Why changed:
  - Исключить утечки и гонки уведомлений после уничтожения экрана/VM в сложном primary source flow.
- Scope (files/modules):
  - `lib/viewmodels/primary_source_view_model.dart`
  - `lib/controllers/image_preview_controller.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: защитный override `notifyListeners` скрывает late-уведомления после dispose, поэтому важно держать async-потоки под контролем в будущей декомпозиции.
  - Mitigations: при разбиении `PrimarySourceViewModel` (Phase 3) вынести async orchestration в отдельные сервисы с cancel tokens.
  - Next task: Phase 1 / P1 — разбить `utils/common.dart` на логические модули и/или закрыть задачу по неиспользуемым DI регистрациям.

#### [2026-03-08 19:29] Phase 1 / Task P1 / Remove unused DI registration and dependency (cache manager)
- Статус: done
- Priority: P1
- What changed:
  - Удалена неиспользуемая DI регистрация `BaseCacheManager` из `AppDi`.
  - Удалена зависимость `flutter_cache_manager` из `pubspec.yaml`.
  - Обновлен `pubspec.lock`.
- Why changed:
  - Закрыть архитектурный долг по неиспользуемым DI/dependencies и убрать шум из composition слоя.
- Scope (files/modules):
  - `lib/app/di/app_di.dart`
  - `pubspec.yaml`
  - `pubspec.lock`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `flutter pub get` временно падал из-за locked `.plugin_symlinks` на Windows.
  - Mitigations: удален `windows/flutter/ephemeral/.plugin_symlinks`, после чего `flutter pub get` завершился успешно.
  - Next task: Phase 1 / P1 — разбить `utils/common.dart` на логические модули.

#### [2026-03-08 19:34] Phase 1 / Task P1 / Split utils/common.dart into logical modules
- Статус: done
- Priority: P1
- What changed:
  - `utils/common.dart` преобразован в barrel-экспорт.
  - Вынесены модули `links/dialogs/platform/markdown/file-sync` и сопутствующие утилиты в `lib/utils/common/*`.
  - Сохранена обратная совместимость импортов через `import 'package:revelation/utils/common.dart';`.
- Why changed:
  - Снизить связность "utility sink" и подготовить кодовую базу к feature-first границам без массового импорт-чёрна.
- Scope (files/modules):
  - `lib/utils/common.dart`
  - `lib/utils/common/common_logger.dart`
  - `lib/utils/common/platform_utils.dart`
  - `lib/utils/common/links_utils.dart`
  - `lib/utils/common/dialogs_utils.dart`
  - `lib/utils/common/markdown_utils.dart`
  - `lib/utils/common/file_sync_utils.dart`
  - `lib/utils/common/localization_utils.dart`
  - `lib/utils/common/styled_text_utils.dart`
  - `lib/utils/common/xml_parsers.dart`
  - `lib/utils/common/diagnostics_utils.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: пока сохранен compatibility barrel, часть границ остается "мягкой" до Phase 2/3.
  - Mitigations: новые утилиты добавлять в модульные файлы, а не обратно в barrel.
  - Next task: Phase 2 / P0 — создать target folders `app/core/infra/shared/features`.

#### [2026-03-08 19:56] Phase 2 / Task P0 / Create target folders app/core/infra/shared/features
- Статус: done
- Priority: P0
- What changed:
  - Создана целевая структура верхнего уровня: `lib/core`, `lib/infra`, `lib/shared`, `lib/features`.
  - Добавлены feature-папки для pilot migration: `lib/features/settings/*`, `lib/features/about/*`.
- Why changed:
  - Зафиксировать базовые structural boundaries перед переносом pilot фич.
- Scope (files/modules):
  - `lib/core/.gitkeep`
  - `lib/infra/.gitkeep`
  - `lib/shared/.gitkeep`
  - `lib/features/*`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: новые папки пока не защищены import boundary rules (планируется отдельным шагом Phase 2 / P1).
  - Mitigations: для мигрируемых фич добавлены compatibility adapters на старых путях.
  - Next task: Phase 2 / P0 — pilot migration `settings` и `about`.

#### [2026-03-08 19:56] Phase 2 / Task P0 (P2.1 + P2.2) / Pilot migration for settings and about
- Статус: done
- Priority: P0
- What changed:
  - Перенесены `settings` и `about` в `lib/features/*` (presentation + data для settings).
  - Обновлены composition imports на новые feature-пути (`main`, `bootstrap`, `di`, `router`, связанные экраны/контроллеры).
  - Добавлены compatibility wrappers на legacy-путях (`lib/screens/about/*`, `lib/screens/settings/settings_screen.dart`, `lib/viewmodels/{settings,about}_view_model.dart`, `lib/repositories/settings_repository.dart`) через `export` из новых модулей.
- Why changed:
  - Выполнить безопасную pilot-миграцию feature-first без массового import-breakage.
- Scope (files/modules):
  - `lib/features/settings/data/repositories/settings_repository.dart`
  - `lib/features/settings/presentation/viewmodels/settings_view_model.dart`
  - `lib/features/settings/presentation/screens/settings_screen.dart`
  - `lib/features/about/presentation/viewmodels/about_view_model.dart`
  - `lib/features/about/presentation/screens/*.dart`
  - `lib/main.dart`
  - `lib/app/bootstrap/app_bootstrap.dart`
  - `lib/app/di/app_di.dart`
  - `lib/app_router.dart`
  - `lib/controllers/audio_controller.dart`
  - `lib/screens/main/main_screen.dart`
  - `lib/screens/main/topic_list.dart`
  - `lib/screens/topic/topic_screen.dart`
  - `lib/screens/about/*.dart` (compat wrappers)
  - `lib/screens/settings/settings_screen.dart` (compat wrapper)
  - `lib/viewmodels/settings_view_model.dart` (compat wrapper)
  - `lib/viewmodels/about_view_model.dart` (compat wrapper)
  - `lib/repositories/settings_repository.dart` (compat wrapper)
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: временные wrappers сохраняют старые import-пути и могут затянуть полный переход.
  - Mitigations: на следующем шаге Phase 2 добавить boundary import checks и постепенно сужать legacy imports.
  - Next task: Phase 2 / P1 — ввести boundary import rules (lint/grep).

#### [2026-03-08 20:04] Phase 2 / Task P1 / Introduce boundary import rules for feature layers
- Статус: done
- Priority: P1
- What changed:
  - Расширен `scripts/check_forbidden_patterns.dart`: добавлен path-scoped фильтр (`filePathPattern`) для проверок в конкретных частях `lib/features/*`.
  - Добавлено правило: `lib/features/*/presentation/*` не должен импортировать legacy layer-first модули (`screens`, `viewmodels`, `repositories`, `managers`).
  - Добавлено правило: `lib/features/*/data/*` не должен импортировать `lib/features/*/presentation/*`.
- Why changed:
  - Зафиксировать минимально enforceable boundary rules на этапе Phase 2, чтобы новая feature-first структура не деградировала обратно в legacy import-пути.
- Scope (files/modules):
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: regex-based проверки могут потребовать уточнения по мере расширения `features/*`.
  - Mitigations: держать правила узкими по path scope и корректировать вместе с миграцией `topics`.
  - Next task: Phase 2 / P1 — мигрировать `topics` presentation/data поэтапно.

#### [2026-03-08 20:14] Phase 2 / Task P1 / Migrate topics presentation and data to feature module
- Статус: done
- Priority: P1
- What changed:
  - Перенесены `main/topic` presentation-модули в `lib/features/topics/presentation/*`:
    - `screens`: `main_screen.dart`, `topic_screen.dart`
    - `widgets`: `topic_list.dart`, `topic_card.dart`, `drawer_content.dart`, `drawer_item.dart`
    - `viewmodels`: `main_view_model.dart`
  - Перенесен `TopicInfo` в `lib/features/topics/data/models/topic_info.dart`.
  - Добавлен `lib/features/topics/data/repositories/topics_repository.dart` как data-adapter над `DBManager` для:
    - списка тем,
    - markdown/метаданных темы,
    - загрузки `CommonResource`.
  - `TopicList/TopicCard/TopicScreen` переключены на `TopicsRepository` (без прямого доступа к `DBManager` в feature presentation).
  - В `scripts/check_forbidden_patterns.dart` удален legacy allowlist для `DBManager()` в `lib/screens/*`, так как прежние исключения больше не нужны после migration.
  - Добавлены compatibility wrappers на legacy путях:
    - `lib/screens/main/*`
    - `lib/screens/topic/topic_screen.dart`
    - `lib/viewmodels/main_view_model.dart`
    - `lib/models/topic_info.dart`
  - Обновлены composition imports на новые feature-пути:
    - `lib/app_router.dart`
    - `lib/app/di/app_di.dart`
- Why changed:
  - Выполнить следующий шаг Phase 2 / P1 и закрепить topics в hybrid feature-first структуре без ломки существующих импортов.
- Scope (files/modules):
  - `lib/features/topics/*`
  - `lib/screens/main/*` (compat wrappers)
  - `lib/screens/topic/topic_screen.dart` (compat wrapper)
  - `lib/viewmodels/main_view_model.dart` (compat wrapper)
  - `lib/models/topic_info.dart` (compat wrapper)
  - `lib/app_router.dart`
  - `lib/app/di/app_di.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: временные compatibility wrappers могут задержать финальный переход на feature imports.
  - Mitigations: на следующем шаге Phase 2 / P2 сузить и документировать lifecycle временных wrappers.
  - Next task: Phase 2 / P2 — добавить/нормализовать временные barrel exports для мягкого перехода import-путей.

#### [2026-03-08 20:23] Phase 2 / Task P2 / Normalize temporary barrel exports for transition imports
- Статус: done
- Priority: P2
- What changed:
  - Добавлены публичные barrel-exports для migrated features:
    - `lib/features/about/about.dart`
    - `lib/features/settings/settings.dart`
    - `lib/features/topics/topics.dart`
  - Legacy wrappers переведены на `show`-экспорт из feature barrels вместо deep-path exports:
    - `lib/screens/about/*`, `lib/screens/settings/settings_screen.dart`, `lib/screens/main/*`, `lib/screens/topic/topic_screen.dart`
    - `lib/viewmodels/{about,settings,main}_view_model.dart`
    - `lib/repositories/settings_repository.dart`
    - `lib/models/topic_info.dart`
  - Обновлены composition imports на публичные feature API в:
    - `lib/main.dart`
    - `lib/app/bootstrap/app_bootstrap.dart`
    - `lib/app/di/app_di.dart`
    - `lib/app_router.dart`
    - `lib/controllers/audio_controller.dart`
- Why changed:
  - Закрыть шаг Phase 2 / P2 и зафиксировать единый transition layer для мягкой миграции import-путей с минимальным churn.
- Scope (files/modules):
  - `lib/features/about/about.dart`
  - `lib/features/settings/settings.dart`
  - `lib/features/topics/topics.dart`
  - `lib/screens/about/*`
  - `lib/screens/settings/settings_screen.dart`
  - `lib/screens/main/*`
  - `lib/screens/topic/topic_screen.dart`
  - `lib/viewmodels/{about,settings,main}_view_model.dart`
  - `lib/repositories/settings_repository.dart`
  - `lib/models/topic_info.dart`
  - `lib/main.dart`
  - `lib/app/bootstrap/app_bootstrap.dart`
  - `lib/app/di/app_di.dart`
  - `lib/app_router.dart`
  - `lib/controllers/audio_controller.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: расширение public surface через barrels может скрывать избыточные зависимости.
  - Mitigations: на Phase 3/5 сократить public exports до минимального API после стабилизации миграции.
  - Next task: Phase 3 / P0 — декомпозировать `DBManager` на data sources/repositories/cache policy.

#### [2026-03-08 20:28] Phase 3 / Task P0 (partial) / Start DBManager decomposition for topics slice
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен infra data source для topics-среза: `lib/infra/db/data_sources/topics_data_source.dart` (`TopicsDataSource` + `DbManagerTopicsDataSource`).
  - `lib/features/topics/data/repositories/topics_repository.dart` переведен с прямого `DBManager` на `TopicsDataSource` (инверсия зависимости через `infra`).
  - В `scripts/check_forbidden_patterns.dart` добавлен guardrail: `Feature modules should not call DBManager() directly`.
- Why changed:
  - Начать Phase 3 без big-bang: вынести доступ к DB для topics из feature data в infra-слой и зафиксировать правило против возврата к singleton-вызовам в features.
- Scope (files/modules):
  - `lib/infra/db/data_sources/topics_data_source.dart`
  - `lib/features/topics/data/repositories/topics_repository.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `DBManager` остается источником данных для `primary_sources` и части сервисов, поэтому декомпозиция пока неполная.
  - Mitigations: следующим шагом вынести `primary_sources` read paths в отдельные infra data sources и сократить surface `DBManager`.
  - Next task: Phase 3 / P0 — продолжить декомпозицию `DBManager` (primary sources slice).

#### [2026-03-08 20:34] Phase 3 / Task P0 (partial) / Continue DBManager decomposition for primary sources slice
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен infra data source для `primary_sources`: `lib/infra/db/data_sources/primary_sources_data_source.dart` (`PrimarySourcesDataSource` + `DbManagerPrimarySourcesDataSource`).
  - `lib/repositories/primary_sources_db_repository.dart` переведен с прямой зависимости от `DBManager` на `PrimarySourcesDataSource`.
  - В `scripts/check_forbidden_patterns.dart` добавлен целевой guardrail: `Primary sources repository should not call DBManager() directly`.
- Why changed:
  - Продолжить декомпозицию `DBManager` по вертикальным срезам и вынести доступ к cached DB rows из repository в infra-слой без изменения внешнего поведения `PrimarySourcesDbRepository`.
- Scope (files/modules):
  - `lib/infra/db/data_sources/primary_sources_data_source.dart`
  - `lib/repositories/primary_sources_db_repository.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `DescriptionContentService` и bootstrap все еще завязаны на `DBManager`, поэтому полная декомпозиция P0 пока не завершена.
  - Mitigations: следующим шагом выделить отдельный data source для strong/greek data и поэтапно сократить прямой доступ сервисов к `DBManager`.
  - Next task: Phase 3 / P0 — продолжить декомпозицию `DBManager` (description/strong slice).

#### [2026-03-08 20:38] Phase 3 / Task P0 (partial) / Continue DBManager decomposition for description/strong slice
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен infra data source для strong/greek данных: `lib/infra/db/data_sources/description_data_source.dart` (`DescriptionDataSource` + `DbManagerDescriptionDataSource`).
  - `lib/services/description_content_service.dart` переведен с прямой зависимости `DBManager` на `DescriptionDataSource`.
  - В `scripts/check_forbidden_patterns.dart` добавлен guardrail: `Services should not call DBManager() directly`.
- Why changed:
  - Продолжить декомпозицию `DBManager` по вертикальным срезам и убрать прямой singleton-доступ к БД из service-слоя.
- Scope (files/modules):
  - `lib/infra/db/data_sources/description_data_source.dart`
  - `lib/services/description_content_service.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `DBManager` все еще используется в bootstrap и как адаптер за infra data sources, поэтому декомпозиция P0 пока неполная.
  - Mitigations: следующим шагом выделить bootstrap-facing database facade (или infra coordinator) и сократить роль `DBManager` до thin compatibility adapter.
  - Next task: Phase 3 / P0 — продолжить декомпозицию `DBManager` (bootstrap/init slice).

#### [2026-03-08 22:02] Phase 3 / Task P0 (partial) / Continue DBManager decomposition for bootstrap/init slice
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен bootstrap-facing runtime adapter: `lib/infra/db/runtime/database_runtime.dart` (`DatabaseRuntime` + `DbManagerDatabaseRuntime`).
  - `lib/app/bootstrap/app_bootstrap.dart` переведен с прямого `DBManager()` на `DatabaseRuntime` abstraction.
  - В `scripts/check_forbidden_patterns.dart` добавлен guardrail: `App bootstrap should not call DBManager() directly`.
- Why changed:
  - Снять прямую singleton-зависимость из app bootstrap и продолжить перенос доступа к БД в infra-слой.
- Scope (files/modules):
  - `lib/infra/db/runtime/database_runtime.dart`
  - `lib/app/bootstrap/app_bootstrap.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `DBManager` остается внутренним адаптером для нескольких infra data sources, поэтому P0-деcomposition формально еще не завершен.
  - Mitigations: следующим шагом определить target facade/contract для чтения cached DB rows и подготовить поэтапное сужение публичной поверхности `DBManager`.
  - Next task: Phase 3 / P0 — завершить декомпозицию `DBManager` (final facade/policy slice).

#### [2026-03-08 22:06] Phase 3 / Task P0 / Finalize DBManager decomposition via infra gateway contract
- Статус: done
- Priority: P0
- What changed:
  - Добавлен единый infra gateway contract: `lib/infra/db/runtime/db_manager_gateway.dart` (`DatabaseGateway` + `DbManagerDatabaseGateway`).
  - `topics/primary_sources/description` data sources и bootstrap runtime (`database_runtime.dart`) переведены с прямого `DBManager` на `DatabaseGateway`.
  - В `scripts/check_forbidden_patterns.dart` добавлен guardrail: `Infra layers should instantiate DBManager() only via gateway`.
- Why changed:
  - Закрыть `Phase 3 / P0` задачу декомпозиции `DBManager` на уровне контракта: оставить `DBManager` только как thin compatibility adapter за infra gateway, а использование в слоях приложения и feature/data ограничить abstraction-слоями.
- Scope (files/modules):
  - `lib/infra/db/runtime/db_manager_gateway.dart`
  - `lib/infra/db/runtime/database_runtime.dart`
  - `lib/infra/db/data_sources/topics_data_source.dart`
  - `lib/infra/db/data_sources/primary_sources_data_source.dart`
  - `lib/infra/db/data_sources/description_data_source.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: `DBManager` пока остается legacy internal store/cache hub, поэтому финальная внутренняя декомпозиция может потребоваться в следующих фазах.
  - Mitigations: в следующих шагах рефакторить orchestration (`PrimarySourceViewModel`) и сужать surface gateway по мере стабилизации.
  - Next task: Phase 3 / P0 — разделить `PrimarySourceViewModel` на orchestrators (P3.1/P3.2/P3.3).

#### [2026-03-08 22:16] Phase 3 / Task P0 (partial, P3.1 done) / Extract image loading orchestration from PrimarySourceViewModel
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен orchestrator: `lib/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart`.
  - Вынесены из `PrimarySourceViewModel` image-loading responsibilities:
    - загрузка image bytes (web/local),
    - проверка локального наличия страниц,
    - refresh fallback поведение.
  - `lib/viewmodels/primary_source_view_model.dart` переключен на orchestrator (`PrimarySourceImageLoadingOrchestrator`) вместо локальных методов `_downloadImage/_saveImage/_getLocalFilePath`.
  - Для соблюдения boundary rule добавлен infra download client:
    - `lib/infra/remote/image/image_download_client.dart`
    - orchestrator использует `ImageDownloadClient`, а не прямой `ServerManager()`.
- Why changed:
  - Закрыть подшаг `P3.1` и уменьшить размер/ответственность `PrimarySourceViewModel`, отделив image loading orchestration.
- Scope (files/modules):
  - `lib/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart`
  - `lib/infra/remote/image/image_download_client.dart`
  - `lib/viewmodels/primary_source_view_model.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: пока не вынесены page settings и description orchestration, `PrimarySourceViewModel` остается перегруженным.
  - Mitigations: следующими шагами вынести `P3.2` (page settings) и `P3.3` (description panel) в отдельные orchestrators.
  - Next task: Phase 3 / P0 — `P3.2` page settings orchestration.

#### [2026-03-08 22:20] Phase 3 / Task P0 (partial, P3.2 done) / Extract page settings orchestration from PrimarySourceViewModel
- Статус: partial
- Priority: P0
- What changed:
  - Добавлен orchestrator: `lib/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart`.
  - Вынесены из `PrimarySourceViewModel` page settings responsibilities:
    - чтение сохраненных page settings,
    - сериализация/сохранение page settings,
    - очистка page settings для выбранной страницы.
  - `lib/viewmodels/primary_source_view_model.dart` переключен на `PrimarySourcePageSettingsOrchestrator`.
- Why changed:
  - Закрыть подшаг `P3.2` и уменьшить объем state orchestration в `PrimarySourceViewModel` перед финальным подшагом `P3.3`.
- Scope (files/modules):
  - `lib/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart`
  - `lib/viewmodels/primary_source_view_model.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: описание/навигация description panel пока остаются в `PrimarySourceViewModel`, поэтому задача split на orchestrators еще не закрыта полностью.
  - Mitigations: следующий шаг — вынести `P3.3` description panel orchestration.
  - Next task: Phase 3 / P0 — `P3.3` description panel orchestration.

#### [2026-03-08 22:25] Phase 3 / Task P0 (P3.3 done) / Extract description panel orchestration from PrimarySourceViewModel
- Статус: done
- Priority: P0
- What changed:
  - Добавлен orchestrator: `lib/features/primary_sources/application/orchestrators/description_panel_orchestrator.dart`.
  - Вынесены из `PrimarySourceViewModel` description panel responsibilities:
    - хранение состояния панели (visibility/content/current selection),
    - обработка word/verse/strong info запросов,
    - навигация по выбранному description (word/strong/verse).
  - `lib/viewmodels/primary_source_view_model.dart` переключен на `PrimarySourceDescriptionPanelOrchestrator`; публичный API VM для `PrimarySourceScreen` сохранен.
- Why changed:
  - Закрыть подшаг `P3.3` и завершить `P0`-задачу разделения `PrimarySourceViewModel` на orchestrators (`P3.1/P3.2/P3.3`).
- Scope (files/modules):
  - `lib/features/primary_sources/application/orchestrators/description_panel_orchestrator.dart`
  - `lib/viewmodels/primary_source_view_model.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: orchestration вынесена, но в VM по-прежнему остается значимый UI-state (zoom/color/selection), возможна дальнейшая декомпозиция в следующих P1 шагах.
  - Mitigations: следующий P0 шаг Phase 3 — убрать untyped `Map extra` contracts для critical routes.
  - Next task: Phase 3 / P0 — убрать untyped `Map extra` contracts для critical routes.

#### [2026-03-08 22:30] Phase 3 / Task P0 / Remove untyped map-based contracts for critical routes
- Статус: done
- Priority: P0
- What changed:
  - Удален legacy map parsing из `TopicRouteArgs.tryParse` и `PrimarySourceRouteArgs.tryParse` в `lib/app/router/route_args.dart`.
  - Удалена map-based ветка из `_getRouteArgs` в `lib/app_router.dart`.
  - Усилен guardrail в `scripts/check_forbidden_patterns.dart`: для проверки `Critical routes should avoid map-based state.extra contracts` убрано исключение `lib/app_router.dart`.
  - Обновлены тесты `test/app/router/route_args_test.dart` под новый контракт (legacy map now rejected).
- Why changed:
  - Закрыть `Phase 3 / P0` задачу удаления untyped `Map extra` контрактов для критичных роутов и завершить переход к typed route args.
- Scope (files/modules):
  - `lib/app/router/route_args.dart`
  - `lib/app_router.dart`
  - `scripts/check_forbidden_patterns.dart`
  - `test/app/router/route_args_test.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: legacy deeplink/code paths, которые могли передавать map в `extra`, теперь будут отклоняться.
  - Mitigations: сохранить query fallback для `/topic`, а для `/primary_source` использовать только `PrimarySourceRouteArgs`/`PrimarySource`.
  - Next task: Phase 3 / P1 — ввести error/result model и user-facing fallback states.

#### [2026-03-08 22:40] Phase 3 / Task P1 / Introduce AppResult model and user-facing fallback states
- Статус: done
- Priority: P1
- What changed:
  - Введена общая error/result модель:
    - `lib/core/errors/app_failure.dart`
    - `lib/core/errors/app_result.dart`
  - `TopicsRepository` переведен с null/empty fallback на `AppResult<T>`:
    - `getTopics`
    - `getArticleMarkdown`
    - `getTopicByRoute`
    - `getCommonResource`
  - Добавлены user-facing fallback states в topics presentation:
    - `TopicList` показывает `ErrorMessage` при `AppFailureResult`.
    - `TopicScreen` показывает `ErrorMessage` при ошибке загрузки markdown.
    - `TopicCard` откатывается на default icon при ошибке загрузки ресурса.
  - `PrimarySourcesDbRepository` дополнен `loadGroupedSourcesResult()` на `AppResult`.
  - `PrimarySourcesViewModel` теперь хранит `lastFailure/hasError`.
  - `PrimarySourcesScreen` показывает явный fallback экран ошибки при пустых данных и ошибке загрузки.
  - Добавлен l10n ключ `error_loading_primary_sources` во все поддерживаемые локали (`en/es/uk/ru`) и обновлена генерация l10n.
- Why changed:
  - Закрыть `Phase 3 / P1` задачу стандартизации обработки ошибок через типизированный результат и дать пользователю предсказуемые fallback состояния вместо silent failures.
- Scope (files/modules):
  - `lib/core/errors/app_failure.dart`
  - `lib/core/errors/app_result.dart`
  - `lib/features/topics/data/repositories/topics_repository.dart`
  - `lib/features/topics/presentation/widgets/topic_list.dart`
  - `lib/features/topics/presentation/widgets/topic_card.dart`
  - `lib/features/topics/presentation/screens/topic_screen.dart`
  - `lib/repositories/primary_sources_db_repository.dart`
  - `lib/viewmodels/primary_sources_view_model.dart`
  - `lib/screens/primary_sources/primary_sources_screen.dart`
  - `lib/l10n/app_en.arb`
  - `lib/l10n/app_es.arb`
  - `lib/l10n/app_uk.arb`
  - `lib/l10n/app_ru.arb`
  - `lib/l10n/app_localizations*.dart` (generated)
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: часть legacy слоев все еще использует null/exception-based contracts, поэтому error/result модель пока внедрена не во всех feature потоках.
  - Mitigations: на следующем шаге P1 стандартизировать async patterns (request token/cancel/ignore stale result) и продолжить выравнивание контрактов.
  - Next task: Phase 3 / P1 — стандартизировать async patterns (request token/cancel/ignore stale result).

#### [2026-03-08 22:53] Phase 3 / Task P1 / Standardize async patterns with latest-request guard
- Статус: done
- Priority: P1
- What changed:
  - Добавлен общий async guard `LatestRequestGuard` (`lib/core/async/latest_request_guard.dart`) для паттерна request-token/latest-only.
  - `PrimarySourceViewModel` переведен на latest-request semantics для `loadImage` и `_checkLocalPages`:
    - устаревшие async ответы игнорируются;
    - состояние применяется только для активного request token;
    - на `dispose` активные токены инвалидируются.
  - `PrimarySourcesViewModel.loadPrimarySources()` переведен с `isLoading-return` на latest-request semantics:
    - конкурентные вызовы допускаются;
    - stale результат не перезаписывает состояние более нового запроса;
    - добавлена безопасная логика `dispose`/`notifyListeners`.
  - Добавлены unit tests:
    - `test/core/async/latest_request_guard_test.dart`
    - `test/viewmodels/primary_sources_view_model_test.dart`
- Why changed:
  - Закрыть `Phase 3 / P1` задачу стандартизации async поведения (request token/cancel/ignore stale result) и убрать race-риск перезаписи актуального UI-состояния устаревшими результатами.
- Scope (files/modules):
  - `lib/core/async/latest_request_guard.dart`
  - `lib/viewmodels/primary_source_view_model.dart`
  - `lib/viewmodels/primary_sources_view_model.dart`
  - `test/core/async/latest_request_guard_test.dart`
  - `test/viewmodels/primary_sources_view_model_test.dart`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: no (для этого шага не требуется)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: часть non-critical VM (например, `about/settings`) пока использует базовый async pattern без request-token.
  - Mitigations: при Phase 4 тестовом усилении добавить целевые unit tests на async/dispose сценарии и при необходимости расширить guard pattern.
  - Next task: Phase 4 / P0 — усиление CI test enforcement (unit+widget matrices).

#### [2026-03-08 22:59] Phase 4 / Task P0 (partial) / Enforce separate unit and widget PR gates
- Статус: partial
- Priority: P0
- What changed:
  - PR workflow `pr_quality.yml` разделен на отдельные шаги:
    - `flutter test --exclude-tags widget` (unit suite),
    - `flutter test --tags widget` (widget suite).
  - Добавлен первый tagged widget smoke test для critical flow:
    - `test/widget/primary_sources/primary_sources_screen_test.dart`
    - проверка user-facing error fallback состояния.
  - Добавлен `dart_test.yaml` с тегом `widget`.
  - Обновлены testing strategy docs (RU/EN) под новый CI-паттерн (`unit + widget` отдельно).
- Why changed:
  - Начать `Phase 4 / P0` с enforceable разделения unit/widget тестов в PR CI и зафиксировать минимальный widget baseline.
- Scope (files/modules):
  - `.github/workflows/pr_quality.yml`
  - `test/widget/primary_sources/primary_sources_screen_test.dart`
  - `dart_test.yaml`
  - `docs/testing/strategy.ru.md`
  - `docs/testing/strategy.en.md`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass (`flutter test --exclude-tags widget`)
  - Widget tests: pass (`flutter test --tags widget`)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/testing/strategy.ru.md`, `docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: yes (`docs/testing/strategy.en.md`)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: widget coverage пока минимальное (1 smoke test), что недостаточно для матрицы критичных модулей.
  - Mitigations: следующим шагом покрыть матрицей critical modules (`topics`, `settings`, `primary_sources`) и закрепить это в CI.
  - Next task: Phase 3.5 / P0 — структурный аудит и file placement governance (по запросу владельца проекта).

#### [2026-03-08 23:10] Phase 3.5 / Task P0 (partial) / Structure audit and mandatory file placement governance
- Статус: partial
- Priority: P0
- What changed:
  - Проведен полный аудит текущей структуры `lib/*` против `section 10` target-structure.
  - Добавлены отдельные docs по границам и размещению файлов:
    - `docs/architecture/module-boundaries.ru.md`
    - `docs/architecture/module-boundaries.en.md`
  - Зафиксировано обязательное правило размещения новых файлов:
    - новые файлы допускаются только в `app/core/infra/shared/features/l10n`,
    - новые файлы в legacy-папках запрещены (кроме явно задокументированных compatibility adapters).
  - Усилен автоматический контроль структуры:
    - `scripts/check_forbidden_patterns.dart` теперь проверяет появление новых `.dart` файлов в legacy-папках;
    - добавлен baseline allowlist: `scripts/legacy_structure_allowlist.txt`;
    - добавлена проверка approved top-level папок `lib/`.
- Why changed:
  - Вынести контроль структуры каталогов в отдельный архитектурный этап и сделать размещение файлов enforceable, а не только “рекомендованным”.
- Scope (files/modules):
  - `docs/architecture/module-boundaries.ru.md`
  - `docs/architecture/module-boundaries.en.md`
  - `scripts/check_forbidden_patterns.dart`
  - `scripts/legacy_structure_allowlist.txt`
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/module-boundaries.ru.md`, `docs/architecture/revelation_refactor_work_roadmap_ru.md`)
  - EN updated: yes (`docs/architecture/module-boundaries.en.md`)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: миграция legacy к canonical структуре остается объемной и требует поэтапного переноса модулей.
  - Mitigations: использовать allowlist как анти-регрессионный stop-gap и дальше переносить legacy срезами (`primary_sources`, затем `shared widgets`, затем `services/repositories`).
  - Next task: Phase 3.5 / P1 — выполнить первый structural migration slice и сократить legacy footprint.

#### [2026-03-08 23:18] Phase 3.5 / Task P0 (done) / Add zero-legacy migration plan for all legacy folders
- Статус: done
- Priority: P0
- What changed:
  - Выполнен полный inventory legacy-каталогов и зафиксирован в roadmap (`screens/viewmodels/repositories/services/common_widgets/controllers/models/db/managers/utils`).
  - В `Phase 3.5` добавлен детальный zero-legacy чеклист по каждому legacy-каталогу.
  - Добавлена отдельная секция `4.1 Zero-Legacy План Миграции Каталогов`:
    - таблица текущего inventory с количеством файлов,
    - волны миграции `Wave A..G`,
    - финальные criteria/definition of done без legacy-каталогов.
  - Обновлены правила module boundaries (RU/EN):
    - legacy-каталоги обозначены как временное состояние,
    - конечный статус зафиксирован как canonical `app/core/infra/shared/features/l10n`.
- Why changed:
  - По запросу владельца проекта приоритизирована полная ликвидация legacy-каталогов как отдельная архитектурная цель до продолжения дальнейших этапов.
- Scope (files/modules):
  - `docs/architecture/revelation_refactor_work_roadmap_ru.md`
  - `docs/architecture/module-boundaries.ru.md`
  - `docs/architecture/module-boundaries.en.md`
- Validation:
  - Analyze: pass
  - Unit tests: pass
  - Widget tests: pass (текущий `flutter test` suite)
  - Integration smoke: n/a
  - Grep boundary checks: pass
- Docs:
  - RU updated: yes (`docs/architecture/revelation_refactor_work_roadmap_ru.md`, `docs/architecture/module-boundaries.ru.md`)
  - EN updated: yes (`docs/architecture/module-boundaries.en.md`)
  - ADR updated: no
- Risks / follow-ups:
  - New risks: объем migration waves высокий, возможны большие PR и конфликты import-path.
  - Mitigations: выполнять волнами по вертикальным срезам (сначала `primary_sources`), фиксируя compile-ready состояние после каждой волны.
  - Next task: Phase 3.5 / P1 — Wave A (`primary_sources`) migration с удалением соответствующих legacy-путей.

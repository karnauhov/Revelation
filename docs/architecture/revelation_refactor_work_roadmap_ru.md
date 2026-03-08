# Revelation — Рабочий Roadmap Миграции Архитектуры (RU)

Источник: раздел `16. Phased migration roadmap` и `21. Progress journal template` из  
[revelation_architecture_refactor_roadmap_ru.md](C:/Users/karna/Projects/Revelation/docs/architecture/revelation_architecture_refactor_roadmap_ru.md)

Статус: `Phase 0 и Phase 1 завершены, Phase 2 не начата`  
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
- [ ] Цель фазы зафиксирована: перейти к hybrid feature-first структуре без массовой ломки.
- [ ] Обоснование фазы зафиксировано: текущая структура мешает масштабированию/онбордингу.
- [ ] Задача [P0]: создать target folders `app/core/infra/shared/features`.
- [ ] Задача [P0]: мигрировать `settings` и `about` как pilot features.
- [ ] Подшаг [P2.1]: миграция `settings`.
- [ ] Подшаг [P2.2]: миграция `about`.
- [ ] Задача [P1]: мигрировать `topics` presentation/data поэтапно.
- [ ] Задача [P1]: ввести boundary import rules (lint/grep).
- [ ] Задача [P2]: добавить временные barrel exports для мягкого перехода import-путей.
- [ ] Affected areas верифицированы: `lib/screens/*`, `lib/viewmodels/*`, `lib/repositories/*`, `lib/utils/*`, `lib/common_widgets/*`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 1 completed`).
- [ ] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены.
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

### Phase 3 — State/data/navigation refactors
- [ ] Цель фазы зафиксирована: устранить ключевой долг в state/data/router.
- [ ] Обоснование фазы зафиксировано: здесь максимальный architectural risk.
- [ ] Задача [P0]: декомпозировать `DBManager` на data sources/repositories/cache policy.
- [ ] Задача [P0]: перенести direct DB access из `TopicList/TopicCard/TopicScreen` в feature controllers/services.
- [ ] Задача [P0]: разделить `PrimarySourceViewModel` на orchestrators.
- [ ] Подшаг [P3.1]: image loading orchestration.
- [ ] Подшаг [P3.2]: page settings orchestration.
- [ ] Подшаг [P3.3]: description panel orchestration.
- [ ] Задача [P0]: убрать untyped `Map extra` contracts для critical routes.
- [ ] Задача [P1]: ввести error/result model и user-facing fallback states.
- [ ] Задача [P1]: стандартизировать async patterns (request token/cancel/ignore stale result).
- [ ] Affected areas верифицированы: `lib/managers/db_manager.dart`, `lib/repositories/primary_sources_db_repository.dart`, `lib/screens/topic/*`, `lib/screens/primary_source/*`, `lib/viewmodels/primary_source_view_model.dart`, `lib/app_router.dart`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 2 completed`).
- [ ] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены.
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

### Phase 4 — Testing hardening and CI enforcement
- [ ] Цель фазы зафиксирована: сделать качество воспроизводимым и enforceable.
- [ ] Обоснование фазы зафиксировано: без этого архитектура деградирует обратно.
- [ ] Задача [P0]: unit+widget tests обязательны в PR CI.
- [ ] Задача [P0]: тестовые матрицы по critical feature modules.
- [ ] Задача [P1]: selective integration smoke tests (nightly/manual/label-based).
- [ ] Задача [P1]: coverage trend tracking.
- [ ] Задача [P2]: golden tests для стабильных экранов.
- [ ] Affected areas верифицированы: `.github/workflows/*`, `test/*`, `integration_test/*`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 3 key refactors merged`).
- [ ] Relevant skills назначены.
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

# Revelation — Рабочий Roadmap Миграции Архитектуры (RU)

Источник: раздел `16. Phased migration roadmap` и `21. Progress journal template` из  
[revelation_architecture_refactor_roadmap_ru.md](C:/Users/karna/Projects/Revelation/docs/architecture/revelation_architecture_refactor_roadmap_ru.md)

Статус: `готов к старту, миграция не начата`  
Версия roadmap: `v1`  
Дата создания: `2026-03-08`

## 1. Глобальный чеклист по фазам (пустые чекбоксы)

### Phase 0 — Audit stabilization / safety net / baseline
- [ ] Цель фазы зафиксирована: безопасная точка старта и baseline.
- [ ] Обоснование фазы зафиксировано: без baseline нельзя управлять регрессиями.
- [ ] Задача [P0]: зафиксировать baseline docs (RU/EN).
- [ ] Подшаг [P0.1]: создать `overview.ru`.
- [ ] Подшаг [P0.2]: создать `overview.en` (можно отложить контент до финала, но файл/план должны быть).
- [ ] Подшаг [P0.3]: создать `testing.strategy.ru`.
- [ ] Подшаг [P0.4]: создать `testing.strategy.en` (как минимум каркас).
- [ ] Задача [P0]: добавить PR workflow c `format + analyze + test`.
- [ ] Подшаг [P0.5]: включить `dart format --output=none --set-exit-if-changed .`.
- [ ] Подшаг [P0.6]: включить `flutter analyze`.
- [ ] Подшаг [P0.7]: включить `flutter test`.
- [ ] Задача [P0]: создать test harness skeleton (fake logger, fake env, fake remote).
- [ ] Подшаг [P0.8]: подготовить test utilities/fakes.
- [ ] Задача [P1]: ввести initial grep checks для forbidden patterns.
- [ ] Подшаг [P0.9]: добавить быстрые проверки на `DBManager()/ServerManager()` в UI.
- [ ] Подшаг [P0.10]: добавить проверку на map-based route contracts в критичных местах.
- [ ] Affected areas верифицированы: `.github/workflows/*`, `test/*`, `docs/*`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`нет`).
- [ ] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены (RU + EN plan).
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

### Phase 1 — Quick wins / high-impact low-risk improvements
- [ ] Цель фазы зафиксирована: убрать high-impact structural anti-patterns без функциональной ломки.
- [ ] Обоснование фазы зафиксировано: быстрый и безопасный выигрыш перед большими миграциями.
- [ ] Задача [P0]: убрать дублирование `MainViewModel` provider registration.
- [ ] Задача [P0]: выделить bootstrap/DI из `main.dart` в `app/bootstrap` и `app/di`.
- [ ] Подшаг [P1.1]: вынести bootstrap sequence.
- [ ] Подшаг [P1.2]: вынести DI registration.
- [ ] Задача [P0]: ввести typed route args wrappers (с временной backward-compatible адаптацией).
- [ ] Задача [P0]: добавить `dispose`/lifecycle cleanup в длинные state holders.
- [ ] Задача [P1]: разбить `utils/common.dart` на логические модули (links/dialogs/platform/markdown/file-sync).
- [ ] Задача [P1]: убрать или обосновать неиспользуемые DI регистрации/dependencies.
- [ ] Affected areas верифицированы: `lib/main.dart`, `lib/app_router.dart`, `lib/utils/common.dart`, `lib/viewmodels/primary_source_view_model.dart`, `lib/screens/main/main_screen.dart`.
- [ ] Риски проверены и записаны.
- [ ] Dependencies/prerequisites подтверждены (`Phase 0 completed`).
- [ ] Relevant skills назначены.
- [ ] Test expectations выполнены.
- [ ] Docs update expectations выполнены.
- [ ] Quality gates пройдены.
- [ ] Criteria of done выполнен.

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


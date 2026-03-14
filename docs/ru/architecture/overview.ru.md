# Architecture Overview (RU)

Doc-Version: `0.3.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать архитектурный baseline проекта Revelation перед глубокой миграцией.

## 2. Current Architecture Baseline
- Composition root перегружен: `lib/main.dart` одновременно инициализирует логирование, платформу, DI, БД и UI.
- Критические singleton-узлы: `DBManager`, `ServerManager`, `AppRouter`.
- Навигационные контракты частично не типизированы (`Map<String, dynamic>` в `state.extra`).
- Структура каталогов уже выровнена в canonical layout (`app/core/infra/shared/features/l10n`), а runtime state-слой уже мигрирован на `BLoC/Cubit` (в рамках Phase 3.7, hardening-этап остается).

## 3. Main Strengths To Preserve
- Рабочий multi-platform стек Flutter + Drift + Supabase.
- Стабильный runtime logging через Talker и глобальные error hooks.
- Синхронные локализации `en`, `es`, `uk`, `ru`.
- Рабочий релизный pipeline для desktop/mobile/web артефактов.

## 4. Critical Architectural Debt
- Крупные файлы с высокой концентрацией ответственности.
- Прямой доступ UI-слоя к data/singleton зависимостям.
- Неполные quality gates в CI для change (до Phase 0).
- Минимальное тестовое покрытие.

## 5. Target Direction
- Эволюционная миграция без rewrite.
- Hybrid feature-first структура (`features/`, `shared/`, `core/`, `infra/`).
- Явные границы между presentation/application/data/infra.
- Runtime state management в режиме `BLoC/Cubit`-only (Phase 3.7 target достигнут) и последующий hardening через guardrails/regression suites.
- Детальный ownership state-контрактов зафиксирован в `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md` (EN twin: `.en.md`).
- Типизированные route args для критичных переходов.

## 6. Boundary Rules (Migration Baseline)
- Presentation не обращается напрямую к `DBManager()/ServerManager()`.
- Router-контракты постепенно уходят от untyped map-передачи.
- Новый или изменяемый stateful presentation код реализуется только через `BLoC/Cubit`.
- Все структурные изменения сопровождаются тестами и обновлением RU/EN docs.

## 7. Phase 0 Exit Criteria
- Созданы baseline docs RU/EN.
- Добавлен CI workflow с `format + analyze + test`.
- Добавлен skeleton test harness (fake logger/env/remote).
- Добавлены fast grep-проверки для запрещенных паттернов с baseline-allowlist.

## 8. Out Of Scope
- Big-bang rewrite без фазовой миграции.
- Сохранение mixed state frameworks после завершения Phase 3.7.
- Ослабление архитектурных quality gates ради ускорения миграции.

## 9. Residual Debt Backlog
- Актуальный список остаточного архитектурного долга зафиксирован в:
  - `docs/ru/architecture/residual_debt_backlog.ru.md`
  - `docs/en/architecture/residual_debt_backlog.en.md`
- Backlog поддерживается как живой артефакт governance и обновляется по итогам architecture review.


# Architecture Overview (RU)

Doc-Version: `0.2.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать архитектурный baseline проекта Revelation перед глубокой миграцией.

## 2. Current Architecture Baseline
- Composition root перегружен: `lib/main.dart` одновременно инициализирует логирование, платформу, DI, БД и UI.
- Критические singleton-узлы: `DBManager`, `ServerManager`, `AppRouter`.
- Навигационные контракты частично не типизированы (`Map<String, dynamic>` в `state.extra`).
- Структура каталогов уже выровнена в canonical layout (`app/core/infra/shared/features/l10n`), но state-слой еще требует полного перехода на `BLoC/Cubit`.

## 3. Main Strengths To Preserve
- Рабочий multi-platform стек Flutter + Drift + Supabase.
- Стабильный runtime logging через Talker и глобальные error hooks.
- Синхронные локализации `en`, `es`, `uk`, `ru`.
- Рабочий релизный pipeline для desktop/mobile/web артефактов.

## 4. Critical Architectural Debt
- Крупные файлы с высокой концентрацией ответственности.
- Прямой доступ UI-слоя к data/singleton зависимостям.
- Неполные quality gates в CI для PR (до Phase 0).
- Минимальное тестовое покрытие.

## 5. Target Direction
- Эволюционная миграция без rewrite.
- Hybrid feature-first структура (`features/`, `shared/`, `core/`, `infra/`).
- Явные границы между presentation/application/data/infra.
- Полный переход state management на `BLoC/Cubit` (Phase 3.7) с финальным `zero Provider/ChangeNotifier`.
- Типизированные route args для критичных переходов.

## 6. Boundary Rules (Migration Baseline)
- Presentation не обращается напрямую к `DBManager()/ServerManager()`.
- Router-контракты постепенно уходят от untyped map-передачи.
- Новый или изменяемый stateful presentation код реализуется только через `BLoC/Cubit`.
- Все структурные изменения сопровождаются тестами и обновлением RU/EN docs.

## 7. Phase 0 Exit Criteria
- Созданы baseline docs RU/EN.
- Добавлен PR workflow с `format + analyze + test`.
- Добавлен skeleton test harness (fake logger/env/remote).
- Добавлены fast grep-проверки для запрещенных паттернов с baseline-allowlist.

## 8. Out Of Scope
- Big-bang rewrite без фазовой миграции.
- Сохранение mixed state frameworks после завершения Phase 3.7.
- Ослабление архитектурных quality gates ради ускорения миграции.

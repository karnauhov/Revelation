# Architecture Overview (RU)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-08`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать архитектурный baseline проекта Revelation перед глубокой миграцией.

## 2. Current Architecture Baseline
- Composition root перегружен: `lib/main.dart` одновременно инициализирует логирование, платформу, DI, БД и UI.
- Критические singleton-узлы: `DBManager`, `ServerManager`, `AppRouter`.
- Навигационные контракты частично не типизированы (`Map<String, dynamic>` в `state.extra`).
- Структура кода в основном type-first (`screens/`, `viewmodels/`, `repositories/`), но с гибридными элементами.

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
- Типизированные route args для критичных переходов.

## 6. Boundary Rules (Migration Baseline)
- Presentation не обращается напрямую к `DBManager()/ServerManager()`.
- Router-контракты постепенно уходят от untyped map-передачи.
- Все структурные изменения сопровождаются тестами и обновлением RU/EN docs.

## 7. Phase 0 Exit Criteria
- Созданы baseline docs RU/EN.
- Добавлен PR workflow с `format + analyze + test`.
- Добавлен skeleton test harness (fake logger/env/remote).
- Добавлены fast grep-проверки для запрещенных паттернов с baseline-allowlist.

## 8. Out Of Scope
- Полный rewrite state management.
- Массовая миграция feature папок (Phase 2+).
- Декомпозиция `DBManager`/`PrimarySourceViewModel` (Phase 3).

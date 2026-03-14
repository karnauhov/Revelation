# Module Boundaries (RU)

Doc-Version: `0.2.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать обязательные границы модулей и правило размещения файлов для `lib/`.

## 2. Canonical Top-Level Structure
Целевая структура верхнего уровня:
- `lib/app` — composition root, bootstrap, DI, router.
- `lib/core` — общие platform/env/errors/async/logging контракты.
- `lib/infra` — реализации доступа к БД/remote/storage.
- `lib/shared` — переиспользуемый UI и утилиты без feature-бизнес логики.
- `lib/features` — feature-first модули (presentation/application/data).
- `lib/l10n` — локализации.

Запрещенные legacy-каталоги (не допускаются к повторному появлению):
- `lib/screens`, `lib/viewmodels`, `lib/repositories`, `lib/services`,
- `lib/common_widgets`, `lib/managers`, `lib/controllers`,
- `lib/models`, `lib/db`, `lib/utils`.

## 3. Mandatory File Placement Rule
Критичное правило:
- Новый файл должен создаваться в `app/core/infra/shared/features/l10n`.
- Создание нового файла в legacy-каталогах запрещено.
- Исключение допускается только как временный compatibility adapter и должно быть зафиксировано в migration log.

Это правило равноценно по важности корректности функционала слоя.

## 4. Placement Decision Tree
При добавлении файла:
1. Это бизнес-функция конкретной фичи?  
`-> lib/features/<feature>/(presentation|application|data)/...`
2. Это инфраструктурная реализация (db/remote/storage)?  
`-> lib/infra/...`
3. Это app composition/bootstrap/router/di?  
`-> lib/app/...`
4. Это переиспользуемый UI без feature-логики?  
`-> lib/shared/ui/...`
5. Это общая platform/env/errors/async/logging абстракция?  
`-> lib/core/...`

Если ни один пункт не подходит, сначала обновить architecture docs/roadmap, потом добавлять файл.

## 5. Boundary Rules
- `presentation` не импортирует `infra` напрямую.
- `presentation` общается через `application/controller/orchestrator`.
- `presentation` state management выполняется только через `BLoC/Cubit`.
- `provider`/`ChangeNotifier` запрещены для нового и модифицируемого runtime-кода.
- ownership state-контрактов определяется matrix: `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md`.
- `data` знает про raw db/json; UI не знает.
- `shared` не содержит feature-бизнес логики.
- `core` не зависит от feature-кода.

## 6. Zero-Legacy Target
- Legacy-каталоги являются только временным состоянием.
- Конечный статус архитектуры: в `lib` остаются только `app/core/infra/shared/features/l10n`.
- Любой новый код в legacy-пути считается архитектурным дефектом.

## 7. Enforcement
- `scripts/check_forbidden_patterns.dart` выполняет:
  - запрет ключевых anti-pattern imports/calls;
  - запрет существования legacy-каталогов в `lib/`;
  - запрет использования `provider`/`ChangeNotifier` после завершения Phase 3.7;
  - контроль набора top-level директорий `lib/`.


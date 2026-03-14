# Docs Sync Policy (RU)

Doc-Version: `0.2.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать обязательный набор RU/EN документов и правила их синхронизации.

## 2. Approved RU/EN Docs Set

| RU | EN | Scope |
|---|---|---|
| `docs/ru/architecture/overview.ru.md` | `docs/en/architecture/overview.en.md` | Архитектурный baseline |
| `docs/ru/architecture/module-boundaries.ru.md` | `docs/en/architecture/module-boundaries.en.md` | Границы модулей и placement rules |
| `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md` | `docs/en/architecture/state_migration_matrix_phase_3_7.en.md` | Контракты state migration |
| `docs/ru/testing/strategy.ru.md` | `docs/en/testing/strategy.en.md` | Тестовая стратегия и CI policy |
| `docs/ru/architecture/residual_debt_backlog.ru.md` | `docs/en/architecture/residual_debt_backlog.en.md` | Финальный residual architecture debt backlog |

## 3. Approved Single-Language Exceptions
- `docs/ru/architecture/revelation_refactor_work_roadmap_ru.md` — рабочий execution log.
- `docs/ru/architecture/revelation_architecture_refactor_roadmap_ru.md` — мастер-план миграции.

Эти файлы разрешены в RU-only формате до отдельного решения по их дублированию на EN.

## 4. Sync Rules (Mandatory)
- Любое семантическое изменение в RU-файле из approved set требует синхронного изменения EN-twin в том же change set.
- Любое семантическое изменение в EN-файле из approved set требует синхронного изменения RU-twin в том же change set.
- Для каждой RU/EN пары должны совпадать:
  - смысл секций;
  - обязательные заголовки документа (`Doc-Version`, `Last-Updated`, `Source-Commit`);
  - ссылки на связанные policy/roadmap документы.
- Если изменение касается только формулировок без изменения смысла, twin все равно обновляется.

## 5. Minimal Validation
- Проверить наличие обеих сторон каждой пары из раздела 2.
- Проверить, что в change set нет "односторонних" изменений только RU или только EN для approved pairs.
- Проверить, что `Doc-Version` и `Last-Updated` обновлены консистентно в затронутой паре.
- Запустить automated check:
  - `dart run scripts/check_docs_sync.dart`

## 6. Ownership
- Author change: обновляет обе стороны RU/EN.
- Reviewer: отклоняет изменение, если нарушены правила синхронизации из разделов 2-5.

## 7. Instruction Workflow
- Подробный порядок действий: `docs/ru/architecture/docs_sync_instruction_workflow.ru.md` и EN twin `.en.md`.


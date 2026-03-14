# Docs Sync Policy (EN)

Doc-Version: `0.2.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define the mandatory RU/EN documentation set and synchronization rules.

## 2. Approved RU/EN Docs Set

| RU | EN | Scope |
|---|---|---|
| `docs/ru/architecture/overview.ru.md` | `docs/en/architecture/overview.en.md` | Architecture baseline |
| `docs/ru/architecture/module-boundaries.ru.md` | `docs/en/architecture/module-boundaries.en.md` | Module boundaries and placement rules |
| `docs/ru/architecture/state_migration_matrix_phase_3_7.ru.md` | `docs/en/architecture/state_migration_matrix_phase_3_7.en.md` | State migration contracts |
| `docs/ru/testing/strategy.ru.md` | `docs/en/testing/strategy.en.md` | Testing strategy and CI policy |
| `docs/ru/architecture/residual_debt_backlog.ru.md` | `docs/en/architecture/residual_debt_backlog.en.md` | Final residual architecture debt backlog |

## 3. Approved Single-Language Exceptions
- `docs/ru/architecture/revelation_refactor_work_roadmap_ru.md` - working execution log.
- `docs/ru/architecture/revelation_architecture_refactor_roadmap_ru.md` - master migration plan.

These files are allowed to remain RU-only until a separate decision introduces EN twins.

## 4. Sync Rules (Mandatory)
- Any semantic change in an RU file from the approved set must include the EN twin update in the same change set.
- Any semantic change in an EN file from the approved set must include the RU twin update in the same change set.
- For each RU/EN pair, the following must stay aligned:
  - section intent;
  - required document headers (`Doc-Version`, `Last-Updated`, `Source-Commit`);
  - links to related policy/roadmap documents.
- Even wording-only updates must be mirrored in the twin document.

## 5. Minimal Validation
- Verify both sides exist for each pair listed in section 2.
- Verify the change does not contain one-sided updates (RU-only or EN-only) for approved pairs.
- Verify `Doc-Version` and `Last-Updated` are updated consistently in the affected pair.
- Run the automated check:
  - `dart run scripts/check_docs_sync.dart`

## 6. Ownership
- Change author: updates both RU and EN sides.
- Reviewer: rejects the change if sync rules from sections 2-5 are violated.

## 7. Instruction Workflow
- Detailed procedure: `docs/en/architecture/docs_sync_instruction_workflow.en.md` and RU twin `.ru.md`.


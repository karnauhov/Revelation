# Docs Sync Instruction Workflow (RU)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Определить пошаговый workflow синхронизации RU/EN документации для архитектурных и тестовых изменений.

## 2. When To Run
- Для любого изменения файлов из утвержденного RU/EN набора (`docs_sync_policy.ru/en.md`).
- Для изменений в архитектурных границах, state-контрактах, тестовой стратегии или governance-правилах.

## 3. Workflow Steps
1. Определить затронутые документы и их RU/EN пары.
2. Внести изменения в RU и EN twin в рамках одного change set.
3. Синхронизировать заголовки документа:
   - `Doc-Version`
   - `Last-Updated`
   - `Source-Commit`
4. Проверить ссылки на связанные policy/roadmap документы в обеих версиях.
5. Запустить автоматическую проверку docs sync:
   - `dart run scripts/check_docs_sync.dart`
6. Если изменение допустимо только как approved RU-only exception:
   - обновить RU-only файл;
   - зафиксировать обоснование в рабочем roadmap.

## 4. Expected Result
- Нет одностороннего RU/EN drift в approved pairs.
- Заголовки и смысловые секции остаются синхронизированными.

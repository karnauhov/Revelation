# Docs Sync Instruction Workflow (EN)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define a step-by-step RU/EN documentation sync workflow for architecture and testing changes.

## 2. When To Run
- For any change touching files from the approved RU/EN set (`docs_sync_policy.ru/en.md`).
- For changes in architecture boundaries, state contracts, testing strategy, or governance rules.

## 3. Workflow Steps
1. Identify affected documents and their RU/EN pairs.
2. Apply updates to both RU and EN twins in the same change set.
3. Keep document headers synchronized:
   - `Doc-Version`
   - `Last-Updated`
   - `Source-Commit`
4. Verify links to related policy/roadmap documents in both twins.
5. Run the automated docs sync check:
   - `dart run scripts/check_docs_sync.dart`
6. If the change is valid only for an approved RU-only exception:
   - update the RU-only file;
   - log the rationale in the working roadmap.

## 4. Expected Result
- No one-sided RU/EN drift in approved pairs.
- Header fields and semantic sections remain aligned.

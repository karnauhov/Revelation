# Module Boundaries (EN)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-08`  
Source-Commit: `working-tree`

## 1. Purpose
Define mandatory module boundaries and file placement rules for `lib/`.

## 2. Canonical Top-Level Structure
Target top-level layout:
- `lib/app` - composition root, bootstrap, DI, router.
- `lib/core` - shared platform/env/errors/async/logging contracts.
- `lib/infra` - database/remote/storage implementations.
- `lib/shared` - reusable UI and utilities without feature business logic.
- `lib/features` - feature-first modules (presentation/application/data).
- `lib/l10n` - localization assets/code.

Current legacy directories (must be fully removed in zero-legacy migration):
- `lib/screens`, `lib/viewmodels`, `lib/repositories`, `lib/services`,
- `lib/common_widgets`, `lib/managers`, `lib/controllers`,
- `lib/models`, `lib/db`, `lib/utils`.

## 3. Mandatory File Placement Rule
Critical rule:
- New files must be created under `app/core/infra/shared/features/l10n`.
- New files in legacy directories are forbidden.
- Exceptions are allowed only for temporary compatibility adapters and must be logged in the migration journal.

This rule is considered as important as correct layer behavior.

## 4. Placement Decision Tree
When adding a file:
1. Feature-specific business behavior?  
`-> lib/features/<feature>/(presentation|application|data)/...`
2. Infra implementation (db/remote/storage)?  
`-> lib/infra/...`
3. App composition/bootstrap/router/di?  
`-> lib/app/...`
4. Reusable UI without feature business logic?  
`-> lib/shared/ui/...`
5. Shared platform/env/errors/async/logging abstraction?  
`-> lib/core/...`

If none applies, update architecture docs/roadmap first, then add the file.

## 5. Boundary Rules
- `presentation` must not import `infra` directly.
- `presentation` communicates via `application/controller/orchestrator`.
- `data` owns raw db/json knowledge; UI does not.
- `shared` must not contain feature business logic.
- `core` must not depend on feature modules.

## 6. Zero-Legacy Target
- Legacy directories are a temporary transition state only.
- Final architecture state: `lib` contains only `app/core/infra/shared/features/l10n`.
- Any new code in legacy paths is treated as an architectural defect.

## 7. Enforcement
- `scripts/check_forbidden_patterns.dart` enforces:
  - critical anti-pattern imports/calls;
  - no new `.dart` files in legacy directories;
  - approved top-level `lib/` directory set.
- Legacy file baseline lives in:
  - `scripts/legacy_structure_allowlist.txt`.

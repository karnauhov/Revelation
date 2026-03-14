# Module Boundaries (EN)

Doc-Version: `1.1.4`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Define mandatory module boundaries and file placement rules for `lib/`.

## 2. Canonical Top-Level Structure
- `lib/app` - bootstrap, DI, router, composition root.
- `lib/core` - platform and cross-cutting contracts (`errors`, `async`, `logging`, `platform`, `audio`, `diagnostics`).
- `lib/infra` - database/remote/storage implementations.
- `lib/shared` - reusable UI and shared models/utils without feature business logic.
- `lib/features` - feature-first modules.
- `lib/l10n` - ARB assets and generated localization code.

## 3. Feature Module Layout
Recommended feature layout:
- `presentation` - screens, widgets, cubit/bloc, and UI coordination.
- `application` - orchestration/use-case/service logic (optional for simple features).
- `data` - repositories, data contracts, and mapping (optional when a feature has no data access).

A lightweight feature module without all three layers is allowed, but dependency boundaries remain mandatory for every layer that is present.

## 4. Dependency Rules
- `presentation` must not import `infra` directly.
- `presentation` works through feature repositories/services/cubit contracts.
- Cross-slice presentation orchestration is implemented as `Cubit`/`Bloc` classes (for example, `*OrchestrationCubit`), not as mutable controller singletons.
- UI expand/collapse state for primary source list cards is owned by screen-scoped `PrimarySourcesExpansionCubit`, not by mutable fields on `PrimarySource`.
- If one state slice already owns selection and display fields (for example, `PrimarySourceDescriptionState.currentType/currentNumber`), do not introduce a separate duplicate cubit for the same source of truth.
- Do not add duplicate visibility flags (`imageShown`, `showDescription`) to detail state when visibility is already derivable from existing data and active UI modes.
- `application` must not contain UI widgets.
- `data` may depend on `infra` data source/gateway contracts.
- `infra` must not import feature `presentation`.
- `shared` must not contain feature-specific orchestration logic.
- `core` must not depend on feature modules.

## 5. File Placement Rules
1. App bootstrap/router/DI -> `lib/app/...`
2. Platform and cross-cutting contracts -> `lib/core/...`
3. Infrastructure implementations -> `lib/infra/...`
4. Reusable UI and shared models -> `lib/shared/...`
5. Feature logic -> `lib/features/<feature>/...`

## 6. Forbidden Paths
These folders must not exist in `lib/`:
- `screens`, `viewmodels`, `repositories`, `services`
- `common_widgets`, `managers`, `controllers`
- `models`, `db`, `utils`

## 7. Enforcement
- Automated architecture checks: `dart run scripts/check_forbidden_patterns.dart`.
- `provider`/`ChangeNotifier` ban is enforced in CI and local checks.
- `flutter analyze` and `flutter test` are required before merge.

# Residual Architecture Debt Backlog (EN)

Doc-Version: `0.1.2`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Capture the remaining architecture debt after Phase 5 completion and define a prioritized, incremental closure plan without a full rewrite.

## 2. Review Snapshot (2026-03-14)
- `shared/utils/common.dart` remains a global barrel and is imported in `36` runtime/test files.
- Large `primary_sources` presentation nodes:
  - `primary_source_screen.dart` - `927` lines;
  - `image_preview.dart` - `1142` lines;
  - `primary_source_toolbar.dart` - `1079` lines;
  - `primary_source_view_model.dart` - `472` lines.
- `4` `deprecated_member_use` suppressions remain in platform/runtime code.
- `DBManager` is reduced to runtime/composition responsibility; feature-level DB caches are moved into domain-specific gateways (`articles`, `lexicon`, `primary_sources`).

## 3. Prioritized Backlog

| ID | Priority | Debt item | Evidence | Target action | Exit criteria |
|---|---|---|---|---|---|
| `RAD-01` | P1 | Decompose `primary_sources` detail UI monoliths | Large files: `primary_source_screen.dart`, `image_preview.dart`, `primary_source_toolbar.dart` | Split into smaller widgets/flows by responsibility (navigation shell, image canvas, description panel, toolbar actions) | No detail-scope presentation files above `700` lines and widget tests cover key subtrees |
| `RAD-02` | P1 | Remove orchestration concentration in `PrimarySourceViewModel` | `primary_source_view_model.dart` combines lifecycle, routing callbacks, and image/viewport orchestration | Move lifecycle and orchestration to dedicated coordinator/use-case layer and reduce VM surface | VM no longer owns cubit lifecycle flags or manual disposal chains |
| `RAD-03` | P1 | Remove global `shared/utils/common.dart` barrel | `36` imports across layers (`app/core/infra/features/shared`) | Replace barrel usage with explicit imports (`core/logging`, `shared/ui/dialogs`, `core/platform`, etc.), then delete barrel | `rg "shared/utils/common.dart" lib test` -> `0` matches |
| `RAD-06` | P2 | Remove `deprecated_member_use` suppressions outside generated scope | `deprecated_member_use` appears in `core/platform`, `core/diagnostics`, `shared/utils/links_utils.dart` | Migrate to non-deprecated APIs and remove suppressions | `rg "deprecated_member_use" lib` reports only allowed generated exceptions |
| `RAD-07` | P2 | Normalize terminology in master architecture docs | Defective tokens were recorded after mass terminology replacement | Clean master roadmap docs from artifacts and stabilize glossary usage | Search by known defective tokens in `docs/architecture` returns no matches |

## 4. Backlog Governance
- Revisit this backlog for each significant architecture change (or at least once per release cycle).
- New architecture debt entries must include:
  - measurable evidence;
  - a target owner scope;
  - explicit exit criteria.
- Closed entries must be recorded in the migration journal of the relevant phase.

## 5. Recently Closed
- `2026-03-14`: `RAD-05` closed - `integration_test/smoke` expanded to `5` scenarios (`about`, `download`, `settings -> about -> download`, `primary_sources` navigation, `settings -> topics` language sync), while keeping the manual-triggered policy (`workflow_dispatch`).
- `2026-03-14`: `RAD-04` closed - `DBManager` decomposition completed, runtime layer kept composition-only, and feature-level caches moved into domain-specific gateways.

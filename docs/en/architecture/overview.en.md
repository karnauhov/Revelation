# Architecture Overview (EN)

Doc-Version: `0.3.0`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Capture the architecture baseline of Revelation before deep refactoring begins.

## 2. Current Architecture Baseline
- The composition root is overloaded: `lib/main.dart` initializes logging, platform setup, DI, DB, and UI wiring.
- Critical singleton nodes: `DBManager`, `ServerManager`, `AppRouter`.
- Navigation contracts are partially untyped (`Map<String, dynamic>` in `state.extra`).
- Folder layout is already aligned to the canonical structure (`app/core/infra/shared/features/l10n`), and runtime state management has been migrated to `BLoC/Cubit` (Phase 3.7, migration hardening remains).

## 3. Main Strengths To Preserve
- Stable multi-platform Flutter stack with Drift and Supabase.
- Runtime observability via Talker and global error hooks.
- Synchronized localizations for `en`, `es`, `uk`, `ru`.
- Existing release pipeline for desktop/mobile/web artifacts.

## 4. Critical Architectural Debt
- Large files with concentrated responsibilities.
- Direct UI access to data/singleton dependencies.
- Missing enforceable CI gates (before Phase 0).
- Minimal automated test coverage.

## 5. Target Direction
- Evolutionary migration without rewrite.
- Hybrid feature-first structure (`features/`, `shared/`, `core/`, `infra/`).
- Explicit boundaries between presentation/application/data/infra.
- `BLoC/Cubit`-only runtime state layer (Phase 3.7 target achieved), plus follow-up hardening via guardrails and regression suites.
- The detailed state-ownership contracts are defined in `docs/en/architecture/state_migration_matrix_phase_3_7.en.md` (RU twin: `.ru.md`).
- Typed route args for critical navigation flows.

## 6. Boundary Rules (Migration Baseline)
- Presentation must not call `DBManager()/ServerManager()` directly.
- Router contracts should move away from untyped map payloads.
- New or modified stateful presentation code must be implemented with `BLoC/Cubit` only.
- Every structural change must include tests and RU/EN docs updates.

## 7. Phase 0 Exit Criteria
- Baseline docs are created in RU/EN.
- CI workflow includes `format + analyze + test`.
- Test harness skeleton exists (fake logger/env/remote).
- Fast grep checks exist for forbidden patterns with a baseline allowlist.

## 8. Out Of Scope
- Big-bang rewrite without phased migration.
- Keeping mixed state frameworks after Phase 3.7.
- Weakening architecture quality gates just to speed up migration.

## 9. Residual Debt Backlog
- The current residual architecture debt list is maintained in:
  - `docs/ru/architecture/residual_debt_backlog.ru.md`
  - `docs/en/architecture/residual_debt_backlog.en.md`
- The backlog is treated as a living governance artifact and updated after architecture reviews.


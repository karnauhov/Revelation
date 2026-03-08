# Architecture Overview (EN)

Doc-Version: `0.1.0`  
Last-Updated: `2026-03-08`  
Source-Commit: `working-tree`

## 1. Purpose
Capture the architecture baseline of Revelation before deep refactoring begins.

## 2. Current Architecture Baseline
- The composition root is overloaded: `lib/main.dart` initializes logging, platform setup, DI, DB, and UI wiring.
- Critical singleton nodes: `DBManager`, `ServerManager`, `AppRouter`.
- Navigation contracts are partially untyped (`Map<String, dynamic>` in `state.extra`).
- The codebase is mainly type-first (`screens/`, `viewmodels/`, `repositories/`) with hybrid elements.

## 3. Main Strengths To Preserve
- Stable multi-platform Flutter stack with Drift and Supabase.
- Runtime observability via Talker and global error hooks.
- Synchronized localizations for `en`, `es`, `uk`, `ru`.
- Existing release pipeline for desktop/mobile/web artifacts.

## 4. Critical Architectural Debt
- Large files with concentrated responsibilities.
- Direct UI access to data/singleton dependencies.
- Missing PR quality gates in CI (before Phase 0).
- Minimal automated test coverage.

## 5. Target Direction
- Evolutionary migration without rewrite.
- Hybrid feature-first structure (`features/`, `shared/`, `core/`, `infra/`).
- Explicit boundaries between presentation/application/data/infra.
- Typed route args for critical navigation flows.

## 6. Boundary Rules (Migration Baseline)
- Presentation must not call `DBManager()/ServerManager()` directly.
- Router contracts should move away from untyped map payloads.
- Every structural change must include tests and RU/EN docs updates.

## 7. Phase 0 Exit Criteria
- Baseline docs are created in RU/EN.
- PR workflow includes `format + analyze + test`.
- Test harness skeleton exists (fake logger/env/remote).
- Fast grep checks exist for forbidden patterns with a baseline allowlist.

## 8. Out Of Scope
- Full state management rewrite.
- Mass feature folder migration (Phase 2+).
- `DBManager`/`PrimarySourceViewModel` decomposition (Phase 3).

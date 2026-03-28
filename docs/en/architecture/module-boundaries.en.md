# Module Boundaries (EN)

Doc-Version: `2.1.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Purpose

Define where code belongs and how layers depend on each other.

## Top-Level Structure

- `lib/app` - bootstrap, startup shell, DI, router, top-level composition
- `lib/core` - cross-cutting primitives such as errors, async guards, logging, audio, platform utilities, diagnostics
- `lib/infra` - database, remote, and storage implementations
- `lib/shared` - reusable UI, shared models, localization helpers, and common utilities
- `lib/features` - feature-first modules
- `lib/l10n` - ARB files and generated localization code

## Feature Layout

When a feature needs internal layering, use this structure:

- `presentation` - `bloc/`, `screens/`, `widgets/`
- `application` - orchestration and use-case services
- `data` - repositories, data models, and mapping

A smaller feature may omit layers that it does not need, but the dependency direction stays the same.

## Dependency Rules

- `presentation` may depend on feature services, repositories, and DI factories, but not on low-level infra managers directly.
- `app/startup` may depend on app bootstrap/composition code and shared localization/theme primitives, but it must not move feature-specific state ownership into the root shell.
- `presentation/bloc` and `application` must not receive `BuildContext`.
- `application` contains no widgets.
- `data` may use infra gateways and storage implementations.
- `infra` does not import feature presentation code.
- `shared` stays reusable and does not own feature-specific orchestration.
- `core` stays feature-agnostic.

## State Rules

- Stateful presentation uses `Cubit`/`Bloc` only.
- A single UI data slice has a single source of truth.
- Do not introduce duplicate cubits or duplicate visibility flags when state can be derived from existing values.
- Async cubits must guard post-`await` state application with `isClosed` and stale-request protection where needed.

## Usual Validation

- `dart run scripts/check_forbidden_patterns.dart`
- `flutter analyze`
- `flutter test`

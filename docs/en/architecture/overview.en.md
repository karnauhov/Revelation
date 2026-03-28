# Architecture Overview (EN)

Doc-Version: `2.0.0`  
Last-Updated: `2026-03-28`  
Source-Commit: `working-tree`

## Purpose

Describe the current Revelation runtime architecture.

## Runtime Shape

- `lib/main.dart` creates `Talker`, registers core services in `AppDi`, installs `AppBlocObserver`, delegates startup to `AppBootstrap`, and launches `RevelationApp`.
- `AppBootstrap` initializes Flutter bindings, global error handling, platform setup, settings, Supabase, local databases, and the default handlers for `word:` and Strong links.
- `RevelationApp` builds `MaterialApp.router`, applies locale/theme/font settings from `SettingsCubit`, and exposes `en`, `es`, `uk`, and `ru`.
- `AppRouter` uses `go_router` and routes to the main, topic, primary source list, primary source detail, settings, about, and download screens.
- `AppDi.appBlocProviders` wires the global app state: `SettingsCubit`, `TopicsCatalogCubit`, and `PrimarySourcesCubit`.
- `PrimarySourceScreen` creates feature-scoped detail state with `session`, `image`, `page-settings`, `description`, `viewport`, and `orchestration` cubits. `PrimarySourceDetailCoordinator` is a screen helper, not the source of truth.

## Data and Services

- App settings are persisted with `shared_preferences`.
- Local content is read from Drift-backed SQLite databases.
- Remote downloads use Supabase Storage through `ServerManager`.
- `AboutCubit` reads database metadata from `db_metadata` and exposes app/build/database version information to the UI.
- `LatestRequestGuard` is used in async flows where stale responses must not overwrite newer state.

## Architectural Invariants

- The runtime structure of `lib/` is `app`, `core`, `infra`, `shared`, `features`, `l10n`.
- Stateful presentation logic uses `Cubit`/`Bloc`.
- Presentation does not talk directly to low-level DB or remote managers.
- Database schema changes must keep code-level schema versions and distributed SQLite files synchronized.

## Related Documents

- [Module Boundaries](./module-boundaries.en.md)
- [State Management Matrix](./state_management_matrix.en.md)
- [Testing Strategy](../testing/strategy.en.md)

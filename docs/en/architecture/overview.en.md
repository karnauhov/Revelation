# Architecture Overview (EN)

Doc-Version: `1.1.5`  
Last-Updated: `2026-03-21`  
Source-Commit: `working-tree`

## 1. Purpose
Define the current Revelation architecture as-is.

## 2. Runtime Architecture Snapshot
- Entry point: `lib/main.dart` configures `Talker`, registers core dependencies, sets `AppBlocObserver`, initializes `AppBootstrap`, and starts `MaterialApp.router`.
- Bootstrap: `AppBootstrap` performs `WidgetsFlutterBinding.ensureInitialized`, global error hooks, platform initialization, settings loading, Supabase initialization, and local database initialization.
- Navigation: `go_router` in `AppRouter`; critical routes use typed route args (`TopicRouteArgs`, `PrimarySourceRouteArgs`).
- `word:` link handling: `shared/navigation` uses callback contracts; the default handler is registered at bootstrap level (`AppBootstrap`).
- Global state scope: `AppDi.appBlocProviders` provides `SettingsCubit`, `TopicsCatalogCubit`, and `PrimarySourcesCubit`.
- Primary source list UI state: `PrimarySourcesScreen` owns expand/collapse state via screen-scoped `PrimarySourcesExpansionCubit`; `PrimarySource` model is kept free of mutable UI flags.
- Primary source detail state: `PrimarySourceScreen` creates a `MultiBlocProvider` with `session/image/page-settings/description/viewport` cubit slices; selection fields (`currentType/currentNumber`) belong to `PrimarySourceDescriptionState`.
- Primary source detail image/description state does not keep duplicate visibility flags (`imageShown`, `showDescription`): visibility is derived from actual data and active UI modes.
- Primary source detail orchestration: `PrimarySourceDetailOrchestrationCubit` coordinates `loadImage`, `changeSelectedPage`, and debounced save/restore across detail cubit slices.
- About screen DB metadata: `AboutCubit` loads `schema_version`, `data_version`, and `date` from `db_metadata` in the common/localized SQLite files and renders localized version/date information.
- Data flow: `presentation cubit -> feature repository -> data source -> infra gateway -> drift db`.
- Remote layer: `ServerManager` uses Supabase Storage for database and file downloads.
- Logging and diagnostics: `Talker`, `TalkerRouteObserver`, `AppBlocObserver`.
- Localization: supported locales are `en`, `es`, `uk`, `ru`.

## 3. Architectural Invariants
- `lib/` keeps only these top-level folders: `app`, `core`, `infra`, `shared`, `features`, `l10n`.
- Stateful presentation is implemented with `BLoC/Cubit` only.
- `provider`/`ChangeNotifier`/`notifyListeners` are forbidden in runtime/test code.
- Presentation does not call `DBManager()`/`ServerManager()` directly.
- DB schema version is stored inside SQLite `db_metadata.schema_version`; schema changes must keep Drift `schemaVersion`, SQLite `PRAGMA user_version`, and distributed DB files in sync.
- `core` and `shared` do not contain feature-specific orchestration or feature-module dependencies.
- RU and EN architecture docs are updated together.

## 4. Core Cross-Cutting Contracts
- Operation errors/results: `AppFailure` and `AppResult`.
- Stale async response protection: `LatestRequestGuard`.
- Platform-specific behavior is isolated in `core/platform`.

## 5. Related Docs
- Module boundaries: `docs/en/architecture/module-boundaries.en.md` and RU twin.
- State ownership contracts: `docs/en/architecture/state_management_matrix.en.md` and RU twin.
- Testing strategy: `docs/en/testing/strategy.en.md` and RU twin.
- RU/EN sync rules are defined in `AGENTS.md`.

# Phase P02 - Inventory & Traceability Map (RU)

Дата фиксации: **March 15, 2026**.

## 1) Source-of-truth и метод

Приоритет источников для P02:

1. Код и тесты в репозитории (`lib/**`, `test/**`, `integration_test/**`).
2. Репо-правила и CI (`AGENTS.md`, workflows, scripts).
3. Документация как baseline, но не абсолютный источник истины.

Команды инвентаризации:

```bash
rg --files lib
rg --files test
rg --files integration_test
dart run scripts/coverage_baseline.dart
```

## 2) Snapshot инвентаризации

- `lib/**/*.dart`: **150** файлов
- `test/**/*.dart`: **29** файлов
- `integration_test/**/*.dart`: **3** файла
- Baseline coverage:
  - `ALL_LIB`: `16.58%`
  - `EFFECTIVE_LIB`: `25.66%`

Распределение production feature-файлов:
- `primary_sources`: 40
- `topics`: 14
- `about`: 11
- `settings`: 5
- `download`: 2

Распределение `test/features`:
- `primary_sources`: 10
- `topics`: 3
- `settings`: 1
- `about`: 1

Распределение `test/widget`:
- `primary_sources`: 3
- `settings`: 1
- `topics`: 1

## 3) Traceability matrix (module-level)

| Production area | Current test contracts | Missing test contracts | Status | Suggested phase |
|---|---|---|---|---|
| `lib/main.dart`, `lib/app/bootstrap/**`, `lib/app/router/**`, `lib/app/di/**` | `test/app/router/route_args_test.dart` | bootstrap, app entry, router shell, DI wiring contracts | `real issue` | `P06` |
| `lib/features/primary_sources/presentation/bloc/**` | Хорошее покрытие unit/cubit тестами | расширение high-risk регрессий | `good coverage base` | `P07` |
| `lib/features/primary_sources/presentation/screens/**` | частично `test/widget/primary_sources/**` | contracts для `primary_source_screen.dart` и state rendering full matrix | `real issue` | `P12` |
| `lib/features/primary_sources/application/**` | `test/utils/pronunciation_test.dart` (misplaced), частично indirect | сервисные контракты для reference/description orchestration | `real issue` | `P08` |
| `lib/features/primary_sources/data/**` | почти нет прямых unit контрактов | repositories/data-source behavior tests | `real issue` | `P08` |
| `lib/features/topics/presentation/bloc/**` | есть cubit/state tests | screen-level widget contracts (`main_screen/topic_screen`) | `real issue` | `P12` |
| `lib/features/topics/data/**` | минимально | repository mapping/error branches | `real issue` | `P09` |
| `lib/features/settings/**` | сильная база cubit + 1 widget screen test | data/repository and edge-case contracts | `partial` | `P10`, `P13` |
| `lib/features/about/**` | есть cubit tests | screen/widget contracts и retry/failure UI | `real issue` | `P10`, `P13` |
| `lib/features/download/**` | по сути только smoke-навигация | unit+widget contracts | `real issue` | `P10`, `P13` |
| `lib/infra/**` | крайне мало (почти отсутствуют прямые unit tests) | db/runtime/connectors/remote/storage contracts | `real issue` | `P11` |
| `lib/shared/**`, `lib/core/**` | частично (`latest_request_guard`, `app_link_handler`) | xml/link/diagnostics/utils contracts | `real issue` | `P10`, `P11` |
| `integration_test/smoke/**` | 3 smoke теста по навигации | startup-through-main и критичные e2e sanity paths | `partial` | `P14` |

## 4) Prioritized production gap registry

### 4.1 Critical (High risk + low contract)

| File | Signal | Classification | Why | Target phase |
|---|---|---|---|---|
| `lib/main.dart` | missing in LCOV | `real issue` | нет прямого startup contract | `P06` |
| `lib/app/bootstrap/app_bootstrap.dart` | missing in LCOV | `real issue` | init path не защищен тестами | `P06` |
| `lib/app/router/app_router.dart` | `0/18` | `real issue` | нет route shell contract tests | `P06` |
| `lib/app/di/app_di.dart` | `0/27` | `real issue` | DI wiring не тестируется | `P06` |
| `lib/features/about/presentation/screens/about_screen.dart` | `0/256` | `real issue` | крупный экран без contract tests | `P13` |
| `lib/features/download/presentation/screens/download_screen.dart` | `0/55` | `real issue` | feature почти не покрыт | `P10/P13` |
| `lib/features/topics/presentation/screens/topic_screen.dart` | `0/160` | `real issue` | ключевой экран без widget contracts | `P12` |
| `lib/features/topics/presentation/screens/main_screen.dart` | `0/63` | `real issue` | entry screen темы без contract tests | `P12` |
| `lib/features/primary_sources/presentation/screens/primary_source_screen.dart` | `2/425 (0.47%)` | `real issue` | высокорисковый detail flow | `P12` |
| `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart` | `3/183 (1.64%)` | `real issue` | data contracts почти отсутствуют | `P08` |
| `lib/features/primary_sources/application/services/description_content_service.dart` | `6/253 (2.37%)` | `real issue` | complex service logic без unit coverage | `P08` |
| `lib/features/primary_sources/application/services/primary_source_reference_service.dart` | `2/70 (2.86%)` | `real issue` | reference resolution fragile зона | `P08` |
| `lib/features/topics/data/repositories/topics_repository.dart` | `1/53 (1.89%)` | `real issue` | data layer topics почти не тестируется | `P09` |
| `lib/infra/db/runtime/database_runtime.dart` | missing in LCOV | `real issue` | runtime gateway orchestration не покрыт | `P11` |
| `lib/infra/db/common/db_common.dart` | `0/100` | `real issue` | DB infra contracts отсутствуют | `P11` |
| `lib/infra/db/localized/db_localized.dart` | `0/47` | `real issue` | DB infra contracts отсутствуют | `P11` |
| `lib/shared/xml/xml_parsers.dart` | `0/50` | `real issue` | parser edge cases без защиты | `P10` |
| `lib/shared/utils/links_utils.dart` | `0/35` | `real issue` | link parsing behavior не зафиксирован | `P10` |
| `lib/core/diagnostics/diagnostics_utils.dart` | `0/103` | `real issue` | диагностическая логика без regression shield | `P10` |

### 4.2 Needs explicit architectural decision

| File | Signal | Classification | Decision needed |
|---|---|---|---|
| `lib/infra/db/connectors/web.dart` | missing in LCOV | `needs explicit architectural decision` | уровень покрытия web-only drift connector: unit-fakes vs integration-web |
| `lib/core/platform/web.dart` | missing in LCOV | `needs explicit architectural decision` | где фиксировать web interop behavior (unit boundary vs integration) |
| `lib/core/platform/file_downloader_web.dart` | missing in LCOV | `needs explicit architectural decision` | тестировать JS-interop напрямую или через adapter contract |
| `lib/core/platform/webgl_interop.dart` | missing in LCOV | `needs explicit architectural decision` | webgl bridge coverage strategy |

### 4.3 Acceptable tradeoff / low-value-to-test now

| File/group | Signal | Classification | Why |
|---|---|---|---|
| `lib/features/*/*.dart` barrel exports (`about.dart`, `download.dart`, `settings.dart`, `topics.dart`, `primary_sources.dart`) | missing in LCOV | `low-value-to-test` | экспортные ре-экспорты без бизнес-логики |
| `lib/core/platform/dependent.dart`, `lib/core/platform/file_downloader.dart`, `lib/infra/db/connectors/shared.dart`, `lib/infra/db/connectors/unsupported.dart` | mostly missing in LCOV | `acceptable tradeoff` | conditional export glue, ценность unit coverage ограничена |
| `lib/shared/config/app_constants.dart`, `lib/shared/models/description_kind.dart` | missing in LCOV | `low-value-to-test` | константы/enum, низкая регрессионная ценность |
| `lib/core/logging/app_bloc_observer.dart`, `lib/core/logging/app_logger_formatter.dart` | missing in LCOV | `low-value-to-test` | вторичный logging glue, покрывать позже при наличии инцидентов |

## 5) Docs divergence register

| Area | Docs claim | Code reality | Classification | Action |
|---|---|---|---|---|
| Integration smoke trigger | `docs/ru/testing/strategy.ru.md` описывает ручной запуск smoke workflow | `.github/workflows/integration_smoke.yml` имеет `workflow_dispatch` и weekly `cron` | `likely docs issue` | обновить формулировку в соответствующей фазе docs sync |
| Widget test tagging policy | стратегия говорит о widget suite с тегом `@Tags(['widget'])` | есть `testWidgets` вне `test/widget` и без тега (например `primary_source_description_cubit_test.dart`, `app_link_handler_test.dart`) | `likely code/process issue` | закрыть в `P03` (structural normalization) |

## 6) Ownership map by feature (execution ownership)

| Feature/area | Execution owner stream | Scope | Planned phases |
|---|---|---|---|
| App bootstrap/router | App Core stream | startup/router/DI contracts | `P06` |
| Primary sources | Primary Sources stream | application/data + widget contracts | `P08`, `P12` |
| Topics | Topics stream | data/application + widget contracts | `P09`, `P12` |
| Settings | Settings stream | repository edge cases + widget contracts | `P10`, `P13` |
| About | About stream | screen contracts + failure/retry | `P10`, `P13` |
| Download | Download stream | feature bootstrap + UI state flows | `P10`, `P13` |
| Infra DB/Remote/Storage | Infra stream | adapters/runtime contracts | `P11` |
| Shared/Core | Platform & Shared stream | parsers/utils/diagnostics | `P10`, `P11` |
| Integration smoke | QA/Smoke stream | critical end-to-end sanity paths | `P14` |

## 7) P02 checklist completion

- [x] Сформировать список production файлов без тест-контракта.
- [x] Пометить зоны: `real issue` / `acceptable tradeoff` / `low-value-to-test` / `needs explicit architectural decision`.
- [x] Отметить docs divergence и тип (code/docs/decision).
- [x] Сформировать ownership map по feature.

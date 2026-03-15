**Executive Summary**
- Аудит выполнен по Priority A>B>C: сначала код/тесты/CI/правила, затем best practices, затем docs как baseline.
- Массовых изменений не делал, только анализ.
- Текущее покрытие низкое для цели 90%: `~16.58%` по всему `lib`, `~25.66%` по `lib` без generated/l10n.
- Сильные стороны: хорошие Cubit-тесты в части `settings/topics/primary_sources`, есть проверки `latest-request-wins` и lifecycle safety в ряде мест.
- Основные structural проблемы: частичное несоответствие `test/` и `lib/`, смешение widget/unit через теги, слабое использование общего `test_harness`.
- Основные quality проблемы: часть тестов слишком поверхностная/smoke-like, есть риск недетерминизма (зависимость от реальных ассетов), integration smoke не покрывает полноценно bootstrap/DI/runtime поведение.
- Главные coverage gaps: `infra/**` почти пусто, крупные экраны `about/download/topics/primary_sources` почти не покрыты, ряд application/data сервисов near-zero.
- Достижение 90% реалистично только по согласованному “effective coverage scope” (исключив generated/l10n/баррели/платформенные glue files) и через поэтапный план.
- Попытка сделать все за один проход почти гарантированно даст low-value тесты, flaky-риск и ухудшит поддерживаемость.

Ключевые файлы, на которых базировался аудит:
- [AGENTS.md](C:/Users/karna/Projects/Revelation/AGENTS.md)
- [flutter_build.yml](C:/Users/karna/Projects/Revelation/.github/workflows/flutter_build.yml)
- [integration_smoke.yml](C:/Users/karna/Projects/Revelation/.github/workflows/integration_smoke.yml)
- [dart_test.yaml](C:/Users/karna/Projects/Revelation/dart_test.yaml)
- [check_forbidden_patterns.dart](C:/Users/karna/Projects/Revelation/scripts/check_forbidden_patterns.dart)
- [check_docs_sync.dart](C:/Users/karna/Projects/Revelation/scripts/check_docs_sync.dart)
- [strategy.ru.md](C:/Users/karna/Projects/Revelation/docs/ru/testing/strategy.ru.md)

---

## 1) Current Test Suite Assessment

**Current strengths**
- CI уже валидирует формат, analyze, split тест-прогон, forbidden-pattern checks.
- Есть рабочие unit тесты для части Cubit flow и race/lifecycle-сценариев.
- Есть smoke integration слой (`integration_test/smoke`) для базовой sanity-проверки.
- Архитектурные ограничения (BLoC/Cubit, запреты provider/ChangeNotifier) соблюдаются.

**Current weaknesses**
- Покрытие сильно неравномерное между модулями.
- `infra` и data-слой покрыты слабо, при этом это зона высокой регрессионной стоимости.
- Недостаточно контрактных тестов на app bootstrap/router.
- Недостаточно системного покрытия failure/edge веток у сервисов/парсеров.

**Structural issues**
- `test/widget/**` частично не зеркалит `lib/features/**/presentation/{screens,widgets}`.
- Есть misplacement: логика feature тестируется в “утилитном” пути.
- Тегирование widget-тестов неполное, из-за чего split в CI не полностью чистый.

**Quality issues**
- Есть smoke-стиль тестов с низкой диагностической ценностью при регрессии.
- Есть тесты с внешней файловой зависимостью (asset-driven), что повышает flaky risk.
- Дублирование fake/mocks между файлами вместо консолидации в harness.

**Coverage issues**
- Критические near-zero зоны: экраны `about/download/topics/primary_sources`, repositories/services в `primary_sources/topics`, большая часть `infra`.
- Значимые файлы не попадают в coverage-map как контрактные точки (`main.dart`, bootstrap/runtime точки).

**Risk areas**
- Async stale race и rapid switching в detail/catalog flows.
- Lifecycle (`close-before-complete`) не унифицирован по всем Cubit.
- Router/deep-link/contracts и startup path.
- DB/runtime и remote/storage интеграционные адаптеры.

**Docs divergence (baseline check)**
- Найдено расхождение: docs о запуске integration smoke “только manual”, но workflow содержит и cron.
- Классификация: `likely docs issue` (не code issue).

---

## 2) Test Structure Map

| Area | Current state | Issue type | Action |
|---|---|---|---|
| `test/features/**` | В целом ближе к feature-first | Частичная неполнота зеркала к `lib/features/**` | Достроить зеркалирование по screens/widgets/data/application |
| `test/widget/**` | Смешанные сценарии из разных feature | Misplacement + discoverability loss | Переразложить по feature path |
| `test/utils/**` | Есть feature-логика вне feature-пути | Misplacement | Перенести в соответствующий feature/application |
| `test/test_harness/**` | Есть, но используется ограниченно | Duplication of fakes/helpers | Консолидировать common fakes/builders/wrappers |
| `integration_test/smoke/**` | Базовый smoke | Недостаточно end-to-end контрактов | Добавить критические journeys без усложнения |
| Widget tag split | Есть `dart_test.yaml` tag `widget` | Не все `testWidgets` помечены | Нормализовать тегирование и policy |

---

## 3) Module-by-Module Testing Map

| Module/Area | Production path | Current situation | Missing test types | Risk | Priority | Recommended scope | Tricky scenarios | Suggested phase |
|---|---|---|---|---|---|---|---|---|
| App bootstrap/router | `lib/main.dart`, `lib/app/**` | Частично/слабо | unit+widget contract tests | High | Critical | bootstrap init path, route guards, fallback/error routing | init async order, DI failures | P06 |
| Primary sources presentation | `lib/features/primary_sources/presentation/**` | Частично, но крупные экраны слабые | widget contracts, interaction regressions | High | Critical | state rendering, switching, detail behaviors | rapid switching, stale response | P12 |
| Primary sources application/data | `lib/features/primary_sources/application/**`, `data/**` | Near-zero в ряде сервисов/repo | unit tests | High | Critical | services/repository behavior contracts | invalid input, parser errors | P08 |
| Topics presentation | `lib/features/topics/presentation/**` | Частично, экраны near-zero | widget contracts | High | High | list/detail states, navigation triggers | filter/sort + refresh races | P12 |
| Topics data/application | `lib/features/topics/data/**`, `application/**` | Низко | unit tests | High | High | repository/data mapping/error handling | stale cache vs refresh | P09 |
| Settings | `lib/features/settings/**` | Относительно лучше | edge/error/lifecycle expansion | Medium | High | persistent settings flows | close-before-complete | P10/P13 |
| About | `lib/features/about/**` | Экран почти не покрыт | widget + cubit edge tests | Medium | High | load/fail/retry render contracts | async load + reopen | P10/P13 |
| Download | `lib/features/download/**` | Практически пусто | unit+widget | High | Critical | download flow states/errors/retry | network unavailable, partial progress | P10/P13 |
| Infra DB/runtime | `lib/infra/db/**` | Почти ноль | unit tests with fakes | High | Critical | repository/data-source runtime behavior | migration/runtime fallback | P11 |
| Infra remote/storage | `lib/infra/remote/**`, `storage/**` | Почти ноль | unit tests | High | High | client wrappers/error mapping/retry | transient failures | P11 |
| Shared/core utilities | `lib/shared/**`, `lib/core/**` | Неравномерно, есть 0% файлы | unit tests | Medium | High | parsers/link utils/diagnostics contracts | malformed input | P10/P11 |
| Integration smoke | `integration_test/smoke/**` | Есть база | critical e2e sanity paths | Medium | High | startup + critical navigation | runtime init + feature open | P14 |

---

## 4) Prioritized Phased Plan

| Phase | Title | Priority | Why phase exists | Expected outcome | Dependencies | Risk | Complexity | Order |
|---|---|---|---|---|---|---|---|---|
| P01 | Coverage Baseline Contract | Critical | Зафиксировать честную точку старта и denominator | Согласованные метрики покрытия | None | Low | Low | 1 |
| P02 | Inventory & Traceability Map | Critical | Полная карта `lib`↔`test` | Таблица соответствий и gaps | P01 | Low | Medium | 2 |
| P03 | Structural Normalization | Critical | Устранить misplacement и tag hygiene | Консистентная структура `test/` | P02 | Medium | Medium | 3 |
| P04 | Harness Stabilization | High | Снизить flaky/duplication | Единый deterministic test harness | P03 | Medium | Medium | 4 |
| P05 | Existing Tests Quality Triage | High | Укрепить ценность уже имеющихся тестов | Классификация keep/rewrite/remove/strengthen | P04 | Medium | Medium | 5 |
| P06 | App Bootstrap/Router Contracts | Critical | Закрыть startup/navigation regressions | Контрактные тесты app entry/route | P04 | High | Medium | 6 |
| P07 | Async/Lifecycle Regression Pack | Critical | Закрыть самые опасные race/lifecycle | Набор стабильных regression tests | P05 | High | Medium | 7 |
| P08 | Unit Expansion: Primary Sources | Critical | Большой gap + высокий риск | Поведенческое покрытие services/repo | P07 | High | High | 8 |
| P09 | Unit Expansion: Topics | High | Рискованные data/application gaps | Контракты для data+logic topics | P07 | Medium | Medium | 9 |
| P10 | Unit Expansion: Settings/About/Download + Shared Core | High | Закрыть near-zero зоны и utility gaps | Unit contracts для remaining features/utils | P07 | Medium | High | 10 |
| P11 | Unit Expansion: Infra DB/Remote/Storage | Critical | Высокая цена регрессий infra | Изолированные deterministic infra tests | P04 | High | High | 11 |
| P12 | Widget Contracts: Primary Sources + Topics | Critical | Закрыть крупные screen-level дырки | State-driven widget contracts | P08,P09 | High | High | 12 |
| P13 | Widget Contracts: Settings/About/Download + Shared Widgets | High | Довести UI contract layer | Стабильные widget tests по остальным зонам | P10 | Medium | Medium | 13 |
| P14 | Integration Smoke Expansion | High | End-to-end sanity критичных путей | Короткий, стабильный smoke suite | P06,P12,P13 | Medium | Medium | 14 |
| P15 | Final Coverage Push + Gates + Cleanup | Critical | Дойти до agreed target и закрепить | Threshold policy, final cleanup | P08-P14 | Medium | Medium | 15 |

---
## 5) Detailed Checklist Per Phase

### Phase P01
- phase id: `P01`
- title: `Coverage Baseline Contract`
- priority: `critical`
- scope: фиксация метрик и правил denominator
- target modules: all
- main test types involved: meta/measurement
- estimated value: very high
- estimated risk: low
- dependencies: none
- why this phase exists: без единого denominator “90%” будет спорной метрикой
- expected outcome: baseline report + agreed scope coverage
- recommended execution order: 1
- checklist:
- [x] Зафиксировать baseline `%` для `ALL_LIB` и `EFFECTIVE_LIB` — завершено, когда оба значения сохранены в артефакте.
- [x] Утвердить exclude-list: generated/l10n/barrels/platform glue — завершено, когда список формализован в одном месте.
- [x] Согласовать target ladder (например 40→55→70→80→90) — завершено, когда есть этапные thresholds.
- [x] Зафиксировать метод расчета в CI/readme для тестов — завершено, когда любой участник может повторить расчет.
- deliverables: baseline coverage report, denominator policy.
- exit criteria: повторяемый расчет coverage без двусмысленности.
- validation commands: `flutter test --coverage`, `flutter analyze`.
- likely pitfalls: гонка за “процентом” без ценности.
- notes for future execution: не менять прод-код в этой фазе.

### Phase P02
- phase id: `P02`
- title: `Inventory & Traceability Map`
- priority: `critical`
- scope: карта соответствия `lib/**` ↔ `test/**`
- target modules: all
- main test types involved: audit
- estimated value: high
- estimated risk: low
- dependencies: P01
- why this phase exists: нужно видеть точные пробелы до написания тестов
- expected outcome: module map + gap registry
- recommended execution order: 2
- checklist:
- [x] Сформировать список production файлов без тест-контракта — завершено, когда есть приоритизированный gap list.
- [x] Пометить зоны: `real issue`/`acceptable tradeoff`/`low-value-to-test` — завершено, когда каждый gap имеет класс.
- [x] Отметить docs divergence и тип (code/docs/decision) — завершено, когда расхождения классифицированы.
- [x] Сформировать ownership map по feature — завершено, когда видно кто и в какой фазе покрывает модуль.
- deliverables: traceability matrix.
- exit criteria: нет “слепых зон” без классификации.
- validation commands: `rg --files test`, `rg --files lib`, `flutter test --coverage`.
- likely pitfalls: считать docs source of truth вместо кода.
- notes for future execution: обновлять матрицу после каждой фазы.

### Phase P03
- phase id: `P03`
- title: `Structural Normalization`
- priority: `critical`
- scope: структура тестов, пути, теги
- target modules: test folder + integration_test
- main test types involved: structural maintenance
- estimated value: high
- estimated risk: medium
- dependencies: P02
- why this phase exists: без структуры suite сложно поддерживать
- expected outcome: единый layout и корректный split unit/widget
- recommended execution order: 3
- checklist:
- [x] Перенести misplaced тесты в feature-aligned пути — завершено, когда путь теста отражает production path.
- [x] Нормализовать `@Tags(['widget'])` для всех `testWidgets` — завершено, когда split-команды не пересекаются.
- [x] Удалить/архивировать dead/stale тест-файлы — завершено, когда нет “висячих” или дублирующих файлов.
- [x] Проверить naming convention тестов — завершено, когда имена отражают behavioral contract.
- deliverables: clean test tree.
- exit criteria: структура консистентна и discoverable.
- validation commands: `flutter test --exclude-tags widget`, `flutter test --tags widget`.
- likely pitfalls: механический перенос без обновления imports.
- notes for future execution: маленькие PR/запросы по 1-2 директории.

### Phase P04
- phase id: `P04`
- title: `Harness Stabilization`
- priority: `high`
- scope: `test_harness`, common fakes, deterministic helpers
- target modules: `test/test_harness/**`
- main test types involved: shared test infra
- estimated value: high
- estimated risk: medium
- dependencies: P03
- why this phase exists: снизить flaky и дубли
- expected outcome: переиспользуемый deterministic toolkit
- recommended execution order: 4
- checklist:
- [x] Выделить повторяемые fake/mock builders из тестов — завершено, когда дубли уменьшены.
- [x] Вынести time/async helper utilities для стабильных await flows — завершено, когда исключены wall-clock зависимости.
- [x] Добавить стандартный app test wrapper для widget tests — завершено, когда routing/localization setup унифицирован.
- [x] Документировать harness usage кратким README в test_harness — завершено, когда новый тест можно писать по шаблону.
- deliverables: shared harness utilities.
- exit criteria: новые тесты пишутся с минимумом boilerplate.
- validation commands: `flutter test --exclude-tags widget`, `flutter test --tags widget`.
- likely pitfalls: чрезмерная абстракция harness.
- notes for future execution: prefer small reusable helpers, не framework внутри framework.

### Phase P05
- phase id: `P05`
- title: `Existing Tests Quality Triage`
- priority: `high`
- scope: review existing tests by quality class
- target modules: all existing tests
- main test types involved: unit/widget/integration review
- estimated value: high
- estimated risk: medium
- dependencies: P04
- why this phase exists: сначала укрепить текущие тесты, потом расширять
- expected outcome: each test marked keep/strengthen/rewrite/remove
- recommended execution order: 5
- checklist:
- [x] Классифицировать тесты по ценности регресс-защиты — завершено, когда каждому файлу присвоен статус.
- [x] Усилить слабые asserts (behavior over implementation) — завершено, когда тест проверяет эффект, а не внутреннюю деталь.
- [x] Убрать недетерминизм (assets/time/network dependencies) — завершено, когда тест стабилен локально и в CI.
- [x] Зафиксировать backlog “rewrite later” отдельно — завершено, когда нет скрытого техдолга.
- deliverables: quality triage sheet.
- exit criteria: нет критично слабых тестов в high-risk зонах.
- validation commands: `flutter test`, `flutter test integration_test/smoke`.
- likely pitfalls: переписывать слишком много сразу.
- notes for future execution: лимит scope по фазе.

### Phase P06
- phase id: `P06`
- title: `App Bootstrap & Router Contracts`
- priority: `critical`
- scope: app entry, DI init, base routing
- target modules: `lib/main.dart`, `lib/app/**`
- main test types involved: unit + widget contract tests
- estimated value: very high
- estimated risk: high
- dependencies: P04
- why this phase exists: startup regressions блокируют весь продукт
- expected outcome: стабильные контракты старта и маршрутизации
- recommended execution order: 6
- checklist:
- [x] Добавить тесты happy/failure startup path — завершено, когда init ошибки детерминированно тестируются.
- [x] Проверить route contracts и неизвестные маршруты — завершено, когда fallback behavior зафиксирован.
- [x] Покрыть базовый deep-link/open behavior — завершено, когда обработка URI тестируема.
- [x] Добавить smoke widget contract для app shell — завершено, когда основной shell рендерится в тестовой среде.
- deliverables: bootstrap/router test pack.
- exit criteria: критические startup/nav сценарии закрыты.
- validation commands: `flutter test test/app`, `flutter test --tags widget`.
- likely pitfalls: чрезмерная зависимость от конкретной реализации go_router internals.
- notes for future execution: фокус на публичный behavior.

### Phase P07
- phase id: `P07`
- title: `Async/Lifecycle Regression Pack`
- priority: `critical`
- scope: cross-feature async hazards
- target modules: primary_sources, topics, settings, about
- main test types involved: cubit/bloc unit tests
- estimated value: very high
- estimated risk: high
- dependencies: P05
- why this phase exists: эти баги часто возвращаются после рефакторинга
- expected outcome: стандартизированный набор high-risk regression tests
- recommended execution order: 7
- checklist:
- [x] Для ключевых Cubit добавить `latest-request-wins` — завершено, когда stale responses игнорируются тестами.
- [x] Добавить `close-before-complete` для async flows — завершено, когда нет emit after close.
- [x] Проверить side-effect call counts при rapid-switch — завершено, когда нет дублей вызовов.
- [x] Зафиксировать retry/reopen contracts — завершено, когда повторные открытия не ломают state.
- deliverables: high-risk cubit regression suite.
- exit criteria: high-risk async class закрыт по ключевым модулям.
- validation commands: `flutter test test/features/**/presentation/bloc`.
- likely pitfalls: flaky из-за таймеров.
- notes for future execution: использовать deterministic fake async/pump policies.

### Phase P08
- phase id: `P08`
- title: `Unit Expansion: Primary Sources`
- priority: `critical`
- scope: application/data/services/repositories
- target modules: `lib/features/primary_sources/application/**`, `data/**`
- main test types involved: unit tests
- estimated value: very high
- estimated risk: high
- dependencies: P07
- why this phase exists: крупный gap + высокая функциональная сложность
- expected outcome: надежные поведенческие контракты data/application слоя
- recommended execution order: 8
- checklist:
- [ ] Покрыть repositories happy/error/empty cases — завершено, когда поведение при каждом исходе проверено.
- [ ] Покрыть parsers/mappers/normalizers invalid input paths — завершено, когда bad data не падает неожиданно.
- [ ] Покрыть orchestration сервисы и reference resolution — завершено, когда side effects проверяются контрактно.
- [ ] Добавить regression кейсы на известные fragile места detail flow — завершено, когда сценарии воспроизводимы тестом.
- deliverables: primary_sources unit pack.
- exit criteria: zero/near-zero файлы модуля выходят из красной зоны.
- validation commands: `flutter test test/features/primary_sources`.
- likely pitfalls: тестирование приватных деталей вместо контракта.
- notes for future execution: делить на микро-шаги по 1 сервису/репозиторию.

### Phase P09
- phase id: `P09`
- title: `Unit Expansion: Topics`
- priority: `high`
- scope: topics data/application contracts
- target modules: `lib/features/topics/data/**`, `application/**`
- main test types involved: unit tests
- estimated value: high
- estimated risk: medium
- dependencies: P07
- why this phase exists: topics участвует в ключевой навигации и контенте
- expected outcome: стабильное поведение catalog/content data logic
- recommended execution order: 9
- checklist:
- [ ] Покрыть repository branches (success/error/empty) — завершено, когда нет непроверенных веток.
- [ ] Покрыть маппинг/сортировку/фильтрацию — завершено, когда бизнес-правила зафиксированы.
- [ ] Добавить invalid payload tests — завершено, когда defensive handling проверен.
- [ ] Добавить regression tests для refresh/switch scenarios — завершено, когда race-кейсы закрыты.
- deliverables: topics unit pack.
- exit criteria: data/application coverage модуля заметно поднят.
- validation commands: `flutter test test/features/topics`.
- likely pitfalls: хрупкие тесты, завязанные на детали коллекций.
- notes for future execution: проверять бизнес-инварианты явно.

### Phase P10
- phase id: `P10`
- title: `Unit Expansion: Settings/About/Download + Shared Core`
- priority: `high`
- scope: remaining feature units + shared/core helpers
- target modules: `features/settings`, `features/about`, `features/download`, `shared`, `core`
- main test types involved: unit tests
- estimated value: high
- estimated risk: medium
- dependencies: P07
- why this phase exists: закрыть near-zero и utility contract gaps
- expected outcome: контракты ошибок/edge cases в оставшихся модулях
- recommended execution order: 10
- checklist:
- [ ] Settings: persistence/read/write/error branches — завершено, когда настройки устойчивы к ошибкам.
- [ ] About/Download: load/fail/retry logic — завершено, когда сценарии поведения зафиксированы.
- [ ] Shared/core utilities (xml, links, diagnostics) — завершено, когда invalid input обработка покрыта.
- [ ] Исключить network/time зависимости через fakes — завершено, когда тесты полностью локальные.
- deliverables: unit tests for remaining feature/core gaps.
- exit criteria: критичные utility/remainder зоны больше не 0%.
- validation commands: `flutter test test/features/settings test/features/about test/features/download test/shared test/core`.
- likely pitfalls: писать “assert true”-стиль тестов ради покрытия.
- notes for future execution: фокус на behavior contracts.

### Phase P11
- phase id: `P11`
- title: `Unit Expansion: Infra DB/Remote/Storage`
- priority: `critical`
- scope: infra adapters and runtime behavior
- target modules: `lib/infra/db/**`, `lib/infra/remote/**`, `lib/infra/storage/**`
- main test types involved: unit tests with fakes/mocks
- estimated value: very high
- estimated risk: high
- dependencies: P04
- why this phase exists: наибольшая регрессионная цена при низком покрытии
- expected outcome: deterministic contracts для infra-слоя
- recommended execution order: 11
- checklist:
- [ ] DB runtime/adapters: success/failure/fallback contracts — завершено, когда ключевые runtime path протестированы.
- [ ] Remote wrappers: error mapping/retry semantics — завершено, когда ошибки нормализованы тестами.
- [ ] Storage adapters: missing/corrupt data handling — завершено, когда защитные ветки закрыты.
- [ ] Исключить внешние вызовы (network/fs нестабильный) — завершено, когда тесты полностью isolated.
- deliverables: infra deterministic unit pack.
- exit criteria: infra перестает быть near-zero по покрытию.
- validation commands: `flutter test test/infra`.
- likely pitfalls: попытка сделать pseudo-integration вместо unit.
- notes for future execution: четко мокаем boundaries.

### Phase P12
- phase id: `P12`
- title: `Widget Contracts: Primary Sources + Topics`
- priority: `critical`
- scope: state-driven screen/widget behavior
- target modules: `features/primary_sources/presentation`, `features/topics/presentation`
- main test types involved: widget tests
- estimated value: very high
- estimated risk: high
- dependencies: P08,P09
- why this phase exists: большие экраны сейчас с минимальной контрактной защитой
- expected outcome: надежные UI contracts ключевых экранов
- recommended execution order: 12
- checklist:
- [ ] Для каждого ключевого экрана закрыть `loading/empty/error/content` — завершено, когда 4 состояния покрыты тестами.
- [ ] Проверить основные user interactions и side effects — завершено, когда действия дают ожидаемый визуальный/state результат.
- [ ] Проверить navigation triggers на уровне practical widget scope — завершено, когда переходы инициируются корректно.
- [ ] Убрать asset-driven недетерминизм через controlled fixtures — завершено, когда тесты стабильны на CI.
- deliverables: widget contract pack for two largest features.
- exit criteria: screen-level gaps существенно сокращены.
- validation commands: `flutter test --tags widget test/features/primary_sources test/features/topics`.
- likely pitfalls: golden-heavy стратегия без нужды.
- notes for future execution: prefer semantic finders и behavior assertions.

### Phase P13
- phase id: `P13`
- title: `Widget Contracts: Settings/About/Download + Shared Widgets`
- priority: `high`
- scope: remaining presentation contracts
- target modules: settings/about/download/shared widgets
- main test types involved: widget tests
- estimated value: high
- estimated risk: medium
- dependencies: P10
- why this phase exists: довести консистентность UI contract layer
- expected outcome: предсказуемые regression checks для оставшихся UI зон
- recommended execution order: 13
- checklist:
- [ ] Settings screens: state render + interactions — завершено, когда ключевые UI контракты зафиксированы.
- [ ] About/Download screens: load/fail/retry rendering — завершено, когда критичные состояния покрыты.
- [ ] Reusable widgets: contract tests на входные параметры/колбэки — завершено, когда reusable UI защищен.
- [ ] Привести все widget tests к единым tags/pump policy — завершено, когда suite однороден.
- deliverables: widget contract pack for remaining features.
- exit criteria: все feature presentation зоны имеют базовый контрактный слой.
- validation commands: `flutter test --tags widget test/features/settings test/features/about test/features/download test/shared`.
- likely pitfalls: over-mocking UI и потеря поведенческой ценности.
- notes for future execution: тестировать сценарии, не реализацию верстки.

### Phase P14
- phase id: `P14`
- title: `Integration Smoke Expansion`
- priority: `high`
- scope: короткие критические e2e пути
- target modules: `integration_test/smoke/**`
- main test types involved: integration tests
- estimated value: high
- estimated risk: medium
- dependencies: P06,P12,P13
- why this phase exists: защитить критичные user journeys от cross-layer regressions
- expected outcome: стабильный и быстрый smoke gate
- recommended execution order: 14
- checklist:
- [ ] Startup smoke через реальный app entry path — завершено, когда приложение поднимается в integration smoke.
- [ ] Критичная навигация по 2-3 главным маршрутам — завершено, когда сценарии проходят end-to-end.
- [ ] Feature open/load/render sanity (topics + primary sources + settings/about/download минимум) — завершено, когда ключевые экраны доступны.
- [ ] Ограничить runtime smoke suite по времени — завершено, когда smoke стабильно быстрый.
- deliverables: expanded integration smoke suite.
- exit criteria: weekly/manual smoke устойчиво проходит.
- validation commands: `flutter test integration_test/smoke`.
- likely pitfalls: превращение smoke в тяжелые e2e.
- notes for future execution: strict scope, no brittle UI-detail assertions.

### Phase P15
- phase id: `P15`
- title: `Final Coverage Push + Gates + Cleanup`
- priority: `critical`
- scope: закрытие хвостов, thresholds, финальная чистка
- target modules: all
- main test types involved: all
- estimated value: very high
- estimated risk: medium
- dependencies: P08-P14
- why this phase exists: закрепить результат и предотвратить откат
- expected outcome: достижение согласованного target и guardrails в CI
- recommended execution order: 15
- checklist:
- [ ] Закрыть top remaining high-value gaps — завершено, когда high-risk list пуст или обоснованно отложен.
- [ ] Ввести coverage thresholds (этапные/финальные) — завершено, когда CI фейлит при деградации.
- [ ] Удалить stale/duplicate tests и debt-технику — завершено, когда suite чище без потери ценности.
- [ ] Обновить docs/test strategy (RU/EN sync при изменениях) — завершено, когда docs и код синхронны.
- deliverables: stable high-value suite + CI gates.
- exit criteria: agreed coverage target достигнут и защищен в CI.
- validation commands: `flutter analyze`, `flutter test`, `flutter test --coverage`, `dart run scripts/check_docs_sync.dart`.
- likely pitfalls: искусственный coverage padding.
- notes for future execution: quality > percentage.

---

## 6) Coverage Strategy

- Стратегия к 90%: только через `effective coverage scope`.
- Что покрывать первым:
- high-risk + low-coverage: `infra`, `primary_sources data/application`, startup/router.
- screen-level contracts для крупных экранов с near-zero coverage.
- Где coverage растет быстрее и полезнее:
- крупные 0%-экраны в feature presentation.
- pure utilities/parsers/link handlers с минимальными зависимостями.
- repositories/services с множеством веток ошибок.
- Что не over-test:
- generated (`*.g.dart`), `l10n generated`, баррель-файлы, платформенные registrant/glue.
- мелкие пассивные DTO без логики.
- Как не гнаться искусственно:
- каждый новый тест обязан фиксировать observable behavior или регрессионный риск.
- исключать implementation-coupled asserts.
- использовать ladder targets по фазам, а не “рывок до 90” за один цикл.

---

## 7) Validation Strategy

**Per phase validation**
- Локально: таргетные тесты затронутого модуля.
- Полный контур: `flutter analyze`, `flutter test --exclude-tags widget`, `flutter test --tags widget`.
- Coverage snapshot после каждой high-impact фазы: `flutter test --coverage`.
- Архитектурные правила: запреты provider/ChangeNotifier и BuildContext в запрещенных слоях.
- Документация (если меняется): `dart run scripts/check_docs_sync.dart`.

**Evidence of completion**
- До/после coverage delta по модулю.
- Список добавленных/усиленных behavioral contracts.
- Отсутствие flaky-признаков в повторных прогонах.
- CI green на соответствующих джобах.

**Anti-flaky safeguards**
- без реальной сети;
- без wall-clock sleep, только deterministic async control;
- controlled fixtures вместо “первого файла из assets”;
- минимизация случайности в order-dependent assertions.

---

## 8) Risks and Pitfalls

- Low-value work risk:
- написание тестов ради строк покрытия, а не поведения.
- чрезмерная детализация UI implementation (хрупкие widget tests).
- Flaky risk:
- реальные assets/network/time.
- гонки в async-тестах без четкой pump/await стратегии.
- Context overflow risk:
- слишком большие фазы типа “покрыть все unit tests”.
- отсутствие строгого phase scope и stop criteria.
- Suite degradation risk:
- массовые переписывания без triage.
- смешивание structural migration и logic rewrite в одном шаге.

---

## 9) Reusable Execution Template

Используй этот шаблон для любого следующего шага:

```text
Запрос: Выполни Phase <ID> из плана тестового покрытия.

Вход:
- Phase ID: <ID>
- Scope override (опционально): <module/path>
- Ограничения:
  - Не делать массовый рефакторинг production кода.
  - Работать маленькими безопасными изменениями.
  - Сохранять BLoC/Cubit и repo rules из AGENTS.md.
- Цель фазы: <вставить цель из плана>

Что нужно сделать:
1) Выполнить checklist фазы полностью.
2) Сделать только изменения, необходимые для этой фазы.
3) Прогнать validation commands фазы.
4) Дать короткий отчёт по deliverables, coverage delta, рискам.

Что НЕ делать:
- Не переходить к следующей фазе.
- Не пытаться закрыть весь coverage сразу.
- Не добавлять low-value/artificial tests.

Формат отчёта:
- Сделано:
- Что не удалось/ограничения:
- Измененные файлы:
- Результаты команд:
- Coverage delta:
- Остаточные риски:
- Рекомендованный следующий Phase ID:
```

---

## 10) Prioritization Matrix

| Bucket | What goes here | Do now / later |
|---|---|---|
| High risk / High value / Low coverage | infra, primary_sources data/services, startup/router, download | Do first |
| High risk / Existing weak tests | async race/lifecycle gaps, shallow smoke tests | Do first |
| Medium risk / High reuse | shared/core utilities, reusable widgets, harness | Do second |
| Low risk / Low value | generated/barrels/passive glue | Defer / exclude |
| Good enough for now | стабильные cubit-тесты с уже хорошими контрактами | Keep, only spot improvements |

---

## 11) Top 10 Highest-Priority Phases

1. P01 Coverage Baseline Contract  
2. P03 Structural Normalization  
3. P04 Harness Stabilization  
4. P06 App Bootstrap & Router Contracts  
5. P07 Async/Lifecycle Regression Pack  
6. P08 Unit Expansion: Primary Sources  
7. P11 Unit Expansion: Infra DB/Remote/Storage  
8. P12 Widget Contracts: Primary Sources + Topics  
9. P14 Integration Smoke Expansion  
10. P15 Final Coverage Push + Gates

---

## 12) Top 10 Biggest Test Coverage Gaps

1. `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`
2. `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`
3. `lib/features/primary_sources/application/services/description_content_service.dart`
4. `lib/features/primary_sources/application/services/primary_source_reference_service.dart`
5. `lib/features/topics/data/repositories/topics_repository.dart`
6. `lib/features/about/presentation/screens/about_screen.dart`
7. `lib/features/download/presentation/screens/download_screen.dart`
8. `lib/features/topics/presentation/screens/topic_screen.dart`
9. `lib/features/topics/presentation/screens/main_screen.dart`
10. `lib/infra/**` (db/runtime/remote/storage adapters as a group)

---

## 13) Top 10 Weakest Existing Tests or Weak Test Areas

1. Неполная tag hygiene для `testWidgets` (мешает чистому split).
2. Misplacement тестов (feature logic вне feature path).
3. Asset-dependent widget tests (файловая нестабильность).
4. Shallow smoke tests без глубокого behavioral контракта.
5. Недостаточная проверка side-effect call-count в rapid-switch сценариях.
6. Недостаток failure-path assertions в части feature services.
7. Дублирующиеся локальные fakes вместо harness reuse.
8. Ограниченное покрытие router/bootstrap контракта.
9. Недостаточное покрытие infra error mapping/retry behavior.
10. Недостаток тестов на invalid/malformed input в parsers/utils.

---

## 14) Top 10 Regression-Prone Areas To Cover Early

1. Primary source detail flow при быстром переключении.
2. Topics catalog/content refresh race conditions.
3. Cubit lifecycle: `close-before-complete`.
4. Startup/DI init failures и fallback behavior.
5. Router/deep-link route contract handling.
6. Download state machine: retry/reopen/fail transitions.
7. DB runtime/fallback behavior across platform contexts.
8. Remote/storage transient failures and retries.
9. XML/parser malformed input handling.
10. Multi-cubit coordination between list/detail settings flows.

---

## 15) Final Recommended Execution Order

1. P01  
2. P02  
3. P03  
4. P04  
5. P05  
6. P06  
7. P07  
8. P08  
9. P09  
10. P10  
11. P11  
12. P12  
13. P13  
14. P14  
15. P15

Если хочешь, следующий шаг можно сделать сразу в рабочем режиме: `Выполни Phase P03` (самый безопасный старт перед реальным наращиванием покрытия).


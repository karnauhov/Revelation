# State Management Audit + Remediation Plan (рабочий, временный)

Дата аудита: `2026-03-14`  
Область: весь Flutter-проект (`lib/`, `test/`, `integration_test/`, `docs/`, CI/scripts)  
Фокус: только state management и связанные архитектурные аспекты  
Статус выполнения плана: `в процессе (Step 1 выполнен)`  

Как использовать документ:
- Этот файл предназначен как пошаговый execution-plan.
- Каждый пункт плана ниже оформлен как чекбокс `[ ]`.
- После выполнения пункта переключаем его в `[x]`.
- Документ временный (по запросу можно удалить после завершения работ).

---

## Executive Summary

Текущее состояние state management в проекте: **рабочее, но неоднородное**.

Ключевые выводы:
- Базовый архитектурный вектор соблюден: проект использует `Cubit` как основной паттерн, `provider/ChangeNotifier` в runtime/test отсутствуют.
- Глобальные source-of-truth срезы определены адекватно (`Settings`, `TopicsCatalog`, `PrimarySources`), но в деталке primary source есть гибридная orchestration-схема с размытыми границами ответственности.
- Есть **критичный риск производительности**: широкие подписки + частые `emit` трансформации в деталке источника.
- Есть **слабые места в predictability async**: `TopicsCatalogCubit` без stale-guard.
- Есть **нарушение deep-immutability ownership**: мутация модели `PrimarySource` из UI.
- Есть **заметный docs/code drift** в части реальной orchestration и immutable-контрактов.
- Переход после рефакторинга в целом завершен на уровне структуры, но видны остаточные legacy-паттерны в primary source detail.

Итог: архитектура не аварийная, но для “полного порядка” нужен целевой цикл исправлений в 3 приоритета:
1) стабильность и производительность detail-flow,
2) ownership/immutability контракты,
3) консолидация архитектуры + docs/test regression coverage.

---

## 1) Actual State Architecture

### Как реально устроен state management сейчас
- Глобальный app scope:
  - `SettingsCubit` (`lib/main.dart`, `lib/app/di/app_di.dart`)
  - `TopicsCatalogCubit` (`lib/app/di/app_di.dart`)
  - `PrimarySourcesCubit` (`lib/app/di/app_di.dart`)
- Экранный scope:
  - `TopicScreen` поднимает локальный `TopicContentCubit`.
  - `AboutScreen` поднимает локальный `AboutCubit`.
  - `PrimarySourceScreen` поднимает `MultiBlocProvider` с 5 detail-cubit slices:
    - `PrimarySourceSessionCubit`
    - `PrimarySourceImageCubit`
    - `PrimarySourcePageSettingsCubit`
    - `PrimarySourceDescriptionCubit`
    - `PrimarySourceViewportCubit`
- Поверх detail-cubit slices используется дополнительный orchestration-слой:
  - `PrimarySourceDetailOrchestrationCubit` (state = `{}`),
  - `PrimarySourceDetailCoordinator` (facade + mutable callbacks),
  - `ImagePreviewController`,
  - `ValueNotifier<ZoomStatus>`.

### Сильные стороны
- Единый state stack основан на `flutter_bloc` (`Cubit` везде, `Bloc` не используется без необходимости).
- Запрещенные legacy-паттерны (`provider/ChangeNotifier/notifyListeners`) отсутствуют.
- В нескольких критичных местах уже есть stale/race protection (`LatestRequestGuard`) и тесты на это (`PrimarySourcesCubit`, `PrimarySourceImageCubit`, orchestration detail image load).
- Есть покрытие unit/widget тестами по большинству cubit-срезов.

### Системные слабости
- Гибрид orchestration в primary source detail увеличивает cognitive load и размывает owner boundaries.
- Широкие подписки на полный state-объект в деталке + частые transform updates создают rebuild pressure.
- Не везде одинаково жестко соблюдается async safety (stale/close checks).
- Контракты state и модели не полностью immutable в deep-смысле (мутабельный `PrimarySource`).

---

## 2) Alignment with Skills / Rules / Best Practices

### Соответствие внутренним правилам и AGENTS
- Соответствует:
  - State management через `Cubit/BLoC`.
  - Нет `provider/ChangeNotifier/notifyListeners`.
  - Feature-first структура и базовые module boundaries соблюдены.
- Частично расходится:
  - В деталке primary source orchestration формально “через cubit”, но фактически часть координации сидит в mutable coordinator/controller/notifier.
  - Есть mutable model state (`PrimarySource.showMore`), что конфликтует с идеей предсказуемого owner-driven состояния.

### Соответствие best practices flutter_bloc
- Плюсы:
  - Логика в cubits разделена по срезам.
  - Есть `copyWith`.
  - Async-guarding применяется в важных потоках.
- Минусы:
  - Side effects в `build`.
  - Broad subscriptions (`context.select` на весь state объект).
  - Неполная консистентность equality/immutability.
  - Недостаток regression tests под конкретные race/rebuild риски.

### Спорные места
- `PrimarySourceDetailOrchestrationCubit` без meaningful state + отдельный `PrimarySourceDetailCoordinator`.
  - Оценка: **needs architectural decision** (не критическая поломка, но долг в ясности архитектуры).

---

## 3) State Ownership Review

### Текущие owners (фактически по коду)
- App-level:
  - Настройки: `SettingsCubit`.
  - Каталог тем: `TopicsCatalogCubit`.
  - Список первоисточников: `PrimarySourcesCubit`.
- Topic detail:
  - Контент темы: `TopicContentCubit`.
- Primary source detail:
  - Session/page selection: `PrimarySourceSessionCubit`.
  - Image bytes/loading/availability: `PrimarySourceImageCubit`.
  - Page settings/render toggles: `PrimarySourcePageSettingsCubit`.
  - Description content/selection: `PrimarySourceDescriptionCubit`.
  - Viewport/selection/color replacement: `PrimarySourceViewportCubit`.
  - Cross-slice orchestration: `PrimarySourceDetailOrchestrationCubit` + `PrimarySourceDetailCoordinator`.

### Проблемы ownership
- `PrimarySource.showMore` хранится в доменной модели и мутируется из виджета.
- `PrimarySourceSessionState.source` хранит ссылку на mutable объект `PrimarySource`.
- Detail-flow ownership размыт между cubit/state, coordinator и `ValueNotifier`.

### Вывод
- Source-of-truth в целом читаем, но в primary source detail есть ownership drift.

---
## 4) Cubit/Bloc Design Review

- `Cubit` используется как основной паттерн: **да**.
- `Bloc` используется без необходимости: **нет**.
- “God cubit”: явного нет.
- “God coordinator”: есть риск в `PrimarySourceDetailCoordinator` (много обязанностей фасада + side-effect routing).

Кандидаты на переработку:
- `PrimarySourceDetailOrchestrationCubit` + `PrimarySourceDetailCoordinator`:
  - либо укрепить orchestration cubit как единую orchestration-точку,
  - либо формально зафиксировать coordinator как допустимый адаптер и максимально упростить его.

---

## 5) Provider Scope and Lifecycle Review

### Scope
- App-level providers заведены централизованно (`AppDi.appBlocProviders`).
- Screen-level providers в целом scoped корректно (`TopicScreen`, `AboutScreen`, `PrimarySourceScreen`).

### Lifecycle
- Закрытие локальных cubits в `dispose` присутствует.
- Риск:
  - async `emit` после `await` без `isClosed`/token checks в нескольких cubits.

### DI/provisioning
- В отдельных местах создание зависимостей идет напрямую в presentation (`PagesRepository()` в `PrimarySourceScreen`, `TopicsRepository()` по умолчанию в cubit).
- Это не ломает runtime, но снижает единообразие DI и усложняет swap/mocking-стратегию.

---

## 6) State Contract Review

Плюсы:
- Почти везде есть `copyWith`.
- В нескольких state-классах коллекции обернуты в unmodifiable.

Недостатки:
- Нет единообразного value equality (`Equatable`/`==`/`hashCode`) для state-классов.
- `ZoomStatus` без equality, что усиливает шум перерисовок.
- `PrimarySource` содержит mutable поле `showMore`, что разрушает deep-immutability в цепочке `SessionState -> source`.

---

## 7) Async Flows and Side Effects Review

Основные риски:
- `TopicsCatalogCubit.loadForLanguage` без stale-request guard.
- Side effects в `build` (`changeSelectedPage`, `showCommonInfo`, `onRestorePositionAndScale`).
- В detail viewport потоке возможен state churn из-за частых трансформационных `emit`.

Что уже сделано хорошо:
- `LatestRequestGuard` корректно используется в `PrimarySourcesCubit`, `PrimarySourceImageCubit`, `PrimarySourceDetailOrchestrationCubit`.

---

## 8) UI Integration Review

Найдено:
- Широкие подписки на полный state сразу 5 cubit-срезов в `PrimarySourceScreen`:
  - `context.select((cubit) => cubit.state)` для каждого среза.
- На частых transform update это приводит к rebuild всего экрана.
- `AboutScreen` использует `context.select(...settings.toMap())`, что создает лишние rebuild.
- Side-effects в build path смешаны с render-логикой.

---

## 9) Legacy and Forbidden Patterns

Проверка forbidden patterns:
- `provider`/`ChangeNotifier`/`notifyListeners`: не обнаружены.

Legacy/candidate cleanup:
- `imageShown` и `showDescription` в primary sources detail-flow выглядят недоиспользуемыми.
- `PrimarySource.showMore` как mutable UI-state в модели — legacy smell.

---

## 10) Testing Review

Сильные стороны:
- Есть unit-тесты большинства cubits.
- Есть widget-тесты ключевых экранов/виджетов.
- Есть test harness/fakes.
- Есть отдельные тесты для `LatestRequestGuard`.

Критичные пробелы:
- Нет regression-теста на stale race в `TopicsCatalogCubit`.
- Нет regression/perf-теста на rebuild storm в primary source detail.
- Нет теста, фиксирующего отсутствие side-effects в `build`.
- Нет архитектурного теста на immutable ownership для `PrimarySource` в state-цепочке.

---

## 11) Docs Drift Review

### Drift D1
- Current code behavior:
  - `PrimarySource` mutable (`showMore`) и мутируется из UI.
- Documented expectation:
  - State contracts described as immutable (`state_management_matrix.*`, overview).
- Assessment: **likely code issue**
- Recommendation: **change code** (убрать mutable UI-state из модели).

### Drift D2
- Current code behavior:
  - Detail orchestration распределена между orchestration cubit + coordinator + controller + value notifier.
- Documented expectation:
  - Orchestration фокусируется на `PrimarySourceDetailOrchestrationCubit`.
- Assessment: **needs architectural decision**
- Recommendation: **decide explicitly** (закрепить целевую модель и обновить код/доки консистентно).

### Drift D3
- Current code behavior:
  - Поля `imageShown/showDescription` почти не участвуют в UI decisions.
- Documented expectation:
  - Matrix фиксирует их как активную часть contract.
- Assessment: **likely docs issue** (или code leftover; требуется верификация)
- Recommendation: **update docs** после cleanup/решения.

### Drift D4
- Current code behavior:
  - `TopicsCatalogCubit` без stale guard.
- Documented expectation:
  - Overview декларирует stale protection (`LatestRequestGuard`) как архитектурный принцип.
- Assessment: **likely code issue**
- Recommendation: **change code** + добавить regression tests.

### Drift D5
- Current code behavior:
  - Side effects внутри `build` на detail screen.
- Documented expectation:
  - Документация напрямую не формализует запрет.
- Assessment: **acceptable divergence** (временно), но плохая практика.
- Recommendation: **change code** для предсказуемости.

---
## Реестр проблем (строгий формат)

### SM-01
- severity: `critical`
- category: `ui-integration`
- path:
  - `lib/features/primary_sources/presentation/screens/primary_source_screen.dart:849`
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart:154`
  - `lib/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart:63`
- issue: Широкие подписки на целые state-срезы + частые viewport emits приводят к полному rebuild detail screen.
- why it matters: Риск jank/lag на масштабировании и панорамировании, особенно на web/mobile web.
- recommended action: Сузить подписки до минимальных селекторов, вынести hot-зоны в локальные builders/selectors, добавить dedup/throttle для transform updates.
- confidence: `high`
- docs relevance: `docs unclear`

### SM-02
- severity: `major`
- category: `async-flow`
- path:
  - `lib/features/topics/presentation/bloc/topics_catalog_cubit.dart:30`
- issue: `TopicsCatalogCubit` не защищен от stale async responses.
- why it matters: Быстрые переключения языка могут завершаться неконсистентным state (старый запрос перетрет новый).
- recommended action: Добавить `LatestRequestGuard` или request token + stale checks перед `emit`.
- confidence: `high`
- docs relevance: `diverges from docs`

### SM-03
- severity: `major`
- category: `state-contract`
- path:
  - `lib/shared/models/primary_source.dart:31`
  - `lib/features/primary_sources/presentation/widgets/source_item.dart:124`
- issue: Mutable UI-state (`showMore`) хранится в доменной модели и мутируется из виджета.
- why it matters: Нарушает immutability/source-of-truth; усложняет предсказуемость и тестирование.
- recommended action: Убрать mutable поле из модели; перенести expand/collapse state в cubit (или в локальный ephemeral state без мутации модели).
- confidence: `high`
- docs relevance: `diverges from docs`

### SM-04
- severity: `major`
- category: `side-effects`
- path:
  - `lib/features/primary_sources/presentation/screens/primary_source_screen.dart:142`
  - `lib/features/primary_sources/presentation/widgets/image_preview.dart:308`
- issue: Side effects запускаются из `build`.
- why it matters: Возможны повторные вызовы, скрытые циклы и сложные для отладки temporal bugs.
- recommended action: Перенести side effects в `BlocListener`, `initState`, `didChangeDependencies`, post-frame callbacks с явной идемпотентностью.
- confidence: `high`
- docs relevance: `docs unclear`

### SM-05
- severity: `major`
- category: `cubit-design`
- path:
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart:18`
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart:23`
- issue: Гибрид orchestration: пустой state cubit + mutable coordinator/controller/notifier.
- why it matters: Размывает ownership, увеличивает сложность сопровождения и порог входа.
- recommended action: Принять архитектурное решение: либо усилить orchestration cubit как единую точку координации, либо зафиксировать coordinator как минимальный adapter и сократить его ответственность.
- confidence: `medium`
- docs relevance: `diverges from docs`

### SM-06
- severity: `major`
- category: `lifecycle`
- path:
  - `lib/features/about/presentation/bloc/about_cubit.dart:26`
  - `lib/features/settings/presentation/bloc/settings_cubit.dart:15`
  - `lib/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart:18`
- issue: После `await` есть `emit` без системной проверки `isClosed`.
- why it matters: Потенциальные `emit after close` ошибки при быстрых переходах/закрытии экрана.
- recommended action: Ввести единый async safety-паттерн (`if (isClosed) return;` / request guard) для всех async cubits.
- confidence: `medium`
- docs relevance: `docs unclear`

### SM-07
- severity: `major`
- category: `state-contract`
- path:
  - `lib/features/about/presentation/bloc/about_state.dart`
  - `lib/features/settings/presentation/bloc/settings_state.dart`
  - `lib/features/topics/presentation/bloc/topics_catalog_state.dart`
  - `lib/features/primary_sources/presentation/bloc/*_state.dart`
  - `lib/shared/models/zoom_status.dart`
- issue: Нет консистентного value equality для state/model классов.
- why it matters: Шумовые rebuild’ы, сложнее контролировать diff-обновления и писать точные тесты переходов.
- recommended action: Стандартизовать equality (`Equatable` или ручные `==/hashCode`) для state contracts и часто сравниваемых value-объектов.
- confidence: `high`
- docs relevance: `docs unclear`

### SM-08
- severity: `minor`
- category: `ui-integration`
- path:
  - `lib/features/about/presentation/screens/about_screen.dart:61`
- issue: `context.select((cubit) => cubit.state.settings.toMap())` создает лишние rebuild.
- why it matters: Ненужная перерисовка AboutScreen при любом изменении map identity.
- recommended action: Селектить только требуемые scalar поля (язык/тема/размер шрифта), без `toMap()`.
- confidence: `high`
- docs relevance: `docs unclear`

### SM-09
- severity: `minor`
- category: `legacy`
- path:
  - `lib/features/primary_sources/presentation/bloc/primary_source_image_state.dart:26`
  - `lib/features/primary_sources/presentation/bloc/primary_source_description_state.dart:25`
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart:51`
- issue: `imageShown`/`showDescription` выглядят как weakly-used/leftover state поля.
- why it matters: Усложняет модель состояния без явной runtime пользы.
- recommended action: Провести cleanup: удалить или реинтегрировать в UI с явным назначением.
- confidence: `medium`
- docs relevance: `docs likely outdated`

### SM-10
- severity: `minor`
- category: `scope`
- path:
  - `lib/features/primary_sources/presentation/screens/primary_source_screen.dart:836`
  - `lib/features/topics/presentation/bloc/topic_content_cubit.dart:19`
- issue: Часть зависимостей создается напрямую в presentation/cubit constructors, обходя централизованный DI.
- why it matters: Снижается консистентность provisioning и тестируемость через DI graph.
- recommended action: Упорядочить фабрики/DI для screen-level зависимостей (без излишней глобализации).
- confidence: `medium`
- docs relevance: `matches docs`

### SM-11
- severity: `major`
- category: `testing`
- path:
  - `test/features/topics/presentation/bloc/topics_catalog_cubit_test.dart`
- issue: Нет regression теста на stale race для `TopicsCatalogCubit`.
- why it matters: Высокий риск повторных регрессий после async-изменений.
- recommended action: Добавить тест “старый запрос не перетирает новый state”.
- confidence: `high`
- docs relevance: `matches docs`

### SM-12
- severity: `major`
- category: `testing`
- path:
  - `test/widget/primary_sources/detail/primary_source_detail_widgets_test.dart`
  - `test/features/primary_sources/presentation/bloc/primary_source_viewport_cubit_test.dart`
- issue: Нет regression/perf тестов на rebuild pressure в detail-flow.
- why it matters: Критичный runtime риск не закрыт тестами.
- recommended action: Добавить widget regression тесты на ограничение rebuild-trigger и корректный listener/builder split.
- confidence: `medium`
- docs relevance: `matches docs`

### SM-13
- severity: `minor`
- category: `testing`
- path:
  - `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`
  - `lib/features/primary_sources/presentation/widgets/image_preview.dart`
- issue: Нет тестов, гарантирующих отсутствие повторных side effects из `build`.
- why it matters: Скрытые циклы и re-entrant поведение могут вернуться незаметно.
- recommended action: Добавить widget tests с проверкой количества вызовов side-effect handlers.
- confidence: `medium`
- docs relevance: `docs unclear`

### SM-14
- severity: `major`
- category: `state-ownership`
- path:
  - `lib/features/primary_sources/presentation/bloc/primary_source_session_state.dart:25`
  - `lib/shared/models/primary_source.dart:31`
- issue: `SessionState` хранит mutable `PrimarySource`, что делает ownership deep-нестрогим.
- why it matters: Возможны обходные мутации “в обход state manager”.
- recommended action: Зафиксировать `PrimarySource` как immutable value object для runtime state или хранить в state только стабильный immutable projection.
- confidence: `medium`
- docs relevance: `diverges from docs`

### SM-15
- severity: `major`
- category: `docs-drift`
- path:
  - `docs/ru/architecture/overview.ru.md:17`
  - `docs/ru/architecture/state_management_matrix.ru.md:31`
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart`
  - `lib/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart`
- issue: Доки описывают orchestration как cubit-центричную, фактическая реализация гибридная.
- why it matters: Архитектурные решения неочевидны для разработчиков и ревьюеров.
- recommended action: Сначала архитектурное решение, затем синхронное обновление кода/доков.
- confidence: `high`
- docs relevance: `diverges from docs`

### SM-16
- severity: `minor`
- category: `docs-drift`
- path:
  - `docs/ru/architecture/state_management_matrix.ru.md:27`
  - `docs/ru/architecture/state_management_matrix.ru.md:29`
  - `lib/features/primary_sources/presentation/bloc/primary_source_image_state.dart`
  - `lib/features/primary_sources/presentation/bloc/primary_source_description_state.dart`
- issue: Matrix содержит поля detail state, чья фактическая runtime-роль минимальна или неочевидна.
- why it matters: Документация перестает быть полезной как operational карта.
- recommended action: После cleanup обновить matrix до фактических owners/контрактов.
- confidence: `medium`
- docs relevance: `docs likely outdated`

---
## Prioritized Remediation Plan (чеклист исполнения)

### Step 1 — Архитектурное решение по detail orchestration
- [x] Цель: Зафиксировать целевую модель ownership в primary source detail.
- [x] Почему приоритет: Без этого последующие правки будут фрагментированными.
- [x] Конкретные действия:
- [x] Зафиксировать решение: `single orchestration cubit` vs `coordinator as adapter`.
- [x] Определить, какие side effects разрешены вне cubit (если разрешены).
- [x] Принятое правило side effects:
- [x] В `build` side effects запрещены.
- [x] Разрешены только локальные UI-эфемерные `setState` (анимация/жесты/hover/scroll UI).
- [x] Бизнесовые и cross-slice side effects: только через cubit/listener/post-frame с идемпотентной защитой.
- [ ] Затрагиваемые файлы/папки: `lib/features/primary_sources/presentation/bloc/`, `docs/ru|en/architecture/*` (выполнено частично: `lib` обновлен, `docs` и явное архитектурное правило pending).
- [x] Риск: Средний (неверное решение может закрепить долг).
- [x] Ожидаемый результат: Ясные ownership boundaries и единый подход для команды.
- [x] Dependency on previous steps: Нет.
- [x] How to validate (оперативно): `flutter analyze` + целевые detail tests passed.
- [ ] How to validate (финально): Архитектурный чек ревью + согласованный ADR/decision record.

### Step 2 — Устранить критичный rebuild hotspot
- [ ] Цель: Снизить rebuild pressure в detail screen до предсказуемого уровня.
- [x] Почему приоритет: Это текущий runtime риск №1.
- [x] Конкретные действия:
- [x] Заменить broad `context.select(... => cubit.state)` на селекторы по точечным полям (hot-path viewport projection вместо полного state).
- [x] Разделить build-дерево на мелкие `BlocSelector/BlocBuilder` горячих зон (локальные `Builder + context.select` для toolbar/body/image/description зон).
- [x] В `updateTransform` добавить защиту от шумовых `emit` при отсутствии изменений.
- [x] Затрагиваемые файлы/папки:
- [x] `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`
- [x] `lib/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_viewport_state.dart` (не потребовалось для текущего пакета).
- [x] Риск: Средний (можно случайно сломать реактивность части UI).
- [ ] Ожидаемый результат: Плавный zoom/pan без полного rebuild экрана (manual smoke/perf pending).
- [x] Dependency on previous steps: Step 1 желателен, но не обязателен.
- [x] How to validate (оперативно): `flutter analyze` + detail widget/unit tests pass.
- [ ] How to validate (финально): Widget/perf regression test + manual profiling на web/mobile web.

### Step 3 — Убрать side effects из build
- [ ] Цель: Сделать UI flow детерминированным и без re-entrant side effects.
- [ ] Почему приоритет: Прямо влияет на предсказуемость и дебаг.
- [ ] Конкретные действия:
- [ ] Перенести `changeSelectedPage/showCommonInfo` из build в listener/init lifecycle.
- [ ] Перенести `onRestorePositionAndScale` из `ImagePreview.build` в безопасный lifecycle trigger.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`
- [ ] `lib/features/primary_sources/presentation/widgets/image_preview.dart`
- [ ] Риск: Средний.
- [ ] Ожидаемый результат: Side effects запускаются контролируемо и ровно один раз в нужных сценариях.
- [ ] Dependency on previous steps: После Step 2 проще проверить.
- [ ] How to validate: Widget tests на количество вызовов handlers + smoke navigation.

### Step 4 — Исправить ownership/immutability модели PrimarySource
- [ ] Цель: Убрать mutable UI-state из доменной модели.
- [ ] Почему приоритет: Это архитектурная гигиена source-of-truth.
- [ ] Конкретные действия:
- [ ] Удалить `showMore` из `PrimarySource`.
- [ ] Перенести expand/collapse состояние в отдельный UI owner (предпочтительно cubit-срез списка).
- [ ] Убрать мутацию `widget.source.showMore = ...` из `SourceItemWidget`.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/shared/models/primary_source.dart`
- [ ] `lib/features/primary_sources/presentation/widgets/source_item.dart`
- [ ] `lib/features/primary_sources/presentation/screens/primary_sources_screen.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/` (если вводится UI cubit)
- [ ] Риск: Средний.
- [ ] Ожидаемый результат: Immutable контракт, прозрачный owner expand-state.
- [ ] Dependency on previous steps: Независим.
- [ ] How to validate: Unit/widget tests на expand/collapse + отсутствие model mutation.

### Step 5 — Добавить stale protection в TopicsCatalogCubit
- [ ] Цель: Защитить catalog flow от race conditions.
- [ ] Почему приоритет: Это прямой async correctness риск.
- [ ] Конкретные действия:
- [ ] Добавить request token/`LatestRequestGuard` в `loadForLanguage`.
- [ ] Добавить проверки перед `emit` после каждого await.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/features/topics/presentation/bloc/topics_catalog_cubit.dart`
- [ ] `test/features/topics/presentation/bloc/topics_catalog_cubit_test.dart`
- [ ] Риск: Низкий.
- [ ] Ожидаемый результат: Старые запросы не перезаписывают новый state.
- [ ] Dependency on previous steps: Нет.
- [ ] How to validate: Новый regression test “ignores stale result”.

### Step 6 — Стандартизировать lifecycle safety в async cubits
- [ ] Цель: Свести к нулю `emit after close` риски.
- [ ] Почему приоритет: Влияет на надежность при быстрых переходах/dispose.
- [ ] Конкретные действия:
- [ ] Ввести общий шаблон `if (isClosed) return;` после await.
- [ ] Применить в `AboutCubit`, `SettingsCubit`, `PrimarySourcePageSettingsCubit` и других async местах.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/features/about/presentation/bloc/about_cubit.dart`
- [ ] `lib/features/settings/presentation/bloc/settings_cubit.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart`
- [ ] Риск: Низкий.
- [ ] Ожидаемый результат: Устойчивый lifecycle при повторной навигации.
- [ ] Dependency on previous steps: Нет.
- [ ] How to validate: Unit tests “close before async completes”.

### Step 7 — Усилить state contracts (equality + шум emit)
- [ ] Цель: Снизить churn и сделать переходы состояния прозрачнее.
- [ ] Почему приоритет: Основа для производительности и предсказуемости.
- [ ] Конкретные действия:
- [ ] Ввести единый policy equality для state/value-классов (`Equatable` или `==/hashCode`).
- [ ] Добавить dedup checks в часто дергаемые обновления (viewport/zoom status).
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/features/**/presentation/bloc/*_state.dart`
- [ ] `lib/shared/models/zoom_status.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart`
- [ ] Риск: Средний (можно случайно поменять семантику сравнений).
- [ ] Ожидаемый результат: Меньше лишних rebuild, лучше тестируемость state transitions.
- [ ] Dependency on previous steps: Рекомендуется после Step 2.
- [ ] How to validate: State unit tests + widget rebuild assertions.

### Step 8 — Cleanup legacy state leftovers
- [ ] Цель: Упростить модель detail-state без потери функциональности.
- [ ] Почему приоритет: Уменьшает архитектурный шум и когнитивную нагрузку.
- [ ] Конкретные действия:
- [ ] Проверить runtime необходимость `imageShown/showDescription`.
- [ ] Удалить неиспользуемые поля/методы или реально встроить в UI flow.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_image_state.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_description_state.dart`
- [ ] `lib/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart`
- [ ] Риск: Низкий/средний.
- [ ] Ожидаемый результат: Более компактные и ясные state contracts.
- [ ] Dependency on previous steps: Лучше после Step 1.
- [ ] How to validate: Search no-unused + full test suite pass.

### Step 9 — Привести provisioning к единому стилю DI
- [ ] Цель: Повысить консистентность создания зависимостей.
- [ ] Почему приоритет: Упростит поддержку, подмену зависимостей и тесты.
- [ ] Конкретные действия:
- [ ] Убрать из UI прямое создание репозиториев/оркестраторов там, где это мешает DI.
- [ ] Выделить screen-level factories/registrations в согласованный слой.
- [ ] Затрагиваемые файлы/папки:
- [ ] `lib/app/di/app_di.dart`
- [ ] `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`
- [ ] `lib/features/topics/presentation/bloc/topic_content_cubit.dart` (опционально)
- [ ] Риск: Средний.
- [ ] Ожидаемый результат: Предсказуемый provisioning без скрытых new().
- [ ] Dependency on previous steps: Желательно после Step 1.
- [ ] How to validate: Unit/widget tests с простым mock/fake injection.

### Step 10 — Закрыть тестовый и документационный контур
- [ ] Цель: Зафиксировать изменения в тестах и RU/EN docs синхронно.
- [ ] Почему приоритет: Защита от повторного drift.
- [ ] Конкретные действия:
- [ ] Добавить missing regression tests (race/rebuild/side-effects/lifecycle).
- [ ] Обновить `overview`, `module-boundaries`, `state_management_matrix`, `testing strategy` (RU+EN пары).
- [ ] Проверить `Doc-Version/Last-Updated/Source-Commit` в RU/EN парах.
- [ ] Затрагиваемые файлы/папки:
- [ ] `test/features/**`, `test/widget/**`
- [ ] `docs/ru/architecture/*.md`, `docs/en/architecture/*.md`
- [ ] `docs/ru/testing/strategy.ru.md`, `docs/en/testing/strategy.en.md`
- [ ] Риск: Низкий.
- [ ] Ожидаемый результат: Код/доки/тесты синхронны и проверяемы CI.
- [ ] Dependency on previous steps: После Step 1-9.
- [ ] How to validate:
- [ ] `dart run scripts/check_docs_sync.dart`
- [ ] `dart run scripts/check_forbidden_patterns.dart`
- [ ] `flutter analyze`
- [ ] `flutter test --exclude-tags widget`
- [ ] `flutter test --tags widget`

---

## Top 10 Most Important State Management Issues

1. `SM-01` — Critical rebuild hotspot в primary source detail.
2. `SM-02` — Нет stale guard в `TopicsCatalogCubit`.
3. `SM-03` — Mutable `PrimarySource.showMore` и мутация модели из UI.
4. `SM-04` — Side effects внутри `build`.
5. `SM-05` — Размытая orchestration модель detail-flow.
6. `SM-06` — Неполный lifecycle safety после `await`.
7. `SM-07` — Нет единого value equality policy для state/value classes.
8. `SM-14` — Deep ownership leak через mutable `source` в `SessionState`.
9. `SM-11` — Нет regression теста для stale race в topics catalog.
10. `SM-12` — Нет regression/perf теста на detail rebuild pressure.

---

## Top 10 Quick Wins

1. Заменить `settings.toMap()` селектор в `AboutScreen` на точечные поля.
2. Добавить stale guard в `TopicsCatalogCubit`.
3. Добавить `isClosed` checks после `await` в `AboutCubit` и `SettingsCubit`.
4. Убрать side effect `onRestorePositionAndScale()` из `ImagePreview.build`.
5. Убрать `changeSelectedPage/showCommonInfo` из `build` в detail screen.
6. Добавить dedup check перед `viewportCubit.updateTransform`.
7. Добавить unit regression “old request ignored” в `topics_catalog_cubit_test`.
8. Добавить widget test на side-effect call count для detail screen.
9. Удалить/реально задействовать `imageShown`.
10. Удалить mutable `showMore` из `PrimarySource`.

---

## Top 10 Risky Areas for Future Regressions

1. `PrimarySourceScreen` (подписки + orchestration + navigation).
2. `PrimarySourceDetailOrchestrationCubit` (debounce/timers/transform listener).
3. `PrimarySourceViewportCubit` (частые emits).
4. `ImagePreview` (сложный виджет + interaction-heavy logic).
5. `TopicsCatalogCubit` (language-driven async reload).
6. `SettingsCubit` (async persist under fast navigation).
7. `AboutCubit` (async load + screen dispose races).
8. Границы между cubit/coordinator/controller/notifier в detail flow.
9. Документационные контракты state matrix vs runtime code.
10. Тесты, где нет explicit regression на предыдущие реальные риски.

---

## Top 10 Docs/Code Drift Findings

1. Immutable expectation vs mutable `PrimarySource.showMore` (`likely code issue`).
2. Matrix/overview описывает orchestration cubit-центрично, реализация гибридная (`needs architectural decision`).
3. `imageShown/showDescription` задокументированы как активный контракт, runtime-роль слабая (`likely docs issue` + cleanup).
4. Overview подчеркивает stale protection, но `TopicsCatalogCubit` без guard (`likely code issue`).
5. Документация не отражает side-effect hotspots в build (`docs unclear`).
6. Документация не фиксирует policy по equality state-классов (`docs unclear`).
7. DI/provisioning style (screen-level new()) не описан как допустимый/запрещенный в деталях (`docs unclear`).
8. Глубина immutable ownership (`SessionState.source`) не формализована (`docs unclear`).
9. Role `PrimarySourceDetailCoordinator` как архитектурный элемент не явно зафиксирован в boundaries (`needs architectural decision`).
10. Testing strategy не перечисляет конкретные high-risk regression suites для detail performance/race (`likely docs issue`).

---

## Final Verdict on State Architecture Quality

Оценка: **6.8/10 (рабочая, но с заметным техническим долгом в detail-flow)**.

Вердикт:
- Архитектурный фундамент (Cubit-first, feature-first, базовые boundaries) — хороший.
- Для “полного порядка” требуются обязательные улучшения в:
  - predictability async (`TopicsCatalog`),
  - ownership/immutability (`PrimarySource`/detail state contracts),
  - производительности UI (rebuild hotspot),
  - фиксации архитектурного решения по orchestration detail-flow,
  - закрытии regression-тестами и синхронизации docs.

---

## Отдельный чеклист исполнения (короткая версия)

- [ ] Step 1: Архитектурное решение по detail orchestration (частично выполнен: решение + код + side-effects rule, осталось docs/ADR)
- [ ] Step 2: Устранить rebuild hotspot detail screen (частично выполнен: narrow subscriptions + split hot zones + dedup emits; ожидается ручной perf smoke/profiling)
- [ ] Step 3: Убрать side effects из build
- [ ] Step 4: Убрать mutable state из `PrimarySource`
- [ ] Step 5: Добавить stale guard в `TopicsCatalogCubit`
- [ ] Step 6: Привести async lifecycle safety к единому стандарту
- [ ] Step 7: Стандартизовать equality и dedup state updates
- [ ] Step 8: Очистить legacy state leftovers
- [ ] Step 9: Упорядочить DI/provisioning style
- [ ] Step 10: Закрыть тесты + синхронизировать RU/EN docs

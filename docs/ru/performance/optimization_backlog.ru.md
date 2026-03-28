# Бэклог оптимизации производительности (RU)

Версия документа: `1.0.0`  
Дата: `2026-03-15`  
Основание: performance-аудит проекта (full code review).

## Назначение
Этот документ — рабочий backlog задач по оптимизации производительности.  
Каждая задача оформлена отдельно, чтобы ее можно было брать в работу независимо.

## Как использовать
1. Выберите задачу по приоритету (`HIGH` -> `MED` -> `LOW`).
2. Оцените изменения и риски в PR.
3. После выполнения поменяйте чекбокс `- [ ]` на `- [x]`.
4. Добавьте ссылку на PR рядом с задачей (по желанию).

## Легенда
- `HIGH` — высокий приоритет, заметный эффект для пользователя.
- `MED` — важные улучшения без срочности `HIGH`.
- `LOW` — улучшения качества и масштабируемости.
- `profiling needed before change` — сначала профилирование, потом решение о внедрении.

---

## 1) Базовые метрики и контроль

- [ ] `PERF-001` (`HIGH`) Зафиксировать baseline-метрики startup (`first frame`, `time to interactive`) для Android, Windows, Web.
  Файлы/зоны: `lib/main.dart`, `lib/app/bootstrap/**`.
  Критерий готовности: есть таблица baseline-метрик в задаче/PR и повторяемый способ замера.

- [ ] `PERF-002` (`HIGH`) Зафиксировать baseline по экрану первоисточников: время загрузки списка, память, frame time при скролле.
  Файлы/зоны: `lib/features/primary_sources/**`.
  Критерий готовности: есть baseline с одинаковыми входными данными и устройствами.

- [ ] `PERF-003` (`MED`) Добавить шаблон perf-checklist в PR (замеры до/после для затронутых hot paths).
  Файлы/зоны: `.github/change_checklist.md` или отдельный шаблон PR.
  Критерий готовности: в каждом perf-PR есть раздел с замерами.

- [ ] `PERF-004` (`MED`) Добавить smoke-профилирование для critical flows (manual workflow).
  Файлы/зоны: `.github/workflows/integration_smoke.yml`, `integration_test/smoke/**`.
  Критерий готовности: есть отдельный workflow/джоб с целевыми perf-сценариями.

---

## 2) Startup и bootstrap

- [ ] `PERF-005` (`HIGH`) Перенести тяжелую инициализацию за первый кадр (ранний `runApp`, deferred warm-up).
  Файлы/зоны: `lib/main.dart`, `lib/app/bootstrap/app_bootstrap.dart`.
  Критерий готовности: `runApp` не блокируется полным bootstrap-пайплайном.

- [ ] `PERF-006` (`HIGH`) Разделить bootstrap на критический и некритический этапы.
  Файлы/зоны: `lib/app/bootstrap/app_bootstrap.dart`.
  Критерий готовности: настройки/минимальная навигация готовы сразу, фоновые инициализации догружаются позже.

- [ ] `PERF-007` (`HIGH`) Убрать network-зависимость из cold-start пути для native DB.
  Файлы/зоны: `lib/infra/db/connectors/native.dart`, `lib/infra/storage/file_sync_utils.dart`.
  Критерий готовности: приложение стартует с локальной БД без ожидания сервера.

- [ ] `PERF-008` (`MED`) Добавить timeout/backoff для удаленных вызовов `ServerManager` в startup/update путях.
  Файлы/зоны: `lib/infra/remote/supabase/server_manager.dart`, `lib/infra/storage/file_sync_utils.dart`.
  Критерий готовности: нет бесконечных/долгих зависаний при проблемной сети.

- [ ] `PERF-009` (`MED`) Оптимизировать web DB version sync (свести к легковесному version endpoint/manifest).
  Файлы/зоны: `lib/infra/db/connectors/web.dart`.
  Критерий готовности: уменьшено количество network-шагов до открытия БД на web.

- [ ] `PERF-010` (`MED`) Ленивая инициализация `primary_sources` gateway (по первому заходу в фичу).
  Файлы/зоны: `lib/infra/db/runtime/database_runtime.dart`, `lib/infra/db/runtime/gateways/primary_sources_database_gateway.dart`.
  Критерий готовности: heavy preload первоисточников не выполняется при старте без открытия экрана.

---

## 3) Data layer и кэширование (primary sources)

- [ ] `PERF-011` (`HIGH`) Ввести кэш результата `getAllSourcesSync()` с инвалидцией по языку/версии данных.
  Файлы/зоны: `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`.
  Критерий готовности: повторные вызовы не пересобирают полный граф моделей.

- [ ] `PERF-012` (`HIGH`) Разделить модели списка и деталей первоисточника.
  Файлы/зоны: `lib/features/primary_sources/data/**`, `lib/shared/models/**`, `lib/features/primary_sources/presentation/**`.
  Критерий готовности: список не тянет в память words/verses для всех источников.

- [ ] `PERF-013` (`HIGH`) Сделать lazy загрузку `previewBytes` (visible-first), а не для всех карточек сразу.
  Файлы/зоны: `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`, `lib/features/primary_sources/presentation/widgets/source_item.dart`.
  Критерий готовности: при первом открытии загружается только нужный подмножество превью.

- [ ] `PERF-014` (`MED`) Добавить индексированные lookup-структуры (`sourceId`, `pageName`) для reference navigation.
  Файлы/зоны: `lib/features/primary_sources/application/services/primary_source_reference_service.dart`, `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`.
  Критерий готовности: `findSourceById` не требует полного повторного обхода тяжелого графа.

- [ ] `PERF-015` (`MED`) Уменьшить churn копирования моделей при подгрузке preview (`_copyWithPreviewBytes`).
  Файлы/зоны: `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`.
  Критерий готовности: исключено массовое клонирование полного `PrimarySource` для update preview.

- [ ] `PERF-016` (`MED`) Оптимизировать JSON decode пайплайн (rectangles/contours/int lists) через memo/предподготовку.
  Файлы/зоны: `lib/features/primary_sources/data/repositories/primary_sources_db_repository.dart`.
  Критерий готовности: декодирование не повторяется без необходимости.

---

## 4) State-management и перезагрузки экранов

- [ ] `PERF-017` (`HIGH`) Исключить повторную полную загрузку `PrimarySourcesCubit` при каждом заходе на экран.
  Файлы/зоны: `lib/features/primary_sources/presentation/screens/primary_sources_screen.dart`, `lib/features/primary_sources/presentation/bloc/primary_sources_cubit.dart`.
  Критерий готовности: повторный вход использует актуальный кэш, reload только по явному trigger.

- [ ] `PERF-018` (`HIGH`) Не очищать списки на `isLoading=true` при refresh (keep previous data).
  Файлы/зоны: `lib/features/primary_sources/presentation/bloc/primary_sources_cubit.dart`.
  Критерий готовности: отсутствует визуальный flicker и лишний state churn.

- [ ] `PERF-019` (`MED`) Ввести `isRefreshing`/`lastLoadedAt` в state для предсказуемой политики reload.
  Файлы/зоны: `lib/features/primary_sources/presentation/bloc/primary_sources_state.dart`, `primary_sources_cubit.dart`.
  Критерий готовности: reload-policy формализована и покрыта тестами.

- [ ] `PERF-020` (`MED`) Провести аудит широких подписок `context.select` в detail screen и локализовать rebuild-области.
  Файлы/зоны: `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`.
  Критерий готовности: root `build` не подписан на несколько независимых slices одновременно.

---

## 5) UI rendering, rebuild и скролл

- [ ] `PERF-021` (`HIGH`) Убрать тяжелый расчет ширины dropdown из каждого `build` detail screen (memoize `calcPagesListWidth`).
  Файлы/зоны: `lib/features/primary_sources/presentation/screens/primary_source_screen.dart`.
  Критерий готовности: `TextPainter.layout()` не выполняется на каждом rebuild экрана.

- [ ] `PERF-022` (`HIGH`) Удалить/переписать custom drag-scroll с `setState` на каждом pointer move.
  Файлы/зоны: `main_screen.dart`, `topic_screen.dart`, `about_screen.dart`, `primary_sources_screen.dart`, `drawer_content.dart`.
  Критерий готовности: скролл не вызывает full subtree rebuild на каждом движении.

- [ ] `PERF-023` (`MED`) Перевести `TopicList` на lazy rendering (`ListView.builder`/slivers).
  Файлы/зоны: `lib/features/topics/presentation/widgets/topic_list.dart`, `lib/features/topics/presentation/screens/main_screen.dart`.
  Критерий готовности: масштабируемость списка тем по памяти/кадрам при росте данных.

- [ ] `PERF-024` (`MED`) Оптимизировать render path About widgets с большими `Column` + `FutureBuilder`.
  Файлы/зоны: `lib/features/about/presentation/screens/about_screen.dart`, `lib/features/about/presentation/widgets/*.dart`.
  Критерий готовности: меньше layout cost и стабильный скролл на слабых устройствах.

- [ ] `PERF-025` (`MED`) Убрать `TapGestureRecognizer()` из `build` Stateless виджетов.
  Файлы/зоны: `source_item.dart`, `institution_card.dart`, `primary_source_attributes_footer.dart`.
  Критерий готовности: recognizer lifecycle управляется корректно, без лишних аллокаций.

---

## 6) Image pipeline (primary source detail)

- [ ] `PERF-026` (`HIGH`) Вынести `_createModifiedRegionImage` в isolate/`compute`.
  Файлы/зоны: `lib/features/primary_sources/presentation/widgets/image_preview.dart`.
  Критерий готовности: тяжелая pixel-processing не выполняется на UI isolate.

- [ ] `PERF-027` (`HIGH`) Кэшировать decoded RGBA для pipette mode.
  Файлы/зоны: `image_preview.dart`.
  Критерий готовности: повторные тапы в pipette не декодируют изображение заново.

- [ ] `PERF-028` (`MED`) Мемоизировать геометрию overlays (`word separators`, `strong labels`) по данным страницы.
  Файлы/зоны: `image_preview.dart`.
  Критерий готовности: `_prepareWordSeparators`/`_preparStrongNumbers` не пересчитываются без изменения входных данных.

- [ ] `PERF-029` (`MED`) Предрассчитать hitboxes для strong labels.
  Файлы/зоны: `image_preview.dart`.
  Критерий готовности: нет `TextPainter.layout()` по всем labels в каждом tap path.

- [ ] `PERF-030` (`MED`) Сделать debounce/throttle для частых apply color replacement по slider/tolerance.
  Файлы/зоны: `replace_color_dialog.dart`, `image_preview.dart`, orchestration cubit.
  Критерий готовности: при активном изменении слайдера нет jank и лишних перерасчетов.

- [ ] `PERF-031` (`LOW`, profiling needed before change) Оптимизировать `Image.memory` usage для крупных изображений (cacheWidth/cacheHeight или provider-level tuning).
  Файлы/зоны: `image_preview.dart`, `source_item.dart`, `topic_card.dart`.
  Критерий готовности: профилирование подтверждает снижение памяти/декодирования без деградации качества.

---

## 7) Async, I/O и конкурентность

- [ ] `PERF-032` (`MED`) Параллелизовать проверку локальной доступности страниц с ограничением конкуренции.
  Файлы/зоны: `lib/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart`.
  Критерий готовности: `detectLocalPageAvailability` не выполняется строго последовательно.

- [ ] `PERF-033` (`MED`) Добавить дедупликацию и TTL-кэш для повторных image download attempts при быстрых переключениях страниц.
  Файлы/зоны: `image_loading_orchestrator.dart`, `primary_source_image_cubit.dart`.
  Критерий готовности: при rapid navigation не дублируются идентичные загрузки.

- [ ] `PERF-034` (`MED`) Ввести явные timeout-границы для file update/check операций.
  Файлы/зоны: `file_sync_utils.dart`, `server_manager.dart`.
  Критерий готовности: каждая remote операция имеет ограничение по времени и fallback.

- [ ] `PERF-035` (`LOW`, profiling needed before change) Оптимизировать markdown image resource path (`FutureBuilder` per-image) через pre-resolve.
  Файлы/зоны: `lib/features/topics/presentation/screens/topic_screen.dart`, `topic_content_cubit.dart`.
  Критерий готовности: подтверждено профилированием, что pre-resolve снижает jitter при рендере.

---

## 8) Тесты и защита от regressions

- [ ] `PERF-036` (`HIGH`) Добавить тесты stale-race для `PrimarySourceImageCubit` (`latest request wins`).
  Файлы/зоны: `test/features/primary_sources/presentation/bloc/primary_source_image_cubit_test.dart`.
  Критерий готовности: старый async результат не перетирает новый.

- [ ] `PERF-037` (`HIGH`) Добавить тест `close before async completes` для `PrimarySourceImageCubit`.
  Файлы/зоны: `primary_source_image_cubit_test.dart`.
  Критерий готовности: нет state update после `close()`.

- [ ] `PERF-038` (`MED`) Добавить regression-тесты rapid switch/page reopen для detail image flow.
  Файлы/зоны: `test/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit_test.dart`, `test/widget/primary_sources/detail/**`.
  Критерий готовности: покрыты сценарии быстрых переключений и устойчивость side effects.

- [ ] `PERF-039` (`MED`) Добавить тесты на call-count для тяжелых side effects (color replace, pipette decode).
  Файлы/зоны: `test/widget/primary_sources/detail/image_preview_test.dart`.
  Критерий готовности: количество тяжелых вызовов под контролем при burst interactions.

- [ ] `PERF-040` (`MED`) Добавить widget regression на лишние rebuild при desktop/web drag-scroll.
  Файлы/зоны: `test/widget/topics/**`, `test/widget/about/**`, `test/widget/primary_sources/**`.
  Критерий готовности: есть тесты/индикаторы на отсутствие rebuild storm.

- [ ] `PERF-041` (`LOW`) Добавить lightweight perf benchmark script для локального прогона hot paths.
  Файлы/зоны: `scripts/**`.
  Критерий готовности: один командный сценарий запуска замеров с унифицированным выводом.

---

## 9) Legacy cleanup и архитектурные решения

- [ ] `PERF-042` (`MED`) Утвердить целевой контракт: `Coordinator` + `OrchestrationCubit` или только один orchestration слой.
  Файлы/зоны: `primary_source_detail_coordinator.dart`, `primary_source_detail_orchestration_cubit.dart`.
  Критерий готовности: принято и задокументировано единое архитектурное решение.

- [ ] `PERF-043` (`MED`) Централизовать и переиспользовать scroll-behavior для desktop/web.
  Файлы/зоны: `lib/shared/ui/**` + экраны с drag-scroll.
  Критерий готовности: нет копипасты однотипного drag logic в нескольких экранах.

- [ ] `PERF-044` (`LOW`) Документировать startup/performance architecture (фактический runtime-путь и ограничения).
  Файлы/зоны: `docs/ru/architecture/**` (и EN twin только если меняются утверждения парных документов).
  Критерий готовности: docs отражают реальный код после оптимизаций.

---

## Рекомендуемый порядок на следующую версию

1. `PERF-001`, `PERF-005`, `PERF-007`, `PERF-011`, `PERF-012`.
2. `PERF-013`, `PERF-017`, `PERF-018`, `PERF-021`, `PERF-022`, `PERF-026`, `PERF-027`.
3. `PERF-036`, `PERF-037`, `PERF-038`.
4. Остальные `MED/LOW` по ресурсу команды.

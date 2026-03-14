# Residual Architecture Debt Backlog (RU)

Doc-Version: `0.1.3`  
Last-Updated: `2026-03-14`  
Source-Commit: `working-tree`

## 1. Purpose
Зафиксировать остаточный архитектурный долг после завершения Phase 5 и определить приоритизированный, поэтапный план его закрытия без полного переписывания проекта.

## 2. Review Snapshot (2026-03-14)
- `shared/utils/common.dart` остается глобальным barrel и импортируется в `36` runtime/test файлах.
- Крупные узлы `primary_sources` presentation:
  - `primary_source_screen.dart` - `927` строк;
  - `image_preview.dart` - `1142` строки;
  - `primary_source_toolbar.dart` - `1079` строк;
  - `primary_source_view_model.dart` - `472` строки.
- `deprecated_member_use` suppressions вне generated scope устранены (`rg "deprecated_member_use" lib` -> `0` matches).
- `DBManager` сведен к runtime/composition роли; feature-level DB кэши вынесены в domain-specific gateways (`articles`, `lexicon`, `primary_sources`).

## 3. Prioritized Backlog

| ID | Priority | Debt item | Evidence | Target action | Exit criteria |
|---|---|---|---|---|---|
| `RAD-01` | P1 | Декомпозировать UI-монолиты `primary_sources` detail | Крупные файлы: `primary_source_screen.dart`, `image_preview.dart`, `primary_source_toolbar.dart` | Разделить на меньшие widgets/flows по зонам ответственности (navigation shell, image canvas, description panel, toolbar actions) | Нет presentation-файлов detail-scope более `700` строк, ключевые поддеревья покрыты widget-тестами |
| `RAD-02` | P1 | Убрать концентрацию orchestration в `PrimarySourceViewModel` | `primary_source_view_model.dart` совмещает lifecycle, routing callbacks и image/viewport orchestration | Перенести lifecycle и orchestration в выделенный coordinator/use-case слой и сократить surface VM | VM больше не владеет lifecycle-флагами cubit и ручной цепочкой dispose |
| `RAD-03` | P1 | Удалить глобальный barrel `shared/utils/common.dart` | `36` импортов через разные слои (`app/core/infra/features/shared`) | Заменить использование barrel на точечные импорты (`core/logging`, `shared/ui/dialogs`, `core/platform` и т.д.), затем удалить barrel | `rg "shared/utils/common.dart" lib test` -> `0` matches |
| `RAD-07` | P2 | Нормализовать терминологию в master architecture docs | После массовой терминологической замены были зафиксированы дефектные токены | Очистить master roadmap-документы от артефактов и зафиксировать единый glossary | Поиск по известным дефектным токенам в `docs/architecture` не возвращает совпадений |

## 4. Backlog Governance
- Пересматривать backlog при каждом значимом архитектурном изменении (или минимум раз в релизный цикл).
- Любой новый пункт architecture debt должен содержать:
  - измеримый evidence;
  - целевой owner scope;
  - явный exit criteria.
- Закрытые пункты фиксируются в migration journal соответствующей фазы.

## 5. Recently Closed
- `2026-03-14`: закрыт `RAD-06` — suppressions `deprecated_member_use` удалены из runtime-кода; `file_downloader_web` переведен на `package:web`, `WidgetsBinding.instance.window` заменен на `PlatformDispatcher.instance.implicitView`, `rg "deprecated_member_use" lib` возвращает `0` совпадений.
- `2026-03-14`: закрыт `RAD-05` — `integration_test/smoke` расширен до `5` сценариев (`about`, `download`, `settings -> about -> download`, `primary_sources` navigation, `settings -> topics` language sync), manual-triggered policy сохранена (`workflow_dispatch`).
- `2026-03-14`: закрыт `RAD-04` — декомпозиция `DBManager` завершена, runtime слой оставлен composition-only, feature-level кэши перенесены в domain-specific gateways.

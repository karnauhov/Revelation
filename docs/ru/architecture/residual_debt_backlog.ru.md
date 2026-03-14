# Residual Architecture Debt Backlog (RU)

Doc-Version: `0.1.0`  
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
- В platform/runtime коде остается `4` suppression для `deprecated_member_use`.
- `DBManager` уже ограничен infra runtime usage, но продолжает хранить агрегированные кэши с пересечением ответственностей.

## 3. Prioritized Backlog

| ID | Priority | Debt item | Evidence | Target action | Exit criteria |
|---|---|---|---|---|---|
| `RAD-01` | P1 | Декомпозировать UI-монолиты `primary_sources` detail | Крупные файлы: `primary_source_screen.dart`, `image_preview.dart`, `primary_source_toolbar.dart` | Разделить на меньшие widgets/flows по зонам ответственности (navigation shell, image canvas, description panel, toolbar actions) | Нет presentation-файлов detail-scope более `700` строк, ключевые поддеревья покрыты widget-тестами |
| `RAD-02` | P1 | Убрать концентрацию orchestration в `PrimarySourceViewModel` | `primary_source_view_model.dart` совмещает lifecycle, routing callbacks и image/viewport orchestration | Перенести lifecycle и orchestration в выделенный coordinator/use-case слой и сократить surface VM | VM больше не владеет lifecycle-флагами cubit и ручной цепочкой dispose |
| `RAD-03` | P1 | Удалить глобальный barrel `shared/utils/common.dart` | `36` импортов через разные слои (`app/core/infra/features/shared`) | Заменить использование barrel на точечные импорты (`core/logging`, `shared/ui/dialogs`, `core/platform` и т.д.), затем удалить barrel | `rg "shared/utils/common.dart" lib test` -> `0` matches |
| `RAD-04` | P1 | Продолжить декомпозицию `DBManager` в domain-specific data gateways | `DBManager` сохраняет агрегированные table caches и смешанные read API | Выделить целевые gateways/data-sources (`articles`, `lexicon`, `primary_sources`) и упростить роль runtime adapter | `DBManager` не содержит feature-level aggregate caches либо сведен к composition-only adapter |
| `RAD-05` | P2 | Расширить integration smoke coverage для критичных фич | Текущий smoke-suite ограничен выборочными ручными сценариями | Добавить smoke-сценарии для `about`, `download` и минимум одного cross-feature navigation flow | `integration_test/smoke` покрывает минимум `4` сценария и остается manual-triggered |
| `RAD-06` | P2 | Убрать `deprecated_member_use` suppressions вне generated scope | `deprecated_member_use` встречается в `core/platform`, `core/diagnostics`, `shared/utils/links_utils.dart` | Перейти на не-deprecated API и удалить suppressions | `rg "deprecated_member_use" lib` возвращает только допустимые generated-исключения |
| `RAD-07` | P2 | Нормализовать терминологию в master architecture docs | После массовой терминологической замены были зафиксированы дефектные токены | Очистить master roadmap-документы от артефактов и зафиксировать единый glossary | Поиск по известным дефектным токенам в `docs/architecture` не возвращает совпадений |

## 4. Backlog Governance
- Пересматривать backlog при каждом значимом архитектурном изменении (или минимум раз в релизный цикл).
- Любой новый пункт architecture debt должен содержать:
  - измеримый evidence;
  - целевой owner scope;
  - явный exit criteria.
- Закрытые пункты фиксируются в migration journal соответствующей фазы.

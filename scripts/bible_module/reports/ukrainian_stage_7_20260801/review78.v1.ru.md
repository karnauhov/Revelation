# 7.8 — B_review/manual workbench по development taxonomy

Doc-Version: `1.0.0`
Last-Updated: `2026-10-17`
Source-Commit: `working-tree`

Реализован отдельный локальный read-only workbench для **5782 существующих development error cases**: 4311 `B_review`, 1471 `C_unresolved` в 1257 стихах folds 0–2. Открыть [Manual review](http://127.0.0.1:8878); инструкция запуска и границы поведения — [README workbench](../../review78/README.ru.md).

Цель — сделать ошибки из [taxonomy](precision78_development_taxonomy.v1.ru.md) проверяемыми по полным группам и исходному evidence. Этот отобранный набор известных ошибок не представляет весь B_review и не является precision sample, новой annotation cohort или certification. Структурный NO_GO сохраняется: **A_auto=0**, новых принятых labels/overrides/production links нет.

## Что показывает интерфейс

- Точный immutable OH1988 `plain_text_nfc` со source mapping, печатными страницами, spans и SHA; текст не реконструируется соединением tokens.
- Полную frozen top-1 hyperedge с relation/null reason, всеми original/target IDs, source morphology/Strong и OH1988 scalar/byte spans.
- Каждую ближайшую historical gold-группу отдельно. Все nearest ties сохранены: 1839 cases имеют несколько ближайших групп; всего 7845 самостоятельных сравнений. Missing/extra endpoints вычислены отдельно на каждой стороне для каждой группы, без слияния альтернатив или pairwise expansion.
- Все конфликтующие eligible candidate hyperedges: 3503 references между case и полным конфликтующим ребром. Указано членство в сохранённых n-best. Доступны полные decompositions, constituent edges и остальные historical gold-группы стиха.
- Полное source evidence/provenance и dependency groups, generator IDs/input channels, raw input-row digests, source locators/commit/SHA, lemma/morphology и исходные evidence fields. Производные одного источника не становятся независимыми votes, legacy остаётся zero-vote.
- Отдельные compatible shared declarations по reciprocal frozen contract. В данной development error cohort таких references 0; поведение проверено синтетическими reciprocal/unilateral cases. Представительный corpus coverage для этого поведения не заявлен.

В packets сохранены 16366 intact eligible candidate edges, 17760 provenance rows и 6278 decompositions. 162 встреченных в этих стихах whole-deferred edges исключены до semantic presentation; отсутствующий candidate не превращается в NULL, registered deferrals не переоткрываются. Counts относятся к этому development packet universe, не ко всему OH1988 graph.

## Заметки и сохранность

Reviewer может скачать `review_note_draft`: reviewer, timestamp, rationale, complete semantic identity, nearest gold IDs, graph/gold/packet/build SHA. В текущей вкладке заметка восстанавливается после переключения case только при matching packet digest. Скачать нужные заметки следует до закрытия вкладки. Экспорт явно `is_label=false`, `is_override=false`, `production_acceptance=0`; сервер не принимает write requests. Ручные judgments в этой работе не выполнялись; сохранённый smoke note обозначен `[UI smoke]` и не является решением.

Защита stale data: startup source/input checks; при API access — hash index/manifest/packet; клиент связывает ответ с requested case и build SHA загруженного index. Latest-request guard и abort защищают быстрое переключение. Изменившийся пакет отклоняется, автоматической пересборки или переноса заметки на другой source нет. Сервер — `127.0.0.1`, GET/HEAD only, без внешних libraries/network services.

Frozen 7.4/7.6/7.7, precision78 source/locks/payload/reports, finalized gold v2, mask/folds и SHA-bound shared report/log остаются прежними. Код размещён отдельно в `scripts/bible_module/review78`. Прежние roadmap/alignment-plan docs также сохранены: они связаны SHA в completion precision78. Новая навигация добавлена append в [HANDOFF](HANDOFF.ru.md). Ни runtime/DB, ни schema, routes, localization, dependencies/release/changelog не менялись.

## Проверка и evidence chain

Автор `/root`; независимый reviewer и inventory writer сохраняют отдельные роли. UI проверен в живом IAB: class/taxonomy/text filtering, full groups, заметка при switching, download с полными source bindings; browser console errors 0. Screenshot — [проверенный экран](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/workbench.desktop.v1.jpg). Проверка mobile viewport отдельно не заявлена.

Независимый raw recount восстанавливает каждый packet и каждый case из frozen inputs; API и JS async/runtime проверяются отдельно от author tests. Мутации выполняются только на synthetic copies, frozen files не меняются. Независимость source families и новые precision claims не выводятся из этой инженерной проверки.

- [Protocol lock](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/protocol.v1.lock.json), [input lock](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/inputs.v1.lock.json), [source/runtime lock](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/source_runtime.v1.lock.json).
- [Build manifest и все verse packet SHA](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/build.v1/manifest.json), [index](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/build.v1/index.json).
- [Regression receipt](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/regression.v1.json). Python tests 530 (10 review78 +520 predecessors), Node tests 4; preflight stages 3 offline/4/5/6/7 PASS. UI-specific HTTP/mutation/async tests дополняют визуальную проверку.
- [Browser UI receipt и smoke draft](../../work/ukrainian_stage_7_20260801/session_review78_20261017_root_01/browser_ui.v1.json).
- [Независимый raw/API/runtime QC](../../work/ukrainian_stage_7_20260801/session_review78_20261017_independent_01/independent_review.v1.ru.md), [independent manifest](../../work/ukrainian_stage_7_20260801/session_review78_20261017_independent_01/independent_validation.v1.manifest.json).

Применён `.github/change_checklist.md`. Targeted Python/Node coverage соответствует новому offline tooling; Dart/Flutter runtime не менялся. Docs sync/forbidden patterns/navigation и финальные immutable/input/inventory checks фиксируются в completion и HANDOFF. Сохранённая source policy и gold не модифицируются ради прохождения проверок. Весь manual review 7.8 и этап 7 остаются открыты; это улучшение workbench, а не принятие links.

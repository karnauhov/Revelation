# Mat/Mark — ограниченное разрешение источников группы №2

Дата: 2026-10-03. Автор: `codex-group002-mat-mark-source-author-20261003`.
Роль: автор исследования, без авторства новых corrections или собственного независимого QC.

Результат: один разумно ограниченный цикл завершён для четырёх мест. **19 прежних
QC keys** (Mat15, Mark4) предлагаются как `deferred_strong_unassigned`; никаких новых
Strong links или consensus corrections не предлагается. **34 source-only atoms** Short
Ending — отдельная доказанная reference-vs-print absence, не 34 прежних QC uncertainties.
Только distinct reviewer/root может принять operational disposition и завершённость книг.

## Входы и provenance

До полного чтения work JSONL самостоятельно проверены exact SHA-256 и bytes входов по
inventory SHA `99b3cfd9328308e19e823eefdea5659d4ddcbf9fcd1f2a20fb53335cc9f7f29f`.
Receipt и exact preserved mutable report snapshots находятся в research session.
Mat batch040: 1358 final stable decisions, old QC0error/15uncertain.
Mark batch041: 1328 decisions, old QC0error/4uncertain. Frozen old artifacts сохраняются.
Mark metadata rebase inspected отдельно: repaired pass2 `941ffd00…4933d`, comparison
`6ed8cb5c…6477c`, adjudication `19cc5703…421a2`, QC `b40721a7…5483e`.
Это metadata-only chain с прежними reviewers и нулём semantic changes.

## Mat21.30

Exact [OH1988 leaf1220/printed1216](https://uk.wikisource.org/wiki/Сторінка:Ivan_Ohienko_Bible.djvu/1220)
проверен визуально: первый сын согласился и не пошёл; второй отказался, изменил
решение и пошёл; ответ21.31 — последний. Локальной source attribution note нет.
[Official SBLGNT edition apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/Matt.txt)
сопоставляет WH с этим реальным целостным эпизодом; доступный [WH21](https://ccel.org/ccel/westcott/gnt/files/matthew/matthew_21.htm)
дает отрицательный ответ и repent/go. Это подтверждает вариант, не создаёт occurrence IDs.

Нынешний [pinned TAGNT Mat21.30](https://github.com/STEPBible/STEPBible-Data/blob/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt)
содержит affirmative/not-go base и WH flags, но не полный стабильный alternate
negative/repent/go occurrence layer. «Я» нельзя привязать к ego другого ответа,
«не» — к отрицанию ухода, G2309/G3338 — молча перенести из21.29. «другого» допускает
лексическую альтернативу G2087/G1208. Отсутствие у совместимого alternate reading
нынешних baseслов не доказывает translation omission или addition.

Поэтому15exact keys, включая6source и9target nodes, deferred. Недостающий довод —
проверяемый alternate occurrence/span crosswalk и reciprocal accounting, а не обязательное
название исторического издания и не платная внешняя экспертиза. Кандидаты G2309/G3338,
G5305 и прочие в JSON являются гипотезами, не assigned Strongs.

## Mark1.2 и16.9

[Exact leaf1235/printed1231](https://uk.wikisource.org/wiki/Сторінка:Ivan_Ohienko_Bible.djvu/1235)
показывает «Як» и Isaiah reading, одновременно preserving continuation «перед Тобою».
[Official Mark apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/Mark.txt)
и pinned TAGNT действительно различают καθώς/G2531 и ὡς/G5613. Но украинский союз
не различает их, а соседний mixed critical/TR profile не доказывает его выбор.
Source-choice и «Як» —2deferred reciprocal nodes.

[Exact leaf1263/printed1259](https://uk.wikisource.org/wiki/Сторінка:Ivan_Ohienko_Bible.djvu/1263)
показывает Long Ending; footnote16.9 объясняет воскресенье. Спорное «із» соответствует
παρά/G3844 либо ἀπό/G575 при изгнании демонов. Official apparatus и TAGNT удостоверяют
вариант, но ни print, ни Sunday note, ни presence Long Ending не выбирают предлог.
Ещё2reciprocal nodes deferred. Это не спор о πρῶτον/πρώτῃ morphology.

## Short Ending Mark16.8

На exact print leaf1263 обычный16.8 переходит сразу к16.9–20, сноски Short Ending нет.
В [official SBL text](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/Mark.txt)
и TAGNT это bracketed source branch.34atoms TAGNT20–53 (включая amen) имеют
exact source IDs/Strong candidates, но нет украинских spans. Их прежние source-only
`source_text_not_rendered` nodes сохраняются как verified reference-vs-print absence;
новых target nodes нет. Не доказаны переводческий пропуск или историческая Vorlage.
Отдельная conservative consumer policy: не обучать translation_omission на отсутствии
этой apparatus branch и не назначать Strong несуществующему target. Это не требует
расширять19oldQCdeferrals до53 и не меняет frozen semantics.

## Сохранённые файлы и предел вывода

[Машинная disposition](../../work/ukrainian_stage_7_20260801/session_group2_20261003_mat_mark_research_01/Mat_Mark.source_disposition.v1.json)
содержит все53considered keys, точные target scalar/byte spans, source IDs, candidates,
final frozen semantics,19required deferrals,34source-status-only nodes, supersedes трёх
old shared issues, missing proof, attempted alternatives и optional follow-up.
[Source registry](../../work/ukrainian_stage_7_20260801/session_group2_20261003_mat_mark_research_01/source_evidence_registry.v1.json)
содержит downloaded evidence SHA/bytes и URL. Exact TAGNT download SHA совпадает
с frozen source; SBL Matt apparatus SHA также совпадает с прежним primary audit.
CCEL Python fetch был недоступен из-за expired TLS certificate, web WH21/Mark1 был
доступен; official pinned apparatus достаточен, ещё один research cycle не выполнялся.

Research self-check подтверждает IDs/counts/digests, но не является independent content QC.
Frozen QC verdicts uncertain сохраняются; новая evidence/disposition supersedes только
операционную research recommendation. Shared inventory/canonical manifests/root docs не
изменялись этим автором. OT39completed/38strict не переоткрывались. Stage8/SQLite,
production Strong, runtime, release, commit/push не выполнялись. Runtime/test/docs-sync
gates из change checklist здесь N/A: это isolated evidence authoring; нужные checks —
exact inputs, JSON/IDs/scalar-byte preservation, output locks и distinct review.

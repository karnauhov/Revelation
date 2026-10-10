# Группа № 7: выполненные corrections и границы corrector

Дата: 2026-10-10. Actual actor: `/root/corrector_group007`.

Выполнены девять exact semantic rows: семь в 1John.2.22/4.13 и два classifier-only rows в 2Pet.3.5/3.7. Existing `seal-correction` и `check-correction` PASS для обеих книг, exit 0. Четыре неизменённых reciprocal rows перепроверены. Остальные 3605 payloads трёх книг сохранены; frozen source selection, passes, adjudication и original QC не редактировались.

Actual role — отдельный correction author и scope inspector. Я прочитал обе exact native/target grids 1John.2.22/4.13 и 2Pet.3.5/3.7, визуально прочитал DjVu leaf1499/1501 (printed1495/1497) и leaf1497 (printed1493), inspected отдельно authored Johannine packet v1 и отдельно authored native blocking QC. Чтение чужих research/QC artifacts является inspection, не authorship. Я не автор source research, independent QC, registry или book completion. Full reconstruction 97 grids/3614 labels здесь является structural reproduction; содержательная независимая проверка всех final grids принадлежит reviewer.

## 1John.2.22

`ἀρνούμενος` o008 теперь one_to_one→t007 «відкидає»; reciprocal target содержит только этот supplier. Native `οὐκ` o011 остаётся в source grid, но получает original_omitted/NULL с точным `grammatical_function_not_overt`. Burton §473 remark разбирает redundant negation именно данного стиха; exact scan печатает положительное «що Ісус є Христос». Это non-overt redundant grammatical function. Авторское предложение v1 `translation_omission` не принято; classifier independently proven в separately sealed native QC. Ни accidental omission, ни отсутствие source token не утверждается.

## 1John.4.13

Полное `ἐν τούτῳ` o001+o002 jointly→t012 «тим» как many_to_one; оба original rows и target edge взаимно согласованы. Italic t011 «це» — resumptive pronoun для fronted content clause «Що ми пробуваємо…», поэтому translation_addition с пустым source list. Exact scan и independently inspected NET note12 различают содержание первого ὅτι и explanation second ὅτι для ἐντούτῳ. Первый ὅτι→fronted «Що» неизменён.

## 2Pet.3.5 и 3.7

В τῷ τοῦ θεοῦ λόγῳ → «словом Божим» и τῷ αὐτῷ λόγῳ → «тим самим словом» nominal group переводится, но separate definite article не выражен. Только null_reason двух native τῷ меняется translation_omission→grammatical_function_not_overt; NULL, native occurrence IDs, source atoms и все existing edges сохранены. Ни direct article→«словом»/«тим», ни новый Strong edge не добавлен. Основание — separately authored/physically locked independent native QC и exact leaf1497; полный Petrine source-resolution report ещё не был опубликован при выполнении этих corrections и не выдаётся за прочитанный.

## Exact before/after locks

| Verse / stable key | Before alignment SHA256 | After alignment SHA256 |
| --- | --- | --- |
| 1John.2.22<br>`original:gold7:original:e90657c037b59c358f7a6586aeaecb72` | `3ce9cdc56378e9b21d22aa15f714ca0e628aca085e5c1a753b928a804ff71277` | `952d2827c747554e3d90c8459d75384c7ba2a19ae09ebde2640a531d04c861c7` |
| 1John.4.13<br>`original:gold7:original:eed73045ec74eb4c38f61b3cc007fa71` | `feeb1c07fe4aefff839c2f00a13068502ff305787c012bc1b4794c92b4cbaf38` | `cb19def76c8f05b4257aa0a7cf12a4efcabf20609f8dcd21b0789d7cef284f9b` |
| 1John.4.13<br>`original:gold7:original:f3f7dcb8181a785209bd8d3f822a7a2d` | `3553426ecb2324fa6d2755bbd4ab81c0f7c2c63d9107d5cad3f9ed19d6b39907` | `87bed06edc098565038262c96407fba7852cc82da9b9403b40f829f535bbc305` |
| 1John.2.22<br>`original:gold7:original:f48e0cc15d20b52138af31204ba46b3a` | `9fca29c11ec26a81134f52ccdb5069737e37375934463ccd31b368977bd35afb` | `81955fa74462cdbe883debce1fd6323666fe4763380f92ba537fdbe506ee506c` |
| 1John.4.13<br>`target:gold7:target:13acef4bffbe0669888e4c63c201d56a` | `1618d70bf9ae8cc1a2117dd5c7fc6620abfc97dcf17298be38e3f9791fb970ab` | `794f579e0a4ec2be4f2b90ba82cde7afffec43fe494f3d00c260002ab9a5ca29` |
| 1John.2.22<br>`target:gold7:target:2f1254202a03ea1f43da851da73abcd4` | `7a098895c8c0e7e7afe456853802543a53f47f88c05a08e33268aa09ec735615` | `9b7dbd07fcbbd844af9289df868397835096f239b8312f74976f800078e306f3` |
| 1John.4.13<br>`target:gold7:target:9dd9b3e414bd949ba16d465dfa190d13` | `449b40e24ed516fad09353a857dbafec4289169b99c550769495f6ebb9c32922` | `42e459c3265cb46ddb240663ceee90086237aa70aaf02a0fc33165ea36b1c032` |
| 2Pet.3.7<br>`original:gold7:original:08bb4bdd1f7207c308f5737ca4efbe8b` | `9888260df55907df9e583c513be0d4f28d8c88f31d431a3265d8ac5bff7770cf` | `ea39bd90cbcc23bba94baa87f2ab2f0a365db6ff4b5b69e9695f001b0a726998` |
| 2Pet.3.5<br>`original:gold7:original:0ce8877a263911e6513957b281d6d136` | `3a2cacc28b9d3d66ec83c673e4b4dd07957ac825246f6759748907c101d82a4d` | `a050a174f117abd23a0b94d605306064a0dc7279ecabdc1e1c623cf057076e73` |

Все occurrence IDs, target IDs, before/after semantic payloads и supersedes locks сохранены в [1John scope inspection](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.scope_inspection.v1.json) и [2Pet scope inspection](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/2Pet.scope_inspection.v1.json).

## Не выполненные изменения и сохранённые verdicts

Все 43 исторических blocking keys в 20 loci сохранены payload-identical: 1Pet10, 2Pet17, 1John16; исходные uncertain/error verdicts не переименованы. Ни один совпадает с девятью выполненными corrections. Exact preservation proof фиксирует stable keys и payload/alignment digests; это immutable evidence, а не параллельный editable registry.

В частности, source-variant cases 1John.1.7/3.13/3.14/3.19/4.19/4.20/5.8/5.9 не исправлялись. Узкая lemma correspondence или plausibility сама не создаёт selected-source/reciprocal-grid disposition. Для 5.9 v1 тезис exclusive relative-source correspondence не принят как execution proof: reviewer NET inspection допускает relative-like selected ὅτι; historical uncertainty сохранена. Две actual 4.20 error rows также остаются historical error. Остальные source-variant cases 1Pet/2Pet не получили invented source absence, нового NULL classifier или Strong number. Root должен закрыть точные unresolved groups registered deferrals с effective exclusions; corrector не утверждает, что root registry/coverage уже завершены.

## Проверки и цепочки

Stage3 offline /4/5/6 PASS в моём read-only preflight. Shared physically inspected root preflight receipt подтверждает stage7 PASS и SHA/bytes всех5113 entries до author writes. Мой поздний current-inventory stage7 check ожидаемо отверг изменённый validation_log; это сохранённый stale diagnostic, не новый acceptance PASS. Затем physical old-inventory roster verification5113 PASS с тремя explicitly declared preserved-input bridges; critical49 chain/source locks и70 Johannine packet/scope references PASS. Inventory не refresh-ился. [Pre-read receipt](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/pre_read_receipt.v1.json).

[1John correction chain](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/1John.correction_chain_locks.v1.json); [2Pet correction chain](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/2Pet.correction_chain_locks.v1.json); [historical preservation proof](../../work/ukrainian_stage_7_20260801/session_group7_20261010_corrector_01/historical_scope_preservation.v1.json); [manifest](gold_group_007_correction_scope.v1.manifest.json).

Change checklist применён: runtime/module boundaries, dependencies/acknowledgements, localization, release и approved RU/EN docs pairs не затронуты; Flutter format/analyze/tests/smoke N/A для evidence-only correction packet. Existing seal/check и full-grid structural/reciprocal accounting PASS. New validator не добавлен, quality gates/logging не изменены, registry/runtime/DB/other books/commit/push не менялись. Post-correction actual content QC pending отдельного reviewer; strict acceptance, book completion и export corrector не объявляет.

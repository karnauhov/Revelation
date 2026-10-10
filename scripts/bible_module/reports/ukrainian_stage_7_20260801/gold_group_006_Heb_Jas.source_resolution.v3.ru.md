# Group006 OH1988 Heb/Jas: source-resolution v3 — Heb 10:31 addendum

Дата: 2026-10-10. Фактический автор: `/root/heb_jas_research`, только source research; не corrector и не независимый QC reviewer.

Full machine cases v3 содержат **19 unique target_ref**: все 18 raw records v2 сохранены побайтно, добавлен ровно один case Heb.10.31. Предыдущие bounded cycles не повторялись. Addendum scope — только `original:gold7:original:8666c73c23d6fd85434a92487d724c18`. Новых target uncertainties, Strong assignments, gold corrections и definitive errors нет. Исторические три initial actual errors из parent final-review сохранены; этот research не переписывает QC verdicts.

Supersedes full scope roster [v2 manifest](gold_group_006_Heb_Jas.source_resolution.v2.manifest.json), сохраняя [полный отчёт v2](gold_group_006_Heb_Jas.source_resolution.v2.ru.md) и все предыдущие seals. Результат — `deferred_strong_unassigned` одного source key, без нового NULL/omission утверждения и без forced classifier replacement.

## Exact inputs и печать

До full JSONL чтения проверены **131 input/previous-seal lock references PASS**, включая chain_inputs.v3, frozen sources, v2 inputs/outputs. Native case audit: семь original tokens, template/selected-source exact set equality, raw TAGNT digests, exact target scalar/UTF-8 byte spans и text SHA PASS. Source identities из исходной цепочки:

- `o002` `tagnt:b98346509b658d6c0c0b7b06aedcfcbfdc98c6b1188342d58b5e5b15323944bb:c01`; `original:gold7:original:8666c73c23d6fd85434a92487d724c18`; `τὸ`, lemma `ὁ`, `G3588`, `T-NSN`; `Heb.10.31#02=NKO`; raw SHA `d0920985adfce51b6152844b4352e6fcfe8a04ef985bcb7aadc2fa355d13b6af`.
- Text SHA `8114e9d00911e23415642919bc482d46844fce74cb29deb50a7a713cc812f804`; DjVu page **1481**, printed page **1477**; locked DjVu SHA `0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34`. Exact verse: «Страшна́ річ — упасти в руки Бога Живого!». Перепроверен оригинальный page rendering; текст и scan не изменены.

Target spans приводятся только как контекст, **не affected keys**:

- `t001` `uk7:N9X:001:0:8` «Страшна́»; scalar [0,8) / UTF-8 bytes [0,16).
- `t002` `uk7:N9X:002:9:12` «річ»; scalar [9,12) / UTF-8 bytes [17,23).
- `t003` `uk7:N9X:003:15:21` «упасти»; scalar [15,21) / UTF-8 bytes [28,40).

## Один bounded classifier cycle

Закреплённый source token o002 τὸ, lemma ὁ/G3588, T-NSN, Heb.10.31#02=NKO засвидетельствован всеми восемью TAGNT editions. UGNT и официальный SBLGNT text независимо содержат тот же article перед ἐμπεσεῖν. Поэтому source absence не имеется и competing lemma нет. По Smyth §§1966,1968–1970 инфинитив является также verbal noun, может быть субъектом/объектом, а neuter article оформляет его nominal/substantive функцию. Здесь φοβερόν — предикативная характеристика, τὸ ἐμπεσεῖν — action-subject. OH1988 действительно печатает «Страшна́ річ — упасти в руки Бога Живого!», сохраняя инфинитивное действие как subject при nominal predicate. Наличие грамматической функции в OH опровергает автоматическую уверенность в classifier translation_omission на основании отсутствия отдельного артикля, но само по себе не определяет единственный pipeline classifier. Нынешняя accepted связь φοβερόν→Страшна+річ сохранена как whole neuter-predicate rendering; річ не объявлена addition и не перепривязана к τὸ. Возможное grammatical_function_not_overt остаётся гипотезой для отдельного corrector/QC, а не выпущенной заменой NULL.

Первичные evidence: [Smyth 1920, Greek Grammar, Verbal Nouns §§1966,1968–1970](https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.04.0007%3Apart%3D4%3Achapter%3D45), [UBS Ellingworth/Nida 1983, Heb10:31](https://tips.translation.bible/story/translation-commentary-on-hebrews-1031/), locked TAGNT STEP source, UGNT v0.34 и official SBLGNT text. Smyth general grammar подтверждает nominal function инфинитива/article; UBS handbook подтверждает fearful-predicate/action structure и допускает restructuring. Эти источники не утверждают exact gold classifier или source-specific отсутствие украинского grammatical function.

Две ограниченные поисковые queries; один successful ordinary HTTPS retrieval Smyth chapter и UBS page. Direct articular-section web-tool URL не fetched, однако весь primary Smyth chapter прочитан из successful HTML; нужные §§1966,1968–1970 закреплены. SBTS scholarly PDF вернул 403; не использован как полнотекстовое доказательство, повторных обходов не было. Платный эксперт, новая dependency или дальнейшее исследование старых случаев не требовались.

Missing proof: Нет достаточного exact classifier proof, устанавливающего translation_omission вместо сохранённой nonovert nominalizing function, либо однозначно разрешающего заменить frozen NULL на grammatical_function_not_overt в действующем контракте без separate correction и независимой QC. Общая грамматика подтверждает функцию article, но не author-specific atom/classifier decision. Недоказанный classifier оставлен deferred; source identity G3588 сохранена как evidence-only.

Попытки: lexical omission из отсутствия отдельного артикля; nonovert nominalizing function; direct article→річ (не принято, текущая predicate связь сохранена); Greek nominal grammar + exact source/control/OH comparison. Никакой альтернативе не присвоен definitive classifier. Рекомендация: exact one-source-key deferral; accepted target predicate/action links не затрагивать.

Future follow-up optional: при новом classifier-specific доказательстве или owner request — отдельные scoped corrector inspection и independent QC. Registered deferral удовлетворяет completion; второй research cycle не нужен.

## Артефакты и границы

[Full cases v3](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/source_resolution.cases.v3.jsonl), [conclusion map v3](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/source_resolution.conclusion_map.v3.json), [native evidence](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/heb1031_native_evidence.v3.json), [grammar evidence](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/heb1031_grammar_evidence.v3.json), [validation](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/heb1031_validation.v3.json).

Это versioned source research/technical proof, не editable issue registry. Shared registry, QC answers, correction payloads, sources, old seals, runtime, DB, stage8, другие группы, global finalize, commit/push не затронуты. JSON/JSONL/UTF-8, exact identity/spans, prior raw prefix preservation и SHA/byte locks проверены. Runtime/tests/docs RU/EN пары не изменены; Flutter validation здесь не применима. Parent root интегрирует navigation и exact completion exclusion.

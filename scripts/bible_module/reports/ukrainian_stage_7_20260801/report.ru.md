# Этап 7: evidence-first Strong alignment OH1988

Doc-Version: `1.0.0`
Last-Updated: `2026-09-08`
Source-Commit: `working-tree`
Schema-Version: `1`
Contract-Version: `ukrainian-stage-7-evidence-alignment-v1`
Input-SHA-256: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`
Processed/Skipped/Errors: `31102 / 682836 / 0`

## Статус

Этап **не закрыт**. Доказаны immutable input freeze, точная украинская
токенизация, raw primary/alternative component reparse, native-token control
layer, source/license registry и аудит первичных исторических документов.
Исторический и 53-locus textual fingerprint завершён; пять прежних локальных
choices получили двухпроходные post-candidate manual dispositions, причём три
неразличимых места намеренно не выводят Strong. Target-side bridge proof и gold
остаются частичными и fail-closed. Первый blind gold-проход завершён по всем
66 книгам: 2 171 стих, 45 831 original и 41 807 target-accounting decisions.
Оба независимых прохода и post-blind comparison завершены для `Gen–Isa`
(814 стихов, 19 207 original и 16 692 target). Для `1Sam–1Kgs` завершены
distinct third adjudication и независимый QC; `Deut`, `Ezra`, `Neh` и `Esth`
также полностью приняты. Pass 2 для `Jer–Rev` ещё не выполнен.
По строгому критерию владельца «pass 1 + pass 2 + полная adjudication +
независимый QC без `error`/`uncertain`» приняты `22/66` книг: `Gen`, `Exod`,
`Lev`, `Num`, `Deut`, `Josh`, `Judg`, `Ruth`, `1Sam`, `2Sam`, `1Kgs`, `2Kgs`,
`1Chr`, `2Chr`, `Ezra`, `Neh`, `Esth`, `Job`, `Ps`, `Prov`, `Eccl`, `Song`.
Незавершённые или только частично проверенные книги в
этот счётчик не входят.
Поэтому finalized gold по-прежнему содержит `0 / 25 000` принятых
assignment/null решений, а candidate tuning, A/B/C calibration и production
Strong markup намеренно не выполнялись.

## Зафиксированные результаты

- exact stage-6 texts/comments: 31,102 позиций;
- украинские surface tokens: 595,077;
- raw original components (включая 14 primary-null) после повторного чтения TAHOT/TAGNT: 682,836;
- отдельно адресуемые TAHOT/TAGNT apparatus alternatives: 28,543;
- raw OSHB/UXLC/UGNT control tokens: 751,557;
- exact unique control→TAHOT/TAGNT crosswalks: 632,592; unresolved/service: 118,965;
- покрытие original refs application grid: 31,102 / 31 102;
- RUSSYN/YLT manual bridge records audited: 836,745;
- украинские comparison lexemes: 44,721;
- авторские сноски exact OH1988: 1,329
  uses (verse + heading), все как zero-vote corroboration/manual-review evidence;
- book-balanced annotation panel: 2,171 стихов,
  45,831 projected original decisions;
- закреплённые legacy negative counterexamples: 12;
- fail-closed candidate rows across all independent generators: 872,025
  (first-party 501,518; bidirectional statistical
  163,140; multilingual contextual
  207,367; resolver-eligible `0`);
- accepted production Strong links/markers: `0` (fail-closed).

## Gold workflow

Все 58 внешних pass-1 submissions `1Sam–Rev` прошли локальные format-only
canonicalization, exact `expand/check` и deterministic audit. Вместе с
внутренними `Gen–Ruth` полный pass 1 объединён без пропусков: 66 shards,
66 reviewer IDs, 45 831 original и 41 807 target decisions; merged SHA-256
`40a644da0193fc705dd9af9ff5cc63901d2e2e9f3394ac83cc586b21ef37eaee`,
validated SHA-256
`681dc4fb5265146518aab2dd9b6cd806436a41be655786337e95f18f19becb7b`.

Независимый pass 2 дополнительно завершён и повторно проверен для `1Sam`,
`2Sam` и `1Kgs`. Post-blind comparison отделяет реальные link/null
расхождения от разной терминологии `severity/phenomena`: из 5 274 решений
этих трёх книг 2 793 совпали по alignment, а все 2 481 разрешены отдельными
третьими adjudicators. Совпавшие link/null решения сохраняют оба
evidence/rationale, объединение phenomena и максимальную severity. Exact
adjudication повторно прошла полный verse-local accounting для 5 274 решений;
независимый QC проверил 1 128 уникальных adjudicated строк, включая все
critical/high и новые/pass-2 решения (`error=0`, `uncertain=0`). Digests
закреплены в `gold_adjudication_batch_009_011.manifest.json`. Внешний ChatGPT
остаётся одним blind pass, а не источником gold truth.

Для `Deut` оба независимых blind-прохода были повторно сведены post-blind
comparison: 33 стиха, 852 original и 710 target-accounting decisions. Из 1 562
stable decisions совпали 1 363, а 199 substantive disagreement без сглаживания
переданы distinct adjudication. Затем component-by-component разрешены 199/199
расхождений в 28 стихах, сохранены 1 363 agreements и grid 1 562/1 562; все 91
high закрыты, unresolved/error — 0. `Deut.32.8` проверен по frozen primary-MT
fingerprint. Два comparison/adjudication прогона побайтно совпали; exact digests
закреплены в `gold_review_batch_005.manifest.json` и
`gold_adjudication_batch_005.manifest.json`. Distinct QC проверил 199/199 IDs,
все 91 high, 19 new, 33/33 template-стиха и grid 1 562/1 562; generic validator
и root canonical/SHA audit дали `error=0`, `uncertain=0`. Книга полностью
принята и входит в строгий счётчик. QC SHA-256
`3c994118fc83365131d3ebec9a344b9dae63413eb043f59267465fad658603e4`,
sidecar SHA-256
`51d8a9f3c8bdc435fda028d64cfe70c7511514430df5ad373a614096db1aa154`.

Следующая blind-партия `2Kgs–2Chr` также завершена и повторно проверена:
98 стихов, 2 675 original и 2 149 target-accounting decisions. Из 4 824 stable
решений 3 793 совпали, 1 031 substantive disagreement ожидают distinct
adjudication на этой post-blind контрольной точке; впоследствии все три книги
прошли distinct adjudication и independent QC. Exact comparison digests
закреплены в `gold_review_batch_012_014.manifest.json`.

Для `2Kgs` distinct third adjudication разрешила 402/402 substantive
disagreement в 251 компоненте и 32 стихах, сохранила 1 316 согласованных
решений и полный grid 1 718/1 718. Distinct reviewer проверил все 402 решения,
114/114 high и exact stage-6 text/comment 32/32; `accepted=402`, `error=0`,
`uncertain=0`, dangling/cross-verse и unresolved critical/high — 0. QC SHA-256
`4d12c29d…`, manifest SHA-256 `1d1c9a14…`; цепочка закреплена в
`gold_adjudication_batch_012.manifest.json`, и книга входит в строгий счётчик.

Для `1Chr` distinct third adjudication разрешила 273/273 substantive
disagreement в 178 компонентах и 32 стихах, сохранила 991 согласованное
решение и полный grid 1 264/1 264. Distinct reviewer проверил все 273 решения,
126/126 high и exact stage-6 text/comment 32/32; `accepted=273`, `error=0`,
`uncertain=0`, dangling/cross-verse и unresolved critical/high — 0. QC SHA-256
`2e4880fa…`, manifest SHA-256 `a8e2fc4b…`; цепочка закреплена в
`gold_adjudication_batch_013.manifest.json`, и книга входит в строгий счётчик.

Для `2Chr` distinct third adjudication разрешила 356/356 substantive
disagreement в 266 компонентах, сохранила 1 486 согласованных решений и полный
grid 1 842/1 842. Distinct reviewer проверил все 356 решений, 96/96 high и
exact stage-6 text/comment 34/34; `accepted=356`, `error=0`, `uncertain=0`,
dangling/cross-verse и unresolved critical/high — 0. QC SHA-256 `43d27d08…`,
manifest SHA-256 `8140bbbd…`; цепочка закреплена в
`gold_adjudication_batch_014.manifest.json`, и книга входит в строгий счётчик.

Следующий blind shard `Ezra` также завершён и повторно проверен: 32 стиха,
906 original и 695 target-accounting decisions. Из 1 601 stable decision
совпали 1 110, а 491 substantive disagreement ожидает distinct adjudication;
exact digests закреплены в `gold_review_batch_015.manifest.json`. Это описание
post-blind контрольной точки; ниже зафиксирована уже завершённая adjudication и
QC книги.

Distinct third adjudication `Ezra` затем разрешила 491/491 substantive
disagreement в 259 компонентах и 32 стихах, сохранила 1 110 согласованных
решений и полный grid 1 601/1 601. Все 27 critical и 268 high разрешены без
unresolved critical/high; adjudication SHA-256 `3e80aac7…`, sidecar SHA-256
`3c493c4a…`, exact цепочка закреплена в
`gold_adjudication_batch_015.manifest.json`. Distinct independent QC затем
проверил все 491 stable IDs, 32/32 стиха, все 268 high и 27 critical, exact
stage-6 text/comments и reciprocal grid 1 601/1 601. Generic validator и
отдельная root-проверка canonical/unique/SHA дали `accepted=491`, `error=0`,
`uncertain=0`; QC SHA-256 `f4765d62…`, sidecar `fa4bb85d…`. Книга входит в
строгий счётчик `22/66`.

Blind shard `Neh` завершён и повторно проверен: 32 стиха, 621 original и 485
target-accounting decisions. Из 1 106 stable decisions совпали 868, а 238
substantive disagreement затем полностью разрешены distinct third adjudicator:
238/238, 868 соглашений сохранены, reciprocal grid 1 106/1 106, все 3 critical
и 18 high закрыты, unresolved/error — 0. Critical `Neh.13.27` сохранён
fail-closed как original omission плюс украинская translation addition без
ложной связи. Double deterministic validator прошёл; exact digests закреплены в
`gold_review_batch_016.manifest.json` и
`gold_adjudication_batch_016.manifest.json`. Первый independent QC выявил ровно
7 high-ошибок в `Neh.6.7`/`Neh.12.47`; consensus correction исправила 4 original
и 3 target решения. Post-correction QC принял 247/247 наблюдений, 240 unique IDs
и grid 1 106/1 106 с `error=0`, `uncertain=0`; все SHA и повторная генерация
проверены. Correction/QC SHA-256 соответственно `cea4dad1…` / `7f7eee3c…`,
их sidecars `463638c4…` / `32b69092…`. Книга полностью принята.

Blind shard `Esth` завершён и дважды проверен: 32 стиха, 1 083 original и 855
target-accounting decisions. Из 1 938 stable decisions совпал 461, а 1 477
substantive disagreement полностью разрешены distinct third adjudicator:
1 477/1 477, 382 компонента, 461 agreement сохранён, reciprocal grid
1 938/1 938, все 401 high закрыты, unresolved/error — 0. Для 14 компонентов
созданы новые семантические декомпозиции. Exact digests закреплены в
`gold_review_batch_017.manifest.json` и
`gold_adjudication_batch_017.manifest.json`. Distinct QC проверил 1 477/1 477
IDs, 382/382 компонента, все 401 high и 14 new, grid 1 938/1 938; generic
validator и root canonical/SHA audit дали `error=0`, `uncertain=0`. Книга
полностью принята. QC SHA-256 `14397af3…`, sidecar `9b7dca74…`.

Blind shard `Job` завершён и дважды проверен: 32 стиха, 435 original и 435
target-accounting decisions. Из 870 stable decisions совпали 627, а 243
substantive disagreement разрешены distinct adjudicator в 105 компонентах.
Сохранены 627 agreements и полный grid 870/870; 31 компонент выбран из pass 1,
69 из pass 2, для 5 построены новые семантические decompositions. Все 4 critical
и 122 high разрешены, unresolved/error — 0; `Job.39.18` сохранён по primary MT
fail-closed. Adjudication/sidecar SHA-256 `5a57b794…` / `e2161bbb…`, double
deterministic validator прошёл. До отдельного independent QC книга не входит в
строгий счётчик (`22/66`).

Blind shard `Ps` завершён и дважды проверен: 97 стихов, 1 399 original и 1 862
target-accounting decisions. Из 3 261 stable decision совпали 1 589, а 1 672
substantive disagreement разрешены distinct adjudicator в 632 компонентах.
Сохранены 1 589 agreements и полный grid 3 261/3 261; row-level выбраны 1 168
pass-1, 440 pass-2 и 64 new решения. Все 930 adjudicated high разрешены,
unresolved critical/high — 0; `Ps.22.16`, `Ps.40.6`, `Ps.145.13` сохранены по
frozen fingerprint. Adjudication/sidecar SHA-256 `a2b35520…` / `a1ea1259…`,
double deterministic validator прошёл. Отдельный fail-closed QC затем проверил
1 672/1 672 строк, 632/632 компонента, все 930 high, 64 new, 97 стихов и grid
3 261/3 261: принято 1 659, найдено 13 ошибок, uncertain — 0. Ошибки ограничены
`Ps.61.1`, `Ps.70.1`, `Ps.80.1`: H9012 должен быть отдельно связан с `же/ж`, а
не объединён с глаголом при маркировке `же/ж` как addition. Blocking
QC/sidecar SHA-256 `6b3acd2e…` / `6ed953cc…` воспроизведены.
Exact correction уже завершена отдельным reviewer: изменены только 13
QC-scoped high-строк (6 original + 7 target), H9012 отдельно связан с `же/ж`,
остальные 1 659 adjudicated rows и grid 3 261/3 261 сохранены. Double
`check-correction` прошёл; correction/sidecar SHA-256 `57c57e7d…` /
`7c68870a…`, corrected adjudication/sidecar `2e1d6495…` / `1bcc754d…`.
Финальный independent post-correction QC принял 1 688/1 688 наблюдений по
1 672 unique stable IDs, все 632 компонента, 930 high, 97 стихов и полный grid;
`error=0`, `uncertain=0`. Double `check-correction-qc`, byte-identical
regeneration и root 16/16 SHA audit прошли; QC/sidecar SHA-256 `f5858df0…` /
`67e699c4…`, цепочка закреплена в `gold_adjudication_batch_019.manifest.json`.
Псалтирь входит в строгий счётчик `22/66`.

Blind shard `Prov` завершён и дважды проверен: 32 стиха, 424 original и 389
target-accounting decisions. Из 813 stable decisions совпали 649, а 164
substantive disagreement сохранены для distinct adjudication. Pass 1 не
открывался до заморозки и двойной проверки raw pass 2; expansion и comparison
побайтно воспроизведены, exact digests закреплены в
`gold_review_batch_020.manifest.json`. Distinct adjudication разрешила 164/164
расхождения в 89 компонентах и сохранила grid 813/813; отдельный QC проверил
все 164 строки, 5 critical, 93 high и 11 new. Двойной generic validator и
root-проверка 10/10 SHA-lock дали `error=0`, `uncertain=0`; QC/sidecar SHA-256
`ae11abe3…` / `36130c5f…`, цепочка закреплена в
`gold_adjudication_batch_020.manifest.json`. Книга входит в строгий счётчик
`22/66`.

Blind shard `Eccl` завершён и повторно проверен: 32 стиха, 780 original и 625
target-accounting решений. Pass 1 не открывался до заморозки raw pass 2. Из
1 405 stable decisions совпали 970, а 435 substantive disagreement (307
original + 128 target) переданы distinct adjudication. Root compact check и
byte-identical comparison прошли; четыре SHA-lock закреплены в
`gold_review_batch_021.manifest.json`. Distinct adjudication разрешила 435/435
расхождений в 229 компонентах, сохранила 970 agreements и grid 1 405/1 405;
все 2 critical и 186 high разрешены без unresolved. Adjudication/sidecar
SHA-256 `b18d6ca4…` / `d80dbfb5…`. Distinct QC проверил 435/435 IDs, 229
компонентов, все 2 critical, 186 high, 12 declared-new и grid 1 405/1 405;
`Eccl.2.25` принят только как явно документированное translation divergence,
без выдуманного alternative source, а unresolved `Eccl.9.2` исключён.
Двойной generic validator и root 10/10 SHA audit дали `error=0`,
`uncertain=0`; QC/sidecar SHA-256 `0a25f883…` / `e7267c93…`, цепочка
закреплена в `gold_adjudication_batch_021.manifest.json`. Книга принята.

Blind shard `Song` завершён: 32 стиха, 623 original и 577 target-accounting
решений. Из 1 200 stable decisions совпало 591, а 609 substantive disagreement
(346 original + 263 target) переданы distinct adjudication. Root compact check,
byte-identical comparison и 4/4 physical SHA-lock прошли; pass2/comparison SHA
закреплены в `gold_review_batch_022.manifest.json`. Distinct adjudication
разрешила 609/609 расхождений в 207 компонентах, сохранила 591 agreement и
полный grid 1 200/1 200; row-level выбраны 385 pass-1, 115 pass-2 и 109 новых
семантических декомпозиций. Все 21 critical и 142 high разрешены, unresolved
critical/high — 0; adjudication/sidecar SHA-256 `a0b62523…` / `f6cf5218…`.
Distinct QC проверил 609/609 IDs, 207 компонентов, все 21 critical, 142 high,
109 adjudicator-declared-new и grid 1 200/1 200. Двойной generic validator,
byte-identical regeneration и root 10/10 SHA audit дали `error=0`,
`uncertain=0`; QC/sidecar SHA-256 `9dd78e31…` / `854b3250…`, цепочка
закреплена в `gold_adjudication_batch_022.manifest.json`. Книга принята.

Blind shard `Isa` завершён и повторно проверен: 34 стиха, 716 original и 649
target-accounting решений. До заморозки pass 2 не открывались pass 1,
candidates, legacy или Strong; `Isa.7.14` и `Isa.53.5` обработаны fail-closed.
Из 1 365 stable decisions совпали 1 113, а 252 substantive disagreement (183
original + 69 target) сохранены для distinct adjudication. Double compact
check, root byte-identical comparison и 4/4 SHA-lock прошли; exact digests
закреплены в `gold_review_batch_023.manifest.json`. До adjudication и QC книга
в строгий счётчик не входит (`22/66`).

В накопленной очереди `Gen–Ruth` третья adjudication завершена для `Gen`,
`Exod`, `Lev`. `Gen` полностью принят после независимого QC всех 230/230 строк
(`error=0`, `uncertain=0`). `Lev` также полностью принят: checkpoint 145/216
возобновлён строго по exact remaining IDs, проверены оставшиеся 71/71 строки,
итоговый QC 216/216 дал `error=0`, `uncertain=0`; QC SHA-256
`21bb8fc1c6d9f28b84bdffd828616d9093415c1a77c5daa042729d81ed001534`.

Для `Num` distinct third adjudication разрешила 310/310 substantive
disagreement, сохранила 1 186 согласованных решений и полный overlay
1 496/1 496. Отдельный reviewer затем проверил все 310 adjudication rows,
включая 56 high и 22 new, exact 33/33 stage-6 texts/comments, 812 original и
684 target records. Итог: `accepted=310`, `error=0`, `uncertain=0`, unresolved
critical/high и dangling/cross-verse links — 0. QC SHA-256 `04873c06…`,
manifest SHA-256 `2401c4fe…`; цепочка закреплена в
`gold_adjudication_batch_004.manifest.json`, и `Num` входит в строгий счётчик
`22/66`.

Для `Josh` distinct third adjudication разрешила 464/464 расхождения,
сохранила 1 102 согласованных решения и полный grid 1 566/1 566. Отдельный
reviewer затем проверил все 464 решения, включая 33 high и 59 new, exact
stage-6 text/comment 32/32 и полный reciprocal grid. Итог: `accepted=464`,
`error=0`, `uncertain=0`, unresolved critical/high и dangling/cross-verse
links — 0. QC SHA-256 `9bf8b729…`, manifest SHA-256 `d310eb8b…`; цепочка
закреплена в `gold_adjudication_batch_006.manifest.json`, и `Josh` входит в
строгий счётчик `22/66`.

Для `Judg` distinct third adjudication разрешила 562/562 расхождения,
сохранила 1 187 согласованных решений и полный grid 1 749/1 749. Distinct
reviewer проверил все 562 решения, 40/40 high, 32/32 затронутых стиха и exact
stage-6 text/comment для 33/33 template-стихов. Итог `accepted=562`,
`error=0`, `uncertain=0`, dangling/cross-verse и unresolved critical/high — 0.
QC SHA-256 `44a7a121…`, manifest SHA-256 `785e0503…`; цепочка закреплена в
`gold_adjudication_batch_007.manifest.json`, и книга входит в строгий счётчик
`22/66`.

Для `Ruth` distinct third adjudication выполнена только на принятых external
pass 1 v3 и исправленном independent pass 2 v2; отклонённый over-grouped pass 2
не использовался. Разрешены 252/252 расхождения, сохранены 1 333 согласованных
решения и полный grid 1 585/1 585. Distinct reviewer проверил все 252 решения,
56/56 high, 30/30 затронутых стихов и exact stage-6 text/comment 32/32. Итог
`accepted=252`, `error=0`, `uncertain=0`, dangling/cross-verse и unresolved
critical/high — 0. QC SHA-256 `b782950a…`, manifest SHA-256 `ac86a7e2…`;
цепочка закреплена в `gold_adjudication_batch_008.manifest.json`, и книга
входит в строгий счётчик `22/66`.

Book-level QC теперь имеет единый tracked fail-closed валидатор
`check-adjudication-qc`: он требует trusted digest sidecar и заново проверяет
все SHA, reviewer independence, exact adjudication semantics/evidence,
stage-6 text/comment, reciprocal grid и нулевые error/uncertain. Реальные
артефакты `Lev`, `Num`, `Josh`, `Judg`, `Ruth`, `2Kgs`, `1Chr`, `2Chr` проходят
этот контракт. Валидатор
раздельно проверяет alignment- и semantic-selection counts по явному
`selection_basis`; смешанный набор категорий отклоняется fail-closed.
Первый `Exod` QC 130/130 обнаружил шесть ошибочных reciprocal
rows в трёх фразах, где украинские `той/те` следует связать с отдельным
еврейским артиклем `הַ/הָ`, а не с noun atom. Отдельный fail-closed
consensus-correction уже сформирован: ровно 9 разрешённых semantic changes в
трёх стихах, после overlay учтены 1 382/1 382 stable decisions; correction
SHA-256 `ca53be00c26a2ab6d238e1abe495d8a9f306ca91c0493080a1860db38feb4c5a`.
Новый distinct reviewer затем проверил 130 adjudication + 9 correction + 3
revalidate-only rows: 142 наблюдения / 136 unique stable IDs, включая все 42
high, `error=0`, `uncertain=0`; итоговый QC SHA-256
`d79b394b22c516b814a2017f3660e3018f558c4f3176d40eacbc1b39adc19c67`.
`H9009` сохранён как связанный raw grammatical code, но не может рендериться
как classic Strong. `Gen–Lev` запечатаны в
`gold_adjudication_batch_001_003.manifest.json`.

## Авторские сноски как evidence

Все 1,329 стиховые и заголовочные uses
exact OH1988 разобраны отдельно от текста стиха; затронуто
1,222 target refs; все
1,204 определения учтены хотя бы одним
use. Категории: `{"cross_reference":196,"edition_or_translation_note":15,"explicit_original_language_claim":333,"general_author_commentary":581,"lexical_semantic_claim":478,"morphology_grammar_claim":7,"original_script_source_form":139,"textual_variant_claim":7,"transliteration_or_source_form":288}`.
Языковые указатели: `{"aramaic":23,"greek":185,"hebrew":142,"latin":6}`;
review-состояния: `{"author_original_form_matches_multiple_selected_tokens":27,"author_original_form_uniquely_corroborates_selected_token":83,"context_only_no_original_token_claim":910,"explicit_original_claim_without_exact_selected_token_match":222,"manual_textual_review_required":7,"partial_original_form_match_requires_manual_scope":80}`.
Найдено 267 exact
transliteration/original-script совпадений; ещё
355 упоминаний сохранены
неразрешёнными. Совпадения только подтверждают stable original IDs и имеют
автоматический вес `0`. Все
336 partial/ambiguous/
unmatched/variant uses получили безопасные manual-review records. Найденные
7 явные variant-note uses
добавлены в manual review; до component-level решения и gold span/null review
они не могут вывести Strong. Ни одна сноска не поступает на вход
statistical/contextual alignment и stage-6 comments не изменяются. Exact
`target_comment` доступен blind gold-reviewer как предкандидатное первичное
пояснение переводчика, но не считается независимым вторым witness.

## Source integrity

Новый importer читает exact raw STEP files и не наследует пропуски stage-4
нормализации. Current-main YLT-NT positional alias отклонён; используется tagged
SBLGNT transfer `v0.1.0`; только однозначная часть selectors имеет verse-wide
surface+Strong crosswalk к stable TAGNT token, остальные сохранены отклонёнными
как unproven. RUSSYN и YLT остаются разными bridge families, но их общая Clear
инфраструктура отражена как dependency, а target→OH link не считается
доказанным самим наличием bridge.

OSHB, UXLC и UGNT повторно разобраны из exact ZIP inputs с source-qualified
stable IDs. Их native ref grids точно равны TAHOT/TAGNT grids: 23 213 OT и
7 958 NT. Crosswalk использует native verse, surface и совместимый Strong, но
никогда не создаёт direct control→OH1988 link. Ketiv/qere, brackets, повторы и
210 nonzero UGNT Strong encodings остаются unresolved.

Bridge status counts: `{"accepted_manual_bridge":565670,"accepted_manual_bridge_with_null_member":5,"accepted_manual_null_source":3377,"canonicalized_terminal_part_alias":1154,"fully_null_source_records":3377,"mixed_null_source_records":6,"rejected_unproven_original_crosswalk":267693}`.

## Textual fingerprint

Exact 1 538-листовой OH1988 scan и его front/back matter полностью проверены;
также зафиксированы первичные документы Огиенко 1927 и Илариона 1963. Они
доказывают Hebrew как общую основу OT, Greek как общую основу NT и эпизодическое
использование LXX, но не называют точные исходные редакции и не доказывают
неизменность 1962→1988. Диагностическая панель расширена до
53 loci. TAHOT `X` хранится только как
реконструированная LXX-alternative, а Treg+TR/Byz без NA/SBL/WH больше не
считается modern-critical reading. Из 53 diagnostic loci
53 получили fail-closed component-level
selection/disposition, включая 5
post-candidate manual choices; unresolved critical/high среди этих loci:
0. Отдельно во всём raw apparatus остаются
1,970 fail-closed refs /
4,008 components; они блокируют
только соответствующие loci до adjudication и gold calibration.

## Почему markup не создан

Legacy baseline имеет 1 457 duplicate original assignments и известную ошибку
`Luke.2.11 G3739 → вас`, хотя старый класс назывался `high`. Его 440 280
occurrences и confidence не участвуют в голосовании. Без frozen gold и Wilson
one-sided lower bound ≥ 99.5% автоматический класс A был бы недоказан. B/C без
ручной проверки также запрещены нормативным планом.

## Границы

SQLite не создавался. Working DB, `web/db`, KJV, LXX_TR, content tool, Flutter,
runtime и этап 8 не изменялись. В дорожной карте отмечены только доказанные
автономные подпункты и промежуточные артефакты; общий этап и exit criteria
остаются открытыми.

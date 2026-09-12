# Этап 7: evidence-first Strong alignment OH1988

Doc-Version: `1.0.0`
Last-Updated: `2026-09-12`
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
Оба независимых прохода и post-blind comparison завершены для `Gen–Phlm`
(1 923 стиха, 41 128 original и 37 209 target). Для `1Sam–1Kgs` завершены
distinct third adjudication и независимый QC; `Deut`, `Ezra`, `Neh` и `Esth`
также полностью приняты. Pass 2 для `Heb–Rev` ещё не выполнен.
Для `Isa` третья адъюдикация 252/252 substantive disagreement закончена и
прошла double deterministic `check-adjudication`; независимый content-QC нашёл
одну ошибку, затрагивающую три stable ID в `Isa.66.15`, и заблокировал книгу.
Отдельная scoped correction трёх строк, independent post-correction QC и
real-input correction-aware registry probe всех 1 365 семантик прошли;
`Isa` принята на уровне книги. Для `Jer` и `Lam` blind pass 2 и comparison
заморожены, distinct adjudication 404/404 и 180/180 завершены; обе книги
прошли independent QC. Для `Ezek` independent QC всех
233/233 adjudicated и 1 329/1 329 agreed решений завершён без ошибок;
книга принята. `Dan` после blocking QC пяти согласованных решений в `7.15`
прошла отдельную correction, distinct post-correction QC и реальный
one-book correction-aware registry probe; `Hos` прошла independent QC без
ошибок. `Joel` прошла blocking QC, two-row correction, distinct re-QC и
real-input correction-aware book proof; `Amos`, `Obad`, `Jonah`, `Hab` и `Hag` прошли independent QC.
По строгому критерию владельца «pass 1 + pass 2 + полная adjudication +
независимый QC без `error`/`uncertain`» приняты `36/66` книг: `Gen`, `Exod`,
`Lev`, `Num`, `Deut`, `Josh`, `Judg`, `Ruth`, `1Sam`, `2Sam`, `1Kgs`, `2Kgs`,
`1Chr`, `2Chr`, `Ezra`, `Neh`, `Esth`, `Job`, `Ps`, `Prov`, `Eccl`, `Song`, `Isa`, `Jer`, `Lam`, `Ezek`, `Dan`, `Hos`, `Joel`, `Amos`, `Obad`, `Jonah`, `Mic`, `Hab`, `Hag`, `Mal`.
Незавершённые или только частично проверенные книги в
этот счётчик не входят.
Поэтому finalized gold по-прежнему содержит `0 / 25 000` принятых
assignment/null решений, а candidate tuning, A/B/C calibration и production
Strong markup намеренно не выполнялись.

Коррекционно-осведомлённый global finalizer теперь реализован и проверен на
CC0 регрессии: он применяет SHA/QC/role-locked book corrections после обычной
adjudication и не теряет исправленный originally agreed ID. Production требует
точный registry из 66 versioned accepted book manifests в отчётном каталоге;
для неисправленных книг также повторно проверяет независимый QC и совпадение
локальных/global stable-ID семантик. Targeted 17/17 и bible-module 400/400
тестов прошли. Реальный global registry ещё не может быть собран до полного
66-book QC, поэтому finalized gold остаётся заблокированным; book-level `Isa`
принята после отдельного реального one-book chain/overlay proof.

## Зафиксированные результаты

Промежуточное доказательство `Isa` (shard 023): 34 стиха, 716 original и 649
target decisions, 1 113 неизменённых соглашений двух проходов и 252 разрешённых
расхождения в 144 компонентах; шесть компонентов получили новую семантическую
декомпозицию. Полный reciprocal grid — 1 365/1 365, структурный validator —
`error_count=0`. `Isa.7.14` и `Isa.53.5` проверены на frozen primary-MT
fingerprint; это не разрешение на Strong markup. Adjudication/sidecar SHA-256:
`bb79e3daa4ec2bb32e6000690fbdf463a9a7507482853cda8b7c6285bebda47c` /
`0690822875dcc68dd55005e5d31c6f32e5662ab75d5668e9cb087574517d49e4`.
Версионный указатель — `gold_adjudication_batch_023.manifest.json`; полный
корпус решений лежит только в gitignored `work`. Первый independent QC выявил
ошибку в трёх stable IDs `Isa.66.15`; отдельная correction и новый независимый
post-correction QC закрыли её с `error=0`, `uncertain=0`. Real-input one-book
registry probe на семи SHA-locked звеньях подтвердил сохранение исправленного
исходно согласованного target ID и совпадение всех 1 365/1 365 семантик с
corrected overlay. Книга принята на book-level; global 66-book finalize ещё
впереди.

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
закреплены в `gold_review_batch_023.manifest.json`. Последующая adjudication
252/252 прошла, но blocking QC выявил `Isa.66.15/C0141`: один исходный предлог
`בָּ` (H9003) связан с украинским «в» при «огні», а «у» в frozen `у в огні`
остаётся добавленным дублем. Проверены 252/252 adjudicated и 1 113/1 113
согласованных решений; QC обнаружил три ошибочные stable-ID строки и ни одного
uncertain. QC/sidecar SHA-256 `f4890fdb…` / `0031caca…`. Отдельный reviewer
выполнил точечную correction трёх stable-ID строк: H9003 → «в», лишнее «у» →
translation addition; `seal-correction`/`check-correction`, двойная генерация
и grid 1 365/1 365 прошли. Correction/sidecar SHA-256 `92932046…` /
`000b4591…`. Новый distinct post-correction QC принял 256/256 наблюдений
(252 adjudication + 3 correction + 1 revalidate-only), 254 unique stable ID,
все 34 стиха и grid 1 365/1 365, `error=0`, `uncertain=0`;
QC/sidecar SHA-256 `31879520…` / `e4c292e9…`. Полный corrected overlay
1 365/1 365 имеет SHA-256 `467a44de…` / `a69b9410…` и сохраняет исправление
исходно agreed t005 «у». Но существующий global finalizer ещё не принимает
correction agreed ID, поэтому book-level принятие отложено до поддержанного
correction-aware merge; книга не входит в строгий счётчик (`24/66`).

Blind shard `Jer` (024) заморожен до чтения pass 1: 32 стиха, 946 original и
773 target решений. Double `gold_compact check` и byte-identical comparison
дали 1 315 agreements / 404 substantive disagreements (311 original + 93
target), `error_count=0`; четыре output SHA закреплены в
`gold_review_batch_024.manifest.json`. Аналогично `Lam` (025): 32 стиха,
538 original + 515 target, 873 agreements / 180 substantive disagreements
(127 original + 53 target), `error_count=0`, exact SHA в
`gold_review_batch_025.manifest.json`. Оба pass-2 результата сами по себе не
означали принятие книг.

`Jer` third adjudication разрешила все 404 substantive disagreement в 261
verse-local компоненте, сохранила 1 315 agreements и grid 1 719/1 719;
`Jer.25.38` оставлен без ложной связи исходного «anger» H2740 с украинским
«меча». Double deterministic generation и root `check-adjudication` дали
`error_count=0`; adjudication/sidecar SHA-256 `da312d83…` / `d93dc611…`
закреплены в `gold_adjudication_batch_024.manifest.json`. Для `Lam` отдельная
adjudication разрешила 180/180 disagreement в 116 компонентах, сохранила 873
agreements и grid 1 053/1 053; `Lam.4.4` получила новую декомпозицию.
Double validator и root check прошли, SHA `84fba5b1…` / `0194bf68…` в
`gold_adjudication_batch_025.manifest.json`. Для `Jer` отдельный reviewer
проверил 404/404 adjudicated, 1 315/1 315 agreed и grid 1 719/1 719 в 32
стихах; 2 critical и 80 high, `error=0`, `uncertain=0`. Double generation,
root `check-adjudication-qc` и physical SHA `d9467f06…` / `f37c0770…`
закреплены в `gold_adjudication_batch_024.manifest.json`; книга принята. Для `Lam`
отдельный reviewer проверил 180/180 adjudicated решений, 116 компонентов,
873 agreed и grid 1 053/1 053 во всех 32 стихах. Double generation и root
`check-adjudication-qc` дали `error=0`, `uncertain=0`; QC/sidecar SHA-256
`c15a7107…` / `81d4132a…` закреплены в том же manifest. `Lam` принята и
входит в строгий счётчик `24/66`.

Blind `Ezek` (026) заморожен до открытия pass 1: 32 стиха, 845 original и
717 target decisions, 1 329 agreements и 233 substantive disagreement (192
original + 41 target). Двойной `gold_compact check` и canonical comparison
прошли без ошибок; exact SHA закреплены в `gold_review_batch_026.manifest.json`.
Затем distinct third adjudication разрешила 233/233 расхождения в 184
компонентах, сохранила 1 329 agreements и reciprocal grid 1 562/1 562;
`Ezek.14.4` повтор `בָא` разобран verse-local без позиционного переноса.
Двойная генерация и root `check-adjudication` прошли с `error_count=0`, SHA
`a161a533…` / `ddbef116…` закреплены в
`gold_adjudication_batch_026.manifest.json`. Distinct independent reviewer
затем проверил 233/233 adjudicated, 184 компонента, 1 329/1 329 agreed и
полный grid 1 562/1 562 во всех 32 стихах. Double generation и root
`check-adjudication-qc` дали `error=0`, `uncertain=0`; QC/sidecar SHA-256
`f37208a2…` / `30c6ce09…` закреплены там же. `Ezek` принята.

`Dan` (027) blind pass 2/comparison: 32 стиха, 844 original + 721 target,
1 090 agreements / 475 substantive disagreements, `error_count=0`; exact
SHA в `gold_review_batch_027.manifest.json`. `Hos` (028) blind pass 2 /
comparison: 32 стиха, 615 original + 588 target, 943 agreements / 260
disagreements, `error_count=0`; exact SHA в
`gold_review_batch_028.manifest.json`. `Dan` затем прошла distinct third
adjudication 475/475 расхождений в 228 verse-local компонентах, сохранив
1 090 agreements и полный grid 1 565/1 565; три генерации и root
`check-adjudication` дали `error_count=0`, SHA `1138d1a2…` / `3977bf82…`
закреплены в `gold_adjudication_batch_027.manifest.json`. `Hos` также прошла
distinct adjudication 260/260 в 135 компонентах, сохранив 943 agreements и
grid 1 203/1 203; root `check-adjudication` PASS, SHA `09ea7233…` /
`0f40b416…` закреплены в `gold_adjudication_batch_028.manifest.json`.
`Dan` independent QC нашёл пять ошибочных исходно agreed stable IDs в
`Dan.7.15`: арамейское пространственное `בְּ ג֣וֹא נִדְנֶ֑ה` не переводится
причинным «через це». Separate five-row correction/sidecar SHA-256
`0f8dbcdf…` / `c5a9e82e…` прошла `seal-correction`; distinct post-correction
QC проверил 503 observations (475 adjudication + 5 correction + 23 unchanged),
все 1 090 agreements и grid 1 565/1 565, `error=0`, `uncertain=0`, SHA
`f0fd4393…` / `ceb8b61f…`. Реальный one-book registry probe повторно
проверил семь SHA-locked звеньев, все пять исходно agreed исправлений и
полный grid; proof `gold_correction_registry_dan_probe.manifest.json`.
`Dan` принята. `Hos` independent QC проверил 260 adjudicated и 943 agreed,
grid 1 203/1 203, `error=0`, `uncertain=0`, SHA `b1529877…` / `afe7d5e2…`;
книга принята. `Joel` (029) blind pass 2/comparison также
заморожены: 32 стиха, 745 original + 644 target, 857 agreements / 532
substantive disagreements, double expansion и root compact check PASS;
exact SHA в `gold_review_batch_029.manifest.json`. `Joel` distinct adjudication
532/532 завершена в 239 компонентах, grid 1 389/1 389, SHA `29844bc0…` /
`ffbcbeca…`. Blocking QC нашёл две ошибочные adjudicated строки в `Joel.2.27`,
после чего отдельная two-row correction и новый независимый QC приняли
535/535 наблюдений с `error=0`, `uncertain=0`; one-book registry proof
подтвердил corrected grid 1 389/1 389 и SHA семантики `7b6deb9a…`.
`Joel` принята, но global 66-book finalize не выполнялся. `Amos` blind pass 2/comparison
и adjudication 372/372 завершены, а distinct QC проверил 1 097 agreements,
grid 1 469/1 469 с `error=0`, `uncertain=0`, SHA `492db6a8…` / `9f9988e3…`;
книга принята. `Obad` pass 2/comparison и adjudication 217/217 завершены;
независимый QC проверил все 759 agreements и grid 976/976 без ошибок, книга
принята. `Jonah`, `Mic`, `Nah` и `Hab` завершили blind pass 2/comparison:
соответственно 452, 331, 175 и 350 substantive disagreement. `Jonah` distinct
adjudication 452/452 прошла root validator, grid 1 527/1 527, включая
локальную семантику `Jonah.1.11` и MT-вариант `Jonah.3.4`; independent QC
проверил 452 adjudicated и 1 075 agreed решений без ошибок, книга принята.
`Mic` прошла distinct adjudication 331/331, затем independent full-grid QC
обнаружил три ошибочные H7725G-решения в `2.8` (grid 1 486/1 486) и
временно заблокировал книгу. Scoped three-row correction с null-accounting
для source «return» и украинских «як здо́бич» прошла два byte-identical
прогона и `seal-correction`; новый distinct re-QC проверил 336 observations,
весь исправленный grid 1 486/1 486 и 1 155 agreements без error/uncertain.
Real-input one-book correction registry probe дважды подтвердил все 1 486
семантик; `Mic` принята на уровне книги, глобальный finalize не запускался.
`Nah` прошла distinct adjudication 175/175, затем full-grid QC (1 197/1 197)
зафиксировал пять critical textual uncertainties в `1.8`; source MT говорит
«its place», локальный LXX-контроль — «those rising up», что напоминает
OH1988 «заколотниками». Точное исходное чтение переводчика не доказано,
номер из соседнего стиха или греческого контроля не переносится; книга
заблокирована. На листе 1156 скана точного издания (печатная стр. 1152)
нет поясняющей сноски к этому стиху. Отдельный diagnostic addendum закрепил
SHA источников и отсутствие права на automatic Strong. `Hab` завершила
distinct adjudication 350/350 и независимый full-grid QC всех 1 410 решений
без error/uncertain; книга принята. `Zeph` завершила adjudication 251/251,
но independent QC оставил четыре high textual uncertainties в `2.14` и
`3.17`, поэтому книга заблокирована. Дополнительный source-audit визуально
проверил печатные страницы OH1988 `Nah.1.8`, `Zeph.2.14`, `Zeph.3.17`
без сносок к этим loci и первичное свидетельство переводчика 1963 года:
основа OT была еврейской, LXX привлекалась выборочно, но точный экземпляр
или чтение этих стихов не названо. Девять high/critical IDs остаются
заблокированными; SHA и границы вывода записаны в
`textual_fingerprint_nah_zeph_primary_audit.manifest.json`.
`Hag` и `Zech` затем завершили distinct adjudication соответственно 522/522
и 278/278 расхождений с полным grid 1 595/1 595 и 1 606/1 606.
`Hag` прошла отдельный independent full-grid QC всех 1 595 решений без
ошибок/uncertain и принята; `Zech` прошла отдельный full-grid QC всех
1 606 решений, но семь high/critical в `11.7`/`14.6` остаются uncertain,
поэтому книга заблокирована. В этих местах textual
решений остаются unresolved: сходство с LXX не является доказательством
точного исходного чтения Огиенко или основанием переносить Strong.
Диагностический addendum `textual_fingerprint_zech_11_7_14_6.manifest.json`
закрепил SHA двух визуально проверенных страниц (печатные с. 1173/1176),
двух стихов MT/LXX и семи high/critical IDs; собственных авторских сносок
к этим стихам нет. Точный исторический оригинал остаётся недоказанным.
`Mal` затем завершила distinct adjudication 440/440 разногласий, сохранив
1 173 agreements и grid 1 613/1 613. Independent full-grid QC обнаружил
две reciprocal ошибочные привязки в `3.11`: raw H9003 (article/preposition)
не доказывает украинское «все». Отдельная two-row correction оставила
H9003↔«те», а «все» — translation addition; три одинаковых прогона и
`seal-correction` прошли. Отдельный reviewer затем принял 443/443
post-correction наблюдения (`error=0`, `uncertain=0`) при полном grid
1 613/1 613. Root physical SHA, `check-correction-qc` и два byte-identical
real one-book correction-aware registry прогона прошли: никаких пропавших
или дублированных stable IDs; exact SHA зафиксированы в
`gold_adjudication_batch_039.manifest.json` и
`gold_correction_registry_mal_probe.manifest.json`. Книга принята, но
66-book gold ещё не финализирован.

`Mat` завершила отдельный blind pass 2 на 39 стихах (691 original + 667
target = 1 358 решений). После SHA-freeze два byte-identical post-blind
comparison прогона зафиксировали 1 072 согласованных решения и 286
substantive disagreements (186 original + 100 target), без ошибок структуры.
Distinct third adjudication затем разобрала все 286/286 substantive
disagreements в 138 verse-local компонентах, сохранила 1 072 agreements и
точную сетку 1 358/1 358; root SHA и `check-adjudication` прошли.
`Mat.21.30` остаётся critical textual-source uncertainty: selected Greek
говорит о не пошедшем сыне, а OH1988 — о первоначально отказавшемся, но
пошедшем. Независимый source-audit издательского аппарата SBLGNT нашёл
семантически близкий вариант Westcott–Hort для `21.29–31`, однако точную
греческую Vorlage Огиенко не доказывает; диагностический SHA закреплён в
`textual_fingerprint_mat_21_30.manifest.json`. Альтернативные чтения не
стали основанием для Strong assignment.
Полный независимый QC теперь проверил 286 adjudicated + 1 072 agreed =
1 358/1 358 stable decisions: 1 343 accepted, 15 critical source-uncertain
(все `Mat.21.30`, включая 8 исходно согласованных), content errors 0.
Три эмиссии побайтно совпали; root SHA QC/sidecar `793f54aa…` /
`f8116493…` подтверждены, `check-adjudication-qc` ожидаемо отклонил
blocking status. Доказательство конкретной исходной редакции и отдельный
re-QC ещё нужны; `Mat` не принята. SHA и ограничения закреплены в
`gold_review_batch_040.manifest.json` и
`gold_adjudication_batch_040.manifest.json`.
`Mark` также завершила отдельный blind pass 2 на 40 стихах (681 original +
647 target = 1 328 решений). После заморозки два побайтно одинаковых
comparison прогона дали 1 039 agreements и 289 substantive disagreements
(201 original + 88 target), `error=0`. Короткое и длинное окончания главы 16,
а также другие source-apparatus места сохраняются раздельно и не служат
автоматическим основанием для Strong. Distinct third adjudication уже
разрешила 289/289 disagreement в 171 компонентах, сохранив 1 039 agreements
и полный grid 1 328/1 328; root `check-adjudication` PASS, три эмиссии
byte-identical. Три critical textual-choice loci `Mark.1.2`, `16.8`, `16.9`
остаются unresolved. В `16.8` 34 bracketed Short Ending source atoms
учтены как `source_text_not_rendered`, не доказанный переводческий пропуск;
Независимый full-grid QC теперь проверил 1 328/1 328 решений: 1 324
accepted, 4 critical source-choice uncertain (все pass-agreed в `1.2` /
`16.9`), content errors 0. `9.38`, `10.7`, `15.28` и 34 Short Ending atoms
проверены отдельно; root physical QC SHA `753de840…` / `416193d2…`, три
byte-identical эмиссии и ожидаемый fail-closed checker. `Mark` не принята:
текстологические чтения и provenance SHA rebase остаются открытыми.
SHA-цепочка закреплена в `gold_review_batch_041.manifest.json` и
`gold_adjudication_batch_041.manifest.json`.
`Luke` завершила независимый blind pass 2 на 39 стихах (606 original +
604 target = 1 210 решений). Двойной post-blind comparison дал 960
agreements и 250 substantive disagreements (160 original + 90 target),
665 metadata-only differences, `error=0`; оба прогона byte-identical.
Distinct third adjudication разрешила 250/250 расхождений в 105 компонентах,
сохранила 960 agreements и полный grid 1 210/1 210; root
`check-adjudication` PASS, две byte-identical эмиссии. `Luke.10.15`
μὴ/G3361 не имеет доказанного отрицательного соответствия в положительном
OH1988; critical source/rendering uncertainty оставлена открытой.
`Luke.2.11` — согласованный контроль: G3739→«Який», G4771→«для»/«вас»,
старое G3739→«вас» не принято. Независимый full-grid QC проверил все
1 210/1 210 решений: 1 196 accepted, 14 source-choice uncertain в
`1.76`, `10.15`, `10.42`, `13.7`, `16.21`, `20.34`, content errors 0.
Три побайтно одинаковых QC выпуска и ожидаемое blocking-отклонение
validator подтверждены; QC/sidecar SHA `9c34b5a2…` / `c5df3e4b…`.
Adjudication и blocking-QC SHA уже явно перебазированы без изменения
ни одного решения; source resolution и независимый re-QC ещё нужны.
Книга не принята. SHA-цепочка в
`gold_review_batch_042.manifest.json` и
`gold_adjudication_batch_042.manifest.json`.
`John` также завершила blind pass 2 на 36 стихах (593 original + 577
target = 1 170 решений). После SHA-freeze два byte-identical comparison
прогона дали 1 039 agreements и 131 substantive disagreement (108 original +
23 target), 719 metadata-only differences, `error=0`. Издательские чтения
`1.18`, `5.4`, `7.53–8.11` и сноска `19.34` требуют отдельной source-qualified
проверки. Distinct adjudication по исправленной provenance SHA-цепочке
разрешила 131/131 disagreement в 98 компонентах, сохранила 1 039
agreements и полный grid 1 170/1 170. Root `check-adjudication` PASS,
два выпуска побайтно одинаковы, физические adjudication/sidecar SHA
`139ffd0f…` / `5410146d…` в `gold_adjudication_batch_043.manifest.json`.
Независимый full-grid QC затем проверил все 1 170/1 170 решений: 1 160
accepted, 10 source-choice uncertain в `1.18`, `1.28`, `8.11`, `14.15`,
content errors 0. Три QC/sidecar выпуска побайтно одинаковы, root
`check-adjudication-qc` ожидаемо отклонил blocking status; физические SHA
`67233ff0…` / `08c0a235…` закреплены в
`gold_adjudication_batch_043.manifest.json`. `5.4` «Господній» не получил
выдуманный `G2962`; `19.34` авторское `πλευράν — бока` сверено.
Source resolution/re-QC ещё нужны; книга не принята.
`Acts` завершила blind pass 2 на 39 стихах (720 original + 716 target =
1 436 решений). Два byte-identical comparison прогона дали 1 175 agreements,
261 substantive disagreement (182 original + 79 target), 962 metadata-only
differences, `error=0`. Distinct third adjudication разрешила 261/261
disagreements в 145 компонентах, сохранила 1 175 agreements и полный
grid 1 436/1 436; root `check-adjudication` PASS, два выпуска побайтно
одинаковы, adjudication/sidecar SHA `69315757…` / `c5adb14b…` в
`gold_adjudication_batch_044.manifest.json`. Independent full-grid QC
проверил все 261 adjudicated и 1 175 agreed решения (1 436/1 436):
1 399 accepted, две reciprocal errors в `13.29` и 35 source/semantic
uncertain в `2.38`, `5.34`, `13.26`, `15.34`, `27.12`.
Одна ошибка затрагивает adjudicated original `καθελόντες/G2507`,
другая — originally agreed украинское «то»: первому соответствуют
«зняли Його», а «то» не имеет этой греческой основы. Три эмиссии
побайтно одинаковы, QC/sidecar SHA `a77ef5dd…` / `0fae5c28…`
закреплены; `check-adjudication-qc` ожидаемо отверг blocking status.
Отдельная exact two-row scoped correction уже прошла три побайтно
одинаковых выпуска и `seal-correction` с исправленным grid
1 436/1 436: correction/sidecar SHA `c1ee34fe…` / `7c30e54b…`.
Distinct independent post-correction full-grid QC уже проверил все
1 436/1 436 решений: 1 401 accepted, `error=0`, 35 source/semantic
uncertain в `2.38`, `5.34`, `13.26`, `15.34`, `27.12`.
Три выпуска побайтно одинаковы, физические QC/sidecar SHA
`1520e928…` / `256a3a70…` закреплены в
`gold_adjudication_batch_044.manifest.json`; root `check-correction-qc`
ожидаемо отклонил блокирующий source-choice status. Нужны отдельное
разрешение источников и новый re-QC; книга не принята.
Blind SHA-цепочка в
`gold_review_batch_044.manifest.json`.
`Rom` завершила blind pass 2 на 33 стихах (520 original + 536 target =
1 056 решений). Два byte-identical comparison/sidecar прогона дали 866
agreements, 190 substantive disagreements (127 original + 63 target),
535 metadata-only differences, `error=0`. Distinct third adjudication
разрешила 190/190 disagreement в 94 компонентах, сохранила 866 agreements
и grid 1 056/1 056; root `check-adjudication` PASS, два выпуска побайтно
одинаковы, adjudication/sidecar SHA `42483a9c…` / `43375656…` в
`gold_adjudication_batch_045.manifest.json`. `3.22`, `6.1`, `6.11`, `13.11`
остались critical source/segmentation unresolved, `ὑμᾶς/G4771` не
назначено «нам» по сходству с альтернативой. Independent full-grid QC
проверил все 190 adjudicated и 866 agreed решения (1 056/1 056):
1 037 accepted, `error=0`, 19 source/semantic uncertain по девяти
loci (`3.22`, `6.1`, `6.11`, `9.31`, `11.25`, `12.5`, `13.11`,
`15.8`, `15.15`). Три выпуска побайтно одинаковы, физические
QC/sidecar SHA `778c7318…` / `670ea20f…` закреплены в
`gold_adjudication_batch_045.manifest.json`; root validator ожидаемо
отклонил blocking status. Source resolution/re-QC ещё нужны, книга
не принята. Blind SHA-цепочка в
`gold_review_batch_045.manifest.json`.
`1Cor` завершила blind pass 2 на 33 стихах (471 original + 481 target =
952 решения). Два byte-identical comparison/sidecar прогона дали 777
agreements, 175 substantive disagreements (116 original + 59 target),
571 metadata-only differences, `error=0`; `8.2`, `10.28`, `11.31`, `14.34`
оставлены source-qualified. SHA-цепочка в `gold_review_batch_046.manifest.json`;
distinct third adjudication разрешила 175/175 disagreement в 96
компонентах, сохранила 777 agreements и grid 952/952; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, adjudication/sidecar
SHA `d6c5cd7a…` / `8ea22cf7…` в
`gold_adjudication_batch_046.manifest.json`. Четыре source-choice
watchpoints после adjudication расширены независимой full-grid QC:
175 adjudicated + 777 agreed = 952/952, 932 accepted, `error=0`,
20 source-choice uncertain (9 adjudicated + 11 agreed) в `8.2`,
`10.28`, `11.26`, `11.31`, `14.34`. Три выпуска побайтно одинаковы,
физические QC/sidecar SHA `6df87695…` / `c8fa94f4…` закреплены в
`gold_adjudication_batch_046.manifest.json`; root validator ожидаемо
отклонил blocking status. Source resolution/re-QC ещё нужны;
книга не принята.
`2Cor` завершила blind pass 2 на 34 стихах (540 original + 543 target =
1 083 решения). Два byte-identical comparison/sidecar прогона дали 916
agreements, 167 substantive disagreements (117 original + 50 target),
706 metadata-only differences, `error=0`; `5.3`, `7.12`, `9.8`, `11.28`
оставлены source-qualified. SHA-цепочка в `gold_review_batch_047.manifest.json`;
distinct third adjudication разрешила 167/167 disagreement в 103
компонентах, сохранила 916 agreements и grid 1 083/1 083; два
выпуска побайтно одинаковы, root `check-adjudication` PASS,
adjudication/sidecar SHA `0ba52794…` / `78d71c65…` в
`gold_adjudication_batch_047.manifest.json`. Семь source/segmentation
watchpoints, включая согласованные target additions `5.18` и
verse-boundary `10.4`, оставлены fail-closed. Independent full-grid
QC проверил 167 adjudicated + 916 agreed = 1 083/1 083 решений:
1 052 accepted, `error=0`, 31 source/verse-boundary uncertain (8
adjudicated + 23 agreed) в десяти loci. Три выпуска побайтно одинаковы,
физические QC/sidecar SHA `8a30d2a8…` / `9fb4091d…` закреплены в
`gold_adjudication_batch_047.manifest.json`; root validator ожидаемо
отклонил blocking status. В `7.12` аппарат фиксирует альтернативное
чтение местоимений; bracketed TAGNT locators в `8.13`/`10.4` лежат
вне замороженного selected layer. Ни один альтернативный или
межстиховой Strong не перенесён. Нужны source resolution/re-QC;
книга не принята.
`Gal` завершила blind pass 2 на 32 стихах (499 original + 556 target =
1 055 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison/sidecar прогона дали 853 agreements, 202
substantive disagreements (120 original + 82 target), 635 metadata-only
differences. Exact SHA-цепочка в `gold_review_batch_048.manifest.json`;
`3.1`, `4.7`, `4.14` остаются source-qualified; книга не принята.
Distinct third adjudication `Gal` разрешила 202/202 disagreement в 91
компоненте, сохранила 853 agreements и grid 1 055/1 055; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `628bf95b…` / `847542aa…` в
`gold_adjudication_batch_048.manifest.json`. `2.2`, `3.1`, `4.7`,
`4.14` остаются source/semantic blockers, а agreed target additions
`3.1`/`4.7` требуют проверки полного grid. Ни один TR/Byz-only Strong
не перенесён. Independent full-grid QC проверила 202 adjudicated +
853 agreed = 1 055/1 055: 1 037 accepted, `error=0`, 18 source-choice
uncertain (9 adjudicated + 9 agreed) по шести loci `2.6`, `3.1`,
`3.23`, `4.7`, `4.14`, `5.10`. Три выпуска побайтно одинаковы,
физические QC/sidecar SHA `4308527f…` / `738fcb27…` закреплены в
`gold_adjudication_batch_048.manifest.json`; root validator ожидаемо
отклонил blocking status. `2.2` корректно остаётся source-omitted/
target-addition. Source resolution/re-QC нужны, книга не принята.
`Eph` завершила blind pass 2 на 32 стихах (530 original + 460 target =
990 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison/sidecar прогона дали 762 agreements, 228
substantive disagreements (171 original + 57 target), 480 metadata-only
differences. Exact SHA-цепочка в `gold_review_batch_049.manifest.json`.
В `5.30` семь украинских слов отсутствующего selected Greek clause
оставлены null; textual/source resolution ещё нужны. Книга не принята.
Distinct third adjudication `Eph` разрешила 228/228 disagreement в
152 компонентах, сохранила 762 agreements и grid 990/990; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `b58d2938…` / `9708ea53…` в
`gold_adjudication_batch_049.manifest.json`. `3.9`, `4.8`, `5.30`
остаются source/semantic blockers; семь согласованных target additions
`5.30` не получили TR/Byz-only Strong. Independent full-grid QC
проверила 228 adjudicated + 762 agreed = 990/990 решений: 970
accepted, две reciprocal originally-agreed content errors `5.2`
(`ἡμᾶς/G3165` ↔ «вас»), 18 source-choice uncertain в шести loci.
Три выпуска побайтно одинаковы, физические QC/sidecar SHA
`27b7ffec…` / `6c0091df…` в
`gold_adjudication_batch_049.manifest.json`; root validator ожидаемо
отклонил blocking status. Требуются exact two-row correction,
source resolution и distinct post-correction QC; книга не принята.
`Phil` завершила blind pass 2 на 32 стихах (499 original + 536 target =
1 035 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison/sidecar выпуска дали 821 agreements, 214
substantive disagreements (127 original + 87 target), 621 metadata-only
differences. Exact SHA-цепочка в `gold_review_batch_050.manifest.json`;
`2.7`, `2.26`, `3.18`, `4.13`, `4.23` оставлены source-qualified
без межстихового переноса Strong. Книга не принята.
Distinct third adjudication `Phil` разрешила 214/214 disagreement в
84 компонентах, сохранила 821 agreements и grid 1 035/1 035; два
выпуска побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `2539e53a…` / `a3cc7e28…` в
`gold_adjudication_batch_050.manifest.json`. `2.7`, `2.26`, `4.13`,
`4.23` остаются source/verse-boundary blockers; согласованные target
additions в `2.7`/`4.13` не получили чужой Strong. Independent
full-grid QC и source resolution обязательны; книга не принята.
`Col` завершила blind pass 2 на 33 стихах (526 original + 491 target =
1 017 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 803 agreements, 214 substantive
disagreements (151 original + 63 target), 544 metadata-only differences.
Физические comparison/sidecar SHA `14adfa41…` / `194f4724…` в
`gold_review_batch_051.manifest.json`. `1.12`, `3.4`, `3.15`, `3.16`,
`3.22` сохраняют critical source-choice blockers; `1.16` содержит
переставленные группы, которые не разрешают позиционный перенос.
Книга не принята.
Distinct third adjudication `Col` разрешила 214/214 disagreement в
127 компонентах, сохранила 803 agreements и grid 1 017/1 017; два
выпуска побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `023c7533…` / `d12d2920…` в
`gold_adjudication_batch_051.manifest.json`. Пять selected-source/OH
mismatch loci `1.12`, `3.4`, `3.15`, `3.16`, `3.22` остаются critical;
аттестованные альтернативы не доказывают точный Vorlage Огиенко.
Переставленные группы `1.16` связаны reciprocal token evidence,
а не позицией. Independent full-grid QC нужна; книга не принята.
`1Thess` завершила blind pass 2 на 32 стихах (531 original + 506 target =
1 037 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 874 agreements, 163 substantive
disagreements (117 original + 46 target), 608 metadata-only differences.
Физические comparison/sidecar SHA `df4c25e6…` / `aeec643c…` в
`gold_review_batch_052.manifest.json`. `2.6`, `2.11`, `3.2`, `3.5`
остаются source/segmentation watchpoints, без переноса Strong по
позиции; книга не принята.
Distinct third adjudication `1Thess` разрешила 163/163 disagreement в
108 компонентах, сохранила 874 agreements и grid 1 037/1 037; два
выпуска побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `8d913a35…` / `b2e8ea43…` в
`gold_adjudication_batch_052.manifest.json`. `2.6`, `2.11`, `3.2`
остаются source/segmentation blockers; нет межстихового или
альтернативного переноса Strong. Independent full-grid QC нужна;
книга не принята.
`2Thess` завершила blind pass 2 на 32 стихах (603 original + 597 target =
1 200 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 948 agreements, 252 substantive
disagreements (163 original + 89 target), 570 metadata-only differences.
Физические comparison/sidecar SHA `ec99f04a…` / `1ed413e7…` в
`gold_review_batch_053.manifest.json`. `1.4`, `2.3`, `2.7`, `2.13`,
`3.6`, `3.11` остаются source/semantic watchpoints; selected Greek
«firstfruits» и украинское «спочатку» в `2.13` не объявлены
эквивалентными без доказательства. Distinct adjudication/QC нужны;
книга не принята.
`1Tim` завершила blind pass 2 на 33 стихах (483 original + 530 target =
1 013 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 814 agreements, 199 substantive
disagreements (113 original + 86 target), 563 metadata-only differences.
Физические comparison/sidecar SHA `34dea918…` / `b13c4dd7…` в
`gold_review_batch_054.manifest.json`. Слитное surface `2.2` сохранено
точно по stage 6; `3.16`, `5.16`, `5.21`, `6.3`, `6.10`, `6.21`
требуют source/lexical adjudication/QC; книга не принята.
`2Tim` завершила blind pass 2 на 32 стихах (513 original + 507 target =
1 020 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 848 agreements, 172 substantive
disagreements (118 original + 54 target), 587 metadata-only differences.
Физические comparison/sidecar SHA `96dfda02…` / `49a084fc…` в
`gold_review_batch_055.manifest.json`. Слитное surface `3.15`
сохранено точно по stage 6; `1.5`, `2.16`, `3.8`, `3.10`, `4.3`,
`4.14`, `4.22` остаются source/lexical watchpoints. Distinct
adjudication/QC нужны; книга не принята.
`Titus` завершила blind pass 2 на 32 стихах (460 original + 473 target =
933 решения). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 789 agreements, 144 substantive
disagreements (92 original + 52 target), 443 metadata-only differences.
Физические comparison/sidecar SHA `01633d4a…` / `0fa88340…` в
`gold_review_batch_056.manifest.json`. `1.4`, `1.6`, `1.9`, `2.7`,
`2.15`, `3.4`, `3.15` остаются source/lexical watchpoints; отсутствующий
selected original не получает Strong. Distinct adjudication/QC нужны;
книга не принята.
`Phlm` завершила blind pass 2 на 25 стихах (338 original + 358 target =
696 решений). Root compact check прошёл с `error_count=0`; два
byte-identical comparison выпуска дали 567 agreements, 129 substantive
disagreements (79 original + 50 target), 429 metadata-only differences.
Физические comparison/sidecar SHA `72865f9d…` / `7044fb2f…` в
`gold_review_batch_057.manifest.json`. `1.2`, `1.7`, `1.10`, `1.16`,
`1.20`, `1.21`, `1.25` остаются source/lexical watchpoints; raw
`G6063` не превращён в выдуманный classic Strong. Distinct
adjudication/QC нужны; книга не принята.

В замороженных blind pass 2 для `Mark`/`Luke`/`John` найден отдельный
provenance-дефект общего renderer: текст `Independent blind Mat pass 2` и
пространство evidence ID `uk7:mat:p2` ошибочно остались в book-specific
ответах. Сами manual maps составлялись по отдельным пакетам книг. Исходные
compact/raw JSONL и их SHA оставлены неизменными. Строгий metadata-only repair
заменил ровно 1 893 служебные подписи; два независимых выпуска для каждой
книги, expanded checks и новый double comparison совпали побайтно. Семантика
всех 3 708 решений осталась неизменной, расхождения сохранились 289/250/131.
Доказательства в `gold_pass2_provenance_repair.manifest.json`. Это не новый
blind pass и не принятие книг. Для `Mark` и `Luke` отдельный SHA-locked
downstream rebase пересвязал прежние 289 + 250 adjudicated decisions с
исправленными pass2/comparison: 539 decision rows не изменились, два
побайтно одинаковых прогона и root `check-adjudication` прошли. Новый
`gold_adjudication_provenance_rebase.manifest.json` фиксирует old/new SHA.
Отдельный `gold_qc_provenance_rebase.manifest.json` фиксирует также
metadata-only reproof уже проведённых blocking-QC `Mark`/`Luke`:
539/539 result rows, 2 538 full-grid positions, 4/14 uncertain и ноль
content errors неизменны, новый SHA/sidecar побайтно воспроизводимы.
QC остаётся заблокированной из-за textual uncertainties; источник нужно
разрешить и провести независимый re-QC, прежде чем принимать книги.
`John` уже прошла distinct adjudication и independent blocking full-grid
QC по исправленной цепочке; десять source-choice uncertainties требуют
отдельного разрешения и re-QC.

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

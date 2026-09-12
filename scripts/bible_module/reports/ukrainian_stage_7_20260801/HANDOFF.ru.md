# Этап 7 — текущий HANDOFF, рабочая точка 2026-09-12

> **CURRENT WORK POINT.** Этот файл полностью заменяет предыдущий HANDOFF.
> Этап 7 остаётся в работе. Этап 8 и SQLite не начинались. Удалённый LLM-сервис
> на `COMP_NAZARA` по прямому указанию владельца остаётся остановленным и не
> должен запускаться или опрашиваться. Commit/push автоматически не выполнять.

## Пауза по просьбе владельца — 2026-09-12

- Все три задействованных агента завершили ограниченные задания и остановлены;
  новых book/QC jobs не начинать до явного возобновления. Запущенные ранее
  проверки Flutter завершились; фоновых команд этого сеанса не осталось.
- Актуальная строгая граница: pass 1 `66/66`, blind pass 2 + comparison
  `57/66` (`Gen–Phlm`), полностью adjudicated + independent full-grid QC
  без ошибок и unresolved `36/66`. Никакой результат следующей книги не
  следует считать принятым только из-за наличия pass 2 либо adjudication.
- Последние результаты: `Phlm` pass 2/comparison (`25` стихов, `696`
  decisions, `129` disagreements); `1Thess` adjudication (`163/163`
  disagreements, `1 037/1 037` grid) при трёх unresolved source loci;
  `Eph` independent QC (`990/990`, `2` content errors в `Eph.5.2`,
  `18` source uncertainties). Все три книги остаются непринятыми.
- При следующем возобновлении начать с проверки `git status` и SHA-lock,
  затем `Heb` blind pass 2 (shard 058), независимые QC для `Phil`/`Col`/
  `1Thess`, exact two-row correction + distinct re-QC `Eph.5.2`, затем
  adjudication/QC `2Thess–Phlm` и разрешение прочих блокирующих source loci.
  Эти направления можно упорядочить по доступности независимых рецензентов,
  но не считать их выполненными заранее. Remote LLM `COMP_NAZARA` не трогать.
- Последняя полная проверка: bible-module `415/415`, content-tool `30/30`,
  stage 3–6 `--check` PASS, docs-sync и forbidden-pattern PASS; `flutter
  analyze` завершился четырьмя warning в нетронутых Dart-файлах, `flutter
  test` — `918` passed / `2` failed в нетронутых Strong-dictionary tests.
  После checkpoint-документирования два изменившихся doc SHA-lock обновлены
  в `artifact_inventory.manifest.json`, итоговый stage-7 `--check` завершился
  PASS (`processed_count=31 102`, `accepted_links=0`, `error_count=0`),
  `git diff --check` — exit 0. Не использовать исторические результаты ниже
  как более свежие. Stage 8, SQLite, commit и push не выполнялись.

## Состояние репозитория

- На начало возобновления последним commit был `64ccae9`
  (`Advance stage 7 gold review through Isaiah [skip ci]`), worktree чист.
  Изменения этого сеанса ограничены stage-7 roadmap/report/log/HANDOFF и новыми
  `gold_adjudication_batch_023.manifest.json`, `gold_review_batch_024.manifest.json`,
  `gold_review_batch_025.manifest.json`, `gold_review_batch_026.manifest.json`,
  `gold_review_batch_027.manifest.json`,
  `gold_review_batch_028.manifest.json`,
  `gold_review_batch_029.manifest.json`,
  `gold_review_batch_030.manifest.json`,
  `gold_review_batch_031.manifest.json`,
  `gold_review_batch_032.manifest.json`,
  `gold_review_batch_033.manifest.json`,
  `gold_review_batch_034.manifest.json`,
  `gold_review_batch_035.manifest.json`,
  `gold_review_batch_036.manifest.json`–`gold_review_batch_057.manifest.json`,
  `gold_adjudication_batch_024.manifest.json`,
  `gold_adjudication_batch_025.manifest.json`,
  `gold_adjudication_batch_026.manifest.json`,
  `gold_adjudication_batch_027.manifest.json`,
  `gold_adjudication_batch_028.manifest.json`,
  `gold_adjudication_batch_029.manifest.json`,
  `gold_adjudication_batch_030.manifest.json`,
  `gold_adjudication_batch_031.manifest.json`,
  `gold_adjudication_batch_032.manifest.json`,
  `gold_adjudication_batch_033.manifest.json`,
  `gold_adjudication_batch_034.manifest.json`–`gold_adjudication_batch_052.manifest.json`,
  `gold_pass2_provenance_repair.manifest.json`,
  `gold_adjudication_provenance_rebase.manifest.json`,
  `gold_qc_provenance_rebase.manifest.json`,
  `gold_correction_registry_mal_probe.manifest.json`,
  `gold_qc_blocking_batch_033_034.manifest.json`,
  `textual_fingerprint_nah_1_8.manifest.json`,
  `textual_fingerprint_nah_zeph_primary_audit.manifest.json`,
  `textual_fingerprint_mat_21_30.manifest.json`,
  `textual_fingerprint_zech_11_7_14_6.manifest.json`,
  `gold_correction_registry_isa_probe.manifest.json`,
  `gold_correction_registry_dan_probe.manifest.json`,
  `gold_correction_registry_joel_probe.manifest.json`,
  `gold_correction_registry_mic_probe.manifest.json`, correction-aware gold,
  provenance/rebase/QC code and tests
  и двумя doc SHA-lock в `artifact_inventory.manifest.json`; рабочие генераторы и полные JSONL
  находятся только в gitignored `work`. Любые последующие изменения владельца
  сохранять без перезаписи.
- Полные corpus/review/comparison/adjudication JSONL находятся только в
  gitignored `scripts/bible_module/work/ukrainian_stage_7_20260801/`.

## Неизменяемые входы

- edition/module/code: `ohienko_1988` / `ohienko_1988` / `OH1988`;
- canon/versification/mapping: `protestant_66` / `kjv_protestant` /
  `oh1988-kjv-protestant-v1`;
- target positions: `31 102`;
- stage-6 text SHA-256:
  `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- stage-6 manifest SHA-256:
  `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- stage-6 comments SHA-256:
  `5c1cf56e94410b6ab6e418dda7be7a6b385cb72221dfb8ca943e3419de42c9f4`;
- production Strong assignments/markers и `resolver_eligible` остаются `0` до
  finalized gold и calibration.

## Текущий результат gold 7.4

1. Все внешние pass-1 результаты `1Sam–Rev` (58 книг) локально
   canonicalized/expanded/checked без исправления смысловых решений догадками:
   1 911 стихов, 39 148 original и 36 248 target-accounting decisions.
2. Вместе с `Gen–Ruth` полный pass 1 объединён и принят workflow:
   2 171 стих, 45 831 original, 41 807 target, 66 reviewer IDs,
   `error_count=0`.
   - merged SHA-256:
     `40a644da0193fc705dd9af9ff5cc63901d2e2e9f3394ac83cc586b21ef37eaee`;
   - validated SHA-256:
     `681dc4fb5265146518aab2dd9b6cd806436a41be655786337e95f18f19becb7b`.
3. Pass 2 и post-blind comparison завершены для `Gen–Phlm` (первые 57 книг):
   1 923 стиха, 41 128 original и 37 209 target decisions. Новые `2Kgs–Phlm`
   независимо повторно прошли `gold_compact check`, `error_count=0`.
   Полная цепочка adjudication + independent QC уже принята для `2Kgs–Esth`;
   `Neh` принят после отдельной seven-row consensus correction и повторного QC;
   `Ps` — после отдельной 13-row correction и post-correction QC. Полная
   четырёхчастная цепочка теперь принята для `Gen–Song`. Для `Isa` 1 113 из
   1 365 stable decisions совпали; 252 расхождения разрешены третьей
   адъюдикацией. Blocking QC обнаружил три ошибочные stable-ID строки в
   `Isa.66.15`; scoped correction, независимый re-QC и real-input
   correction-aware registry probe всех 1 365 семантик приняты. `Isa` входит
   в book-level строгий счётчик, но global 66-book gold ещё не финализирован.
   `Jer` и `Lam` прошли distinct adjudication всех 404 и 180 substantive
   disagreements соответственно; обе прошли independent QC и приняты.
   `Ezek` прошла distinct adjudication 233/233 и independent QC без ошибок и
   принята. `Hos` и `Amos` прошли independent QC без ошибок и приняты. `Dan`
   после blocking QC пяти ошибочных originally-agreed IDs в `Dan.7.15`
   прошла five-row correction, distinct post-correction QC и real-input
   one-book registry probe; книга принята. `Joel` прошла blocking QC,
   two-row correction, distinct post-correction QC и real-input book proof;
   книга принята. `Obad`
   прошла distinct adjudication и independent QC без ошибок; книга принята.
   `Jonah` прошла distinct adjudication и independent QC без ошибок; книга
   принята. `Mic` после блокирующего QC трёх ошибок `Mic.2.8` прошла
   SHA-locked three-row correction, отдельный independent re-QC и реальный
   one-book correction-registry probe всех 1 486/1 486 решений; книга принята.
   `Nah` после полного independent QC заблокирована пятью critical textual
   uncertainties `Nah.1.8`: первичное MT `מְקוֹמָהּ` не поддерживает
   «заколотниками», LXX похожа, но точный Vorlage Огиенко не доказан;
   diagnostic addendum зафиксирован. `Hab` прошла distinct adjudication и
   независимый full-grid QC 1 410/1 410 без ошибок/uncertain; книга принята.
   `Zeph` после QC заблокирована четырьмя high textual uncertainties в 2.14/3.17.
   `Hag` прошла отдельный independent full-grid QC без ошибок и принята;
   `Zech` прошла distinct adjudication и full-grid independent QC,
   но заблокирована семью unresolved high/critical textual IDs;
   `Mal` прошла distinct adjudication; independent full-grid QC выявил две
   reciprocal ошибки в 3.11. SHA-locked correction прошла `seal-correction`,
   но distinct post-correction QC и real one-book registry proof ещё нужны.
4. Реализован новый deterministic post-blind
   `ukrainian_stage_7_gold_compare.py`:
   - реальные link/null расхождения отделяются от разной терминологии
     `severity/phenomena`;
   - совпавший alignment сохраняет union phenomena и максимальную severity;
   - adjudication может содержать только exact substantive disagreement set и
     после overlay повторно проходит полное verse-local accounting.
   Единый `check-adjudication-qc` дополнительно требует trusted QC-sidecar SHA,
   exact key/semantic/evidence/text/comment scope, distinct reviewer, полный
   reciprocal grid и нулевые error/uncertain; реальные `Lev`, `Num`, `Josh`
   проходят этот tracked контракт.
   Дополнительно production `ukrainian_stage_7_gold.py finalize` теперь
   требует `--correction-registry` с exact 66-book versioned accepted roster;
   исправленные и неисправленные книги повторно проходят физические SHA,
   независимый QC и локально-глобальное stable-ID accounting. Corrections
   применяются после adjudication, в том числе к исходно agreed ID. CC0
   regression 17/17 и full bible-module 400/400 PASS. Реальный one-book `Isa`
   probe доказал correction chain и exact 1 365/1 365 overlay; 66-book registry
   и global finalize остаются заблокированы до полного QC всех книг.
5. Сравнение `1Sam–1Kgs`: 5 274 stable decisions, 2 793 alignment agreements,
   2 481 substantive disagreements, 2 413 metadata-only differences. Все 2 481
   расхождение разрешены distinct third adjudication; повторный validator
   подтвердил exact overlay accounting 5 274/5 274. Независимый QC проверил
   1 128 уникальных строк, включая все critical/high и новые/pass-2 решения:
   `error=0`, `uncertain=0`.
6. Для накопленной очереди `Gen–Lev` distinct third adjudication структурно
   завершена и повторно провалидирована: `Gen` 230/230 и overlay 1 507,
   `Exod` 130/130 и overlay 1 382, `Lev` 216/216 и overlay 1 395.
   Content-QC разделяет их так:
   - `Gen` полностью принят: 230/230, включая 15 high и 4 new,
     `error=0`, `uncertain=0`;
   - первый `Exod` QC 130/130 дал 124 accepted / 6 error / 0 uncertain.
     Ошибки — три reciprocal пары в `Exod.27.1`, `32.19`, `32.35`, где
     `той/те` ошибочно связано с noun, а согласованный article `הַ/הָ`
     (HTd/H9009) оставлен null. Отдельный fail-closed consensus-correction уже
     создан и структурно принят: exact 9 semantic changes / 3 verses,
     `article→той/те`, `noun→noun`, overlay 1 382/1 382, correction SHA-256
     `ca53be00c26a2ab6d238e1abe495d8a9f306ca91c0493080a1860db38feb4c5a`;
     новый distinct reviewer проверил 130 adjudication + 9 correction + 3
     revalidate-only rows: 142 observations / 136 unique stable IDs, все 42
     high, `error=0`, `uncertain=0`; книга принята, final QC SHA-256
     `d79b394b22c516b814a2017f3660e3018f558c4f3176d40eacbc1b39adc19c67`;
   - `Lev` полностью принят: checkpoint 145/216 возобновлён по exact remaining
     IDs, проверены оставшиеся 71/71, итог 216/216, все 152 high и 10 new,
     `error=0`, `uncertain=0`; QC SHA-256
     `21bb8fc1c6d9f28b84bdffd828616d9093415c1a77c5daa042729d81ed001534`.
7. Для `Num` distinct adjudication разрешила 310/310 substantive disagreement,
   сохранила 1 186 согласованных решений и полный grid 1 496/1 496; отдельный
   independent QC принял все 310 решений, включая 56 high и 22 new, с
   `error=0`, `uncertain=0`. Для `Josh` adjudication 464/464 и отдельный
   independent QC также завершены: все 464 решения, 33 high и 59 new приняты
   с `error=0`, `uncertain=0`. Для `Judg` и `Ruth` adjudication и отдельный
   independent QC полностью завершены: соответственно 562/1 749 и 252/1 585,
   `error=0`, `uncertain=0`.
8. Строгий счётчик владельца (`pass 1 + pass 2 + full adjudication +
   independent QC` без `error`/`uncertain`) равен `36/66`: `Gen`, `Exod`,
   `Lev`, `Num`, `Deut`, `Josh`, `Judg`, `Ruth`, `1Sam`, `2Sam`, `1Kgs`,
   `2Kgs`, `1Chr`, `2Chr`, `Ezra`, `Neh`, `Esth`, `Job`, `Ps`, `Prov`, `Eccl`,
   `Song`, `Isa`, `Jer`, `Lam`, `Ezek`, `Dan`, `Hos`, `Joel`, `Amos`, `Obad`, `Jonah`,
   `Mic`, `Hab`, `Hag`, `Mal`.

Versioned доказательства текущей точки:

- `external_gold_pass1_batch_049_066.manifest.json`;
- `external_gold_pass1_batch_009_066.manifest.json`;
- `gold_alignment.pass1.manifest.json`;
- `gold_review_batch_005.manifest.json`;
- `gold_review_batch_009_011.manifest.json`;
- `gold_adjudication_batch_009_011.manifest.json`;
- `gold_review_batch_012_014.manifest.json`;
- `gold_review_batch_015.manifest.json`;
- `gold_review_batch_016.manifest.json`;
- `gold_review_batch_017.manifest.json`;
- `gold_review_batch_018.manifest.json`;
- `gold_review_batch_019.manifest.json`;
- `gold_review_batch_020.manifest.json`;
- `gold_review_batch_021.manifest.json`;
- `gold_review_batch_022.manifest.json`;
- `gold_review_batch_023.manifest.json`;
- `gold_review_batch_024.manifest.json`;
- `gold_review_batch_025.manifest.json`;
- `gold_review_batch_026.manifest.json`;
- `gold_adjudication_batch_001_003.manifest.json`;
- `gold_adjudication_batch_004.manifest.json`;
- `gold_adjudication_batch_005.manifest.json`;
- `gold_adjudication_batch_006.manifest.json`;
- `gold_adjudication_batch_007.manifest.json`;
- `gold_adjudication_batch_008.manifest.json`;
- `gold_adjudication_batch_012.manifest.json`;
- `gold_adjudication_batch_013.manifest.json`;
- `gold_adjudication_batch_014.manifest.json`;
- `gold_adjudication_batch_015.manifest.json`;
- `gold_adjudication_batch_016.manifest.json`;
- `gold_adjudication_batch_017.manifest.json`;
- `gold_adjudication_batch_018.manifest.json`;
- `gold_adjudication_batch_019.manifest.json`;
- `gold_adjudication_batch_020.manifest.json`;
- `gold_adjudication_batch_021.manifest.json`;
- `gold_adjudication_batch_022.manifest.json`;
- `gold_adjudication_batch_023.manifest.json` — `Isa` blocking QC,
  correction, distinct re-QC и book-level acceptance;
- `gold_correction_registry_isa_probe.manifest.json` — real-input
  correction-aware 1 365/1 365 proof, не 66-book finalize;
- `gold_adjudication_batch_024.manifest.json` — `Jer` adjudication и independent QC приняты;
- `gold_adjudication_batch_025.manifest.json` — `Lam` adjudication и полный independent QC приняты.
- `gold_adjudication_batch_026.manifest.json` — `Ezek` adjudication и independent QC приняты.
- `gold_review_batch_027.manifest.json` — `Dan` blind pass 2/comparison;
- `gold_review_batch_028.manifest.json` — `Hos` blind pass 2/comparison;
- `gold_adjudication_batch_027.manifest.json` и `gold_correction_registry_dan_probe.manifest.json` — `Dan` blocking QC, five-row correction, distinct post-correction QC и book-level acceptance;
- `gold_adjudication_batch_028.manifest.json` — `Hos` adjudication и independent QC приняты;
- `gold_review_batch_029.manifest.json`, `gold_adjudication_batch_029.manifest.json` и `gold_correction_registry_joel_probe.manifest.json` — `Joel` blocking QC, correction, distinct re-QC и real-input book proof приняты;
- `gold_review_batch_030.manifest.json` и `gold_adjudication_batch_030.manifest.json` — `Amos` comparison/adjudication/QC accepted;
- `gold_review_batch_031.manifest.json` и `gold_adjudication_batch_031.manifest.json` — `Obad` comparison/adjudication/QC приняты;
- `gold_review_batch_032.manifest.json` — `Jonah` blind pass 2/comparison;
- `gold_adjudication_batch_032.manifest.json` — `Jonah` distinct adjudication 452/452 и independent QC приняты;
- `gold_review_batch_033.manifest.json`, `gold_adjudication_batch_033.manifest.json` и `gold_correction_registry_mic_probe.manifest.json` — `Mic` correction, distinct re-QC и book-level acceptance;
- `gold_review_batch_034.manifest.json`, `gold_adjudication_batch_034.manifest.json` и `textual_fingerprint_nah_1_8.manifest.json` — `Nah` заблокирована unresolved critical textual locus;
- `gold_review_batch_035.manifest.json` и `gold_adjudication_batch_035.manifest.json` — `Hab` full-grid QC принят;
- `gold_review_batch_036.manifest.json` и `gold_adjudication_batch_036.manifest.json` — `Zeph` QC выявил четыре unresolved high textual cases;
- `gold_review_batch_037.manifest.json`–`gold_review_batch_057.manifest.json` — `Hag`–`Phlm` blind pass 2/comparison; `Hag` independent full-grid QC принята, `Zech` заблокирована семью textual uncertainties, `Mat` прошла independent full-grid QC с 15 critical uncertain IDs и ждёт source resolution/re-QC, `Mark`/`Luke`/`John` прошли блокирующий QC с 4/14/10 uncertain IDs, `Acts` прошла blocking QC с 2 error/35 uncertain, two-row correction и distinct post-correction QC с 0 error/35 uncertain, `Rom`/`1Cor`/`2Cor`/`Gal` прошли блокирующий QC (19/20/31/18 uncertain), `Eph` прошла blocking QC с 2 errors/18 uncertain, `Phil`/`Col`/`1Thess` прошли adjudication, `2Thess`/`1Tim`/`2Tim`/`Titus`/`Phlm` ждут adjudication/QC;
- `gold_adjudication_batch_041.manifest.json` — `Mark` distinct adjudication 289/289 и independent full-grid QC 1 328/1 328 с четырьмя critical source-choice IDs; книга не принята;
- `gold_adjudication_batch_042.manifest.json` — `Luke` distinct third adjudication 250/250, 1 210/1 210 grid, one unresolved `10.15` source-choice case; книга не принята;
- `gold_pass2_provenance_repair.manifest.json` — scoped metadata-only correction старого Mat renderer label в frozen `Mark`/`Luke`/`John`: 1 893 подписей, 3 708 неизменных semantic decisions, double re-expanded checks/comparisons; old QC SHA ещё требуют rebase, книги не приняты;
- `gold_adjudication_provenance_rebase.manifest.json` — 539 неизменных adjudication rows `Mark`/`Luke` и явно перебазированные SHA на исправленный pass2/comparison, double reproducibility и root validator PASS; это не QC/source resolution и не приёмка;
- `gold_qc_provenance_rebase.manifest.json` — 539 неизменных независимых QC result rows `Mark`/`Luke`, явно перебазированные SHA на исправленный pass2/comparison/adjudication, double reproducibility и ожидаемый blocking validator; 4/14 textual uncertainties остаются, это не новый QC и не приёмка;
- `gold_adjudication_batch_039.manifest.json` и `gold_correction_registry_mal_probe.manifest.json` — `Mal` correction, distinct re-QC и real-input book proof приняты.

## Активная работа на момент записи

На рабочей точке 2026-09-12 полная четырёхчастная цепочка принята для всех книг
`Gen–Song`, включая correction/re-QC `Neh` и `Ps`. `Isa` pass 2/comparison и
третья адъюдикация завершены: 252/252 substantive disagreement в 144
компонентах, 1 113 agreements, full grid 1 365/1 365. Две отдельные
генерации и `check-adjudication` совпали; adjudication/sidecar SHA-256:
`bb79e3daa4ec2bb32e6000690fbdf463a9a7507482853cda8b7c6285bebda47c` /
`0690822875dcc68dd55005e5d31c6f32e5662ab75d5668e9cb087574517d49e4`.
Полные ответы и генератор находятся в
`work/.../gold_review_adjudication/Isa/`; новый versioned указатель —
`gold_adjudication_batch_023.manifest.json`. Отдельный независимый content-QC
проверил 252/252 adjudicated, 144/144 компонента и 1 113/1 113 agreed строк:
250+1 112 приняты, три ошибочных stable ID в `Isa.66.15/C0141`, uncertain=0.
Blocking QC/sidecar SHA-256 `f4890fdb6afa16b0755ac3d0c764bbac80249e443a334b2901eb59ed43664b18` /
`0031caca33fe30d2979cd8b998b12ed9e6b20ea7f7ce4362f73a5ac39779f701`;
полные файлы в `work/.../gold_review_adjudication/Isa/qc/completed/`.
Отдельная scoped correction трёх stable IDs создана и прошла
`seal-correction`/`check-correction`: original H9003 → `в` при `огні`, лишнее
`у` → translation addition; correction/sidecar SHA-256
`929320462dc00f8fbada2c407e91708d19e9e16ac2dc9d63106806e075aa57ba` /
`000b4591d7177712c203e3d4b3216ebec50fcca792c12711618f329d3a3264f3`.
Полные файлы в `work/.../gold_review_adjudication/Isa/correction/completed/`.
Новый distinct post-correction QC проверил все 252 adjudicated решения, три
correction rows, один revalidate-only row и 1 113 исходных agreements:
`error=0`, `uncertain=0`, full grid 1 365/1 365, root `check-correction-qc`
PASS; QC/sidecar SHA-256 `31879520ca4548dbaf8191e7e471d42a73df6d831b46ae5fdb670ca2563a9676` /
`e4c292e968baf722c6d52ca2682022b2f7362fd031124b4b00153c8038b35c0e`.
Полный corrected overlay с исходно agreed t005 имеет SHA-256
`467a44de224a626a5f8aa905976e3e50828d9a473407c96fd38b867f3ce792b3`;
real-input one-book registry probe проверил все семь SHA-locked звеньев и
совпадение corrected semantics 1 365/1 365, включая originally agreed t005;
accepted manifest SHA-256 `9241e931790681da4ad59bc6601b0c420d319e05aaa0dc081cb9aba92ec5f432`,
probe registry SHA-256 `d31525f237ef90ed114496ce633799bbe971f71f3243963f91dab0a421a239f4`.
`Isa` принята на book-level; full 66-book gold не финализирован.
Строгий счётчик `36/66`: `Gen–Song`, `Isa`, `Jer`, `Lam`, `Ezek`, `Dan`, `Hos`, `Joel`, `Amos`, `Obad`, `Jonah`, `Mic`, `Hab`, `Hag` и `Mal`. `Jer` и `Lam` blind pass 2 заморожены до
сравнения; double `gold_compact check` и canonical comparison дали 1 315/404
agreements/disagreements для `Jer` и 873/180 для `Lam`, оба без ошибок.
Versioned SHA-указатели — `gold_review_batch_024.manifest.json` и
`gold_review_batch_025.manifest.json`. `Jer` distinct adjudication 404/404
в 261 компоненте, full grid 1 719/1 719; SHA adjudication/sidecar
`da312d83479485e779da0f4e790780acb0c98ee30c117426491e51c15eb0cc1d` /
`d93dc611a73147160393e5aa719612aa4f812a20879e495b670c2242577dc752`.
`Lam` distinct adjudication 180/180 в 116 компонентах, grid 1 053/1 053;
SHA `84fba5b18d0be56e4b2adc69d7fa64a04f07c66d055f98564c155c16de46f62d` /
`0194bf68a02ae5612b67e4c9bdd39391a5029d30f058e19e299fe2dcd65b722a`.
Оба root `check-adjudication` прошли. `Lam` distinct independent QC проверил
180/180 adjudicated и 873/873 agreed решений, grid 1 053/1 053,
`error=0`, `uncertain=0`; QC/sidecar SHA-256
`c15a7107b09ac53bf083e0fe7cfbcd0dee632195e13b4d5293c0ffdb5bccf35e` /
`81d4132a774d8cb036914b40675f111520d1e94a60c78167a881d936301791a5`.
`Jer` distinct independent QC проверил 404/404 adjudicated и 1 315/1 315
agreed решений, полный grid 1 719/1 719, `error=0`, `uncertain=0`; root
`check-adjudication-qc` и SHA прошли. QC/sidecar SHA-256
`d9467f0622628fc80e7faa5ab8e17aecb8086a8535429429686ac3712f73d1e7` /
`f37c0770efce5617dca385c8450019f736aa2391e819f35c8e66c4c53c1d7649`;
`Jer` принята.
`Ezek` blind pass 2/comparison заморожены: 32 стиха, 845 original + 717
target, 1 329 agreements / 233 disagreements; exact SHA в
`gold_review_batch_026.manifest.json`. Distinct adjudication 233/233 в 184
компонентах прошла double generation и root `check-adjudication`, full grid
1 562/1 562, SHA JSONL/sidecar `a161a533b971f9a7dd30eabf5256239585cdf1c52f76849f9a68cf7af7026517` /
`ddbef1165c37d0e47f6afd199c8bec415ebfca81d3657a214c69117d3e97fc28`.
Отдельный QC `Ezek` теперь выполнен: 233/233 adjudicated, 184 компонента,
1 329/1 329 agreed решений, full grid 1 562/1 562, `error=0`,
`uncertain=0`; root `check-adjudication-qc` и физические SHA прошли. QC/sidecar
SHA-256 `f37208a2bc83f1226eecad87249fb23ded8a4af7befcf1ed1d940dc0c5cf10b7` /
`30c6ce09600151769754e859831b6ed62dacf611ad94a6fde8b924717f22fbc0`;
книга принята. `Dan` blind pass 2/comparison завершены:
32 стиха, 844 original + 721 target, 1 090 agreements / 475 substantive
disagreements, `gold_compact check` PASS. Exact pass2/comparison SHA-256
`d27867d22bfc149a38b7220ce356d2f9899eaa7f6e286a23c8b04cf0c43fb725` /
`49fc7b1e2a0d88a5db4f7bdc61ed19955216bade8a2b41d34de3c3a79df181c8`;
`Dan` distinct adjudication теперь завершена: 475/475 расхождений в 228
verse-local компонентах, полный grid 1 565/1 565, 1 090 agreements сохранены,
root `check-adjudication` PASS. Adjudication/sidecar SHA-256
`1138d1a2aa9ee85a252ac8844d3b5c0d9d678ee6b16a4deb40f6c0287defb3a1` /
`3977bf8212948dea7b8320ba2a18839f8413f3a0ad73528c04c1c82e2429c384`.
Отдельный QC выявил пять ошибочных исходно agreed IDs в `Dan.7.15` (locative
Aramaic `בְּ ג֣וֹא נִדְנֶ֑ה` ≠ causal «через це»): blocking QC/sidecar SHA-256
`383c1b10ecca8ece71f223c6d7595b568abb7bae6009bc4a2976cab4f0f46d6d` /
`f63c1879f2a055ce71496bccf3a2a380d2e31e290911971bf4e120e1bfe787dd`.
Отдельная correction 5/5 IDs прошла `seal-correction`, double generation,
grid 1 565/1 565; correction/sidecar SHA-256
`0f8dbcdf36ad9673a7d39b77200a86a16a65e390e70e61697b5ecb723a11759b` /
`c5a9e82ebad3241d6f0ab3995a444e98667565da9bc389c16b2e3abcf6ac6887`.
Новый distinct post-correction QC проверил 475 adjudication + 5 correction +
23 unchanged observations, все 1 090 agreements и full grid 1 565/1 565,
`error=0`, `uncertain=0`, SHA JSONL/sidecar `f0fd4393…` / `ceb8b61f…`.
Real-input one-book registry probe проверил семь SHA-locked звеньев, пять
исходно agreed corrections, grid 1 565/1 565; proof SHA `322a08dc…`.
`Dan` принята, но реальный global 66-book finalize ещё закрыт.
`Hos` blind pass 2/comparison также
заморожены: 32 стиха, 615 original + 588 target, 943 agreements / 260
disagreements, `gold_compact check` PASS. Exact pass2/comparison SHA-256
`2470f5f42be387fcc89547bda567a3106e2c3b220812658f662ee130fdd610b9` /
`f6b419c82dad4ff0d39ad01f4c07e7bda0473e9aabfde5912f41c43fdb170151`;
distinct adjudication 260/260 в 135 компонентах и grid 1 203/1 203 уже
прошла root `check-adjudication`; SHA JSONL/sidecar `09ea7233…` / `0f40b416…`.
`Hos` independent QC проверил 260 adjudicated, все 943 agreed и grid 1 203/1 203,
`error=0`, `uncertain=0`; root validator/physical SHA прошли, QC/sidecar SHA-256
`b152987734273bbf34a060850205863b6e42721d735734c4aa8ee597f12786ec` /
`afe7d5e2806a666c76840680cf84699d6de975961cea8dcb016cb6f5cb9e62ff`;
книга принята. `Joel` blind pass 2/comparison заморожены: 32 стиха,
745 original + 644 target, 857 agreements / 532 disagreements, root compact
check PASS; exact SHA в `gold_review_batch_029.manifest.json`. `Joel`
adjudication 532/532 в 239 компонентах прошла root validator, SHA
`29844bc0a9c7dcaa30bbd8b08e1e0db024c285388a0bfb410ea1a52e9993db04`.
Blocking QC нашёл два ошибочных adjudicated ID в `Joel.2.27` и правильно
заблокировал книгу; отдельная two-row correction SHA `bfac6d3f…` и distinct
post-correction QC 535/535 observations SHA `cc2e3390…` прошли. Real-input
one-book registry дважды подтвердил corrected grid 1 389/1 389 и две
исправленные семантики (`7b6deb9a…`); `Joel` принята на уровне книги.
`Amos` прошла blind pass 2/comparison и third adjudication 372/372
в 202 компонентах, grid 1 469/1 469, SHA adjudication
`6382f81b36189c39e27ef2ec4a15a02af344bc31f3ebeffbb7c0e47403c136a9`.
Independent QC `Amos` проверил 372 adjudicated + 1 097 agreed, grid 1 469/1 469,
`error=0`, `uncertain=0`, SHA JSONL/sidecar `492db6a8…` / `9f9988e3…`;
книга принята. `Obad` прошла pass 2/comparison: 217 расхождений, 759 agreements,
grid 976/976, SHA comparison `cbe7a7ddc0af7cb3131e68c32792e3e5a42b12d4d020bf9d1cfee29e887941c9`.
Distinct adjudication `Obad` 217/217 в 109 компонентах прошла root validator;
SHA `2c60f5442d44fe1fca5888214b16eb98885d075a4aeb539912f0ba0d349fbcaa`.
Independent QC проверил 217/217 adjudicated и 759/759 agreed, grid 976/976,
`error=0`, `uncertain=0`, QC/sidecar SHA `91f81897…` / `b090c5e4…`;
`Obad` принята. `Jonah`, `Mic`, `Nah` и `Hab` прошли blind pass 2/comparison:
соответственно 1 527/1 486/1 197/1 410 stable decisions и 452/331/175/350
substantive disagreements. `Jonah` distinct adjudication 452/452 в 226
компонентах прошла root `check-adjudication`, grid 1 527/1 527, SHA
`0eac81db…` / `a13544c1…`. Distinct QC проверил 452 adjudicated и 1 075
agreed, grid 1 527/1 527, `error=0`, `uncertain=0`; QC/sidecar SHA
`685de4bf…` / `975ed8b9…`, root validator PASS. `Jonah` принята. `Mic` distinct
adjudication 331/331 в 161 компоненте также прошла root validator, grid
1 486/1 486, SHA `339b1d47…` / `fa5b3ba8…`; independent QC проверил все
1 486 решения и заблокировал три неверных H7725G-связи в `Mic.2.8`.
QC/sidecar SHA `b96e948a…` / `90720a3a…`; root validator ожидаемо отверг
блокирующий QC. Scoped correction трёх stable IDs (`5a7afded…` /
`902744e3…`) прошла двукратную deterministic генерацию и `seal-correction`.
Отдельный independent re-QC проверил 336 observations и полный grid 1 486/1 486
без ошибок/uncertain (`f861d76f…` / `a5c230eb…`); real one-book registry
probe принял exact 1 486 семантик (`4f00c9d2…`). `Mic` принята на book-level.
`Nah` distinct adjudication 175/175 в 107 компонентах прошла root validator,
grid 1 197/1 197, SHA `4ef2b08e…` / `b1a27ce4…`; independent QC просмотрел
все 1 197 решения, отметил пять `critical/uncertain` в `Nah.1.8` и заблокировал
книгу (`5aa0f2f0…` / `ed4ab940…`, root expected reject). Exact scan leaf 1156,
printed page 1152 без сноски; MT `מְקוֹמָהּ` и локальный read-only LXX
`τοὺς ἐπεγειρομένους` расходятся. `textual_fingerprint_nah_1_8.manifest.json`
фиксирует источники и отсутствие права на Strong без текстологического решения.
`Hab` distinct adjudication 350/350 и независимый full-grid QC 1 410/1 410
прошли root validators без ошибок/uncertain (`6c82495c…` / `8edf2e61…`);
книга принята. `Zeph` distinct adjudication 251/251, но independent QC
полного grid 1 479/1 479 обнаружил четыре high textual uncertainties в
`Zeph.2.14` и `Zeph.3.17` (`1e9acf7e…` / `75275ace…`); книга заблокирована.
`Hag` 522/522 и `Zech` 278/278 distinct adjudication завершили.
`Hag` independent QC проверил все 1 595 решений без error/uncertain,
root `check-adjudication-qc` PASS, книга принята (`45b7f26c…` / `96f38086…`).
`Zech` independent full-grid QC проверил 1 606/1 606 решений,
`error=0`, `uncertain=7` high/critical в 11.7/14.6;
QC/sidecar SHA `b4cc4e50…` / `bc4d8585…`, root expected reject.
Отдельный diagnostic addendum закрепил точные сканы листов 1177/1180,
первичный MT, локальные LXX-контроли и отсутствие собственных сносок к обоим
стихам; это не доказывает точную Vorlage Огиенко и не разрешает Strong.
`Mal` завершила distinct adjudication 440/440, grid 1 613/1 613,
root structural validator PASS (`cc7a3201…` / `5433ce1d…`). Independent
full-grid QC нашёл 2 reciprocal error IDs в `Mal.3.11`; v2 blocking QC
(`dd452cbf…` / `b41900a9…`) содержит exact proposal-only scope.
Отдельная two-row correction (`368eed86…` / `1e6dc228…`) трижды
детерминированно совпала и прошла `seal-correction`. Distinct post-correction
QC проверил 443/443 наблюдения и full grid 1 613/1 613,
`error=0`, `uncertain=0`; root SHA и `check-correction-qc` PASS
(`9dfbfbd9…` / `2ade4358…`). Два byte-identical real one-book
correction-aware registry прогона подтвердили все seven chain SHA,
correction scope 2/2 и полную неизменную сетку (`5a0edee2…` /
`087c824f…`). `Mal` принята на уровне книги, но global gold не финализирован.
Отдельный primary-source audit `Nah.1.8` и `Zeph.2.14`/`3.17` проверил
печатные страницы OH1988 и авторское свидетельство 1963 года о еврейской
основе и выборочном обращении к LXX, но не нашёл locus-specific Vorlage.
Все 5 critical `Nah` и 4 high `Zeph` остаются blocked; diagnostic-only
SHA закреплены в `textual_fingerprint_nah_zeph_primary_audit.manifest.json`.
`Mat` blind pass 2 теперь заморожен после 39 стихов и 1 358 exact решений;
два post-blind comparison прогона дали 1 072 agreements и 286 substantive
disagreements, `error=0` (`f109bf7c…` / `b25451cf…`). Distinct adjudication
286/286 в 138 компонентах закончена: full grid 1 358/1 358, root
`check-adjudication` PASS, SHA `02240391…` / `5e9afa62…`. Mat.21.30
остаётся critical textual-source uncertainty: SBLGNT edition apparatus
подтвердил Westcott–Hort analogue для `21.29–31`, но не точную Vorlage
Огиенко (`textual_fingerprint_mat_21_30.manifest.json`). Независимый
full-grid QC проверил 1 358/1 358 решений: 1 343 accepted, 15 critical
source-uncertain в одном locus (7 adjudicated + 8 agreed), content errors 0.
Три byte-identical эмиссии и root физические SHA QC/sidecar `793f54aa…` /
`f8116493…`; `check-adjudication-qc` ожидаемо отклонил blocking status,
`gold_adjudication_batch_040.manifest.json` обновлён. Книгу не принимать до
source resolution и независимого re-QC.
`Mark` blind pass 2 заморожен на 40 стихах и 1 328 exact решений; двойной
post-blind comparison: 1 039 agreements, 289 substantive disagreements,
`error=0`, SHA `55ca5a79…` / `5d3792a7…`. Distinct adjudication 289/289
в 171 компонентах прошла root `check-adjudication` и три byte-identical
эмиссии (SHA `76d2f827…` / `ee29b8e4…`), но `Mark.1.2`, `16.8`, `16.9`
остаются textual-uncertain. В `16.8` bracketed Short Ending 34 атома
`source_text_not_rendered`, а не доказанный переводческий пропуск.
Independent full-grid QC проверил 1 328/1 328: 1 324 accepted, 4 critical
source-choice uncertain в `1.2`/`16.9`, content errors 0; три byte-identical
QC SHA `753de840…` / `416193d2…`, expected fail-closed checker.
Source resolution/re-QC и provenance rebase нужны; книгу не принимать.
`Luke` blind pass 2/comparison заморожен на 39 стихах и 1 210 exact
решениях: 960 agreements, 250 substantive disagreements, `error=0`,
comparison/sidecar SHA `ba0a7788…` / `a5893392…` в
`gold_review_batch_042.manifest.json`. Distinct adjudication 250/250 в 105
компонентах прошла root `check-adjudication` и две byte-identical эмиссии
(SHA `7f4e8a7d…` / `889ccdfb…`), но `Luke.10.15` μὴ/G3361 остаётся
critical source/rendering uncertainty. Independent full-grid QC уже
проверила 1 210/1 210 decisions: 1 196 accepted, 14 source-choice uncertain
в шести loci, content errors 0, QC/sidecar SHA `9c34b5a2…` / `c5df3e4b…`;
validator ожидаемо отклонил blocking status. В `Luke.2.11` QC подтвердила
G3739→«Який», G4771→«для»/«вас», не legacy G3739→«вас». Adjudication SHA
перебазирован на исправленный pass2. Отдельный QC SHA rebase завершён metadata-only с
539/539 неизменных Mark/Luke QC results и сохранёнными 4/14 uncertainty;
`gold_qc_provenance_rebase.manifest.json`. Source resolution и независимый
re-QC ещё нужны. Production Strong нет, книга не принята.
`John` blind pass 2/comparison заморожен на 36 стихах и 1 170 exact
решениях: 1 039 agreements, 131 substantive disagreements, `error=0`,
comparison/sidecar SHA `a18fa1f0…` / `210c5edc…` в
`gold_review_batch_043.manifest.json`. `1.18`, `5.4`, `7.53–8.11`
source-qualified; distinct adjudication уже прошла root validation на
исправленной pass2/comparison цепочке: 131/131 disagreement, 1 039
agreements сохранены, grid 1 170/1 170, adjudication/sidecar SHA
`139ffd0f…` / `5410146d…` в `gold_adjudication_batch_043.manifest.json`.
Independent full-grid QC уже проверила все 1 170/1 170 решений:
1 160 accepted, 10 source-choice uncertain (`1.18`, `1.28`, `8.11`,
`14.15`), content errors 0; QC/sidecar SHA `67233ff0…` / `08c0a235…`,
validator ожидаемо отклонил blocking status. Source resolution/re-QC
ещё нужны, книга не принята.
`Acts` blind pass 2/comparison заморожен на 39 стихах и 1 436 exact
решениях: 1 175 agreements, 261 substantive disagreement, `error=0`,
comparison/sidecar SHA `17ea9ca5…` / `3526ce28…` в
`gold_review_batch_044.manifest.json`.
Distinct adjudication `Acts` разрешила 261/261 disagreement и сохранила
1 175 agreements, grid 1 436/1 436, root validator PASS; adjudication/
sidecar SHA `69315757…` / `c5adb14b…` в
`gold_adjudication_batch_044.manifest.json`. Independent full-grid QC
проверил 261 adjudicated + 1 175 agreed = 1 436/1 436 решений:
1 399 accepted, две reciprocal errors `Acts.13.29` (adjudicated
`καθελόντες/G2507` и originally agreed target «то»), 35 source/semantic
uncertain в `2.38`, `5.34`, `13.26`, `15.34`, `27.12`. Три
побайтно одинаковых выпуска, QC/sidecar SHA `a77ef5dd…` / `0fae5c28…`,
root validator ожидаемо отклонил blocking status. Отдельная exact
two-row mixed correction `Acts.13.29` прошла три побайтно одинаковых
выпуска и `seal-correction` с grid 1 436/1 436; correction/sidecar
SHA `c1ee34fe…` / `7c30e54b…`. Distinct independent post-correction
full-grid QC проверил 261 adjudicated + 1 175 agreed и 2 changed + 2
unchanged reciprocal rows: итоговый grid 1 436/1 436, 1 401 accepted,
`error=0`, 35 source/semantic uncertain в пяти прежних loci. Три
побайтно одинаковых QC/sidecar выпуска, физические SHA
`1520e928…` / `256a3a70…`; `check-correction-qc` ожидаемо отклонил
blocking source-choice status. Source resolution и новый re-QC нужны;
книга не принята.
`Rom` blind pass 2/comparison заморожен на 33 стихах и 1 056 exact
решениях: 866 agreements, 190 substantive disagreements, `error=0`,
comparison/sidecar SHA `5c927827…` / `254b4e2c…` в
`gold_review_batch_045.manifest.json`.
Distinct adjudication `Rom` разрешила 190/190 disagreement и сохранила
866 agreements, grid 1 056/1 056, root validator PASS; adjudication/
sidecar SHA `42483a9c…` / `43375656…` в
`gold_adjudication_batch_045.manifest.json`. `3.22`, `6.1`, `6.11`, `13.11`
source/segmentation unresolved. Independent full-grid QC проверил 190
adjudicated + 866 agreed = 1 056/1 056, 1 037 accepted, `error=0`,
19 source/semantic uncertain по девяти loci (`3.22`, `6.1`, `6.11`,
`9.31`, `11.25`, `12.5`, `13.11`, `15.8`, `15.15`). Три
byte-identical QC выпуска, SHA JSONL/sidecar `778c7318…` /
`670ea20f…`; root validator ожидаемо отклонил blocking status.
Source resolution/re-QC нужны, книга не принята.
`1Cor` blind pass 2/comparison заморожен на 33 стихах и 952 exact
решениях: 777 agreements, 175 substantive disagreements, `error=0`,
comparison/sidecar SHA `acaf2e6d…` / `85f3c618…` в
`gold_review_batch_046.manifest.json`. Distinct third adjudication
разрешила 175/175 disagreement в 96 компонентах, сохранила 777
agreements и grid 952/952; root `check-adjudication` PASS, два
byte-identical выпуска, adjudication/sidecar SHA `d6c5cd7a…` /
`8ea22cf7…` в `gold_adjudication_batch_046.manifest.json`.
`8.2`, `10.28`, `11.31`, `14.34` source-choice unresolved;
independent full-grid QC проверила 175 adjudicated + 777 agreed =
952/952, 932 accepted, `error=0`, 20 source-choice uncertain в пяти
loci (`8.2`, `10.28`, `11.26`, `11.31`, `14.34`). Три выпуска
побайтно одинаковы; физические QC/sidecar SHA `6df87695…` /
`c8fa94f4…` в `gold_adjudication_batch_046.manifest.json`, root
validator ожидаемо отклонил blocking status. Source resolution/re-QC
нужны, книга не принята.
`2Cor` blind pass 2/comparison заморожен на 34 стихах и 1 083 exact
решениях: 916 agreements, 167 substantive disagreements, `error=0`,
comparison/sidecar SHA `4b6388b0…` / `e0e8f481…` в
`gold_review_batch_047.manifest.json`. Distinct third adjudication
разрешила 167/167 disagreement в 103 компонентах, сохранила 916
agreements и grid 1 083/1 083; root `check-adjudication` PASS,
два byte-identical выпуска, adjudication/sidecar SHA `0ba52794…` /
`78d71c65…` в `gold_adjudication_batch_047.manifest.json`.
Семь source/verse-boundary watchpoints, включая agreed-only `5.18`
и `10.4`, остаются fail-closed. Independent full-grid QC проверила 167
adjudicated + 916 agreed = 1 083/1 083: 1 052 accepted, `error=0`,
31 source/verse-boundary uncertain в десяти loci. Три выпуска
побайтно одинаковы, физические QC/sidecar SHA `8a30d2a8…` /
`9fb4091d…` в `gold_adjudication_batch_047.manifest.json`; root
validator ожидаемо отклонил blocking status. В `7.12` аппарат
подтверждает альтернативное местоимение, а в `8.13`/`10.4` есть
bracketed TAGNT locators вне selected layer. Source resolution/re-QC
обязательны, книга не принята.
`Gal` blind pass 2/comparison заморожен на 32 стихах и 1 055 exact
решениях: 853 agreements, 202 substantive disagreements (120 original
+ 82 target), 635 metadata-only differences, root shard-mode compact
check PASS; два comparison/sidecar выпуска побайтно совпали, SHA
`97f5f748…` / `5eb58abf…` в `gold_review_batch_048.manifest.json`.
Distinct third adjudication `Gal` разрешила 202/202 disagreement в 91
компоненте, сохранила 853 agreements и grid 1 055/1 055; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `628bf95b…` / `847542aa…` в
`gold_adjudication_batch_048.manifest.json`. `2.2`, `3.1`, `4.7`,
`4.14` остаются source/semantic blockers; agreed target additions в
`3.1`/`4.7` сохранены fail-closed. Alternative Strong не
перенесён. Independent full-grid QC проверила 202 adjudicated + 853
agreed = 1 055/1 055: 1 037 accepted, `error=0`, 18 source-choice
uncertain в `2.6`, `3.1`, `3.23`, `4.7`, `4.14`, `5.10`.
Три выпуска побайтно одинаковы; физические QC/sidecar SHA
`4308527f…` / `738fcb27…` в `gold_adjudication_batch_048.manifest.json`,
root validator ожидаемо отклонил blocking status. `2.2` корректно
остаётся source-omitted/target-addition; source resolution/re-QC нужны,
книга не принята.
`Eph` blind pass 2/comparison заморожен на 32 стихах и 990 exact
решениях: 762 agreements, 228 substantive disagreements (171 original
+ 57 target), 480 metadata-only differences, root shard-mode compact
check PASS; два comparison/sidecar выпуска побайтно совпали, SHA
`c94804e9…` / `2e5aa6d5…` в `gold_review_batch_049.manifest.json`.
`Eph.5.30` семь target tokens без selected Greek clause оставлены null.
Distinct third adjudication `Eph` разрешила 228/228 disagreement в 152
компонентах, сохранила 762 agreements и grid 990/990; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `b58d2938…` / `9708ea53…` в
`gold_adjudication_batch_049.manifest.json`. `3.9`, `4.8`, `5.30`
остаются source/semantic blockers; согласованные TR/Byz-only target
additions `5.30` не получили Strong. Независимый full-grid QC
проверил 228 adjudicated + 762 agreed = 990/990: 970 accepted,
2 reciprocal originally-agreed content errors `5.2` (`ἡμᾶς/G3165`
↔ «вас»), 18 source-choice uncertain. Три выпуска побайтно одинаковы,
физические QC/sidecar SHA `27b7ffec…` / `6c0091df…` в
`gold_adjudication_batch_049.manifest.json`; root validator ожидаемо
отклонил blocking status. Exact two-row correction, source resolution
и distinct post-correction QC нужны; книга не принята.
`Phil` blind pass 2/comparison заморожен на 32 стихах и 1 035 exact
решениях: 821 agreements, 214 substantive disagreements (127 original
+ 87 target), 621 metadata-only differences, root shard-mode compact
check PASS. Два comparison/sidecar выпуска побайтно одинаковы,
физические SHA `e37fd2c8…` / `8f6b9354…` в
`gold_review_batch_050.manifest.json`. `2.7`, `2.26`, `3.18`, `4.13`,
`4.23` остаются source-qualified; книга не принята.
Distinct third adjudication `Phil` разрешила 214/214 disagreement в 84
компонентах, сохранила 821 agreements и grid 1 035/1 035; два выпуска
побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `2539e53a…` / `a3cc7e28…` в
`gold_adjudication_batch_050.manifest.json`. `2.7`, `2.26`, `4.13`,
`4.23` остаются source/verse-boundary blockers; agreed target additions
`2.7`/`4.13` не получили Strong. Независимый full-grid QC нужен;
книга не принята.
`Col` blind pass 2/comparison заморожен на 33 стихах и 1 017 exact
решениях: 803 agreements, 214 substantive disagreements (151 original
+ 63 target), 544 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические
SHA `14adfa41…` / `194f4724…` в
`gold_review_batch_051.manifest.json`. Critical source-choice loci
`1.12`, `3.4`, `3.15`, `3.16`, `3.22` блокируют автоматический Strong;
`1.16` содержит переставленные группы; книга не принята.
Distinct third adjudication `Col` разрешила 214/214 disagreement в
127 компонентах, сохранила 803 agreements и grid 1 017/1 017; два
выпуска побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `023c7533…` / `d12d2920…` в
`gold_adjudication_batch_051.manifest.json`. Пять source-choice loci
остаются critical; перестановка `1.16` подтверждена reciprocal
token evidence, не позицией. Independent full-grid QC нужна;
книга не принята.
`1Thess` blind pass 2/comparison заморожен на 32 стихах и 1 037 exact
решениях: 874 agreements, 163 substantive disagreements (117 original
+ 46 target), 608 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`df4c25e6…` / `aeec643c…` в
`gold_review_batch_052.manifest.json`. Watchpoints `2.6`, `2.11`,
`3.2`, `3.5` остаются fail-closed; книга не принята.
Distinct third adjudication `1Thess` разрешила 163/163 disagreement в
108 компонентах, сохранила 874 agreements и grid 1 037/1 037; два
выпуска побайтно одинаковы, root `check-adjudication` PASS, физические
adjudication/sidecar SHA `8d913a35…` / `b2e8ea43…` в
`gold_adjudication_batch_052.manifest.json`. `2.6`, `2.11`, `3.2`
остаются source/segmentation blockers. Independent full-grid QC нужна;
книга не принята.
`2Thess` blind pass 2/comparison заморожен на 32 стихах и 1 200 exact
решениях: 948 agreements, 252 substantive disagreements (163 original
+ 89 target), 570 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`ec99f04a…` / `1ed413e7…` в
`gold_review_batch_053.manifest.json`. Watchpoints `1.4`, `2.3`,
`2.7`, `2.13`, `3.6`, `3.11` остаются fail-closed; книга не принята.
`1Tim` blind pass 2/comparison заморожен на 33 стихах и 1 013 exact
решениях: 814 agreements, 199 substantive disagreements (113 original
+ 86 target), 563 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`34dea918…` / `b13c4dd7…` в
`gold_review_batch_054.manifest.json`. Слитное surface `2.2`
сохранено точно по stage 6; `3.16`, `5.16`, `5.21`, `6.3`, `6.10`,
`6.21` остаются source/lexical watchpoints; книга не принята.
`2Tim` blind pass 2/comparison заморожен на 32 стихах и 1 020 exact
решениях: 848 agreements, 172 substantive disagreements (118 original
+ 54 target), 587 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`96dfda02…` / `49a084fc…` в
`gold_review_batch_055.manifest.json`. Слитное surface `3.15`
сохранено точно по stage 6; source/lexical watchpoints fail-closed.
Книга не принята.
`Titus` blind pass 2/comparison заморожен на 32 стихах и 933 exact
решениях: 789 agreements, 144 substantive disagreements (92 original
+ 52 target), 443 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`01633d4a…` / `0fa88340…` в
`gold_review_batch_056.manifest.json`. Watchpoints `1.4`, `1.6`,
`1.9`, `2.7`, `2.15`, `3.4`, `3.15` остаются fail-closed; книга не принята.
`Phlm` blind pass 2/comparison заморожен на 25 стихах и 696 exact
решениях: 567 agreements, 129 substantive disagreements (79 original
+ 50 target), 429 metadata-only differences, root shard-mode compact
check PASS. Два comparison выпуска побайтно одинаковы, физические SHA
`72865f9d…` / `7044fb2f…` в
`gold_review_batch_057.manifest.json`. Raw `G6063` вне classic
Strong не получил выдуманного номера. Следующий blind pass 2 — `Heb`,
shard 058; `Gal`–`Phlm` ещё не приняты.
Для `Mark`/`Luke`/`John` frozen pass2 содержит ошибочный шаблонный
provenance label `Mat`; исходные SHA сохранены. Root metadata-only repair
исправил 1 893 служебных подписей с exact semantic proof 3 708/3 708 и
перевыпустил comparison по двум byte-identical прогонам на книгу, сохранив
disagreement counts 289/250/131. `gold_pass2_provenance_repair.manifest.json`
фиксирует old/new SHA. Для `Mark` и `Luke` отдельный explicit adjudication
SHA-rebase уже выполнен: 539/539 decision rows неизменны, два побайтно
одинаковых выпуска и root `check-adjudication` PASS; old/new SHA в
`gold_adjudication_provenance_rebase.manifest.json`. Старый independent
blocking QC также явно перебазирован с 0 изменённых result rows и сохранённым
blocking status (`gold_qc_provenance_rebase.manifest.json`). Source resolution
и новый независимый re-QC остаются. `John` adjudication и независимый
blocking QC завершены на исправленной цепочке; 10 source-choice uncertain.
Remote LLM не запускался и должен оставаться остановленным.

Полные выходы находятся только в gitignored
`work/.../gold_review_adjudication/<Book>/`, имеют distinct identities и exact
pass/comparison SHA locks. Повторная structural-проверка выполняется командой:

```powershell
python -m scripts.bible_module.ukrainian_stage_7_gold_compare check-adjudication `
  --pass1 <pass1> --pass2 <pass2> --comparison <comparison> `
  --adjudication <completed-adjudication>
```

Точные pause-артефакты:

- `Gen/qc/qc.adjudication.Gen.shard_001.codex-independent-20260905.jsonl`,
  SHA-256 `44d7ab93e80c00fd449a03d96e20ba5267c0218f8940be0efd6d50ecf7725b95`;
- его manifest SHA-256
  `f15febd45ef2ac7fccae4447d1a51f0a18b88e11304e2447c1e59bbd2369d9d7`;
- `Exod/qc/qc.adjudication.Exod.shard_002.codex-independent-20260905.jsonl`,
  SHA-256 `ad2f377aebf8c5510e2cd70dfb1b62210aa90418eef3d050c821ed1a00f39cca`;
- его manifest SHA-256
  `582947981f4fd29d4a4ef3fc456df5337159432d18abab1c8d4d506a7ce523f6`;
- `Lev/qc/qc.checkpoint.adjudication.shard_003.codex-independent-20260905.json`,
  SHA-256 `2c0e98a4dbaf70dbcef57c932731ba84ff8160109fa6f8d11c8b7a88d2ab2fae`;
- его manifest SHA-256
  `fafe80b9c03968253aba51356f66e0d6ee4b9eb1aa105e9d49dff13c60dde8cd`.
- `Lev/qc/qc.adjudication.Lev.shard_003.codex-independent-20260905.jsonl`,
  SHA-256 `21bb8fc1c6d9f28b84bdffd828616d9093415c1a77c5daa042729d81ed001534`;
- его итоговый manifest SHA-256
  `19e2c36bf34919ebec0cc3f57930ce894614809602dd48aed9d4f9c66ac9c51e`;
- `Exod/correction/Exod.shard_002.consensus_correction.jsonl`, SHA-256
  `ca53be00c26a2ab6d238e1abe495d8a9f306ca91c0493080a1860db38feb4c5a`;
- его manifest SHA-256
  `20fd7ead995709b575018a5afb765a10c9a382fd048764eda73ec798c28fe539`.
- `Exod/qc/qc.final.Exod.shard_002.post-consensus-correction.codex-independent-20260907.jsonl`,
  SHA-256 `d79b394b22c516b814a2017f3660e3018f558c4f3176d40eacbc1b39adc19c67`;
- его manifest SHA-256
  `e6e192709d597099fb464196ef7e695822925a3601b33bb19b6f51acbdf0847e`.
- `Num/qc/qc.adjudication.Num.shard_004.codex-independent-20260907.jsonl`,
  SHA-256 `04873c06dfd6c5182e0d7e73e0e44440290b046561a12d6f2525475bdcb0df15`;
- его manifest SHA-256
  `2401c4fe5c464d7ea6844785f968f4481a46fca69f216b8ec8fd58f9f325f88f`.
- `Josh/qc/qc.adjudication.Josh.shard_006.codex-independent-20260907.jsonl`,
  SHA-256 `9bf8b729870009bf2131d42fad132b8dbc7703e32cd8dec10008a8b9ce1daba3`;
- его manifest SHA-256
  `d310eb8b3d414e1cd402f47561aaa4e22323b26249f14f79034a3ed12ba6f42c`.
- `Judg/qc/qc.adjudication.Judg.shard_007.codex-independent-20260907.jsonl`,
  SHA-256 `44a7a12195c42aa2fd472edb704a8b9ab5962ada18004391919f57b118854c67`;
- его manifest SHA-256
  `785e0503f0d2ea355c5cac3b7c8e5bef3300c28ba2bf4d6587f0c3ee9da9580e`.
- `Ruth/qc/qc.adjudication.Ruth.shard_008.codex-independent-20260907.jsonl`,
  SHA-256 `b782950a46cd2806254b03f96d698c4d96f3cc33fd81b9ebfd4bdc87c63898b7`;
- его manifest SHA-256
  `ac86a7e26f40c92ff9c15d102208c4c823df90735559095cdc4048274a40667d`.
- `2Kgs/2Kgs.shard_012.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `c9d7cb5d7735c5ca2f681fd38ea7b1a0ff482d4da11155d5438a8365e078913c`;
- его manifest SHA-256
  `7cd6307c69a31353595f4f4273d7894aee7d5fa8ecd27b4b26f41d1dab044e90`.
- `2Kgs/qc/qc.adjudication.2Kgs.shard_012.codex-independent-20260907.jsonl`,
  SHA-256 `4d12c29dcd3318fe1b6847677b803a115d7b360f4cb8ff5deaad1fbe6aa5c39c`;
- его manifest SHA-256
  `1d1c9a14c6e9a75aeb6041d7ad413304844ac362a48976cf03059f77b74bbb8a`.
- `1Chr/1Chr.shard_013.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `4b3a2d93d2219d9a79c5a9a18f1f38e480a78590b315dd6e2b8724992fe70dbd`;
- его manifest SHA-256
  `a89b10b62f102bae709d8ad883699478264dfbdece03100efd299d122d9a4602`.
- `1Chr/qc/completed/1Chr.shard_013.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `2e4880fa62a04b60603943a814475c2d7f1a269ef5ff3e6d4e94fe73856dc9af`;
- его manifest SHA-256
  `a8e2fc4b87fa3288b14c891cf3d34f30064522efe54fb0769a424d1c54b2b0be`.
- `2Chr/2Chr.shard_014.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `cfc78bb386463cc6256cc80b88ed213c29770712c8c6956db5044b78e75fe733`;
- его manifest SHA-256
  `ba1625e95b9238071206c295c7701b15019107303ccb59210b77d45e42f0d256`.
- `2Chr/qc/qc.adjudication.2Chr.shard_014.codex-independent-20260907.jsonl`,
  SHA-256 `43d27d083d8ba1b5bad469f08b2efa2572258560c63ec1a078e465ccb4888d45`;
- его manifest SHA-256
  `8140bbbd82ea4955a0b1c626cf0bd66a1c32c6337f3e619b57c9d83c28121d05`.
- `Ezra/Ezra.shard_015.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `3e80aac71be6868bda3185a73d5cedd20d6350273751b205492c6c941bf822f5`;
- его manifest SHA-256
  `3c493c4abfee4cf092654eff0fb924b4f40471d215105b2ff6ef1e71d225b596`.
- `Ezra/qc/completed/Ezra.shard_015.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `f4765d6260064410a7009114570fed28867caff3b454745cdc6b072c8bff195a`;
- его QC manifest SHA-256
  `fa4bb85dc1f862133ec99cce69f265148e3971c057ee3b14237906d6a6b35527`.
- `Neh/completed/Neh.shard_016.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `32bcb8a7c4378c247560160f837b550aad188559138a4b4285835d2f0caf9874`;
- его manifest SHA-256
  `3febb24494efc20b647d33a6a961ee28f4d74fed6db13b2e51fcc0d8255f9380`.
- `Neh/correction/Neh.shard_016.consensus_correction.jsonl`, SHA-256
  `cea4dad10bda6870ddb6523c283ea0532c16a87061b877ca2b26234e3dc0bac1`;
- его manifest SHA-256
  `463638c46ef1ea8daa3e97a19e811ce28f3d5007256d3c9acf113d1074291a08`.
- `Neh/qc/completed/Neh.shard_016.post-consensus-correction.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `7f7eee3c3e4d43085d78499ba583816373bd51ea211b7a7fef15f9bd71b44b05`;
- его manifest SHA-256
  `32b6909262704351d3a79cde5bc8b27ea638506c6631990d7770947f44e4e6df`.
- `Esth/Esth.shard_017.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `3b4aa967045251000e3f142fc09e462076c9e9f5f7df829a56f4ad8707e10345`;
- его manifest SHA-256
  `4fbe485772f8737bb69759c2f282e97f49eba20d21f2e14f973e1ab01c9b4b21`.
- `Esth/qc/qc.adjudication.Esth.shard_017.codex-independent-20260907.jsonl`,
  SHA-256 `14397af3a299b8d5086aa581a4f61fa0a24c7d5649c750f3b7d571349dd7d578`;
- его manifest SHA-256
  `9b7dca7490b9ec13c23c0bcfe0739f3db9908f35034ebfa02e770038fcd2eba8`.
- `Deut/Deut.shard_005.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `04c92f11ed2ec476c61df0db85ba4f2b1835a8f55a68f322179eb9c7d32d05e8`;
- его manifest SHA-256
  `17bb2f95a50416a9ab083cc7766b4ee23322a650f4f3b8e1f669c6afd9192b9f`.
- `Deut/qc/completed/Deut.shard_005.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `3c994118fc83365131d3ebec9a344b9dae63413eb043f59267465fad658603e4`;
- его manifest SHA-256
  `51d8a9f3c8bdc435fda028d64cfe70c7511514430df5ad373a614096db1aa154`.
- `Job/completed/Job.shard_018.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `5a57b7944c5e984043ca2c965b13b55189647b33d6cf49bcbe641f3514f071ed`;
- его manifest SHA-256
  `e2161bbb5d7c8b24584ab5a99ec8c36806d194eef06a0d3a1649b834abeaa3cf`.
- `Job/qc/Job.shard_018.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `0476052c538509df84c9fe47183fdf28f08df54b652868b774a67fb6d7eaf0ee`;
- его manifest SHA-256
  `e89703c825f12ecc1e0986cdbfa7c28f49e5a07c7160cdffc42a51b4cadc5d7a`.
- `Ps/qc/blocking/Ps.shard_019.third_adjudication.blocking_content_qc.codex-20260907.jsonl`,
  SHA-256 `6b3acd2eb81dbbf002b399d3e766ede922f688d3c867efb1d219330d0fe312d7`;
- его blocking-QC manifest SHA-256
  `6ed953cc85d5ed71e260d5750b1ce42224f7cc962651001f03e84a9cd229b744`.
- `Ps/correction/Ps.shard_019.consensus_correction.jsonl`, SHA-256
  `57c57e7d53ab191c0848b97450329f4cce38889603fb1cad331bc6158aba393b`;
- его manifest SHA-256
  `7c68870a0de052fa5a8ab30f40a989bf86fb87cce6462c9bb26ad2c295395e86`.
- `Ps/corrected/Ps.shard_019.pass1-pass2.third_adjudication.corrected-v1.jsonl`,
  SHA-256 `2e1d6495b4daecbdc377dbbc6ecd28c6e9734f017c5a8dbce64062757eb4a1f5`;
- его manifest SHA-256
  `1bcc754d7aa3ec8718e5a770aa9251b66a1aa74db9c22bb30d2e761741561fe4`.
- `Ps/qc/post_correction/Ps.shard_019.post-consensus-correction.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `f5858df011da8de6161b0c58a951cbd21e6febde438c63dfdd12c905984467c5`;
- его manifest SHA-256
  `67e699c420ed9cd33411348717661aec26c50bace60c7199465e32951ee8c143`.
- `Prov/completed/Prov.shard_020.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `206b8b28178ede8fd7d17c5c1b8ee98e0e25a48c996563f37f6fb7e42f2aa31b`;
- его manifest SHA-256
  `5d3371ae86a4187cd45bf24de735691b5e91fafa2cc67af8d50183a019c9559f`.
- `Prov/qc/Prov.shard_020.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `ae11abe38e8d8e3f8eae6bf617286ba21acabe032076fed27e22c5df3b3fa64d`;
- его manifest SHA-256
  `36130c5f2db71dd286c5b7599851f691dcaa7d55be810f374c46d67abba4056c`.
- `Eccl` pass-2 raw SHA-256
  `1aac79eac5b30a2df0aecb5bab95cf7aa8fcd3e1d44825b5c73eec47231aff32`;
- его manifest SHA-256
  `dc09fd4a912cfbb5f600d49c94aee18146791854bb8a14a650aa146fcaf9ce2b`;
- `Eccl.pass1-pass2.disagreements.jsonl` SHA-256
  `4bc6dbad205ac2fd93c9c01f74f1e46245e0009697d2bee634644d92ce7d7ca4`;
- его manifest SHA-256
  `f5e4463510c05b7a14b6d020a7e2380adcf23ee0e78e5be94f13b726630460bd`.
- `Eccl/completed/Eccl.shard_021.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `b18d6ca49544007d45d9f5517ce26eda2ec2476e9582062b4e559280ed0c39d2`;
- его manifest SHA-256
  `d80dbfb5b4711dcaa8576fd3bd88255aa533a5ad03ae873980a0a49d5b737628`.
- `Eccl/qc/Eccl.shard_021.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `0a25f883b696b97fb8004ef695207669d7310e18b869babc64ffa6e681c39522`;
- его manifest SHA-256
  `e7267c93aa0d95bdcceaedf42a5b68c87888eb12d794177bf4ddbfc09a757614`.
- `Song` pass-2 raw SHA-256
  `220a39ac8483677ead60de7e3d02adca4f31928caac4117b3e69b589b7a991a1`;
- его manifest SHA-256
  `87d121822c84b9a635ccd0cadf111a2880a9866e5e6b5ba1ce9056fbf299338b`;
- `Song.pass1-pass2.disagreements.jsonl` SHA-256
  `f6677da6af5c4576ae1bfd5a152637a2fd3601fdf5c84747a952d5f7a9b559bc`;
- его manifest SHA-256
  `9f5dc704caa6be1ef5c66914ba7dea54f71ca0cd0ca339c1a9436a9f3f0e39c8`.
- `Song/completed/Song.shard_022.pass1-pass2.third_adjudication.jsonl`, SHA-256
  `a0b625232bde7b8ab4082eb87bb0490de05c0a329df647eec8710896f150f48e`;
- его manifest SHA-256
  `f6cf521807b4c8dd14d6223d08e8f6d2bc2f95501e7618aa3389380268ef01f4`.
- `Song/qc/completed/Song.shard_022.pass1-pass2.third_adjudication.independent_content_qc.codex-20260907.jsonl`,
  SHA-256 `9dd78e3168910fe0f7acd652272cb51238daebe0d8261f9b71887efd3a0997b2`;
- его manifest SHA-256
  `854b3250cf4988e50b8404cc1ece93fd361e57d6e592de51f99fb4addd5271a6`.
- `Isa` pass-2 raw SHA-256
  `5d186e7cb068d03e0ff6a79587f2e881472b7c9de723d85e4f0e3ab72e7fdc45`;
- его manifest SHA-256
  `2b7d4d11c472676f5aa1e2dea69de09fe84c7a2640130d3e0f1a8d684044df7d`;
- `Isa.pass1-pass2.disagreements.jsonl` SHA-256
  `a6cd14b1053f389ccdf6b1835836b0ab005aa5dcc21c557c867482dccc6b53cd`;
- его manifest SHA-256
  `f97cb0646e40354fcb69dcd731cf6d94429b91497db59e032112104b460d75e8`.
- `Isa/completed/Isa.shard_023.pass1-pass2.third_adjudication.jsonl` SHA-256
  `bb79e3daa4ec2bb32e6000690fbdf463a9a7507482853cda8b7c6285bebda47c`;
- его manifest SHA-256
  `0690822875dcc68dd55005e5d31c6f32e5662ab75d5668e9cb087574517d49e4`.

## Проверки текущего сеанса

- обязательные stage 3/4/5/6 `--check` — PASS;
- `python -m scripts.bible_module.ukrainian_stage_7 --check` — PASS после
  механического обновления только двух устаревших doc SHA в
  `artifact_inventory.manifest.json`; прочие 303 SHA-lock совпали, accepted
  production links по-прежнему `0`;
- `python -m unittest` для gold/compact/shards/external — PASS, 36 tests;
- `python -m unittest discover -s scripts/bible_module/tests` — PASS,
  399 tests;
- `python -m unittest discover -s scripts/content_tool/tests` — PASS, 30 tests;
- forbidden-pattern and docs-sync checks — PASS;
- current Flutter `3.47.2` / Dart `3.13.2`: `dart format .` attempted to change
  four out-of-scope tests and `flutter analyze` reported 8 pre-existing
  warnings after automatic dependency/config migration; all unintended tracked
  edits were restored. Analyzer remains a final blocker, not a stage-7 code
  regression;
- `flutter test --no-pub` completed the full repository suite: `918` tests
  passed and `2` pre-existing Strong-dictionary widget tests failed because the
  expected preview strings were absent; a focused rerun reproduced `1` pass / `2`
  failures. Stage 7 changed no Flutter source/test/dependency;
- `python -m py_compile` для изменённых gold modules — PASS;
- локальный `gold_compact check` для `1Sam`, `2Sam`, `1Kgs` — PASS;
- локальный `gold_compact check` для `2Kgs`, `1Chr`, `2Chr`, `Ezra` — PASS;
- `check-adjudication` для `Gen`, `Exod`, `Lev` — PASS structural; content-QC
  после отдельного `Exod` correction принят для всех трёх;
- отдельная root-проверка `Exod` final QC: exact 142 observations / 136 unique
  keys, corrected semantics, 18 input SHA locks, role independence, canonical
  serialization и full grid 1 382/1 382 — PASS;
- отдельная root-проверка `Num` QC: exact 310/310 stable keys and semantics,
  all input SHA locks, canonical serialization, reviewer independence и full
  grid 1 496/1 496 — PASS;
- отдельная root-проверка `Josh` QC: exact 464/464 stable keys and semantics,
  all input SHA locks, canonical serialization, reviewer independence и full
  grid 1 566/1 566 — PASS;
- отдельная root-проверка `Judg` QC: trusted sidecar SHA, exact 562/562 unique
  stable keys and semantics, explicit alignment/semantic selection counts,
  canonical serialization, reviewer independence и full grid 1 749/1 749 — PASS;
- отдельная root-проверка `Ruth` QC: accepted-v3/v2 input locks, exact 252/252
  unique stable keys and semantics, canonical serialization, reviewer
  independence и full grid 1 585/1 585 — PASS;
- все 18 versioned accepted book/batch manifests через shard 022: canonical
  deterministic serialization и физическое совпадение `225/225` output SHA
  locks — PASS;
- `Prov` independent QC: 164/164 accepted, 5 critical, 93 high, 11 new,
  grid 813/813, `error=0`, `uncertain=0`; generic validator дважды и 10/10
  физических SHA-lock — PASS FOR THIS BOOK;
- blind pass 2/comparison `Eccl`: 32/32 стихов, 780 original + 625 target,
  `gold_compact check` с `error_count=0`; из 1 405 stable decisions 970
  совпали, 435 переданы adjudication; root comparison byte-identical и 4/4
  физических SHA-lock; adjudication и independent QC 435/435, grid 1 405/1 405,
  `error=0`, `uncertain=0`, root 10/10 SHA audit — PASS FOR THIS BOOK;
- `Song` adjudication и independent QC: 609/609, 207 компонентов, все 21
  critical, 142 high и 109 declared-new, grid 1 200/1 200, `error=0`,
  `uncertain=0`; double validator и root 10/10 SHA audit — PASS FOR THIS BOOK;
- blind pass 2/comparison `Isa`: 34/34 стиха, 716 original + 649 target,
  compact check дважды; 1 113 agreements / 252 disagreements, root comparison
  byte-identical и 4/4 SHA locks — PASS;
- `Isa` third adjudication: 252/252 disagreements, 144 components, full grid
  1 365/1 365; double deterministic generation and separate
  `check-adjudication` — PASS / INDEPENDENT CONTENT-QC GATE;
- полный Flutter-набор повторён, но остаётся красным по двум указанным
  out-of-scope тестам; после стабилизации окружения/исходного Flutter baseline
  он должен быть чисто повторён перед закрытием этапа.

## Точная следующая последовательность

1. Correction-aware finalizer и реальный one-book `Isa` probe уже проверены;
   `Isa` принята на book-level. До принятия всех 66 книг не создавать
   production correction registry, не запускать global finalize и не считать
   finalized gold готовым.
2. Перед дальнейшим merge перепроверять exact SHA locks всех versioned
   `gold_review_batch_*` и `gold_adjudication_batch_*` manifests.
3. После каждого pass 2 выполнить локальный `gold_compact check`, post-blind
   compare, distinct adjudication и QC. Повторять book batches до `Rev`.
   Текущая очередь: textual resolution и re-QC `Nah`/`Zeph`/`Zech`,
   source resolution и re-QC `Mat`/`Mark`/`Luke`/`John`/`Acts`/`Rom`/
   `1Cor`/`2Cor`/`Gal`; exact correction/source resolution/re-QC `Eph`;
   distinct independent QC `Phil`/`Col`/`1Thess`; distinct adjudication
   и затем independent QC `2Thess`/`1Tim`/`2Tim`/`Titus`/`Phlm`;
   blind pass 2 `Heb–Rev`.
   Scoped provenance downstream rebase
   `Mark`/`Luke` и новая `John` adjudication/QC на repaired chain завершены,
   но книги остаются blocked. `Mal` re-QC и one-book registry proof завершены.
   Pass 1 каждого следующего shard читать
   только после freeze. `Dan`, `Joel`, `Jonah` уже
   приняты; их frozen artifacts не менять.
4. После всех 66 книг объединить pass 2, проверить reviewer independence,
   выполнить `ingest-pass2`, global comparison, собрать exact global
   adjudication и только затем `finalize/check-final`.
5. После finalized gold оценить legacy и новые методы, выполнить calibration
   A/B/C, B/C review, overrides и лишь затем Strong markup с exact 31 102
   text/comment round-trip.
6. Не начинать этап 8, не создавать SQLite, не менять Flutter/content tool/DB.

## Remote LLM

Remote pilot остаётся candidate-only и запечатан в
`local_llm_remote_pilot_checkpoint.manifest.json`; разрешающего verdict нет.
Не запускать `Start`, `BenchmarkAll` или `RunWeekQueue`, пока владелец снова
явно не сообщит, что компьютер доступен.

## Короткая команда возобновления

`Продолжи этап 7 строго с текущей точки HANDOFF: scripts/bible_module/reports/ukrainian_stage_7_20260801/HANDOFF.ru.md`

# OH1988 7.4 — финальный независимый content QC группы № 1, v1

Дата: 2026-10-03. Examiner: `/root/final_content_qc`, reviewer
`codex-final-content-qc-group001-20261003-isolated01`.
[Manifest](gold_group_001_final_content_qc.v1.manifest.json).

**Nah и Zech приняты по полной сетке; Zeph остаётся blocked с двумя high
uncertainties одной согласованной пары.** Этот QC доказывает две новые book
registrations, а не третью. Отдельный технический writer выполнил проверенную
родительскую регистрацию: актуальный реестр **38/66**. Число 39/66 этим
заключением не доказано.

| Книга | Стихи | Original | Target | Полная сетка | Accepted | Error | Uncertain | Live CLI |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Nah | 32 | 604 | 593 | 1197 | 1197 | 0 | 0 | `check-correction-qc`: exit0 |
| Zeph | 32 | 787 | 692 | 1479 | 1477 | 0 | 2 | `check-adjudication-qc`: ожидаемый отказ |
| Zech | 32 | 861 | 745 | 1606 | 1606 | 0 | 0 | `check-adjudication-qc`: exit0 |
| Всего | 96 | 2252 | 2030 | 4282 | 4280 | 0 | 2 | две книги accepted |

## Реальная независимость и входы

Контекст examiner создан через `fork_turns=none`: история разработки решений
root/researcher/corrector не наследовалась. Examiner не был автором проверяемых
blind passes, adjudication, correction или source dispositions. Прочитать эти
файлы для проверки необходимо и не означает авторство. Новый ID/дата/model
сами по себе независимость не доказывают. Attestation ограничена реально
доступным execution context; недоступные сессии не объявлены проверенными.

До full work JSONL физически проверены bytes/SHA всех 3521 pinned inventory
entries, 120 различных входных/выходных файлов предыдущих QC/opinion/accounting
manifests и самостоятельно выполнены stage3/4/5/6/stage7 `--check`: exit0.
После sealing author/corrector отдельно проверены 226 физических immutable
files в `closure_input_locks.v1.json`. Последующее узкое исследование גוי также
проверено по его физическим locks. Исторические mutable registry snapshots
имеют explicit сохранённые byte locators в parent `closure_root_01/entry_snapshot`;
их старые SHA не объявлены SHA будущего live registry.

Все 96 verse panels были прочитаны с original atoms, morphology, raw Strong,
target words, полным текстом и comments. Examiner проверил также agreed links,
omissions/additions, idiomatic groups, повторения и original/target reciprocity.
Затем для каждого из 4282 stable keys сериализованы exact final decision,
semantic projection, source/target evidence, scalar/UTF8 spans, собственный
verse-local rationale и verdict. Accepted не заполнялся вместо ручного чтения.
Тексты/comments каждого выбранного стиха сверены с actual stage6 JSONL; каждый
target substring отдельно проверен в scalar и UTF8 byte координатах.

## Пять source loci: независимое решение

Все прежние **16 source uncertainties** разрешены как доказанная accounting
относительно **неизменного selected MT reference**, с явным исключением alternate
occurrences. Это соответствует прямому [owner request](gold_group_001_owner_request.ru.md)
и [плану выравнивания](../../../../docs/ru/content/ukrainian-bible-strongs-stage-7-alignment-plan.ru.md).
Ни отсутствие edition label, ни одно структурное согласие не были основанием
acceptance. Авторский [source disposition v2](gold_group_001_source_disposition.v2.ru.md)
проверен как вход, а не заимствован как QC verdict.

**Nah.1.8:** selected place/H4725 с feminine suffix является иной NP, чем
rebels с masculine divine possessor в OH. Визуально проверен exact leaf1156,
printed1152. Buhl1885 printed181 непосредственно предлагает personal derivative
и формы с собственным masculine suffix, одна с beth; это положительное
объяснение расхождения, но scholarly conjecture не импортируется как manuscript
occurrence. Greek rebels NP не имеет overt HIS; позднейший possessive относится
к enemies. Поэтому нельзя механически переносить enemy suffix лишь по общему
divine referent. Приняты o007–o011/t008–t012, включая уже omitted enemy suffix,
lexical omissions, target functions и source-relative additions.
[Buhl scan](https://archive.org/details/zeitschriftfrdi04goog),
[Greek](https://www.die-bibel.de/en/bible/LXX/NAM.1),
[NET apparatus](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10).

**Zeph.2.14 raven:** selected desolation/H2721B и threshold bird — разные
леммы. Exact leaf1165/printed1161 и Driver1906 printed129 проверены визуально;
Greek raven стоит в gate clause. Приняты noun NULL и target raven addition,
с сохранением threshold/preposition и отдельных window links. H6158 остаётся
исключённым alternate candidate, не присваивается frozen noun.
[Driver scan](https://biblicalstudies.org.uk/pdf/e-books/driver_s-r/minor-prophets-2_century-bible_driver.pdf),
[Greek](https://www.die-bibel.de/en/bible/LXX/ZEP.2).

**Zeph.3.17:** selected Hiphil silence/H2790B не равен renewal. Exact
leaf1166/printed1162 имеет love как object. Buhl1885 printed183 и Driver1906
printed139 непосредственно объясняют renewal of HIS LOVE, включая Piel с beth.
Это устраняет ошибочный Greek-YOU мост: Greek YOU является иной конструкцией.
Приняты весь o014–o017/t014–t016: silence NULL, renewal addition, любовь и
divine reflexive possessor aligned, beth без overt Ukrainian preposition.
H2318 conjecture не стал selected occurrence.
[Greek](https://www.die-bibel.de/en/bible/LXX/ZEP.3),
[NET](https://classic.net.bible.org/passage.php?passage=Zep+3%3A17).

**Zech.11.7:** actual lexicalized therefore и afflicted не означают merchant;
декомпозиция prefix не даёт самостоятельный recipient token. Finley1982
printed58–59/65 прочитан визуально: он аргументирует alternate word division и
признаёт сильную external MT поддержку. Greek не содержит отдельной flock в
merchant phrase; Peshitta не является вторым merchant vote. Приняты полностью
o008–o012/t008–t011: grammatical NULL, therefore/afflicted omissions,
recipient/trade additions, relative function и сохранённый flock/H6629 с
другим управлением. H3669 из другого стиха не заимствован.
[Finley](https://biblicalstudies.org.uk/pdf/gtj/03-1_051.pdf),
[Micheli2014, printed113](https://asset.library.wisc.edu/1711.dl/SLJSCCINPKDRH9B/R/file-2bf6c.pdf).

**Zech.14.6:** precious/H3368 не cold; выбранный qere frost/H7087 отличён от
ketiv verb и versional cold reading. Exact leaf1180/printed1176, Micheli
printed35–36 и actual source controls проверены. Полный o007–o014/t006–t013
различает negated light и отдельную positive cold/frost clause OH; второй
copula не дублирует original H1961. KD документирует antithetical reading и
его added positive copula, хотя сам предпочитает ketiv; он не объявлен
сторонником OH или общего negative scope. Приняты precious omission, cold
addition, реальные light/frost/conjunction edges и function tokens.
H7135 — исключённый alternate, не reassignment.
[BDB cold entry](https://biblehub.com/hebrew/7135.htm),
[KD](https://biblehub.com/commentaries/kad/zechariah/14.htm).

Exact historical Vorlage Огієнко, manuscript attestation conjectures и
исторический possessive relocation не доказаны. Они прямо сохранены как
исторические ограничения, а не скрытые unresolved gold occurrence selections.
Новый alternate source layer не создавался.

## Nah.1.10 correction

Отдельный corrector изменил ровно два sealed proposal keys. Examiner проверил
всю corrected сетку1197 и unchanged verse context. Comparative עד/H5704
→ t004 поддержан образом thorns и NET comparative apparatus; maqaf NULL и
target demonstrative function не изменились. Проверены175 adjudication
observations,2 correction observations и32 revalidate-only observations:
209 observations,196 distinct keys. Это не дополнительные независимые reviewers.
[Correction manifest](gold_group_001_Nah.correction.v1.manifest.json).

## Остаток Zeph.2.14: точная согласованная пара

| Роль | Stable key | Exact occurrence / span |
|---|---|---|
| Original | `original:gold7:original:10fc92cfed6f96220c8e399e5cae90df` | o011, TAHOT `Zep.2.14#06=L`, H1471A, singular גוי |
| Target | `target:gold7:target:0f7a3987f7a982ea98a91541df10fa80` | t008, scalar[40:48), UTF8[72:88), field adjective |

Эта pair `one_to_one/aligned` была agreed, high; она не входит в251
adjudication rows. Поэтому accepted всех adjudications не доказывает full
Zeph acceptance. Реальный agreed tally —1226 accepted,2 uncertain.

BDB и KD подтверждают animal-species/mass интерпретацию всей Hebrew phrase.
Это существенная polysemy, но не доказательство isolated noun→field adjective.
Официальный UBS handbook прямо относит field rendering к Targum, отличая MT
nation/species. Greek earth и Driver valley/earth alternatives тоже не являются
selected H1471 field occurrences.
[BDB](https://biblehub.com/hebrew/1471.htm),
[KD](https://biblehub.com/commentaries/kad/zephaniah/2.htm),
[UBS Clark/Hatton1989](https://tips.translation.bible/story/translation-commentary-on-zephaniah-214/).

Самостоятельно получен и визуально прочитан Albright1925 JPOSV printed158–159:
он описывает Eitan1924 exact-locus wide-valley proposal и возражает по
Semitic phonology. Eitan p32 непосредственно не прочитан; не заявляется
окончательное опровержение всех homonym accounts. Author narrow v3 после
sealing также прочитан и проверен; его вывод не заменил собственную проверку.
[Авторское narrow v3](gold_group_001_Zeph.goy_source_disposition.v3.ru.md),
[его archive manifest](gold_group_001_Zeph.goy_source_disposition.v3.manifest.json).
[Albright primary review](https://museum.birzeit.edu/sites/default/files/publications/JPOSV.pdf).

**Вердикт uncertain, не definite error.** Для current atom нужно доказать
habitat contribution этого occurrence и её выражение именно в t008. Для
phrase replacement нужно независимо объяснить распределение collective/species
и habitat contributions по exact OH phrase. Для NULL/addition требуется
положительно установить nonexpression; отсутствие доказательства atom-link
само по себе не доказывает NULL. Возможные group/NULL варианты остаются bounded
research proposals, не применёнными corrections и не обходом correction gate.

## Артефакты и воспроизводимость

Полные тексты, token grids, source evidence и CLI logs находятся только в ignored
`session_group1_20261003_closure_final_qc_01`. Checked-in manifest закрепляет
каждый input/output SHA и bytes. Nah/Zech version1 immutable. Для Zeph
используется version2: после первой sealing обнаружен мой inherited metadata
counter, ошибочно считавший1228 agreed accepted. V1 сохранён; v2 исправляет
counter1226accepted/2uncertain. Content verdicts и frozen decisions не изменены.

Каждая finalized emission повторена побайтно в completed/repro1/repro2. Это
детерминированная сериализация **одного** examiner review, а не три reviewer
votes. Обе successful CLI проверки дополнительно выполнены parent read-only.
Expected Zeph rejection не ставит под сомнение фактическую изоляцию: generic
combined status/identity exception вызван blocked overall status.

Source universes, selection/folds/scans, immutable text/comments, previous
reviewer answers, validators/runtime/DB/NT не менялись examiner. Global
registry/roadmap/HANDOFF/log остаются ответственностью parent после этих
конкретных результатов. Stage8, commit/push и production Strong import не
выполнялись. Scholarly controls — read-only research, не новые зависимости
или redistributable corpora.

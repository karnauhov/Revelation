# OH1988 7.4 — независимый content QC группы № 1, v1

Дата: 2026-10-03. ID: `gold7:independent-content-qc:group001:v1:20261003`.
[Задание](gold_group_001_independent_qc_task.v1.ru.md),
[HANDOFF](HANDOFF.ru.md),
[manifest](gold_group_001_independent_content_qc.v1.manifest.json).

Content QC пяти заданных loci выполнен. Полные сетки Nah, Zeph и Zech также
проверены: **4 282/4 282** решений в **96** выбранных стихах. Итог — 4 264
accepted decisions, **2 definite errors** в дополнительном Nah.1.10 и
**16 source-choice uncertainties** в пяти заданных loci. Это acceptance
отдельных проверенных решений, а не приёмка книг. Все три книги **blocked**;
новых accepted books **0**, gold **36/66**, осталось **30**. NT не начат.

## Фактическая независимость роли

Reviewer: `codex-content-qc-group001-20261003-context02`. В доступной истории
этого выполнения до поручения QC присутствуют только инструкции владельца,
IDE-контекст и само поручение. Авторских pass decisions, adjudication,
correction, заключения v1 и accounting audit v1 в этой истории нет. Все эти
проверяемые файлы уже существовали на входе; их физические SHA проверены до
чтения полного review JSONL. Текущая роль их семантику не создавала и не меняла.

Проверены manifests прежних pass 1/pass 2/adjudicator/QC. Их IDs различны и
отличаются от нынешнего reviewer; фактическое основание независимости —
отсутствие авторской работы в доступном контексте и сохранённые входы, а не
новый ID, модель или название чата. Утверждение ограничено доступным контекстом:
недоступную историю иных сеансов удостоверить нельзя. Прежний self-audit
верно описывал прежний авторский контекст и сохранён без переписывания.

В ignored work сохранены `role_and_input_locks.v1.json`, entry snapshot
пользовательских изменений и новые per-book submissions. Этот QC-контекст
не может выступить отдельным corrector или post-correction reviewer собственной
находки простым переименованием роли.

## Результаты книг

| Книга | Adjudicated / agreed | Полная сетка | Accepted decisions | Error | Uncertain | Книга |
| --- | --- | --- | --- | --- | --- | --- |
| Nah | 175 / 1 022 | 1 197 | 1 190 | 2 | 5 | blocked |
| Zeph | 251 / 1 228 | 1 479 | 1 475 | 0 | 4 | blocked |
| Zech | 278 / 1 328 | 1 606 | 1 599 | 0 | 7 | blocked |

Из sealed pass/comparison/adjudication восстановлен действующий final grid.
Ручная проверка прошла по каждому выбранному стиху: lexical links, группы,
повторы, original omissions и target additions/functions. Reciprocity,
source/target membership, metadata merge и exact OH text/comment сверены
отдельно. Bounded packets v2 использованы как вспомогательное представление;
они не заменили полные сетки. Новые full-grid observations содержат каждый
stable key, frozen decision, token evidence и rationale. Прежние QC verdicts
и rationale не использованы как новые ответы; их serialization scaffold
сохранён только для frozen pass/adjudication evidence и input locks.

## Собственные выводы по пяти loci

**Nah.1.8 — 5 critical uncertainties, o007–o008/t008–t010.** Selected MT
действительно содержит место/H4725 и женский suffix, а OH1988 — мятежников
и мужское «Його». MT-relative NULL/function/addition допустим; historical
translator addition этим не доказана. У Greek rebels нет possessive внутри
этой phrase, позднейшее possessive относится к enemies. NET перечисляет
несколько Hebrew retroversions; их нельзя объединить в выдуманный occurrence.
Доступная транскрипция 4Q169 не содержит 1:8 и здесь не подтверждает MT.
Необходимое решение: обосновать primary MT именно как gold universe либо
закрепить допустимый alternate occurrence с lemma/possessive/span; при alternate
перепроверить o007–o011/t008–t012. Точное историческое имя издания не требуется.
[NET apparatus, note 2](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10),
[Greek original](https://www.die-bibel.de/en/bible/LXX/NAM.1),
[4Q169 transcription](https://lexicon.qumran-digital.org/transcriptions/4Q169/2023-05-17/index.html).

**Zeph.2.14 — 2 high uncertainties, o026/t027.** חֹרֶב/H2721B означает
опустошение, не ворону; Greek и apparatus указывают на alternate עורב,
лексический кандидат H6158. В OH ворона принадлежит clause порога, а не
окна. Лексическое различие доказано, замена sealed MT token не выполнена.
Для acceptance нужен обоснованный primary disposition или alternate occurrence
и reciprocal span в этой clause, не dictionary proof другого стиха.
Аппарат note 53 проверен на полной странице; короткая verse page из v1
сама по себе его не показывала.
[NET apparatus](https://classic.net.bible.org/bible.php/d/xml/verse.php?book=Zep&chapter=2&verse=14),
[Greek original](https://www.die-bibel.de/en/bible/LXX/ZEP.2).

**Zeph.3.17 — 2 high uncertainties, o014/t014.** MT יחריש/H2790B —
молчание; OH — обновление собственной любви. Greek renew имеет объект YOU
и оборот IN HIS LOVE. Поэтому кандидат חדש/H2318 не доказывает без дальнейшего
span-разбора ту же конструкцию OH. Любовь/H0160 и possessive MT остаются
совместимыми с действующими links, preposition не выражен отдельно.
Необходимо решить verb occurrence и объект; alternate scope
o014–o017/t014–t016 сохраняется целиком.
[NET apparatus](https://classic.net.bible.org/passage.php?passage=Zep+3%3A17),
[Greek original](https://www.die-bibel.de/en/bible/LXX/ZEP.3).

**Zech.11.7 — 5 uncertainties, o008–o010/t008/t010.** לכן в MT —
lexicalized «поэтому»; его ל нельзя изолированно связать с recipient «тим».
עֲנִיֵּי/H6041 — afflicted, не merchant. Alternate word division имеет
научное основание, но Greek Canaanite phrase не содержит flock; Peshitta
не даёт независимого merchant-подтверждения. Релевантная страница Micheli
проверена по сохранённому PDF/render, printed p.113; весь PDF не заявляется
прочитанным. H3669B в native TAHOT Zec.14.21#18 доказывает lemma, не occurrence
11:7. Действующий flock/H6629 ↔ «отарою» сохраняется относительно MT;
alternate требует o008–o012/t008–t011, включая recipient/relative group.
[NET apparatus](https://classic.net.bible.org/passage.php?passage=Zec+11%3A7),
[Greek original](https://www.die-bibel.de/en/bible/LXX/ZEC.11),
[Micheli, 2014](https://asset.library.wisc.edu/1711.dl/SLJSCCINPKDRH9B/R/file-2bf6c.pdf).

**Zech.14.6 — 2 high uncertainties, o011/t011.** יקרות/H3368 —
precious/splendid, не lexical cold. Кандидат H7135 остаётся лексической
конъектурой, не новым occurrence. Qere קפאון и ketiv variation с H7087
допускают Strong-equivalent freezing смысл и не доказывают H7135.
Связь selected frost ↔ «замерзання» можно сохранить. OH отрицает свет,
затем утверждает холод/замерзание; Greek negative construction нельзя
копировать без clause-разбора. Alternate scope o007–o014/t006–t013 обязательный.
[NET apparatus](https://classic.net.bible.org/passage.php?passage=Zec+14%3A6),
[Greek original](https://www.die-bibel.de/en/bible/LXX/ZEC.14).

Exact OH1988 scans всех пяти loci проверены визуально; повреждения text/comment
не обнаружено. Примечания на страницах не дают конкретного original reading
этих loci. Авторская методология допускает консультацию разных источников,
но не выбирает occurrence за нас. Итог не сводится к отсутствию exact edition
name: нынешние semantic differences не Strong-equivalent, кроме отдельно
ограниченного H7087. Для всех пяти MT-relative accounting подтверждён как
кандидат, **content acceptance source choice не подтверждён**. Все 16 прежних
stable IDs перенесены без переименования в новый manifest.

## Дополнительная definite error: Nah.1.10

При обязательной full-grid проверке отвергнуто основание adjudication:
будто עד/H5704 не может выражать сравнительное «наче». BDB I.3 прямо
рассматривает Nah.1.10 в сравнительном употреблении; NET note 10 объясняет
его через simile. Это доказательство selected lemma в том же occurrence,
а не голосование переводов и не альтернативная реконструкция Hebrew.
[BDB entry, I.3](https://biblehub.com/hebrew/5704.htm),
[NET apparatus, note 10](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10).

Точное предложение изменения двух adjudicated rows:

- `original:gold7:original:92ee1c43bc08d4efdde3892564674eb1`:
  original omitted → one-to-one с `uk7:HIF:004:22:26` («наче»).
- `target:gold7:target:d297904ceebe75c4c22eb9a3777fa26f`:
  function token → aligned с
  `tahot:dda2e598e3ebfe6da975d39c0a2c4875415531ef57476a7974ce9c1fcd06e594:g01:a01`.

ID предложения: `gold7:correction-proposal:group001:Nah.1.10:v1:20261003`.
Full unchanged verse scope сохранён для revalidation; maqaf o003 остаётся NULL,
«той» t005 — function token. `_correction_scope_from_qc` принял ровно эти
два changed IDs и unchanged scope; hypothetical grid прошёл structural и
semantic accounting проверки только в памяти. Correction **не применена**.
Нужны separate consensus corrector и distinct post-correction full-grid QC;
source blocker Nah.1.8 даже после этой коррекции остаётся открытым.

## Артефакты и пределы приёмки

Work root: `scripts/bible_module/work/ukrainian_stage_7_20260801/`
`session_group1_20261003_independent_qc_01/`. В `completed/` находятся новые
adjudication QC JSONL/sidecars и полные full-grid content QC observations.
`repro_run_1/2` побайтно совпадают с completed; это воспроизводимость эмиссии,
не три независимых проверки. Старые passes/adjudication/QC/opinion/audit
не изменены. Global batch/aggregate registry сохранён; supplemental QC
зарегистрирован собственным versioned manifest, accepted registry не повышен.

Live `validate_adjudication_qc` вызван для каждого нового submission с exact
trusted sidecar SHA. Он отверг blocking status всех трёх. Его объединённая
ошибка `Independent adjudication QC status or reviewer independence differs`
не означает установленную зависимость новой роли: status здесь заведомо
`complete_qc_errors_found` / `complete_qc_uncertainty_found`, не accepted.
Дополнительный payload audit проверяет full scope, hashes и evidence отдельно.

Источники apparatus/Greek/PDF использованы read-only, без corpus import и
adoption новых dependencies. Новые HTTP snapshots BDB/4Q169 имеют физические
digests; прямой локальный fetch NET остановлен на expired certificate,
DBG — на 403, поэтому эти страницы проверены через browser tool без заявления
о локально сохранённых binaries. Старые locked controls/scans также сохранены.
Результаты окончательных checks записаны в [validation log](validation_log.md).

Следующая операция группы № 1: отдельная correction Nah.1.10 по sealed proposal,
затем отдельный post-correction QC; source disposition пяти loci остаётся
bounded исследовательской задачей. Внешний платный эксперт не является gate.
NT, этап 8, SQLite, production markup, DB, runtime, commit и push не выполнялись.

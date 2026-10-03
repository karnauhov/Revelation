# OH1988 7.4 — точечный запрос по группе № 1

2026-10-03. Gold принято **36/66**, новых accepted книг **0**.
`Nah`, `Zeph`, `Zech` исследованы, остаются blocked: **16 stable decisions
в пяти loci**. Полные SHA-locked grids сохранены только в gitignored
`scripts/bible_module/work/ukrainian_stage_7_20260801/session_group1_20261003/`.
Это запрос на независимую филологическую экспертизу, не на разрешение
изменить frozen Ukrainian text, mapping, gold selection/folds или gates.

## Что уже проверено

Stage 3/4/5/6 и stage-7 `--check` прошли перед чтением work JSONL.
Frozen text/manifest SHA совпадают с контрактом; exact scan пяти стихов,
сноски на соответствующих страницах и авторские pp232–234 (1963) просмотрены.
Текущие selected MT tokens сверены с pinned TAHOT и сохранёнными controls.
Отдельно восстановлены полные 228 locus decisions из frozen pass2 + adjudication,
сверены scalar/UTF-8 byte spans, stable IDs и blocking QC input/output locks.
Все три live acceptance-validator вызова отклонили existing blocking QC;
definite-error correction proposals в этих QC отсутствуют. Ни одного reviewer
ID не добавлено; source research не выдан за независимый content QC.

## Какое решение требуется

Нужен реальный независимый reviewer, способный проверить original readings и
украинский синтаксис. Для каждого clause требуется source-qualified
lemma/Strong + доказательство token/span links и reciprocal accounting либо
обоснование gold NULL/addition относительно неизменного selected MT.
Точное историческое edition name и точная vowel form не являются отдельными
условиями, когда lemma, Strong и span доказаны; Strong-equivalent формы можно
указать явно. Однако одинаковый Strong не доказывает существование token,
границу слова, suffix antecedent или OH1988 link.

При доказанном source-layer error нужен versioned source overlay с input locks,
stable IDs/supersedes и проверкой всех затронутых links. При definite alignment
error — sealed correction scope, отдельная correction и distinct post-correction
QC по действующему контракту. До этого счётчик accepted не увеличивается.

## Nah.1.8 — пять critical решений

[Manifest / полные IDs и digests](gold_group_001_Nah.source_resolution.v1.manifest.json).
Exact OH1988: «між Його заколо́тниками». MT: place/H4725 + suffix her/3fs.
Аппарат различает lexical reading adversaries/his. Greek сходство не позволяет
назначить Hebrew token или H4725 этому span. Published Qumran-Digital 4Q169
transcription не содержит 1:8; apparatus claim о 4QpNah не принят как witness.

Stable IDs:

- `original:gold7:original:0b721d33cdaba7a076550941918622a7` — o007/place.
- `original:gold7:original:9a94864484391a6831876447136fa8ce` — o008/her.
- `target:gold7:target:daf24d1e267a294a73efda0526dcb58d` — t008/між.
- `target:gold7:target:2fe7f3d4cd153c6dd38fca85806a87ce` — t009/Його.
- `target:gold7:target:41bcb432f700640927d9f8a4df7f49da` — t010/заколотниками.

Не хватает verse-local доказательства конкретного lexical token и suffix/span
связи либо обоснования MT omission/addition/function accounting. Возможные
retroversions не выданы за attested original form.

## Zeph.2.14 — два high решения

[Manifest](gold_group_001_Zeph.source_resolution.v1.manifest.json).
MT desolation/H2721B против OH1988 «воро́на». Аппарат предлагает raven
`עֹרֵב`, candidate H6158, по versional witnesses. Number variance Greek
plural / Ukrainian singular — grammatical-only; сама смена lemma — lexical.

- `original:gold7:original:73917e360ed18eedbd018674885004cd` — o026/desolation.
- `target:gold7:target:a3806d38fd121622e481be1c9b64e935` — t027/ворона.

Не хватает source-qualified original token/reading и решения о raven link
либо translation departure от выбранного MT. H6158 не назначен.

## Zeph.3.17 — два high решения

MT silence/H2790B против «обно́вить». Apparatus renew/candidate H2318
и Greek diagnostic имеют объект «ты»; OH1988 — «любов Свою».

- `original:gold7:original:78ae92bbb60b54c2e3e2d9555fd845c6` — o014/silence.
- `target:gold7:target:10dd1cf013227b7702669734dbe75e42` — t014/обновить.

Нужен полный разбор renew + love/preposition/suffix. Conditional revalidation
scope: o014–o017, t014–t016; остальные принятые rows не переобъявлены errors.
Один переводной bridge или общий метод Огиенко не доказывает данный span.

## Zech.11.7 — пять high/critical решений

[Manifest](gold_group_001_Zech.source_resolution.v1.manifest.json).
MT therefore/afflicted против «тим, хто торгує отарою»; alternative merchants
меняет word division и lexical token, candidate H3669. Peshitta diagnostic
даёт отдельное решение multitude of flock, а не independent vote за merchants.

- `original:gold7:original:182a2d690f608f6eeec928a9872a64b2` — o008/preposition.
- `original:gold7:original:7132cf85f43874f19f893df3cfa4cb77` — o009/therefore.
- `original:gold7:original:da2302d8da6a84a2cd332bb909f552d6` — o010/afflicted.
- `target:gold7:target:b6aac718a75550d594b5a6b7629029a2` — t008/тим.
- `target:gold7:target:cb84d829949305315e9b15556c2d95b0` — t010/торгує.

Нужны source word boundary + merchant lemma + reciprocal group. При выборе
alternative revalidate o008–o012 / t008–t011, включая «хто» и «отарою».
Старые MT IDs нельзя просто переиспользовать для нового merchant token.

## Zech.14.6 — два high решения

MT splendid/H3368 против «холод». Qere noun/ketiv verb normalize to H7087;
это grammatical-only Strong-equivalent variant, уже сохранённый явно,
а связь «замерзання» сама по себе не закрывает cold lemma.

- `original:gold7:original:44abdaf3b1c66777b17cf5b214bc3ce0` — o011/splendid.
- `target:gold7:target:174679b26dc830e3b8c9a3e916ef065d` — t011/холод.

Нужен original cold lemma/token и span отдельно от H7087; candidate Strong
по одной ретроверсии не выбран. Revalidate o011–o014 / t011–t013 при source change.

## Исследовательские ссылки и роли

Все новые scholarly материалы использованы read-only, source corpora не
импортированы. Qumran-Digital CC BY-SA 4.0; NET notes copyrighted research-only;
Micheli PDF copyright 2014, all rights reserved, только ignored local research.

- [Qumran-Digital 4Q169, version 2023-05-17](https://lexicon.qumran-digital.org/transcriptions/4Q169/2023-05-17/index.html).
- [NET Nah 1:8 apparatus](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10).
- [NET Zeph 2:14 apparatus](https://classic.net.bible.org/verse.php?book=Zep&chapter=2&verse=14).
- [NET Zeph 3:17 apparatus](https://classic.net.bible.org/passage.php?passage=Zep+3%3A17).
- [NET Zech 11:7 apparatus](https://classic.net.bible.org/passage.php?passage=Zec+11%3A7).
- [NET Zech 14:6 apparatus](https://classic.net.bible.org/passage.php?passage=Zec+14%3A6).
- [Micheli 2014, pp35–36 и 113–114](https://asset.library.wisc.edu/1711.dl/SLJSCCINPKDRH9B/R/file-2bf6c.pdf).

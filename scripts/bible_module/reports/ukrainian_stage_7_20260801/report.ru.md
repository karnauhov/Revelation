# Этап 7: evidence-first Strong alignment OH1988

Doc-Version: `1.0.0`
Last-Updated: `2026-09-05`
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
Оба независимых прохода и post-blind comparison завершены для `Gen–2Chr`
(459 стихов, 12 220 original и 10 120 target). Для `1Sam–1Kgs` завершены
distinct third adjudication и независимый QC; adjudication `Gen–Ruth` начата,
а pass 2 для `Ezra–Rev` ещё не выполнен.
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

Следующая blind-партия `2Kgs–2Chr` также завершена и повторно проверена:
98 стихов, 2 675 original и 2 149 target-accounting decisions. Из 4 824 stable
решений 3 793 совпали, 1 031 substantive disagreement ожидают distinct
adjudication; exact digests закреплены в
`gold_review_batch_012_014.manifest.json`.

В накопленной очереди `Gen–Ruth` третья adjudication завершена для `Gen`,
`Exod`, `Lev`. `Gen` полностью принят после независимого QC всех 230/230 строк
(`error=0`, `uncertain=0`). `Exod` не принят: полный QC 130/130 обнаружил шесть
ошибочных reciprocal rows в трёх фразах, где украинские `той/те` следует
связать с отдельным еврейским артиклем `הַ/הָ`, а не с noun atom; correction
ещё не применён. `Lev` QC остановлен по просьбе владельца на 145/216; exact 71
remaining IDs и все SHA сохранены в checkpoint со статусом
`partial_not_accepted`.

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

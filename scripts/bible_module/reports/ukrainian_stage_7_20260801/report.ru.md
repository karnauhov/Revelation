# Этап 7: evidence-first Strong alignment OH1988

Doc-Version: `1.0.0`
Last-Updated: `2026-08-08`
Source-Commit: `working-tree`
Schema-Version: `1`
Contract-Version: `ukrainian-stage-7-evidence-alignment-v1`
Input-SHA-256: `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`
Processed/Skipped/Errors: `31102 / 682836 / 0`

## Статус

Этап **не закрыт**. Доказаны immutable input freeze, точная украинская
токенизация, raw primary/alternative component reparse, native-token control
layer, source/license registry и аудит первичных исторических документов.
Exact-edition textual adjudication, target-side bridge proof и gold остаются
частичными и fail-closed. Нормативный gold-набор содержит
`0 / 25 000` принятых assignment/null решений и ни одно решение не прошло два
независимых слепых прохода. Поэтому candidate tuning, A/B/C calibration и
production Strong markup намеренно не выполнялись.

## Зафиксированные результаты

- exact stage-6 texts/comments: 31,102 позиций;
- украинские surface tokens: 595,077;
- raw original components (включая 14 primary-null) после повторного чтения TAHOT/TAGNT: 682,836;
- отдельно адресуемые TAHOT/TAGNT apparatus alternatives: 28,542;
- raw OSHB/UXLC/UGNT control tokens: 751,557;
- exact unique control→TAHOT/TAGNT crosswalks: 632,592; unresolved/service: 118,965;
- покрытие original refs application grid: 31,102 / 31 102;
- RUSSYN/YLT manual bridge records audited: 836,745;
- украинские comparison lexemes: 44,721;
- book-balanced annotation panel: 2,171 стихов,
  45,596 projected original decisions;
- закреплённые legacy negative counterexamples: 12;
- accepted production Strong links/markers: `0` (fail-closed).

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
считается modern-critical reading. Остаются
1,970 unresolved source-apparatus refs /
4,008 components; соответствующие
loci блокируют автоматическое назначение до adjudication и gold calibration.

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

# OH1988 7.4 — задание отдельному QC-контексту группы № 1, v1

Дата: 2026-10-03. ID: `gold7:qc-context:group001:task:v1:20261003`.
[HANDOFF](HANDOFF.ru.md), [заключение v1](gold_group_001_philological_opinion.v1.ru.md),
[аудит контекста/accounting](gold_group_001_qc_context_accounting_audit.v1.ru.md).
Задание подготовлено авторским контекстом; оно не является QC-ответом.

## Перед началом

Рабочая директория `C:\Users\karna\Projects\Revelation`.
Только 7.4, группа № 1: Nah, Zeph, Zech. Без подагентов; NT не начинать.
Владелец не располагает внешней экспертизой/бюджетом; исследовать доступные
оригинальные источники самостоятельно. Не ослаблять acceptance gates.

Зафиксировать фактическую роль: текущий reviewer не должен быть автором
reviewed pass decisions/adjudication/correction или заключения v1. Проверить
контекст разговора и роли в manifests. Новый reviewer ID, новый чат или модель
сами по себе независимость не доказывают. Если контекст сохраняет авторскую
работу, сохранить self-audit и не выпускать independent QC submission.
Чтение reviewed files в отдельном QC-контексте необходимо для проверки и
не означает их авторство. Не объявлять старые независимые passes ложными
только из-за общего слова Codex в IDs.

Полностью прочитать AGENTS.md, .github/change_checklist.md, roadmap,
alignment plan и актуальный HANDOFF. Проверить git status, сохранить
пользовательские изменения. До полных work JSONL выполнить stage 3/4/5/6
`--check`, SHA-locks и stage-7 `--check`; inventory обновлять только отдельным
writer, не регенерировать reviewer answers/book semantics.

## Замороженный контракт

- edition `ohienko_1988`, code `OH1988`, target positions **31 102**;
- mapping `oh1988-kjv-protestant-v1`;
- stage-6 text SHA `e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf`;
- text manifest SHA `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`;
- text/comment и stage-5 mapping не менять; gold selection/folds не менять;
- gold **36/66**, новых принятых книг этим исследованием **0**;
- stage 8/SQLite/production Strong markup/Flutter/content tool/KJV/LXX_TR/
  web/working DB/commit/push не выполнять.

## Точный предмет content QC

Source diagnostics v1, philological opinion v1 и audit v1 manifests содержат
16 полных stable IDs и физические input digests. Переносить их без переименования.
Текущие blockers:

| Locus | Stable index scope | Проверяемая рекомендация |
| --- | --- | --- |
| Nah.1.8 | o007–o008/t008–t010 | MT place/her NULL; між function; Його/заколотники addition; проверить possessive и adversaries occurrence |
| Zeph.2.14 | o026/t027 | desolation NULL / raven addition; отличить lemma proof от occurrence |
| Zeph.3.17 | o014/t014 | silence NULL / renew addition; проверить объект и love/his/preposition при alternate |
| Zech.11.7 | o008–o010/t008/t010 | lexicalized לכן и afflicted NULL против merchant recipient; проверить alternative word division |
| Zech.14.6 | o011/t011 | precious NULL / cold addition; не смешивать H7087 grammar equivalence с lexical cold; проверить negation scope |

Проверять содержание независимо, не подтверждать v1 по умолчанию:

1. Определить, удовлетворяет ли выбранный MT universe gold-контракту каждого
   locus при явном учёте вариантов. Структурное отсутствие counterpart ещё
   не доказывает content acceptance. Не называть source-related addition
   исторической вставкой переводчика без доказательства.
2. Проверить pinned licensed original controls, apparatus, exact OH1988 scans
   и авторские примечания по input locks. Translation bridges — только в
   разрешённой роли; позиция, соседство, verse bag и голоса переводов не
   доказывают Strong/link. Copyright apparatus — read-only, не corpus import.
3. При доказанных lemma/Strong/span не требовать точного исторического имени
   издания ради имени. Strong-equivalent варианты явно записать с пределом
   точности; не выдумывать точную форму или token existence.
4. При alternate selection перепроверить conditional scopes из manifest v1:
   Nah o007–o011/t008–t012; Zeph 3.17 o014–o017/t014–t016;
   Zech 11.7 o008–o012/t008–t011; Zech 14.6 o007–o014/t006–t013.
   У Zeph 2.14 проверить o026/t027 и границы clause.
5. Проверить весь действующий final grid каждой книги, включая reciprocal
   agreed decisions, omissions/additions/groups: 1 197/1 479/1 606 rows.
   Corrected bounded packets v2 — display, не замена sealed input или
   требуемой full-grid QC-проверки. Старый v1 display расходится в agreed
   evidence/severity/phenomena, но не в link/null/group.
6. При content PASS выпускать предусмотренный действующим validator QC
   с input digests, stable IDs, token-level evidence/rationale и truthful
   reviewer independence. Только live acceptance-validator повышает счётчик.
7. При definite error сохранить concrete correction proposals и versioned
   chain. Не подменять uncertainty error ради correction scope; corrector
   и post-correction QC должны удовлетворять отдельным требованиям ролей.
   При нехватке свидетельства сохранить exact locus/IDs/проверенное/недостающее
   и требуемое решение; не объявлять недоступность внешнего эксперта причиной
   отказа от собственного исследования.

## Сохранение и проверки

После каждого bounded блока/книги актуализировать HANDOFF и roadmap,
manifests/report/validation log/inventory. Full corpus/review JSONL только
в gitignored work. Старые checkpoint не являются заданиями повторять passes.
Воспроизводимые выпуски, физические SHA-locks, целевые gold/correction/QC
regression tests, нужные stage checks, inventory audit и `git diff --check`.
При общем code change — соответствующие полные suites; N/A обосновать.

Остановиться после группы № 1. Сообщить принятые/blocked книги, точные остатки,
счётчик, HANDOFF и prompt продолжения; английский commit message `[skip ci]`.
По текущему запросу владельца в конце проиграть Windows Alarm02 три раза.

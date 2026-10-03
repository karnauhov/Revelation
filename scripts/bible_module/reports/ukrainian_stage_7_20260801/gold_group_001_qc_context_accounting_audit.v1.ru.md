# OH1988 7.4 — аудит QC-контекста и MT NULL-accounting, v1

Дата: 2026-10-03. ID: `gold7:qc-context-accounting:group001:audit:v1:20261003`.
Роль: проверка собственной рекомендации, **не независимый content QC**.
[Заключение v1](gold_group_001_philological_opinion.v1.ru.md),
[manifest аудита](gold_group_001_qc_context_accounting_audit.v1.manifest.json),
[задание отдельному QC-контексту](gold_group_001_independent_qc_task.v1.ru.md),
[HANDOFF](HANDOFF.ru.md).

## Результат

Gold **36/66**, новых принятых книг **0**, осталось **30**. Nah, Zeph, Zech
не приняты; NT не начат. Все 16 blockers сохранены в пяти loci.
Рекомендации v1 совпадают с текущим link/NULL/group accounting и проходят
структурные проверки, но их content acceptance не получена.

Проверены 74 физических input locks заключения, 62 locks batch manifests,
154 QC digest references (152 уникальных SHA), 4 282 полных post-adjudication
decisions, 228 bounded decisions и 109 украинских scalar/byte spans.
`_validate_final_grid` и `_validate_semantic_accounting` прошли для полных
книг и каждого bounded grid. Отсутствуют dangling/cross-verse links,
несогласованные hyperedges и links у addition/function tokens.

| Книга | Полный grid | Bounded grid | Exact spans | Не снятые blockers |
| --- | ---: | ---: | ---: | --- |
| Nah | 1 197 | 30 | 15 | 1.8: o007–o008/t008–t010, 5 critical |
| Zeph | 1 479 | 107 | 52 | 2.14: o026/t027; 3.17: o014/t014, 4 high |
| Zech | 1 606 | 91 | 42 | 11.7: o008–o010/t008/t010; 14.6: o011/t011, 7 |

Для каждой книги вызван действующий `validate_adjudication_qc` с её sealed
JSONL/sidecar и input paths. Все три отклонены:
`Independent adjudication QC status or reviewer independence differs`.
У существующих QC статус `complete_qc_uncertainty_found`, а не accepted;
это достаточная причина отказа. Их четыре role IDs различны. Сообщение
validator **не доказывает**, что старый reviewer был фактически зависимым.
`_correction_scope_from_qc` отдельно отклонил все три пакета:
`Blocking QC manifest lacks correction proposals`. Definite errors не выдуманы.

## Проверка независимости текущего контекста

Этот чат сохраняет контекст авторства задания и заключения v1. Сам manifest
v1 фиксирует `author_role=current_Codex_source_research_not_independent_QC`
и `independent_qc_submission=false`. Повторное указание владельцем на v1
не создаёт нового исполнителя. Поэтому текущий аудит не подаётся как QC,
reviewer ID не назначается и старые uncertainty verdicts не меняются.

Проверка отличающихся role IDs в коде — необходимая проверка metadata;
она не измеряет реальную независимость автора/контекста. Основание текущего
вывода — сохранённое авторство в этом разговоре, не название модели, дата,
автоматическое сообщение validator или предположение о старых reviewers.

Отдельный новый чат Codex без истории авторской работы может выполнить
самостоятельную проверку по файлам; платить внешнему эксперту не требуется.
До выпуска QC он должен зафиксировать фактическое отсутствие роли автора
reviewed decisions/заключения, самостоятельно проверить sources и следовать
полному QC-контракту. Сам факт нового чата или нового ID не заменяет эту проверку.
Подготовлено [полное задание](gold_group_001_independent_qc_task.v1.ru.md).

## Проверка рекомендаций относительно selected MT

Для всех восьми спорных original rows проверены singleton group, пустой
target list и допустимый NULL reason; для восьми target rows — допустимый
addition/function status, пустой original list и отсутствие обратного ребра.
Семь original rows имеют `translation_omission`; `Zech.11.7 o008` имеет
`grammatical_function_not_overt`. Семь target rows — `translation_addition`,
`Nah.1.8 t008` — `function_token`. Все 16 semantic projections совпадают
с действующим post-adjudication grid и frozen blocking QC.

| Locus | Accounting-кандидат v1 | Что этот аудит не снимает |
| --- | --- | --- |
| Nah.1.8 | place/her o007–o008 NULL; між t008 function; Його/заколотниками t009–t010 addition | adversaries occurrence и связь possessive; нельзя автоматически перенести уже agreed enemy-his o011 |
| Zeph.2.14 | desolation o026 NULL; ворона t027 addition | Hebrew raven occurrence; H6158 dictionary proof не создаёт token |
| Zeph.3.17 | silence o014 NULL; обновить t014 addition | renew occurrence и объект: «любов Свою» против Greek renew-you; при alternate перепроверить o014–o017/t014–t016 |
| Zech.11.7 | o008–o010 NULL; тим/торгує t008/t010 addition | alternate word division и recipient/relative group; H3669 остаётся lexical candidate |
| Zech.14.6 | precious o011 NULL; холод t011 addition | cold occurrence/link; H7087-equivalent qere/ketiv не доказывают cold; при alternate scope o007–o014/t006–t013 включает отрицание |

Аппарат повторно просмотрен как read-only свидетельство вариантности:
[Nah 1:8](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10)
обсуждает несколько retroversions adversaries;
[Zeph 2:14](https://classic.net.bible.org/verse.php?book=Zep&chapter=2&verse=14)
отличает desolation от raven emendation;
[Zeph 3:17](https://classic.net.bible.org/passage.php?passage=Zep+3%3A17)
отличает silence/soothe от renew-you;
[Zech 11:7](https://classic.net.bible.org/passage.php?passage=Zec+11%3A7)
обсуждает merchant resegmentation;
[Zech 14:6](https://classic.net.bible.org/passage.php?passage=Zec+14%3A6)
различает splendid/congeal и reconstructed cold/ice. Это copyright research
only; новый corpus и Strong annotations не импортированы. Greek/scans/авторские
примечания и дополнительные исследования остаются SHA-locked evidence v1;
их повторный просмотр в этой итерации не заявляется.

**Предел рекомендации:** addition здесь означает отсутствие связи с selected
MT counterpart; это не доказательство авторской вставки Огиенко. Наличие
нормального NULL само по себе не подтверждает правильность selected-source
universe для gold. Отдельный QC должен принять либо обоснованный MT accounting
с явным учётом вариантов, либо доказанный alternate layer и reciprocal spans.
Историческое название точного издания не требуется ради самого названия;
неопределённость token occurrence/lemma/link нельзя снять одинаковым Strong.

## Исправление диагностического экспорта

Начальная строгая проверка равенства bounded v1 rows текущему validator grid
выявила metadata расхождения у **171 agreed rows**: Nah 21, Zeph 93, Zech 57.
Старый exporter брал pass-2 rows вместо `_merge_agreed_review_metadata`.
Различались только rationale, reviewer ID, evidence, severity и phenomena;
link/null/group accounting всех 228 rows совпадает. Все 16 blocking rows
полностью согласуются с текущими semantic projections. Это дефект display
export, не доказанная ошибка original parser или frozen book semantics.

Сохранены versioned `*.bounded_final_grid.v2.jsonl` в ignored
`work/ukrainian_stage_7_20260801/session_group1_20261003_qc_context_01/`.
Новый exporter использует `_validated_post_adjudication_values`, фиксирует
SHA superseded v1 packet, сохраняет stable IDs и exact token indexes.
Per-book audit results содержат все changed stable IDs/fields и digests.
V1 не перезаписаны, заключение v1/его manifest не менялись; book answers,
adjudication, QC и correction history остались побайтно прежними.
Это versioned correction диагностического экспорта; gold correction overlay
не создавался, поскольку доказанного изменения alignment нет.

## Следующая операция

Открыть отдельный QC-контекст по [заданию v1](gold_group_001_independent_qc_task.v1.ru.md)
и актуальному HANDOFF, использовать corrected bounded packets v2 как удобный
display, а sealed full-grid inputs — как источник истины. Сначала подтвердить
реальную независимость, затем провести content QC/source choice. Условия
acceptance остаются прежними. Nah/Zeph/Zech + все 27 NT остаются в очереди;
NT текущей сессией не начинается.

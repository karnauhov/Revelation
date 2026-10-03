# Независимый QC completion overlay и общего issue inventory

Версия 1, 2026-10-03. Reviewer: `codex-completion-overlay-qc-group001-20261003-isolated01`.

**PASS** для подготовленного completion overlay Zeph и механического переноса известных вопросов в общий реестр. [Прямое правило владельца](gold_group_001_completion_policy.v2.manifest.json) допускает `completed_with_registered_deferrals`: после отдельного root seal завершённость OT составляет **39/39**, а строгая полностью доказанная book acceptance остаётся **38/66**. Подготовленный артефакт проверен; публикация completion требует SHA-bound root seal. Это разные показатели.

## Реальная роль и границы независимости

Examiner не автор новой completion policy, overlay, его validator или общего реестра. Он автор [предыдущего sealed strict content QC](gold_group_001_final_content_qc.v1.ru.md), который новый overlay использует как исходный факт. Поэтому настоящая независимость относится к новой механической трансформации авторов, а не заявляется вторым независимым content QC собственных прежних findings. Первоначальное content QC назначение было изолировано с `fork_turns=none`; reviewed pass/adjudication/correction/source decisions тогда не были написаны examiner. Чтение reviewed файлов является инспекцией.

Новый review проверяет policy/учёт deferrals и сохранность доказанных решений. Повторное чтение всех 96 стихов и новое исследование NT не выполнялись. Прежние verdicts, frozen answers, исходные слова/comments, source universes/selection, строгие validators, canonical batches/aggregate, runtime и DB этим examiner не изменены.

## Точный Zeph component и полный учёт

Проверены все **1 479 present nodes**: 787 original и 692 target. В effective projection **1 477 accepted decision labels** сохраняют точные прежние `final_decision`; это количество решений, а не утверждение такого же числа Strong edges. Два оставшихся узла получают `deferred_strong_unassigned`, `assigned_strongs=[]`, `strong_assignment=null`, `leave_without_Strong=true` и исключаются из training/scoring labels.

| Узел | Stable key | Точное свидетельство |
|---|---|---|
| original | `original:gold7:original:10fc92cfed6f96220c8e399e5cae90df` | o011 `ג֔וֹי`, TAHOT `Zep.2.14#06=L`, candidate `H1471A`/`H1471` |
| target | `target:gold7:target:0f7a3987f7a982ea98a91541df10fa80` | t008 `польова́`, `uk7:HLW:008:40:48`, scalar `[40:48)`, UTF-8 bytes `[72:88)` |

Единственный candidate edge `gold7:edge:28cd40f8e91c6c1d4bed9889339bced7` исключён. Компонент замкнут: другие 1 477 решения не ссылаются на эти source/target IDs. Два узла присутствуют в полном учёте; они не переименованы в error, source omission/NULL, translation addition или новое phrase group. Frozen reciprocal one-to-one/aligned snapshot сохранён как исторический кандидат, а content verdict по-прежнему **uncertain**. Deferred nodes в effective projection не содержат принятой alignment-семантики. Реестр связывает их с одним issue `oh1988:strongs-issue:v1:Zeph.2.14:uncertain`.

## Общий реестр известных вопросов

Проверены [JSONL общего реестра](strongs_issue_inventory.v1.jsonl), [читаемый индекс](strongs_issue_inventory.v1.ru.md), его [manifest](strongs_issue_inventory.v1.manifest.json), действительные QC sidecars и extractor. Сверка охватывает **66 unique book QC sources**, **174 активные locus/verdict записи / 515 stable keys**: 503 uncertain и 12 ранее установленных errors. Из них 1 активная запись OT — текущий Zeph component; остальные 173 записи NT перенесены механически. NT completion и новый NT content QC этим review не утверждаются.

Отдельно сохранены **5 закрытых retained-MT-reference loci / 16 accepted source keys** из прежнего source disposition. Они исключены из активного остатка. Проверены **531 точный decision snapshot**, **242 source token records** и **297 target records**, включая scalar/UTF-8 slices по неизменному Stage 6 text. Candidates совпадают с исходными source records и не превращены в Strong assignments. Существующий Eph correction честно отмечен как pending отдельного post-correction QC.

**294** известных agreed findings не имеют индивидуальной QCJSONL строки. Их действительные sidecar key arrays, exact pass snapshots и существующие locus notes сохранены; новые индивидуальные rationales не придуманы. Attempted alternatives/missing proof/follow-up ссылаются на имеющийся QC и research; отсутствие ранее записанного detail обозначено явно. Follow-up остаётся необязательным или выполняется по поручению владельца, а прежняя историческая workflow recommendation не превращена в новый completion gate.

## Выполненные проверки и provenance

До новой работы проверены физические SHA/bytes **250 входов и 40 выходов** прежнего sealed QC; два изменённых policy inputs найдены по явным byte-preserved историческим locators. У общего реестра проверены **220 inputs + 2 outputs** до и после инспекции. Независимый reconcile подтвердил точное равенство всех активных known-QC keys без дублей и потери closed-history distinction.

Actual separate completion `validate` CLI завершился с **exit 0** и повторно проверил 670 физических evidence bindings. Неизменный strict QC продолжает отклонять uncertain Zeph. Семь actual negative checks отклонили placeholder/stale SHA, новый unregistered uncertain key, relabel uncertainty→error, изменение frozen payload, потерю узла и отсутствие reciprocal proof. Обе авторские candidate emissions побайтно одинаковы; повторение emission не выдаётся за нескольких независимых reviewers.

SHA-bound [examiner review proof](../../work/ukrainian_stage_7_20260801/session_group1_20261003_completion_qc_01/independent_completion_review.v1.json), [actual CLI evidence](../../work/ukrainian_stage_7_20260801/session_group1_20261003_completion_qc_01/live_cli_results.v1.json) и [этот QC manifest](gold_group_001_completion_qc.v1.manifest.json) фиксируют точные inputs/outputs. Prepared candidate находится в ignored author session; root может выполнить только согласованный seal. Авторский [completion CLI contract](../../work/ukrainian_stage_7_20260801/session_group1_20261003_closure_completion_01/CLI.ru.md) требует активный, актуальный overlay перед будущими Strong/training exports и запрещает export при его отсутствии или stale SHA. Диагностический projection сейчас ничего не экспортирует; training, Stage 8 и production export не разрешены этим PASS.

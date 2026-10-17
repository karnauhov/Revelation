# Независимая проверка диагностической калибровки 7.7

**Техническая проверка: PASS. Статистический результат: NO_GO.**
Автоматическое принятие Strong links: **0**. Новая оценка test fold4: **SKIPPED**.
Этап 7 целиком не объявляется завершённым.

Проверяющий — `/root/independent_review77`; реализацию написал `/root/calibration_author`.
Это фактически отдельный агентный контекст без истории авторского исполнения.
Проверяющий не писал producer; его файлы — собственные аудиторы, fixtures, receipts
и этот отчёт. Чтение проверяемого кода — inspection, не authorship.
[Role attestation](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/role_attestation.v1.json).

## Порядок и неизменность

Root preflight PASS получен до полного чтения work JSONL. Независимый
[prefit approval](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/prefit_approval.v1.json) выдан до реального fit,
с точными 11 package files (13 с parent initializers). Protocol SHA:
`f605376ddcd09796ca72e4b84a463b4c2aeb224ca50868a68cbcdf022339cefa`; learned pipeline freeze SHA:
`b3393f0a7f6adf51cc169b3e28c10d03bc4b6926a3b45a236f1144a6eb09e517`. После model+policy freeze был один author validation3
claim; независимый пересчёт не вызывал producer fit/evaluator и не создавал claim.
Один преждевременно начатый raw auditor был остановлен до сообщения об окончании
node loading и до labels stage, без output: [phase receipt](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/raw_phase_guard.v1.json).

Fixed rank-only PAVA, equal-score aggregation, adjacent-violation pooling,
нижний block в score gaps и отказ от extrapolation за development range
проверены своей арифметикой. Пороги .995/.5 и 10 reliability bins не подбирались.
Development 0–2 fit и его diagnostics in-sample; validation3 не использовалась
для fit, домена, выбора метода/порога или исправления модели. Fold4 — исторически
использованная partition, не новая untouched holdout; старые aggregate scores
были доступны в обязательных predecessor docs и их exposure признано.
[Исторические результаты 7.6](consensus76.v1.ru.md) остаются отдельным результатом;
они не выданы за новую test4 evaluation калибровки.

Обычная calibrator CV над frozen OOF ranks не была бы nested: например,
обучающий calibrator fold0 score уже зависит upstream от heldout fold2 gold.
Original OOF исключает собственный fold0, но не fold2. Поэтому cross-fitted
calibration и nested-CV не заявлены. 234 названия reviewed taxonomy из frozen
aggregate lock использованы только для 341 обязательной страты; с общей строкой `all`
это 342 metric rows в каждом scope. Counts/outcomes
не влияют на features, applicability, classes или thresholds.
[Lineage review](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/protocol_lineage_review.v1.json).

## Собственный raw пересчёт и полный payload

Stdlib auditor не импортирует producer arithmetic. Проверены raw selected
originals, surface targets, mask, annotation physical accounting и frozen graph:
**31102 verses / 678149 original / 595077 target nodes**, каждый ровно один раз.
Full reviewed nodes 87638; eligible 87108; deferred 530, из них original 240 / target 290.
В 2171 reviewed verses физически 45538 eligible complete gold hyperedges.
Semantic labels folds0–3 пересчитаны; fold4 — только physical denominators,
без нового correctness membership или metrics. Неизменный graph содержит
401983 candidate hyperedges и 297767 selected top1 hyperedges.

Physical IDs, duplicates и cross-verse целостность проверяются до whole-edge
deferral. Relation/NULL/status/phenomena, correctness, features и probability
исключённых rows остаются opaque. Semantic unit — полная declared hyperedge
со всеми endpoints, relation и NULL reason. Multiword, reciprocal accounting
и shared-target union не расширяются в дополнительные Bernoulli trials.
Все 297767 вероятностей/classes, full node incidence/status, raw-candidate
absence/unselected distinction, reciprocal unions, 341 required strata + overall `all`
(342 metric rows) каждого scored
scope и label-free full topology пересчитаны независимо.
[Raw receipt](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/raw_audit.v1.json),
[полный пересчёт](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/metric_payload_recalculation.v1.json).

Первый полный metric comparator остановился на схеме пустого reliability bin:
frozen producer сохраняет в нём служебное `probabilities: []`. Исходный auditor
сохранён, отдельный v2 добавил точное представление этого пустого поля.
Формулы, числовые результаты, classes и scopes не изменялись; producer и
learned freeze остались теми же. Финальный полный повторный пересчёт выполнен
этой versioned oracle: [correction receipt](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/metric_oracle_empty_bin_correction.v1.json).

## Итоговые классы: точные знаменатели

Под NO_GO диагностические A_proposed переходят в C_unresolved.
B_review — очередь проверки; этот слой ничего не принимает.
FN каждого класса использует весь eligible gold denominator partition.
Strata могут пересекаться; их counts нельзя складывать в общий denominator.

| Scope | Final class | TP | FP | FN | P denominator | R denominator | Precision | Recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev0–2 | A_auto | 0 | 0 | 27462 | 0 | 27462 | undefined | 0.0000% |
| dev0–2 | B_review | 6002 | 4311 | 21460 | 10313 | 27462 | 58.1984% | 21.8557% |
| dev0–2 | C_unresolved | 477 | 1471 | 26985 | 1948 | 27462 | 24.4867% | 1.7369% |
| validation3 | A_auto | 0 | 0 | 8541 | 0 | 8541 | undefined | 0.0000% |
| validation3 | B_review | 1921 | 1335 | 6620 | 3256 | 8541 | 58.9988% | 22.4915% |
| validation3 | C_unresolved | 161 | 521 | 8380 | 682 | 8541 | 23.6070% | 1.8850% |

Пустой A_auto не имеет precision, Brier или ECE; undefined не заменено 100%.

## Калибровочные diagnostics по классам

Все probability diagnostics — только для supported probabilities;
unsupported count сохранён отдельно. Разбиение на final classes — отчётное
применение тех же заранее фиксированных формул, без изменения producer/model.
Полные 10 equal-width bins каждого класса и scope находятся в receipt по ключу
`scopes[].calibration_by_final_class`. Development diagnostics остаются in-sample.

| Scope | Final class | All edges | Supported N | Brier | Log loss | ECE |
|---|---|---:|---:|---:|---:|---:|
| dev0–2 | A_auto | 0 | 0 | undefined | undefined | undefined |
| dev0–2 | B_review | 10313 | 10313 | 0.23677083 | 0.66348652 | 0.00000000 |
| dev0–2 | C_unresolved | 1948 | 1948 | 0.16516945 | 0.50766019 | 0.00000000 |
| validation3 | A_auto | 0 | 0 | undefined | undefined | undefined |
| validation3 | B_review | 3256 | 3256 | 0.23533876 | 0.66015763 | 0.00629030 |
| validation3 | C_unresolved | 682 | 682 | 0.15688628 | 0.48819610 | 0.02128736 |

## Почему NO_GO остаётся обязательным

Независимый physical recount даёт лишь 13–97 reviewed eligible verses
на книгу во всех folds вместе. Это верхний ceiling возможных независимых
verse trials, не доказанное Bernoulli n. Даже all-success односторонний 95%
Wilson требует 539 trials для lower bound 99.5%; все 66 books обязательны и
после просмотра outcomes не исключались.

Самостоятельно подтверждены границы: 538/538 FAIL, 539/539 PASS,
892/893 FAIL, 893/894 PASS. Общие исходные слова/lemma/Strong atoms,
украинские формы, стиховые и upstream training зависимости дают фактическое
объединение наблюдений:

- development: 12261 predictions / 1292 verses; 4 lexical/verse components; largest 12253 edges. Proposed-A diagnostic count 61, exact 61; A_auto 0.
- validation3: 3938 predictions / 430 verses; 2 lexical/verse components; largest 3935 edges. Proposed-A diagnostic count 22, exact 22; A_auto 0.

Эти connected components также не доказаны независимыми. All-correct component
Wilson относится к вероятности правильности всего component, иной estimand;
он не certifies edge precision. Edge Wilson и component Wilson — descriptive
числа. Нет обоснованной Bernoulli sampling/dependence модели и достаточной
поддержки обязательных strata; .995 не ослаблено ради coverage. Fixed единственный
метод, пороги и полный scope исключают outcome-driven selection; familywise
или selected-subgroup certification не заявлена. Новый test4 scoring пропущен
заранее заданной веткой, его новые precision/recall/calibration не вычислялись.

## Adversarial проверки, найденные исправления и locks

32 собственные source probe groups PASS, в том числе 300 PAVA cases плюс
перестановки, Wilson, poisoned deferred metadata, physical duplicates/dangling
IDs, nonrequested-fold label poison, NULL identity, multi-Strong overlap,
model/protocol/fold/feature/class spoofing, temporary physical source/runtime
tampering и canonical-copy/one-time claims. Ещё 8 canaries проверили собственный
oracle без producer imports. 26 author fixture tests проверены дополнительно;
они не заменяют независимую арифметику.
[Source probes](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/source_probes.v1.json),
[oracle probes](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/oracle_adversaries.v1.json).

Первоначальный eligible-edge guard FAIL сохранён:
[исходный receipt](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/source_probes.before_guard_fix.v1.json). Исправлял автор
до fit. R77-01..08 разрешены в финальном approved source: mask-first metadata;
eligible per-edge guards; все conflicts→C; split lemma/each-Strong atoms;
полная reporting taxonomy; immutable probability provenance; canonical claim
namespace; одинаковый candidate-dependent anomaly gold support и negative-FN
guard. История первоначальных findings не переписана:
[findings](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/source_review_findings.v1.json),
[resolution approval](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/prefit_approval.v1.json).

Своим physical verifier проверены 13 calibration sources, 1821 runtime files,
1405 predecessor input dependencies, frozen model/output roster и unchanged
historical 7.6 fold4 claim. Mutable current artifact_inventory не связан как
будущий неизменный dependency. Frozen-model byte replay всего нового class payload
с label-free prepared rows совпал побайтно; labels не читались, refit не было.
Реальный новый edge и scalar spoofs отвергнуты прежним production resolver.
[Locks](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/physical_locks.v1.json),
[byte replay](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/frozen_replay.v1.json),
[actual resolver guard](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/actual_resolver_guard.v1.json).

Перестановка строк проверена для PAVA fixtures. Traversal-order invariance
полного producer не заявлена: две полные временные копии actual новых prepared
и prediction outputs с переставленными первыми двумя строками отвергнуты
нормативным physical hash consumer, при том же числе bytes. Frozen оригиналы
и файлы 7.6 не переставлялись: [permutation lock probe](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/row_permutation_lock.v1.json).

Frozen 7.4/7.6, gold/mask/folds/registries и старые JSONL не изменялись этим
reviewer. Новый philological QC, research, bootstrap/ledger, production Strong,
DB/runtime, stage8, commit и push не выполнялись. Этот отчёт завершает только
независимый технический аудит 7.7; последующие root/inventory final checks
публикуются отдельно. [Manifest](calibration77_independent_validation.v1.manifest.json).

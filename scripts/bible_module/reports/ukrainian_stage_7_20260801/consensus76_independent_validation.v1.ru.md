# Независимая проверка candidate-only consensus 7.6

Проверяющий: `/root/independent_review76`; автор реализации: `/root/consensus_author`.
Проверяющий не писал production implementation. Его изменения — собственные
аудиторы, adversarial fixtures, receipts и этот отчёт. Проверка кода, фактического
payload, OOF и арифметики завершена: **PASS**. Это технический аудит нового
candidate-only слоя; нового филологического подтверждения Strong links он не создаёт.

Pipeline SHA-256: `230d671d431763bac09873cd5f90a9b237a667fe6805cdc1556f45ca5764ab80`. До code/payload approval и
freeze новые evaluation scores не запускались. После собственных code/payload
проверок и exact development/validation predecessors проверяющий создал
[presealed_gate.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/presealed_gate.v1.json). Sealed fold 4 запускает только root; независимый
пересчёт не вызывает evaluator и не считается повторным scoring invocation.
Frozen fold 4 уже использовался в 7.4; здесь это та же partition, а не новая
никогда не виденная test set. Калибровка 7.7, bootstrap и production promotion
не выполнялись.

## Фактические проверки

- Полные входы проверены собственным stdlib auditor без импортов producer:
  872025 candidate rows, из них 440280 legacy с нулевым vote и 431745 nonlegacy;
  каждый stable ID, verse boundary, exact target span/digest и Strong derivation
  проверены. [raw_input_audit.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/raw_input_audit.v1.json).
- Независимое сравнение selected layers установило: fingerprint 678144,
  frozen gold-selected 678149; ровно пять дополнительных уже зафиксированных
  source IDs сохранены в полном графе без gold links/features.
  [selected_layer_delta.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/selected_layer_delta.v1.json).
- Весь graph содержит 31102 verses / 678149 original nodes /
  595077 target nodes / 401983 complete semantic
  candidate hyperedges. Каждый node projection/raw digest, candidate provenance,
  dependence cap, rank, n-best compatibility и reciprocal accounting
  перепроверены независимо. [payload_oof_audit.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/payload_oof_audit.v1.json).
  Первый собственный проход остановился из-за пропущенного в auditor allowlist
  raw provenance поля `plain_text_sha256`; exact field diff доказал, что graph
  сохранял его правильно. Исправлен только oracle и выполнен полный повторный
  проход; production freeze остался тем же.
  [payload_oracle_projection_correction.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/payload_oracle_projection_correction.v1.json).
- OOF статистика заново выведена из raw eligible intact gold hyperedges только
  folds 0–2: 26975 observations =
  26972 ordinary +
  3 joint component units.
  Ordinary unit — одна полная declared hyperedge, включая m:n/compound groups.
  Joint bundles сохраняют все 6
  declared constituent hyperedges и их subspans; они не проецируются в singleton
  rank counts и не создают ложную polysemy из совместного употребления.
  По folds 0/1/2 ordinary counts: 9189 /
  8263 / 9520; joint counts:
  2 / 0 / 1; все observation units: 9191 /
  8263 / 9521.
  Сохранённые counter keys `prior_observations_fold_N` в собственном receipt
  относятся к ordinary index; это не total с joint units.
  Повторения одного verse/group deduplicated:
  484.
  Проверены все 401687 queries: predicted development
  fold исключён; folds 3/4 используют только 0–2; коллективные группы не
  распадаются на pairwise labels. Unknown/sparse/multiple-outcome distributions
  сохранены, context не заменён глобальной частотностью.
  Unknown queries: 398653; matching-supported:
  2010; sparse:
  401466; multiple-outcome:
  250.
- Whole-edge deferral исключил из lexical rank/search
  296 candidate edges: prior и rank равны
  null, evidence groups пусты. Все raw edges/nodes сохранены. Frozen mask
  содержит 530 исключённых nodes; текущие source facts в исходном universe
  не превращаются в принятые OH1988 assignments.
- Собственные adversarial probe groups: 15 PASS, включая
  64 small graphs против собственного exhaustive oracle, реальные frozen
  topology fixtures Judg.18.24 / Mat.5.11 / Ruth.2.7, original exclusivity,
  reciprocal shared-target union, conflicting alternatives, mask metadata
  poison, invalid/dangling/cross-verse/duplicate excluded endpoints, OOF,
  polysemy/context, repeated observations и row permutation. Для topology
  fixtures joint-use declarations синтетические и используются только в тесте;
  Gold topology не используется как joint-use evidence в production. Проверен и прежний реальный
  calibrated resolver: новый rank и scalar spoofs не принимаются.
  [contract_probes.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/contract_probes.v1.json).
- В дополнение к fixtures настоящий edge из финального graph
  (`1Chr.1.1` / `c76edge:0103a34d9bc7e7a1ca082b3659d9f0902ef8d66c8312a14660448dad5cfb93b5`)
  передан прежнему consumer с `resolver_eligible=false` и null probability.
  Его raw rank и попытки подменить eligibility/probability отвергнуты; gold
  evaluator не вызывался. [actual_resolver_guard.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/actual_resolver_guard.v1.json).
- Отдельные tiny-fixture probes sealed gate: 14 PASS.
  Real gate/spec/claim code отвергает неверные freeze/reviewer/approval flags,
  missing/duplicate/stale predecessors и подменённый output; повторный claim
  отвергается до label read. Только check_freeze заменён tiny-fixture stub;
  реальный физический freeze проверен отдельными lock adversaries. Реальные
  graph/gold и настоящий fold4 claim этими probes не открывались.
  [presealed_guard_probes.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/presealed_guard_probes.v1.json).
- Actual physical lock adversaries: 16 PASS; без mocks:
  missing/duplicate/redirected/tampered input entries, source/runtime/build/baseline
  rosters, config/protocol и stale generation source. Все 25 frozen root
  `ukrainian_stage_7*.py` побайтно сохранены; parent package initializers входят
  в новый lock. [lock_adversaries.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/lock_adversaries.v1.json).
  Четыре input-copy adversaries не повторялись: physical input lock, io.py consumer и VERSION initializer побайтно совпадают; исходный receipt сохранён и hash-bound. Все новые source/runtime/build/config/protocol/freeze probes исполнены на финальном v3.
  Stale-generation fixture исправлен после проверки причины отклонения:
  valid copied output roster/read-only hardlinks исключают более ранний guard;
  фактическое отклонение — `Generation source changed after build`.
  Первоначальный receipt и snapshot auditor сохранены в correction chain.
- Обе полные сборки нового инструмента совпали побайтно по graph и prior;
  manifests совпали после нормализации только output path strings.
  Собственная физическая проверка: [deterministic_replay.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/deterministic_replay.v1.json).

Исправления, найденные при независимом source review, вносил автор реализации,
до freeze и до scoring. Первоначальные проблемы и их разрешения перечислены
в [source_review_findings.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/source_review_findings.v1.json); чтение исправленного кода не
объявляется его авторством.

Промежуточный v2 freeze был отклонён **до scoring**: два совместно используемых
edges давали две конкурирующие target-conditioned observations. Собственный
exact-shared fixture показал false polysemy, а полный raw gold scan установил
три partial-overlap components по два edges (Judg.18.24, Mat.5.11, Ruth.2.7).
Исторический FAIL сохранён в [shared_target_prior_semantics.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/shared_target_prior_semantics.v1.json),
фактический scan — [full_gold_shared_components.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/full_gold_shared_components.v1.json). V3 исправляет
единицу prior на совместный component occurrence, без механического слияния
graph edges; независимые probes и полный payload oracle это подтверждают.

## Coverage и значение unresolved

`unresolved_uncovered` означает отсутствие выбранного top1 assignment.
Raw candidate incidence остаётся доступной в сохранённых edges; это не утверждение,
что raw кандидатов вообще не было.

| Nodes | Нет raw candidate | Есть raw candidate, но нет top1 assignment | Всего без top1 assignment |
| --- | ---: | ---: | ---: |
| Original | 253970 | 89968 | 343938 |
| Target | 179059 | 69196 | 248255 |

Verses без raw candidate edges: Exod.21.25, Job.24.10.
Их nodes сохранены; отсутствие edge не превращается в invented NULL assignment.

Proven gold сохранён: 2171 verses, 45591 eligible original link/null decisions,
41517 eligible target nodes, 45538 complete eligible gold hyperedges.
Full reviewed nodes 87638; eligible 87108; deferred 530. Эти denominators не
заменяются числом найденных candidates.

## Независимый пересчёт metrics

До sealed gate собственный metric auditor был усилен: physical integrity и
duplicates проверяются до whole-edge mask, semantic labels/membership — только
после него. Poisoned deferred metadata и invalid/duplicate physical cases
прошли отдельные probes. Исходный code/payload approval и auditor snapshot
сохранены; gate явно bind corrected auditor и
[metric_auditor_mask_order_amendment.v2.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/metric_auditor_mask_order_amendment.v2.json). Исправленный auditor имеет
отдельный versioned path; исходный predeclared path восстановлен побайтно.
Pipeline, формулы metrics,
scope и параметры не менялись.

Все scopes пересчитаны из raw graph + raw gold/mask + полного frozen source
universe, без импортов или вызовов author evaluator. Совпали все detail rows,
TP/FP/FN, coverage, taxonomy и все by-book/testament/fold/reviewed/source-frequency
strata. Полные таблицы и точные denominators находятся в
[metric_recalculation.v1.json](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/metric_recalculation.v1.json). Source-frequency predictions вычисляются
по их собственным selected originals; reviewed phenomena учитываются отдельно
и могут пересекаться.
Source-frequency bands также могут пересекаться для разных исходных слов
одной hyperedge; strata не являются непересекающимися суммами общего denominator.

| Folds | Unit | TP | FP | FN | P denominator | R denominator | Precision | Recall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0,1,2 | top1 | 6479 | 5782 | 20983 | 12261 | 27462 | 52.8423% | 23.5926% |
| 0,1,2 | nbest_union | 6795 | 6802 | 20667 | 13597 | 27462 | 49.9743% | 24.7433% |
| 0,1,2 | candidate_union | 7401 | 9208 | 20061 | 16609 | 27462 | 44.5602% | 26.9500% |
| 3 | top1 | 2082 | 1856 | 6459 | 3938 | 8541 | 52.8695% | 24.3765% |
| 3 | nbest_union | 2177 | 2211 | 6364 | 4388 | 8541 | 49.6126% | 25.4888% |
| 3 | candidate_union | 2391 | 3002 | 6150 | 5393 | 8541 | 44.3352% | 27.9944% |
| 4 | top1 | 2403 | 1942 | 7132 | 4345 | 9535 | 55.3049% | 25.2019% |
| 4 | nbest_union | 2520 | 2308 | 7015 | 4828 | 9535 | 52.1955% | 26.4289% |
| 4 | candidate_union | 2716 | 3217 | 6819 | 5933 | 9535 | 45.7779% | 28.4845% |

Top1 — одно выбранное assignment set; n-best union — объединение альтернативных
solutions и отдельная метрика; candidate union — доступность raw complete edges,
а не точность одного решения. Gold recall включает все eligible hyperedges,
в том числе недоступные кандидатам и null cases.

## Ограничения и границы результата

Beam search приблизительный: width 32, n-best 5, local cap 12; pruning записан,
global optimum не заявлен. Rank не является calibrated probability;
`resolver_eligible=false`, `calibrated_probability=null`, automatic promotions 0.
Совпадение scores с независимой арифметикой не подтверждает пригодность auto class A.

Фактических reciprocal raw joint-use declarations:
0; top1 shared-target nodes:
0. Реализация допускает доказанное joint usage,
но не создаёт отсутствующее raw доказательство из gold.
Imported 7.5 bundle содержит lexical edges с обеими сторонами; явные null
relations поддерживаются контрактом и fixtures, но не придумываются для
непокрытых nodes. Нулевые/невыраженные gold cases остаются в recall denominator.
Точные context/group keys могут давать sparse/unknown prior; backoff и bootstrap
не выполняются. Historical 7.4 artifacts сохранены, evaluator 7.4 заново не запускался.

Полные locks, роли и receipt digests перечислены в
[manifest](consensus76_independent_validation.v1.manifest.json). Production Strong,
DB/runtime, release, commit и push данным аудитом не авторизуются.

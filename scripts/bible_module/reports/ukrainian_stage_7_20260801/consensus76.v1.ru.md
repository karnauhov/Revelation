# Этап 7.6 — constrained consensus и однократный OOF lexical prior

Doc-Version: `1.0.0`
Last-Updated: `2026-10-17`
Source-Commit: `working-tree`

Оба подпункта 7.6 roadmap выполнены как инженерный candidate-only результат. Этап 7 целиком открыт; A_auto/B_review/C_unresolved не калибровались. Lower-bound precision 99,5% не изменён. Resolver guard сохранён, `resolver_eligible=false`, `calibrated_probability=null`, automatic promotion и production acceptance **0**. Bootstrap, переобучение, production Strong, этап 8, DB/runtime, commit/push не выполнялись.

Нумерация сопоставлена по содержанию: roadmap 7.6 содержит graph и OOF prior; alignment plan 7.6 описывает consensus, а 7.7 — последующий итеративный ledger. Здесь выполнен только однократный prior по доказанным development labels; итеративная часть и калибровка остаются открыты.

## Frozen inputs и роли

Исходный Git status clean. До полного чтения work JSONL stage 3 offline / 4 / 5 / 6 / 7 и public `check-final-completed` прошли; проверены 5921 исходных inventory entries и 1388 gold/evaluation locks. Frozen preparation status остаётся `blocked_before_gold_and_alignment_acceptance`; он не заменяет отдельный finalized gold v2.

[Preflight receipt](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/preflight.v1.json), [обязательные входы](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/required_input_inspection.v1.json). Registry v7 и фактический registry source из lock — [candidate.v11](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/gold_finalization_registry.candidate.v11.json) — побайтно совпадают; используются фактические SHA-bound paths.

Gold неизменён: 66/66 книг = 38 strict + 28 completed_with_registered_deferrals; 2171 proven verses; full 45831 original + 41807 target = 87638; eligible 45591 + 41517 = 87108; deferred 240 + 290 = 530; 45538 eligible gold hyperedges. Единственный OH1988 issue registry сохранён; исследования и review passes не повторялись.

- Final gold lock SHA256: `265ac4f336ca6260d211628666a977d7b1805c413b789007cca09afce90a89c9`.
- Annotations SHA256: `547c67517fa466682b5cfe602cc669fa35f3a0420d813bad3a41670d0e880d67`.
- Mask SHA256: `d99436f6dedb48c6d7ec99acbaf4631fc009723fdc411851e2dc587e84f844db`.

Автор реализации — `/root/consensus_author`; отдельный reviewer `/root/independent_review76` запущен с `fork_turns=none` и не писал production implementation; root — orchestration, preflight и документация; отдельный `/root/inventory_writer76` — только inventory. [Фактические роли](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/roles.v1.json).

## Candidate-only graph

Полная сетка: **31102 стихов**, **678149 original + 595077 target = 1273226 физических nodes**. Каждый node учтён один раз. Canonical source layer — frozen answer-free `gold_selected_original_layer`: fingerprint-era 678144 и пять уже выбранных source nodes. Shared metadata совпадает; пять дополнительных nodes не порождают кандидатов или gold features. Это сохранение frozen source selection, не новое продвижение textual alternatives.

Исходные строки: 872025 = 431745 nonlegacy + 440280 legacy zero-vote diagnostics. После объединения одинаковой semantic identity сохранено **401983 hyperedges**, raw candidate provenance rows **431745**. Legacy не участвует в score. Compounds, many-to-many и альтернативные разложения сохранены, gold edges в graph не добавлены.

Raw edge incidence отдельно от физических nodes: original 494884, target 528116. Top-1 содержит 297767 гипотез; n-best содержит 155246 разложений. Стихи без nonlegacy candidates: 2; с пустым top-1: 2. Точные refs: Exod.21.25, Job.24.10.

| Сторона | Все nodes | Есть candidate incidence | В top-1 hypothesis | Uncovered: нет ребра | Unresolved: ребро есть, не выбрано | Всего вне top-1 |
|---|---:|---:|---:|---:|---:|---:|
| original | 678149 | 424179 | 334211 | 253970 | 89968 | 343938 |
| target | 595077 | 416018 | 346822 | 179059 | 69196 | 248255 |

Выбранная hypothesis не является принятым Strong label. Отсутствие ребра не превращается в NULL/omission/addition. NULL допускается только как явно предоставленная candidate hypothesis с reason/evidence; проверка не превращает её в gold. Полные mapping/source provenance и digests исходных rows сохранены в nodes и edges.

Независимые votes ограничены dependency components: max внутри связанной группы вместо суммирования производных одного источника; bridge и IBM1 относятся к общей translation family. Rank сочетает исходное evidence quality и OOF support ratio; probability calibration отсутствует. Original exclusivity, candidate-local reciprocal joint-use witnesses и NULL conflicts определяют совместимость. Общие targets не запрещены целиком и не приводят к слиянию declared edges. Без joint-use proof пересечение остаётся альтернативой. Gold shared targets Judg.18.24, Mat.5.11, Ruth.2.7 и reciprocal union сохранены; fixture-only witnesses не вносятся в production graph.

Поиск: deterministic edge-set beam, width32, n-best5, union top12 incident candidates per original; raw edges сохраняются. Approximate result, **global optimum не заявлен**. Отсечено search edges 0; local pruned incidents 0; beam states 5256743 в 27878 стихах. Полные diagnostics по каждому стиху сохранены.

Рёбра с любым deferred endpoint сохранены отдельно и исключены целиком до prior/rank/search/membership/statistics: 296. У них нет rank/prior evidence. Invalid/dangling/cross-verse IDs и duplicate rows проверяются до exclusion. Outside-gold nodes остаются в graph; отсутствие mask entry не является gold label.

Фактические NULL candidates: 0; raw joint-use declarations: 0; top-1 shared-target nodes: 0. Representational support не заменяет отсутствующее evidence. Relation counts: `{"many_to_many": 44333, "many_to_one": 22088, "one_to_many": 40552, "one_to_one": 295010}`.

[Graph accounting](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/graph_accounting.v1.json), [build manifest](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/build.v3/build.v1.manifest.json), [полный graph](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/build.v3/graph.v1.jsonl).

## Leakage-free OOF prior

Используются только eligible reviewed-accepted hyperedges folds0–2. Prediction folds0/1/2 исключает весь собственный fold; folds3/4 используют только development0–2. Fold3/4 labels не входят в counts, rules, параметры или thresholds. Единица наблюдения — target-overlap connected component в одном стихе: обычный singleton сохраняет целую target surface/lemma/context/morphology group → целую ordered original signature с Strong. Shared component считается один раз в отдельном joint index, сохраняя все declared edges, их подмножества target union и multiplicity constituents. Это не слияние gold hyperedges. Joint constituent labels не проецируются в singleton rank evidence; запрос joint prior требует полный совместимый bundle.

Коллективные edges не разворачиваются в pairwise labels. Reciprocal rows не читаются как training observations; одинаковое semantic observation внутри стиха учитывается один раз. Sparse/unknown/polysemous distributions сохраняются без придуманного backoff. Флаг polysemous означает несколько intact original signatures, включая различия morphology; он не утверждает отдельный доказанный lexical sense.

До любой оценки независимая проверка выявила inflation совместного употребления в prototype v2. Этот draft отклонён, исходники и payload сохранены как диагностика. Исправление joint observation unit проверено отдельными same-target, transitive partial-overlap, identical-lexeme multiplicity, whole-bundle ID guards, fold/verse и poisoned deferred probes; затем v3 полностью построен и воспроизведён заново. Supersedes относится только к отвергнутому draft7.6, не к frozen7.4.

[Отклонённая draft-v2 probe](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/shared_target_prior_semantics.v1.json), [точный v2 source snapshot](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/v2_snapshot_flat/snapshot.v2.manifest.json), [фактические gold shared components](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_independent_01/full_gold_shared_components.v1.json). Исторический FAIL сохранён как обнаруженный и исправленный pre-score defect; он не является нерешённым итоговым дефектом.

Prior summary (точные counts):

```json
{
  "allowed_ordinary_rank_observations_by_prediction_fold": {
    "0": 17783,
    "1": 18709,
    "2": 17452,
    "3": 26972,
    "4": 26972
  },
  "allowed_total_observations_by_prediction_fold": {
    "0": 17784,
    "1": 18712,
    "2": 17454,
    "3": 26975,
    "4": 26975
  },
  "auto_acceptance": false,
  "automatic_strong_promotions": 0,
  "calibrated": false,
  "calibrated_probability": null,
  "candidate_only": true,
  "deduplicated_same_verse_whole_semantic_observations": 484,
  "development_folds": [
    0,
    1,
    2
  ],
  "development_input_gold_hyperedges": 27462,
  "excluded_whole_edges": 0,
  "intact_original_outcomes": 13388,
  "joint_constituent_hyperedges": 6,
  "joint_observation_count": 3,
  "joint_observations_by_fold": {
    "0": 2,
    "2": 1
  },
  "joint_outcome_keys": 3,
  "joint_rank_policy": "whole_bundle_only;no_projection_to_singleton_rank_counts",
  "joint_target_group_keys": 3,
  "observations": 26975,
  "ordinary_rank_observations": 26972,
  "ordinary_rank_observations_by_fold": {
    "0": 9189,
    "1": 8263,
    "2": 9520
  },
  "prior_contract_version": "joint_components_v2",
  "resolver_eligible": false,
  "shared_component_unit_reduction": 3,
  "target_group_keys": 22073,
  "total_observations_by_fold": {
    "0": 9191,
    "1": 8263,
    "2": 9521
  },
  "unit": "target_overlap_component_occurrence_with_intact_declared_edges",
  "version": "consensus76-v1"
}
```

В finalized annotations deferred nodes представлены отдельными deferred accounting rows без accepted hyperedges. Поэтому prior `excluded_whole_edges=0` относится к фактически встреченным gold hyperedges и не означает отсутствия eligibility filter: 530 deferred nodes не дают labels/counts. На candidate graph реально исключены целиком 296 edges; добавление poisoned deferred metadata и исключаемых edges проверено отдельными canaries.

Candidate prior query coverage:

```json
{
  "matching_supported_edges": 2010,
  "polysemous": 250,
  "queried_edges": 401687,
  "sparse": 401466,
  "unknown": 398653
}
```

Source-frequency strata вычисляются из frozen raw primary/non-unresolved source universe; это характеристика источника, а не новые OH1988 assignments. Prediction strata выводятся из actual original endpoints; reviewed phenomena представлены отдельно. [Prior payload](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/build.v3/prior.v1.json).

## Freeze и однократная оценка

Порядок: preflight → protocol/config/source contract → independent source/semantic probes → full build/replay → exact pipeline freeze → independent raw graph/OOF/locks audit → development0–2 → predefined validation3 без tuning → independent gate с exact freeze и predecessors → отдельный sealed4. Результаты fold4 не используются для изменения метода. Fold4 — **повторно используемый frozen test partition**, уже оценённый в7.4; это не новый untouched holdout. Обязательное чтение прежних отчётов дало incidental exposure к их historical scores, явно записанный в protocol; score-driven design/tuning отсутствует.

Новый пакет изолирован от root `ukrainian_stage_7*.py` family. Input lock проверяет mandatory role paths, exact dependency closure и25 frozen consumers. Source lock охватывает весь новый код, tests, schema, protocol/config, project import dependencies и Python/stdlib runtime. Generation source зафиксирован до build, stale build не допускается к freeze. Baseline artifacts7.4 сохранены с physical refs; новый контракт additive, без ложного supersedes. Sealed gate связывает проверяющего, exact pipeline и finished development/validation manifests/details. Claim создаётся эксклюзивно до чтения sealed labels.

[Input lock](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/inputs.v3.lock.json), [pipeline freeze](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_author_01/pipeline.v3.lock.json), [execution source/protocol lock](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/execution_protocol.v1.lock.json), [development/validation receipts](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/scoring_unsealed.v1.json), [single fold4 receipt](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/scoring_sealed.v1.json).

Единица scoring — полная semantic hyperedge identity (verse, relation, original IDs, target IDs, null reason). TP/FP/FN считаются по уникальным edges; recall denominator включает **весь eligible gold partition**, включая uncovered. N-best retrieval union и candidate retrieval union не выдаются за top-1 decomposition. Страты могут пересекаться; их нельзя складывать.

| Partition | Mode | TP | FP | FN | Precision denominator | Recall denominator | P | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| development0–2 | candidate_union | 7401 | 9208 | 20061 | 16609 | 27462 | 44.5602% | 26.9500% |
| development0–2 | nbest_union | 6795 | 6802 | 20667 | 13597 | 27462 | 49.9743% | 24.7433% |
| development0–2 | top1 | 6479 | 5782 | 20983 | 12261 | 27462 | 52.8423% | 23.5926% |
| validation3 | candidate_union | 2391 | 3002 | 6150 | 5393 | 8541 | 44.3352% | 27.9944% |
| validation3 | nbest_union | 2177 | 2211 | 6364 | 4388 | 8541 | 49.6126% | 25.4888% |
| validation3 | top1 | 2082 | 1856 | 6459 | 3938 | 8541 | 52.8695% | 24.3765% |
| reused frozen test4 | candidate_union | 2716 | 3217 | 6819 | 5933 | 9535 | 45.7779% | 28.4845% |
| reused frozen test4 | nbest_union | 2520 | 2308 | 7015 | 4828 | 9535 | 52.1955% | 26.4289% |
| reused frozen test4 | top1 | 2403 | 1942 | 7132 | 4345 | 9535 | 55.3049% | 25.2019% |

## Coverage, exclusions и taxonomy

### Development0–2

[SHA-bound manifest и все разрезы](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/evaluation.development.v1/evaluation.v1.manifest.json)

```json
{
  "coverage": {
    "candidate_union_whole_edges_excluded": 166,
    "eligible_gold_graph_verses": 1292,
    "outside_gold_graph_verses": 17275,
    "outside_requested_fold_graph_verses": 12535
  },
  "excluded_gold": {
    "original_nodes": 114,
    "target_nodes": 174
  },
  "retrieval_loss_breakdown": {
    "candidate_retrievable_gold_missing_from_nbest_union": 606,
    "candidate_retrievable_gold_missing_from_top1": 922,
    "gold_missing_from_all_fixed_candidates": 20061
  },
  "support": {
    "hyperedges": 27462,
    "original_decisions": 27511,
    "target_accounting": 24923
  },
  "taxonomy": {
    "candidate_union": {
      "cross_gold_group_endpoints": 8148,
      "exact_complete_hyperedge": 7401,
      "incomplete_or_wrong_group_endpoints": 1060
    },
    "nbest_union": {
      "cross_gold_group_endpoints": 5844,
      "exact_complete_hyperedge": 6795,
      "incomplete_or_wrong_group_endpoints": 958
    },
    "top1": {
      "cross_gold_group_endpoints": 4884,
      "exact_complete_hyperedge": 6479,
      "incomplete_or_wrong_group_endpoints": 898
    }
  }
}
```

### Validation3

[SHA-bound manifest и все разрезы](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/evaluation.validation.v1/evaluation.v1.manifest.json)

```json
{
  "coverage": {
    "candidate_union_whole_edges_excluded": 64,
    "eligible_gold_graph_verses": 430,
    "outside_gold_graph_verses": 5808,
    "outside_requested_fold_graph_verses": 24864
  },
  "excluded_gold": {
    "original_nodes": 67,
    "target_nodes": 62
  },
  "retrieval_loss_breakdown": {
    "candidate_retrievable_gold_missing_from_nbest_union": 214,
    "candidate_retrievable_gold_missing_from_top1": 309,
    "gold_missing_from_all_fixed_candidates": 6150
  },
  "support": {
    "hyperedges": 8541,
    "original_decisions": 8586,
    "target_accounting": 7905
  },
  "taxonomy": {
    "candidate_union": {
      "cross_gold_group_endpoints": 2665,
      "exact_complete_hyperedge": 2391,
      "incomplete_or_wrong_group_endpoints": 337
    },
    "nbest_union": {
      "cross_gold_group_endpoints": 1899,
      "exact_complete_hyperedge": 2177,
      "incomplete_or_wrong_group_endpoints": 312
    },
    "top1": {
      "cross_gold_group_endpoints": 1571,
      "exact_complete_hyperedge": 2082,
      "incomplete_or_wrong_group_endpoints": 285
    }
  }
}
```

### Frozen test4

[SHA-bound manifest и все разрезы](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/evaluation.sealed.v1/evaluation.v1.manifest.json)

```json
{
  "coverage": {
    "candidate_union_whole_edges_excluded": 66,
    "eligible_gold_graph_verses": 449,
    "outside_gold_graph_verses": 5848,
    "outside_requested_fold_graph_verses": 24805
  },
  "excluded_gold": {
    "original_nodes": 59,
    "target_nodes": 54
  },
  "retrieval_loss_breakdown": {
    "candidate_retrievable_gold_missing_from_nbest_union": 196,
    "candidate_retrievable_gold_missing_from_top1": 313,
    "gold_missing_from_all_fixed_candidates": 6819
  },
  "support": {
    "hyperedges": 9535,
    "original_decisions": 9494,
    "target_accounting": 8689
  },
  "taxonomy": {
    "candidate_union": {
      "cross_gold_group_endpoints": 2848,
      "exact_complete_hyperedge": 2716,
      "incomplete_or_wrong_group_endpoints": 369
    },
    "nbest_union": {
      "cross_gold_group_endpoints": 1976,
      "exact_complete_hyperedge": 2520,
      "incomplete_or_wrong_group_endpoints": 332
    },
    "top1": {
      "cross_gold_group_endpoints": 1625,
      "exact_complete_hyperedge": 2403,
      "incomplete_or_wrong_group_endpoints": 317
    }
  }
}
```

## Полные top-1 разрезы

Book/testament/fold/source-frequency/reviewed strata приведены ниже; все три retrieval modes по тем же strata доступны в manifests. Undefined precision означает нулевой prediction support; он не заменяется предположением о качестве.

| Partition | Group | TP | FP | FN | Predictions | Gold support | P | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev0–2 | book:1Chr | 112 | 86 | 330 | 198 | 442 | 56.5657% | 25.3394% |
| dev0–2 | book:1Cor | 73 | 73 | 182 | 146 | 255 | 50.0000% | 28.6275% |
| dev0–2 | book:1John | 91 | 47 | 157 | 138 | 248 | 65.9420% | 36.6935% |
| dev0–2 | book:1Kgs | 89 | 161 | 399 | 250 | 488 | 35.6000% | 18.2377% |
| dev0–2 | book:1Pet | 98 | 71 | 211 | 169 | 309 | 57.9882% | 31.7152% |
| dev0–2 | book:1Sam | 91 | 98 | 305 | 189 | 396 | 48.1481% | 22.9798% |
| dev0–2 | book:1Thess | 126 | 75 | 210 | 201 | 336 | 62.6866% | 37.5000% |
| dev0–2 | book:1Tim | 119 | 76 | 198 | 195 | 317 | 61.0256% | 37.5394% |
| dev0–2 | book:2Chr | 157 | 145 | 596 | 302 | 753 | 51.9868% | 20.8499% |
| dev0–2 | book:2Cor | 109 | 96 | 239 | 205 | 348 | 53.1707% | 31.3218% |
| dev0–2 | book:2John | 52 | 33 | 102 | 85 | 154 | 61.1765% | 33.7662% |
| dev0–2 | book:2Kgs | 139 | 129 | 454 | 268 | 593 | 51.8657% | 23.4401% |
| dev0–2 | book:2Pet | 118 | 92 | 261 | 210 | 379 | 56.1905% | 31.1346% |
| dev0–2 | book:2Sam | 135 | 117 | 440 | 252 | 575 | 53.5714% | 23.4783% |
| dev0–2 | book:2Thess | 131 | 71 | 207 | 202 | 338 | 64.8515% | 38.7574% |
| dev0–2 | book:2Tim | 130 | 77 | 254 | 207 | 384 | 62.8019% | 33.8542% |
| dev0–2 | book:3John | 29 | 29 | 68 | 58 | 97 | 50.0000% | 29.8969% |
| dev0–2 | book:Acts | 131 | 105 | 285 | 236 | 416 | 55.5085% | 31.4904% |
| dev0–2 | book:Amos | 84 | 75 | 338 | 159 | 422 | 52.8302% | 19.9052% |
| dev0–2 | book:Col | 106 | 68 | 207 | 174 | 313 | 60.9195% | 33.8658% |
| dev0–2 | book:Dan | 59 | 87 | 422 | 146 | 481 | 40.4110% | 12.2661% |
| dev0–2 | book:Deut | 78 | 61 | 259 | 139 | 337 | 56.1151% | 23.1454% |
| dev0–2 | book:Eccl | 82 | 105 | 421 | 187 | 503 | 43.8503% | 16.3022% |
| dev0–2 | book:Eph | 86 | 76 | 240 | 162 | 326 | 53.0864% | 26.3804% |
| dev0–2 | book:Esth | 124 | 130 | 515 | 254 | 639 | 48.8189% | 19.4053% |
| dev0–2 | book:Exod | 120 | 95 | 367 | 215 | 487 | 55.8140% | 24.6407% |
| dev0–2 | book:Ezek | 84 | 79 | 343 | 163 | 427 | 51.5337% | 19.6721% |
| dev0–2 | book:Ezra | 86 | 86 | 360 | 172 | 446 | 50.0000% | 19.2825% |
| dev0–2 | book:Gal | 83 | 83 | 206 | 166 | 289 | 50.0000% | 28.7197% |
| dev0–2 | book:Gen | 89 | 88 | 294 | 177 | 383 | 50.2825% | 23.2376% |
| dev0–2 | book:Hab | 72 | 104 | 441 | 176 | 513 | 40.9091% | 14.0351% |
| dev0–2 | book:Hag | 111 | 115 | 477 | 226 | 588 | 49.1150% | 18.8776% |
| dev0–2 | book:Heb | 83 | 61 | 206 | 144 | 289 | 57.6389% | 28.7197% |
| dev0–2 | book:Hos | 88 | 83 | 314 | 171 | 402 | 51.4620% | 21.8905% |
| dev0–2 | book:Isa | 88 | 94 | 350 | 182 | 438 | 48.3516% | 20.0913% |
| dev0–2 | book:Jas | 92 | 51 | 158 | 143 | 250 | 64.3357% | 36.8000% |
| dev0–2 | book:Jer | 125 | 136 | 534 | 261 | 659 | 47.8927% | 18.9681% |
| dev0–2 | book:Job | 28 | 59 | 213 | 87 | 241 | 32.1839% | 11.6183% |
| dev0–2 | book:Joel | 76 | 66 | 325 | 142 | 401 | 53.5211% | 18.9526% |
| dev0–2 | book:John | 152 | 81 | 234 | 233 | 386 | 65.2361% | 39.3782% |
| dev0–2 | book:Jonah | 137 | 107 | 429 | 244 | 566 | 56.1475% | 24.2049% |
| dev0–2 | book:Josh | 80 | 119 | 390 | 199 | 470 | 40.2010% | 17.0213% |
| dev0–2 | book:Jude | 73 | 52 | 164 | 125 | 237 | 58.4000% | 30.8017% |
| dev0–2 | book:Judg | 146 | 138 | 484 | 284 | 630 | 51.4085% | 23.1746% |
| dev0–2 | book:Lam | 57 | 77 | 347 | 134 | 404 | 42.5373% | 14.1089% |
| dev0–2 | book:Lev | 73 | 87 | 329 | 160 | 402 | 45.6250% | 18.1592% |
| dev0–2 | book:Luke | 99 | 60 | 205 | 159 | 304 | 62.2642% | 32.5658% |
| dev0–2 | book:Mal | 79 | 100 | 412 | 179 | 491 | 44.1341% | 16.0896% |
| dev0–2 | book:Mark | 141 | 124 | 346 | 265 | 487 | 53.2075% | 28.9528% |
| dev0–2 | book:Mat | 127 | 71 | 218 | 198 | 345 | 64.1414% | 36.8116% |
| dev0–2 | book:Mic | 64 | 95 | 351 | 159 | 415 | 40.2516% | 15.4217% |
| dev0–2 | book:Nah | 59 | 80 | 319 | 139 | 378 | 42.4460% | 15.6085% |
| dev0–2 | book:Neh | 98 | 56 | 241 | 154 | 339 | 63.6364% | 28.9086% |
| dev0–2 | book:Num | 107 | 122 | 503 | 229 | 610 | 46.7249% | 17.5410% |
| dev0–2 | book:Obad | 57 | 59 | 218 | 116 | 275 | 49.1379% | 20.7273% |
| dev0–2 | book:Phil | 118 | 68 | 218 | 186 | 336 | 63.4409% | 35.1190% |
| dev0–2 | book:Phlm | 75 | 28 | 102 | 103 | 177 | 72.8155% | 42.3729% |
| dev0–2 | book:Prov | 40 | 56 | 194 | 96 | 234 | 41.6667% | 17.0940% |
| dev0–2 | book:Ps | 120 | 146 | 979 | 266 | 1099 | 45.1128% | 10.9190% |
| dev0–2 | book:Rev | 231 | 120 | 382 | 351 | 613 | 65.8120% | 37.6835% |
| dev0–2 | book:Rom | 93 | 62 | 147 | 155 | 240 | 60.0000% | 38.7500% |
| dev0–2 | book:Ruth | 105 | 124 | 445 | 229 | 550 | 45.8515% | 19.0909% |
| dev0–2 | book:Song | 56 | 89 | 363 | 145 | 419 | 38.6207% | 13.3652% |
| dev0–2 | book:Titus | 121 | 48 | 174 | 169 | 295 | 71.5976% | 41.0169% |
| dev0–2 | book:Zech | 117 | 143 | 528 | 260 | 645 | 45.0000% | 18.1395% |
| dev0–2 | book:Zeph | 80 | 87 | 373 | 167 | 453 | 47.9042% | 17.6600% |
| dev0–2 | fold:0 | 2180 | 1994 | 7170 | 4174 | 9350 | 52.2281% | 23.3155% |
| dev0–2 | fold:1 | 1961 | 1799 | 6457 | 3760 | 8418 | 52.1543% | 23.2953% |
| dev0–2 | fold:2 | 2338 | 1989 | 7356 | 4327 | 9694 | 54.0328% | 24.1180% |
| dev0–2 | reviewed:addition | 6 | 251 | 1007 | 257 | 1013 | 2.3346% | 0.5923% |
| dev0–2 | reviewed:adjectival_rendering | 0 | 5 | 7 | 5 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:age_idiom | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:alignment_counterexample | 4 | 3 | 18 | 7 | 22 | 57.1429% | 18.1818% |
| dev0–2 | reviewed:analytic_tense | 0 | 4 | 5 | 4 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:anaphoric_expansion | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:anaphoric_explication | 0 | 0 | 3 | 0 | 3 | undefined | 0.0000% |
| dev0–2 | reviewed:article_genitive_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:article_lexical_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:article_noun_group | 0 | 3 | 5 | 3 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:blind_semantic_review | 268 | 295 | 1109 | 563 | 1377 | 47.6021% | 19.4626% |
| dev0–2 | reviewed:body_part_change | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:case_government | 0 | 11 | 11 | 11 | 11 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:case_realization | 1 | 26 | 25 | 27 | 26 | 3.7037% | 3.8462% |
| dev0–2 | reviewed:case_restructuring | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:cohortative_motion_expansion | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:cohortative_particle_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:comparative_clause | 0 | 2 | 3 | 2 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:comparison | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:compositional_alignment | 0 | 22 | 24 | 22 | 24 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:compound | 28 | 304 | 387 | 332 | 415 | 8.4337% | 6.7470% |
| dev0–2 | reviewed:compound_numeral | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:conditional_particle_repetition | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:contextual_demonstrative_addition | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:contextual_lexical_choice | 0 | 5 | 7 | 5 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:contextual_location_addition | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:contextual_possessor_addition | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:copular_adjectival_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:copular_expression | 1 | 1 | 3 | 2 | 4 | 50.0000% | 25.0000% |
| dev0–2 | reviewed:copular_relative | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:correlative_expansion | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:dative_copular_expansion | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:dative_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:dative_pronominal_group | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:definiteness | 2 | 11 | 13 | 13 | 15 | 15.3846% | 13.3333% |
| dev0–2 | reviewed:deictic_expression | 0 | 3 | 1 | 3 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:deictic_subject | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:deictic_time | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:derivation | 3 | 11 | 28 | 14 | 31 | 21.4286% | 9.6774% |
| dev0–2 | reviewed:derivational_rendering | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:direct_lexical | 63 | 45 | 149 | 108 | 212 | 58.3333% | 29.7170% |
| dev0–2 | reviewed:direct_object_marker_not_overt | 0 | 4 | 9 | 4 | 9 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:directional_place | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:directional_suffix | 0 | 8 | 7 | 8 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:discontinuous_rendering | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:discourse_particle | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:discourse_particle_omission | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:discourse_restructuring | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:distributive | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:duration_phrase | 1 | 0 | 2 | 1 | 3 | 100.0000% | 33.3333% |
| dev0–2 | reviewed:existential_to_indefinite | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:explicit_original_null | 0 | 82 | 297 | 82 | 297 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:explicit_source_null | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:explicit_subject | 0 | 7 | 9 | 7 | 9 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:explicit_target_function | 0 | 1 | 10 | 1 | 10 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:explicit_target_null | 0 | 42 | 59 | 42 | 59 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:explicitation | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:fawn_deer_lexical_group | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:frequent_lemma | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| dev0–2 | reviewed:function_token | 0 | 38 | 60 | 38 | 60 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:genitive_group | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:gentilic_recasting | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:government | 0 | 4 | 5 | 4 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:government_shift | 2 | 3 | 5 | 5 | 7 | 40.0000% | 28.5714% |
| dev0–2 | reviewed:grammatical_expansion | 1 | 24 | 24 | 25 | 25 | 4.0000% | 4.0000% |
| dev0–2 | reviewed:grammatical_function | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:grammatical_function_not_overt | 0 | 59 | 169 | 59 | 169 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:grouped_expression | 0 | 7 | 7 | 7 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiom | 0 | 17 | 15 | 17 | 15 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_armory_rendering | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_degree | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:idiomatic_fullness | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_object_explication | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_paraphrase | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_rendering | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_smooth_speech | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| dev0–2 | reviewed:idiomatic_translation | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:idiomatic_wine_house_rendering | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:impersonal_voice | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:implicit_destination_relation | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:inchoative_aspect | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:kinship | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_alignment | 134 | 92 | 232 | 226 | 366 | 59.2920% | 36.6120% |
| dev0–2 | reviewed:lexical_context | 29 | 52 | 118 | 81 | 147 | 35.8025% | 19.7279% |
| dev0–2 | reviewed:lexical_context_equivalence | 268 | 292 | 790 | 560 | 1058 | 47.8571% | 25.3308% |
| dev0–2 | reviewed:lexical_derivation | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_divergence | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_expansion | 1 | 10 | 16 | 11 | 17 | 9.0909% | 5.8824% |
| dev0–2 | reviewed:lexical_generalization | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_mismatch | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_rendering | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_shift | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_substitution | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:lexical_uncertainty | 0 | 2 | 7 | 2 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:location_expression | 0 | 2 | 7 | 2 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:locative_idiom | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:manual_adjudication | 192 | 524 | 1635 | 716 | 1827 | 26.8156% | 10.5090% |
| dev0–2 | reviewed:manual_semantic_alignment | 541 | 531 | 1681 | 1072 | 2222 | 50.4664% | 24.3474% |
| dev0–2 | reviewed:many_to_many | 0 | 10 | 8 | 10 | 8 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:many_to_one | 0 | 18 | 25 | 18 | 25 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:measure_explication | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:merge_split | 328 | 2810 | 4080 | 3138 | 4408 | 10.4525% | 7.4410% |
| dev0–2 | reviewed:missing_whitespace | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:morphosyntactic_contraction | 0 | 12 | 15 | 12 | 15 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:multiple_strong | 30 | 280 | 410 | 310 | 440 | 9.6774% | 6.8182% |
| dev0–2 | reviewed:named_entity | 707 | 466 | 825 | 1173 | 1532 | 60.2728% | 46.1488% |
| dev0–2 | reviewed:negation | 3 | 6 | 10 | 9 | 13 | 33.3333% | 23.0769% |
| dev0–2 | reviewed:negation_compound | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:negative_copula | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:negative_predicate | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:negative_purpose | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:negative_quantification | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:nominal_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:nominalization | 0 | 3 | 6 | 3 | 6 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:nonlexical_source_marker | 0 | 20 | 85 | 20 | 85 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:number_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:number_shift | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:omission | 24 | 1386 | 4904 | 1410 | 4928 | 1.7021% | 0.4870% |
| dev0–2 | reviewed:one_to_many | 0 | 20 | 22 | 20 | 22 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:one_to_one | 72 | 46 | 109 | 118 | 181 | 61.0169% | 39.7790% |
| dev0–2 | reviewed:orthography | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:overt_subject | 0 | 29 | 36 | 29 | 36 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:particle | 1671 | 2330 | 4956 | 4001 | 6627 | 41.7646% | 25.2150% |
| dev0–2 | reviewed:passive_voice | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:person_number | 0 | 4 | 8 | 4 | 8 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:polarity | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:polysemy | 314 | 1075 | 1887 | 1389 | 2201 | 22.6062% | 14.2662% |
| dev0–2 | reviewed:possessive | 14 | 22 | 48 | 36 | 62 | 38.8889% | 22.5806% |
| dev0–2 | reviewed:possessive_shift | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:prepositional_expansion | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:pronominal_complement | 2 | 23 | 35 | 25 | 37 | 8.0000% | 5.4054% |
| dev0–2 | reviewed:pronoun_repetition | 1 | 0 | 0 | 1 | 1 | 100.0000% | 100.0000% |
| dev0–2 | reviewed:proper_name_component_omission | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:proper_place_mismatch | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:purpose_clause | 0 | 2 | 5 | 2 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:rare_lemma | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| dev0–2 | reviewed:reciprocal_target_accounting | 3 | 8 | 16 | 11 | 19 | 27.2727% | 15.7895% |
| dev0–2 | reviewed:referent_explication | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:reflexive | 0 | 1 | 6 | 1 | 6 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:reflexive_group | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:relative_clause | 0 | 3 | 5 | 3 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:relative_conception_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:relative_expansion | 0 | 4 | 5 | 4 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:relative_participle_expansion | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:relative_subject | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:reorder | 1364 | 1810 | 3640 | 3174 | 5004 | 42.9742% | 27.2582% |
| dev0–2 | reviewed:repetition | 14 | 106 | 135 | 120 | 149 | 11.6667% | 9.3960% |
| dev0–2 | reviewed:resultative | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:semantic_restructuring_requires_second_pass | 0 | 13 | 23 | 13 | 23 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:semantic_uncertainty | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_component_not_overt | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:source_grammar | 0 | 13 | 47 | 13 | 47 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_idiom | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_marker | 0 | 54 | 157 | 54 | 157 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_merge_or_compound | 8 | 74 | 100 | 82 | 108 | 9.7561% | 7.4074% |
| dev0–2 | reviewed:source_tag_uncertainty | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_target_surface_issue | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:source_text_not_rendered | 0 | 60 | 235 | 60 | 235 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:speaker_attribution_addition | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:subject_clause | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:subject_expansion | 0 | 5 | 7 | 5 | 7 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:subordinator_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:target_anomaly | 0 | 1 | 5 | 1 | 5 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:target_split_or_expansion | 14 | 68 | 96 | 82 | 110 | 17.0732% | 12.7273% |
| dev0–2 | reviewed:temporal_addition | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| dev0–2 | reviewed:temporal_clause | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:temporal_connective | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:temporal_subordinator | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:tense_aspect | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:textual_variant | 479 | 478 | 1088 | 957 | 1567 | 50.0522% | 30.5680% |
| dev0–2 | reviewed:translation_addition | 0 | 8 | 18 | 8 | 18 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:translation_choice | 6 | 3 | 13 | 9 | 19 | 66.6667% | 31.5789% |
| dev0–2 | reviewed:translation_omission | 0 | 2 | 15 | 2 | 15 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:translation_paraphrase | 0 | 3 | 10 | 3 | 10 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:unclassified | 2262 | 1952 | 4163 | 4214 | 6425 | 53.6782% | 35.2062% |
| dev0–2 | reviewed:vocative_particle | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:vocative_split | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:vocative_superlative | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | reviewed:volitive | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:volitive_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| dev0–2 | reviewed:word_split | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| dev0–2 | source_frequency:frequent_1000_plus | 2052 | 1858 | 5462 | 3910 | 7514 | 52.4808% | 27.3090% |
| dev0–2 | source_frequency:mid | 3240 | 1908 | 6996 | 5148 | 10236 | 62.9371% | 31.6530% |
| dev0–2 | source_frequency:rare_1_to_5 | 247 | 220 | 759 | 467 | 1006 | 52.8908% | 24.5527% |
| dev0–2 | source_frequency:unclassified | 942 | 2054 | 7943 | 2996 | 8885 | 31.4419% | 10.6021% |
| dev0–2 | testament:NT | 2887 | 1898 | 5581 | 4785 | 8468 | 60.3344% | 34.0931% |
| dev0–2 | testament:OT | 3592 | 3884 | 15402 | 7476 | 18994 | 48.0471% | 18.9112% |
| val3 | book:1Chr | 23 | 18 | 70 | 41 | 93 | 56.0976% | 24.7312% |
| val3 | book:1Cor | 17 | 18 | 58 | 35 | 75 | 48.5714% | 22.6667% |
| val3 | book:1John | 59 | 42 | 113 | 101 | 172 | 58.4158% | 34.3023% |
| val3 | book:1Kgs | 24 | 49 | 104 | 73 | 128 | 32.8767% | 18.7500% |
| val3 | book:1Pet | 38 | 24 | 87 | 62 | 125 | 61.2903% | 30.4000% |
| val3 | book:1Sam | 77 | 65 | 212 | 142 | 289 | 54.2254% | 26.6436% |
| val3 | book:1Thess | 68 | 28 | 84 | 96 | 152 | 70.8333% | 44.7368% |
| val3 | book:1Tim | 15 | 12 | 36 | 27 | 51 | 55.5556% | 29.4118% |
| val3 | book:2Chr | 30 | 29 | 108 | 59 | 138 | 50.8475% | 21.7391% |
| val3 | book:2Cor | 14 | 10 | 31 | 24 | 45 | 58.3333% | 31.1111% |
| val3 | book:2John | 38 | 19 | 48 | 57 | 86 | 66.6667% | 44.1860% |
| val3 | book:2Kgs | 36 | 20 | 110 | 56 | 146 | 64.2857% | 24.6575% |
| val3 | book:2Pet | 35 | 38 | 104 | 73 | 139 | 47.9452% | 25.1799% |
| val3 | book:2Sam | 30 | 29 | 103 | 59 | 133 | 50.8475% | 22.5564% |
| val3 | book:2Thess | 18 | 24 | 54 | 42 | 72 | 42.8571% | 25.0000% |
| val3 | book:2Tim | 32 | 18 | 56 | 50 | 88 | 64.0000% | 36.3636% |
| val3 | book:3John | 22 | 15 | 47 | 37 | 69 | 59.4595% | 31.8841% |
| val3 | book:Acts | 81 | 66 | 176 | 147 | 257 | 55.1020% | 31.5175% |
| val3 | book:Amos | 17 | 21 | 62 | 38 | 79 | 44.7368% | 21.5190% |
| val3 | book:Col | 32 | 18 | 63 | 50 | 95 | 64.0000% | 33.6842% |
| val3 | book:Dan | 28 | 27 | 134 | 55 | 162 | 50.9091% | 17.2840% |
| val3 | book:Deut | 51 | 65 | 229 | 116 | 280 | 43.9655% | 18.2143% |
| val3 | book:Eccl | 17 | 30 | 121 | 47 | 138 | 36.1702% | 12.3188% |
| val3 | book:Eph | 42 | 25 | 64 | 67 | 106 | 62.6866% | 39.6226% |
| val3 | book:Esth | 23 | 36 | 120 | 59 | 143 | 38.9831% | 16.0839% |
| val3 | book:Exod | 31 | 19 | 72 | 50 | 103 | 62.0000% | 30.0971% |
| val3 | book:Ezek | 37 | 27 | 110 | 64 | 147 | 57.8125% | 25.1701% |
| val3 | book:Ezra | 30 | 51 | 210 | 81 | 240 | 37.0370% | 12.5000% |
| val3 | book:Gal | 38 | 37 | 81 | 75 | 119 | 50.6667% | 31.9328% |
| val3 | book:Gen | 25 | 41 | 130 | 66 | 155 | 37.8788% | 16.1290% |
| val3 | book:Hab | 15 | 15 | 84 | 30 | 99 | 50.0000% | 15.1515% |
| val3 | book:Hag | 20 | 30 | 121 | 50 | 141 | 40.0000% | 14.1844% |
| val3 | book:Heb | 27 | 32 | 82 | 59 | 109 | 45.7627% | 24.7706% |
| val3 | book:Hos | 24 | 28 | 105 | 52 | 129 | 46.1538% | 18.6047% |
| val3 | book:Isa | 26 | 22 | 101 | 48 | 127 | 54.1667% | 20.4724% |
| val3 | book:Jas | 49 | 34 | 98 | 83 | 147 | 59.0361% | 33.3333% |
| val3 | book:Jer | 13 | 17 | 69 | 30 | 82 | 43.3333% | 15.8537% |
| val3 | book:Job | 13 | 19 | 69 | 32 | 82 | 40.6250% | 15.8537% |
| val3 | book:Joel | 47 | 46 | 181 | 93 | 228 | 50.5376% | 20.6140% |
| val3 | book:John | 40 | 24 | 62 | 64 | 102 | 62.5000% | 39.2157% |
| val3 | book:Jonah | 25 | 21 | 89 | 46 | 114 | 54.3478% | 21.9298% |
| val3 | book:Josh | 30 | 20 | 62 | 50 | 92 | 60.0000% | 32.6087% |
| val3 | book:Jude | 30 | 30 | 71 | 60 | 101 | 50.0000% | 29.7030% |
| val3 | book:Judg | 15 | 23 | 79 | 38 | 94 | 39.4737% | 15.9574% |
| val3 | book:Lam | 8 | 18 | 64 | 26 | 72 | 30.7692% | 11.1111% |
| val3 | book:Lev | 23 | 30 | 99 | 53 | 122 | 43.3962% | 18.8525% |
| val3 | book:Luke | 44 | 28 | 86 | 72 | 130 | 61.1111% | 33.8462% |
| val3 | book:Mal | 33 | 27 | 118 | 60 | 151 | 55.0000% | 21.8543% |
| val3 | book:Mark | 14 | 7 | 26 | 21 | 40 | 66.6667% | 35.0000% |
| val3 | book:Mat | 66 | 39 | 138 | 105 | 204 | 62.8571% | 32.3529% |
| val3 | book:Mic | 54 | 45 | 178 | 99 | 232 | 54.5455% | 23.2759% |
| val3 | book:Nah | 18 | 21 | 91 | 39 | 109 | 46.1538% | 16.5138% |
| val3 | book:Neh | 26 | 10 | 50 | 36 | 76 | 72.2222% | 34.2105% |
| val3 | book:Num | 19 | 17 | 48 | 36 | 67 | 52.7778% | 28.3582% |
| val3 | book:Obad | 32 | 32 | 141 | 64 | 173 | 50.0000% | 18.4971% |
| val3 | book:Phil | 18 | 24 | 62 | 42 | 80 | 42.8571% | 22.5000% |
| val3 | book:Phlm | 57 | 24 | 72 | 81 | 129 | 70.3704% | 44.1860% |
| val3 | book:Prov | 22 | 26 | 77 | 48 | 99 | 45.8333% | 22.2222% |
| val3 | book:Ps | 31 | 63 | 347 | 94 | 378 | 32.9787% | 8.2011% |
| val3 | book:Rev | 67 | 37 | 119 | 104 | 186 | 64.4231% | 36.0215% |
| val3 | book:Rom | 33 | 27 | 86 | 60 | 119 | 55.0000% | 27.7311% |
| val3 | book:Ruth | 20 | 22 | 78 | 42 | 98 | 47.6190% | 20.4082% |
| val3 | book:Song | 12 | 18 | 71 | 30 | 83 | 40.0000% | 14.4578% |
| val3 | book:Titus | 26 | 13 | 46 | 39 | 72 | 66.6667% | 36.1111% |
| val3 | book:Zech | 29 | 22 | 76 | 51 | 105 | 56.8627% | 27.6190% |
| val3 | book:Zeph | 28 | 24 | 116 | 52 | 144 | 53.8462% | 19.4444% |
| val3 | fold:3 | 2082 | 1856 | 6459 | 3938 | 8541 | 52.8695% | 24.3765% |
| val3 | reviewed:addition | 1 | 92 | 330 | 93 | 331 | 1.0753% | 0.3021% |
| val3 | reviewed:analytic_tense | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:article_genitive_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:article_noun_group | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:aspectual_expansion | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:blind_semantic_review | 65 | 88 | 271 | 153 | 336 | 42.4837% | 19.3452% |
| val3 | reviewed:case_government | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:case_realization | 0 | 6 | 5 | 6 | 5 | 0.0000% | 0.0000% |
| val3 | reviewed:causal_connective | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:clause_relation | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:clause_restructuring | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:comparative_frame | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:comparison | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:compositional_alignment | 0 | 9 | 12 | 9 | 12 | 0.0000% | 0.0000% |
| val3 | reviewed:compound | 7 | 110 | 140 | 117 | 147 | 5.9829% | 4.7619% |
| val3 | reviewed:compound_time | 0 | 1 | 4 | 1 | 4 | 0.0000% | 0.0000% |
| val3 | reviewed:conditional_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:contextual_lexical_choice | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:contextual_private_speech_addition | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| val3 | reviewed:correlative_expansion | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:dative_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:dative_possessive_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:definiteness | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:derivation | 2 | 3 | 4 | 5 | 6 | 40.0000% | 33.3333% |
| val3 | reviewed:direct_lexical | 16 | 17 | 45 | 33 | 61 | 48.4848% | 26.2295% |
| val3 | reviewed:direct_object_marker_not_overt | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:directional_suffix | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:elliptical_predicate_explication | 0 | 2 | 4 | 2 | 4 | 0.0000% | 0.0000% |
| val3 | reviewed:emphasis | 1 | 1 | 2 | 2 | 3 | 50.0000% | 33.3333% |
| val3 | reviewed:existential_restructuring | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:explicit_object | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:explicit_original_null | 0 | 22 | 67 | 22 | 67 | 0.0000% | 0.0000% |
| val3 | reviewed:explicit_subject | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:explicit_target_function | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| val3 | reviewed:explicit_target_null | 0 | 5 | 6 | 5 | 6 | 0.0000% | 0.0000% |
| val3 | reviewed:frequent_lemma | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| val3 | reviewed:function_token | 0 | 5 | 9 | 5 | 9 | 0.0000% | 0.0000% |
| val3 | reviewed:genitive_lexical_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:grammatical_expansion | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:grammatical_function | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| val3 | reviewed:grammatical_function_not_overt | 0 | 7 | 30 | 7 | 30 | 0.0000% | 0.0000% |
| val3 | reviewed:grouped_expression | 0 | 4 | 5 | 4 | 5 | 0.0000% | 0.0000% |
| val3 | reviewed:idiom | 1 | 5 | 5 | 6 | 6 | 16.6667% | 16.6667% |
| val3 | reviewed:idiomatic_rendering | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:infinitive_group | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:instrumental_group | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:interrogative | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| val3 | reviewed:lexical_alignment | 30 | 21 | 61 | 51 | 91 | 58.8235% | 32.9670% |
| val3 | reviewed:lexical_context | 9 | 7 | 25 | 16 | 34 | 56.2500% | 26.4706% |
| val3 | reviewed:lexical_context_equivalence | 65 | 87 | 201 | 152 | 266 | 42.7632% | 24.4361% |
| val3 | reviewed:lexical_expansion | 1 | 2 | 4 | 3 | 5 | 33.3333% | 20.0000% |
| val3 | reviewed:manual_adjudication | 34 | 126 | 375 | 160 | 409 | 21.2500% | 8.3130% |
| val3 | reviewed:manual_semantic_alignment | 227 | 220 | 667 | 447 | 894 | 50.7830% | 25.3915% |
| val3 | reviewed:many_to_many | 0 | 2 | 4 | 2 | 4 | 0.0000% | 0.0000% |
| val3 | reviewed:many_to_one | 0 | 18 | 17 | 18 | 17 | 0.0000% | 0.0000% |
| val3 | reviewed:merge_split | 79 | 909 | 1280 | 988 | 1359 | 7.9960% | 5.8131% |
| val3 | reviewed:morphosyntactic_contraction | 0 | 2 | 7 | 2 | 7 | 0.0000% | 0.0000% |
| val3 | reviewed:multiple_strong | 4 | 108 | 120 | 112 | 124 | 3.5714% | 3.2258% |
| val3 | reviewed:named_entity | 230 | 160 | 256 | 390 | 486 | 58.9744% | 47.3251% |
| val3 | reviewed:negation | 1 | 0 | 0 | 1 | 1 | 100.0000% | 100.0000% |
| val3 | reviewed:nonlexical_source_marker | 0 | 5 | 17 | 5 | 17 | 0.0000% | 0.0000% |
| val3 | reviewed:omission | 3 | 430 | 1429 | 433 | 1432 | 0.6928% | 0.2095% |
| val3 | reviewed:one_to_many | 1 | 8 | 13 | 9 | 14 | 11.1111% | 7.1429% |
| val3 | reviewed:one_to_one | 58 | 26 | 62 | 84 | 120 | 69.0476% | 48.3333% |
| val3 | reviewed:overt_subject | 1 | 4 | 5 | 5 | 6 | 20.0000% | 16.6667% |
| val3 | reviewed:particle | 517 | 761 | 1549 | 1278 | 2066 | 40.4538% | 25.0242% |
| val3 | reviewed:particle_expansion | 0 | 4 | 2 | 4 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:polysemy | 123 | 356 | 617 | 479 | 740 | 25.6785% | 16.6216% |
| val3 | reviewed:possessive | 3 | 6 | 8 | 9 | 11 | 33.3333% | 27.2727% |
| val3 | reviewed:predicate_restructuring | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:prepositional_expansion | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:pronominal_complement | 1 | 4 | 6 | 5 | 7 | 20.0000% | 14.2857% |
| val3 | reviewed:pronominal_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:pronominal_subject | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:rare_lemma | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| val3 | reviewed:reflexive_possessive | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:relative_expansion | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:reorder | 478 | 643 | 1251 | 1121 | 1729 | 42.6405% | 27.6460% |
| val3 | reviewed:repetition | 8 | 39 | 43 | 47 | 51 | 17.0213% | 15.6863% |
| val3 | reviewed:semantic_restructuring_requires_second_pass | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| val3 | reviewed:source_grammar | 0 | 6 | 14 | 6 | 14 | 0.0000% | 0.0000% |
| val3 | reviewed:source_marker | 0 | 15 | 46 | 15 | 46 | 0.0000% | 0.0000% |
| val3 | reviewed:source_merge_or_compound | 1 | 28 | 28 | 29 | 29 | 3.4483% | 3.4483% |
| val3 | reviewed:source_text_not_rendered | 0 | 22 | 52 | 22 | 52 | 0.0000% | 0.0000% |
| val3 | reviewed:subject_absorption | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:subject_expansion | 0 | 5 | 3 | 5 | 3 | 0.0000% | 0.0000% |
| val3 | reviewed:target_split_or_expansion | 1 | 21 | 19 | 22 | 20 | 4.5455% | 5.0000% |
| val3 | reviewed:tense_aspect | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| val3 | reviewed:textual_variant | 160 | 162 | 359 | 322 | 519 | 49.6894% | 30.8285% |
| val3 | reviewed:translation_addition | 0 | 2 | 5 | 2 | 5 | 0.0000% | 0.0000% |
| val3 | reviewed:translation_omission | 0 | 1 | 4 | 1 | 4 | 0.0000% | 0.0000% |
| val3 | reviewed:translation_paraphrase | 0 | 4 | 4 | 4 | 4 | 0.0000% | 0.0000% |
| val3 | reviewed:unclassified | 690 | 580 | 1215 | 1270 | 1905 | 54.3307% | 36.2205% |
| val3 | reviewed:volitive | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| val3 | source_frequency:frequent_1000_plus | 665 | 561 | 1699 | 1226 | 2364 | 54.2414% | 28.1303% |
| val3 | source_frequency:mid | 1063 | 675 | 2230 | 1738 | 3293 | 61.1623% | 32.2806% |
| val3 | source_frequency:rare_1_to_5 | 75 | 88 | 268 | 163 | 343 | 46.0123% | 21.8659% |
| val3 | source_frequency:unclassified | 279 | 627 | 2320 | 906 | 2599 | 30.7947% | 10.7349% |
| val3 | testament:NT | 1020 | 713 | 2050 | 1733 | 3070 | 58.8575% | 33.2248% |
| val3 | testament:OT | 1062 | 1143 | 4409 | 2205 | 5471 | 48.1633% | 19.4114% |
| test4 | book:1Chr | 37 | 28 | 113 | 65 | 150 | 56.9231% | 24.6667% |
| test4 | book:1Cor | 46 | 37 | 95 | 83 | 141 | 55.4217% | 32.6241% |
| test4 | book:1John | 112 | 44 | 164 | 156 | 276 | 71.7949% | 40.5797% |
| test4 | book:1Kgs | 24 | 55 | 123 | 79 | 147 | 30.3797% | 16.3265% |
| test4 | book:1Pet | 38 | 24 | 69 | 62 | 107 | 61.2903% | 35.5140% |
| test4 | book:1Sam | 36 | 52 | 177 | 88 | 213 | 40.9091% | 16.9014% |
| test4 | book:1Thess | 8 | 7 | 24 | 15 | 32 | 53.3333% | 25.0000% |
| test4 | book:1Tim | 50 | 28 | 85 | 78 | 135 | 64.1026% | 37.0370% |
| test4 | book:2Chr | 25 | 17 | 79 | 42 | 104 | 59.5238% | 24.0385% |
| test4 | book:2Cor | 38 | 36 | 102 | 74 | 140 | 51.3514% | 27.1429% |
| test4 | book:2Kgs | 46 | 34 | 141 | 80 | 187 | 57.5000% | 24.5989% |
| test4 | book:2Pet | 28 | 17 | 56 | 45 | 84 | 62.2222% | 33.3333% |
| test4 | book:2Sam | 51 | 38 | 148 | 89 | 199 | 57.3034% | 25.6281% |
| test4 | book:2Thess | 71 | 28 | 105 | 99 | 176 | 71.7172% | 40.3409% |
| test4 | book:2Tim | 21 | 10 | 23 | 31 | 44 | 67.7419% | 47.7273% |
| test4 | book:3John | 10 | 14 | 29 | 24 | 39 | 41.6667% | 25.6410% |
| test4 | book:Acts | 22 | 8 | 25 | 30 | 47 | 73.3333% | 46.8085% |
| test4 | book:Amos | 65 | 53 | 225 | 118 | 290 | 55.0847% | 22.4138% |
| test4 | book:Col | 41 | 25 | 70 | 66 | 111 | 62.1212% | 36.9369% |
| test4 | book:Dan | 23 | 40 | 183 | 63 | 206 | 36.5079% | 11.1650% |
| test4 | book:Deut | 42 | 39 | 153 | 81 | 195 | 51.8519% | 21.5385% |
| test4 | book:Eccl | 17 | 22 | 79 | 39 | 96 | 43.5897% | 17.7083% |
| test4 | book:Eph | 44 | 17 | 62 | 61 | 106 | 72.1311% | 41.5094% |
| test4 | book:Esth | 51 | 41 | 166 | 92 | 217 | 55.4348% | 23.5023% |
| test4 | book:Exod | 40 | 26 | 116 | 66 | 156 | 60.6061% | 25.6410% |
| test4 | book:Ezek | 56 | 51 | 211 | 107 | 267 | 52.3364% | 20.9738% |
| test4 | book:Ezra | 41 | 39 | 130 | 80 | 171 | 51.2500% | 23.9766% |
| test4 | book:Gal | 32 | 21 | 53 | 53 | 85 | 60.3774% | 37.6471% |
| test4 | book:Gen | 57 | 49 | 189 | 106 | 246 | 53.7736% | 23.1707% |
| test4 | book:Hab | 18 | 15 | 101 | 33 | 119 | 54.5455% | 15.1261% |
| test4 | book:Hag | 39 | 29 | 136 | 68 | 175 | 57.3529% | 22.2857% |
| test4 | book:Heb | 44 | 29 | 86 | 73 | 130 | 60.2740% | 33.8462% |
| test4 | book:Hos | 12 | 19 | 82 | 31 | 94 | 38.7097% | 12.7660% |
| test4 | book:Isa | 19 | 24 | 119 | 43 | 138 | 44.1860% | 13.7681% |
| test4 | book:Jas | 37 | 26 | 84 | 63 | 121 | 58.7302% | 30.5785% |
| test4 | book:Jer | 23 | 43 | 157 | 66 | 180 | 34.8485% | 12.7778% |
| test4 | book:Job | 16 | 20 | 87 | 36 | 103 | 44.4444% | 15.5340% |
| test4 | book:Joel | 24 | 18 | 103 | 42 | 127 | 57.1429% | 18.8976% |
| test4 | book:John | 44 | 27 | 62 | 71 | 106 | 61.9718% | 41.5094% |
| test4 | book:Jonah | 25 | 21 | 109 | 46 | 134 | 54.3478% | 18.6567% |
| test4 | book:Josh | 55 | 57 | 193 | 112 | 248 | 49.1071% | 22.1774% |
| test4 | book:Jude | 43 | 28 | 95 | 71 | 138 | 60.5634% | 31.1594% |
| test4 | book:Judg | 57 | 39 | 123 | 96 | 180 | 59.3750% | 31.6667% |
| test4 | book:Lam | 11 | 17 | 77 | 28 | 88 | 39.2857% | 12.5000% |
| test4 | book:Lev | 47 | 43 | 141 | 90 | 188 | 52.2222% | 25.0000% |
| test4 | book:Luke | 51 | 38 | 119 | 89 | 170 | 57.3034% | 30.0000% |
| test4 | book:Mal | 40 | 34 | 162 | 74 | 202 | 54.0541% | 19.8020% |
| test4 | book:Mark | 64 | 37 | 105 | 101 | 169 | 63.3663% | 37.8698% |
| test4 | book:Mat | 54 | 45 | 94 | 99 | 148 | 54.5455% | 36.4865% |
| test4 | book:Mic | 17 | 25 | 94 | 42 | 111 | 40.4762% | 15.3153% |
| test4 | book:Nah | 15 | 27 | 110 | 42 | 125 | 35.7143% | 12.0000% |
| test4 | book:Neh | 53 | 34 | 122 | 87 | 175 | 60.9195% | 30.2857% |
| test4 | book:Num | 39 | 18 | 76 | 57 | 115 | 68.4211% | 33.9130% |
| test4 | book:Obad | 11 | 13 | 55 | 24 | 66 | 45.8333% | 16.6667% |
| test4 | book:Phil | 35 | 21 | 66 | 56 | 101 | 62.5000% | 34.6535% |
| test4 | book:Phlm | 22 | 9 | 31 | 31 | 53 | 70.9677% | 41.5094% |
| test4 | book:Prov | 8 | 16 | 49 | 24 | 57 | 33.3333% | 14.0351% |
| test4 | book:Ps | 54 | 69 | 404 | 123 | 458 | 43.9024% | 11.7904% |
| test4 | book:Rev | 35 | 27 | 72 | 62 | 107 | 56.4516% | 32.7103% |
| test4 | book:Rom | 70 | 29 | 84 | 99 | 154 | 70.7071% | 45.4545% |
| test4 | book:Ruth | 50 | 38 | 128 | 88 | 178 | 56.8182% | 28.0899% |
| test4 | book:Song | 17 | 21 | 88 | 38 | 105 | 44.7368% | 16.1905% |
| test4 | book:Titus | 29 | 22 | 71 | 51 | 100 | 56.8627% | 29.0000% |
| test4 | book:Zech | 22 | 24 | 98 | 46 | 120 | 47.8261% | 18.3333% |
| test4 | book:Zeph | 31 | 40 | 154 | 71 | 185 | 43.6620% | 16.7568% |
| test4 | fold:4 | 2403 | 1942 | 7132 | 4345 | 9535 | 55.3049% | 25.2019% |
| test4 | reviewed:addition | 2 | 99 | 416 | 101 | 418 | 1.9802% | 0.4785% |
| test4 | reviewed:adjectival_explication | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:adjectival_restructuring | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:analytic_future | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:analytic_tense | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:anaphoric_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:article_noun_group | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:blind_semantic_review | 140 | 109 | 393 | 249 | 533 | 56.2249% | 26.2664% |
| test4 | reviewed:case_government | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:case_realization | 1 | 10 | 7 | 11 | 8 | 9.0909% | 12.5000% |
| test4 | reviewed:case_restructuring | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:causal_connective | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:causative_recasting | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:clause_coordination | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:compositional_alignment | 0 | 13 | 16 | 13 | 16 | 0.0000% | 0.0000% |
| test4 | reviewed:compound | 12 | 116 | 135 | 128 | 147 | 9.3750% | 8.1633% |
| test4 | reviewed:compound_numeral | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:contextual_addressee_addition | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:contextual_lexical_choice | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:coordination | 2 | 1 | 2 | 3 | 4 | 66.6667% | 50.0000% |
| test4 | reviewed:copular_construction | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:dative_group | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:definiteness | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:deictic_expression | 1 | 2 | 7 | 3 | 8 | 33.3333% | 12.5000% |
| test4 | reviewed:deictic_time | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:derivation | 1 | 3 | 5 | 4 | 6 | 25.0000% | 16.6667% |
| test4 | reviewed:direct_lexical | 26 | 30 | 65 | 56 | 91 | 46.4286% | 28.5714% |
| test4 | reviewed:direct_object_marker_not_overt | 0 | 3 | 6 | 3 | 6 | 0.0000% | 0.0000% |
| test4 | reviewed:directional_pr_pronominal | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:directional_suffix | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:discourse_particle | 1 | 0 | 0 | 1 | 1 | 100.0000% | 100.0000% |
| test4 | reviewed:explicit_original_null | 0 | 22 | 99 | 22 | 99 | 0.0000% | 0.0000% |
| test4 | reviewed:explicit_subject | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:explicit_target_function | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| test4 | reviewed:explicit_target_null | 1 | 10 | 11 | 11 | 12 | 9.0909% | 8.3333% |
| test4 | reviewed:frequent_lemma | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| test4 | reviewed:function_token | 1 | 11 | 16 | 12 | 17 | 8.3333% | 5.8824% |
| test4 | reviewed:grammatical_expansion | 0 | 5 | 9 | 5 | 9 | 0.0000% | 0.0000% |
| test4 | reviewed:grammatical_function | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:grammatical_function_not_overt | 0 | 12 | 40 | 12 | 40 | 0.0000% | 0.0000% |
| test4 | reviewed:grouped_expression | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:idiom | 2 | 13 | 14 | 15 | 16 | 13.3333% | 12.5000% |
| test4 | reviewed:idiomatic_paraphrase | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:idiomatic_reflexive_particle | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:infinitive | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:interrogative | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:lexical_alignment | 51 | 31 | 78 | 82 | 129 | 62.1951% | 39.5349% |
| test4 | reviewed:lexical_context | 12 | 13 | 21 | 25 | 33 | 48.0000% | 36.3636% |
| test4 | reviewed:lexical_context_equivalence | 140 | 107 | 294 | 247 | 434 | 56.6802% | 32.2581% |
| test4 | reviewed:lexical_divergence | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:lexical_expansion | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:lexical_uncertainty | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:locative_case | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:manual_adjudication | 95 | 159 | 499 | 254 | 594 | 37.4016% | 15.9933% |
| test4 | reviewed:manual_semantic_alignment | 196 | 198 | 644 | 394 | 840 | 49.7462% | 23.3333% |
| test4 | reviewed:many_to_many | 0 | 4 | 4 | 4 | 4 | 0.0000% | 0.0000% |
| test4 | reviewed:many_to_one | 0 | 4 | 4 | 4 | 4 | 0.0000% | 0.0000% |
| test4 | reviewed:merge_split | 144 | 979 | 1389 | 1123 | 1533 | 12.8228% | 9.3933% |
| test4 | reviewed:missing_whitespace | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:morphosyntactic_contraction | 0 | 2 | 3 | 2 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:morphosyntactic_shift | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:multiple_strong | 15 | 116 | 184 | 131 | 199 | 11.4504% | 7.5377% |
| test4 | reviewed:named_entity | 281 | 148 | 283 | 429 | 564 | 65.5012% | 49.8227% |
| test4 | reviewed:named_measure | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:negation | 0 | 2 | 2 | 2 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:negative_concord | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:negative_coordination | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:negative_quantification | 3 | 2 | 3 | 5 | 6 | 60.0000% | 50.0000% |
| test4 | reviewed:nonlexical_source_marker | 0 | 3 | 34 | 3 | 34 | 0.0000% | 0.0000% |
| test4 | reviewed:numeral_mismatch | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:oath_formula_addition | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:omission | 11 | 497 | 1657 | 508 | 1668 | 2.1654% | 0.6595% |
| test4 | reviewed:one_to_many | 0 | 11 | 11 | 11 | 11 | 0.0000% | 0.0000% |
| test4 | reviewed:one_to_one | 28 | 26 | 67 | 54 | 95 | 51.8519% | 29.4737% |
| test4 | reviewed:orthography | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:overt_subject | 0 | 11 | 11 | 11 | 11 | 0.0000% | 0.0000% |
| test4 | reviewed:participial_rendering | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:particle | 556 | 806 | 1664 | 1362 | 2220 | 40.8223% | 25.0450% |
| test4 | reviewed:polarity_anomaly | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:polarity_recasting | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:polysemy | 123 | 386 | 670 | 509 | 793 | 24.1650% | 15.5107% |
| test4 | reviewed:possessive | 7 | 11 | 16 | 18 | 23 | 38.8889% | 30.4348% |
| test4 | reviewed:possessive_derivation | 1 | 2 | 3 | 3 | 4 | 33.3333% | 25.0000% |
| test4 | reviewed:possessive_shift | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:prepositional_restructuring | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:pronominal_complement | 0 | 8 | 11 | 8 | 11 | 0.0000% | 0.0000% |
| test4 | reviewed:pronominal_explication | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:proper_name_group | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:purpose_clause | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:rare_lemma | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| test4 | reviewed:reciprocal_target_accounting | 1 | 0 | 1 | 1 | 2 | 100.0000% | 50.0000% |
| test4 | reviewed:reflexive | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:reflexive_possessive | 1 | 6 | 9 | 7 | 10 | 14.2857% | 10.0000% |
| test4 | reviewed:relative_clause | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:reorder | 546 | 731 | 1427 | 1277 | 1973 | 42.7565% | 27.6736% |
| test4 | reviewed:repetition | 12 | 50 | 70 | 62 | 82 | 19.3548% | 14.6341% |
| test4 | reviewed:resumptive_object | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:rhetorical_question | 0 | 3 | 3 | 3 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:semantic_recasting | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:semantic_restructuring_requires_second_pass | 1 | 7 | 12 | 8 | 13 | 12.5000% | 7.6923% |
| test4 | reviewed:semantic_uncertainty | 0 | 0 | 1 | 0 | 1 | undefined | 0.0000% |
| test4 | reviewed:source_grammar | 0 | 3 | 9 | 3 | 9 | 0.0000% | 0.0000% |
| test4 | reviewed:source_marker | 0 | 14 | 37 | 14 | 37 | 0.0000% | 0.0000% |
| test4 | reviewed:source_merge_or_compound | 4 | 31 | 51 | 35 | 55 | 11.4286% | 7.2727% |
| test4 | reviewed:source_target_surface_issue | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:source_text_not_rendered | 0 | 15 | 81 | 15 | 81 | 0.0000% | 0.0000% |
| test4 | reviewed:subject_expansion | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:subject_shift | 0 | 1 | 1 | 1 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:target_anomaly | 0 | 0 | 2 | 0 | 2 | undefined | 0.0000% |
| test4 | reviewed:target_split_or_expansion | 5 | 27 | 42 | 32 | 47 | 15.6250% | 10.6383% |
| test4 | reviewed:temporal_addition | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:temporal_connective | 0 | 2 | 1 | 2 | 1 | 0.0000% | 0.0000% |
| test4 | reviewed:tense_aspect | 0 | 3 | 2 | 3 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:textual_variant | 151 | 132 | 298 | 283 | 449 | 53.3569% | 33.6303% |
| test4 | reviewed:textual_variant_divergence | 0 | 1 | 2 | 1 | 2 | 0.0000% | 0.0000% |
| test4 | reviewed:translation_addition | 0 | 3 | 6 | 3 | 6 | 0.0000% | 0.0000% |
| test4 | reviewed:translation_omission | 0 | 1 | 3 | 1 | 3 | 0.0000% | 0.0000% |
| test4 | reviewed:translation_paraphrase | 0 | 1 | 4 | 1 | 4 | 0.0000% | 0.0000% |
| test4 | reviewed:unclassified | 835 | 630 | 1331 | 1465 | 2166 | 56.9966% | 38.5503% |
| test4 | source_frequency:frequent_1000_plus | 756 | 636 | 1871 | 1392 | 2627 | 54.3103% | 28.7781% |
| test4 | source_frequency:mid | 1241 | 659 | 2379 | 1900 | 3620 | 65.3158% | 34.2818% |
| test4 | source_frequency:rare_1_to_5 | 58 | 64 | 254 | 122 | 312 | 47.5410% | 18.5897% |
| test4 | source_frequency:unclassified | 348 | 665 | 2683 | 1013 | 3031 | 34.3534% | 11.4814% |
| test4 | testament:NT | 1089 | 654 | 1931 | 1743 | 3020 | 62.4785% | 36.0596% |
| test4 | testament:OT | 1314 | 1288 | 5201 | 2602 | 6515 | 50.4996% | 20.1688% |

## Сравнение с сохранённой7.4

Comparison summary сохраняет exact-hyperedge fixed methods отдельно от legacy target/original/Strong identification. Old scores, source/configurations и artifacts не пересчитывались; их цепочка сохранена. [Сравнение с точными знаменателями](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/baseline_comparison.v1.json).

| Partition | Method | TP | FP | FN | Precision denominator | Recall denominator | P | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| folds0_to3 | awesome-align-multilingual-contextual-v1 | 3857 | 7935 | 32146 | 11792 | 36003 | 32.7086% | 10.7130% |
| folds0_to3 | bridge-full-group-surface-v1 | 501 | 1323 | 35502 | 1824 | 36003 | 27.4671% | 1.3916% |
| folds0_to3 | ibm1-bidirectional-oof-v1 | 6019 | 2519 | 29984 | 8538 | 36003 | 70.4966% | 16.7181% |
| folds0_to3 | local-uk-strong-description-lexical-v1 | 640 | 440 | 35363 | 1080 | 36003 | 59.2593% | 1.7776% |
| folds0_to3 | transliteration-named-entity-v1 | 562 | 140 | 35441 | 702 | 36003 | 80.0570% | 1.5610% |
| fold4_reused_frozen_test | awesome-align-multilingual-contextual-v1 | 1060 | 2091 | 8475 | 3151 | 9535 | 33.6401% | 11.1169% |
| fold4_reused_frozen_test | bridge-full-group-surface-v1 | 133 | 319 | 9402 | 452 | 9535 | 29.4248% | 1.3949% |
| fold4_reused_frozen_test | ibm1-bidirectional-oof-v1 | 1675 | 677 | 7860 | 2352 | 9535 | 71.2160% | 17.5669% |
| fold4_reused_frozen_test | local-uk-strong-description-lexical-v1 | 190 | 122 | 9345 | 312 | 9535 | 60.8974% | 1.9927% |
| fold4_reused_frozen_test | transliteration-named-entity-v1 | 174 | 47 | 9361 | 221 | 9535 | 78.7330% | 1.8249% |
| folds0_to3 | consensus76-v1 | 8561 | 7638 | 27442 | 16199 | 36003 | 52.8489% | 23.7786% |
| fold4_reused_frozen_test | consensus76-v1 | 2403 | 1942 | 7132 | 4345 | 9535 | 55.3049% | 25.2019% |

Legacy имеет другую единицу и приведён отдельно:

| Partition | Unit | TP | FP | FN | Unique P denominator | Triple recall denominator | Unique P | Recall | Strict row P / denominator |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| folds0_to3 | legacy identification | 15520 | 9511 | 10964 | 25031 | 26484 | 62.0031% | 58.6014% | 61.9841% / 25100 |
| fold4_reused_frozen_test | legacy identification | 4146 | 2477 | 2835 | 6623 | 6981 | 62.6000% | 59.3898% | 62.5735% / 6629 |

Новый prior использует development gold по OOF protocol; сохранённые baseline generators не переобучались. Таблица сравнивает измеренные candidate hypotheses на том же frozen eligible gold, не разрешает automatic acceptance.

## Независимая проверка и ограничения

[Independent report](consensus76_independent_validation.v1.ru.md) и [manifest](consensus76_independent_validation.v1.manifest.json) содержат собственный raw input/graph/OOF recount, adversarial canaries, lock tampering, shared-target unions и независимый пересчёт всех новых метрик. Детерминизм проверяется только для новых7.6 payload; старые blind answers, adjudication и global review passes не регенерируются.

Ограничения: approximate bounded search; sparse prior и retained unknowns; совместное sharing требует candidate proof; отсутствие пригодного candidate остаётся uncovered; новые ranking scores не калиброваны. Инженерное завершение7.6 не означает готовность A_auto или завершение всего этапа7.

Полный Python regression:513 PASS =457 existing Bible+26 consensus+30 Content Tool. [Bible/consensus receipt](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/final_regression.v1.json), [Content Tool receipt](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/final_supplementary.v1.json), [stage/docs checks](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/final_stages_docs.v1.json), [immutable baseline preservation](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/final_preservation.v1.json), [navigation/scope](../../work/ukrainian_stage_7_20260801/session_consensus76_20261017_root_01/final_navigation_scope.v1.json). Dart format/analyze/Flutter test/smoke N/A: Python/evidence/content-docs scope; runtime, dependencies, localization, release и production DB не изменены. Approved RU/EN architecture/testing pairs не затронуты.

Применён [change checklist](../../../../.github/change_checklist.md): code/tests/evidence/content docs входят в один набор изменений; runtime, smoke, localization, dependencies, release и approved RU/EN pairs не затронуты.

После завершения всех записей inventory обновляет отдельный writer существующим helper. Только последующий read-only результат и последние receipts записываются в исключённый из inventory [HANDOFF](HANDOFF.ru.md). Этот отчёт не объявляет будущий inventory audit пройденным.

[Итоговый manifest7.6](consensus76.v1.manifest.json), [общий report](report.ru.md), [gold7.4](gold_global_finalization.v2.ru.md).

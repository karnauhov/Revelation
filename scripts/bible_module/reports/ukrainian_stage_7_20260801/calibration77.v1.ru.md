# Этап 7.7 — калибровка и проверенный NO_GO

Doc-Version: `1.0.0`
Last-Updated: `2026-10-17`
Source-Commit: `working-tree`

Инженерный calibration-only pipeline завершён и независимо проверен. Статистическая сертификация **NO_GO; A_auto=0**, production acceptance и automatic promotions **0**. Весь этап7 остаётся открыт. Roadmap7.7 означает calibration; alignment plan7.7 означает iterative ledger, который в этом сеансе не выполнялся.

## Протокол, fit и доказательные ограничения

До fit физически проверены все6115 исходных inventory entries, контрольные SHA, stage3offline/4/5/6/7 и public `check-final-completed`. Исторический preparation status `blocked_before_gold_and_alignment_acceptance` сохранён; authoritative current gold — finalized v2. Исходный Git status clean. Gold66/66 =38 strict+28 completed_with_registered_deferrals,2171 proven verses,45538 eligible hyperedges; full45831+41807=87638 nodes, eligible45591+41517=87108, deferred240+290=530.

[Protocol lock](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/protocol.v1.lock.json), [порядок исполнения](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_root_01/execution_protocol.v1.lock.json), [label-free support](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/support.v1.json), [prefit structural NO_GO](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_root_01/prefit_structural_feasibility.v1.json). Fixed rank-only isotonic PAVA (42 блоков; development score range [0.1; 3.38629436112]), единица label — полная semantic top1 hyperedge identity с relation и NULL reason; equal-score ties агрегируются целиком. Один fit folds0–2, без CV/method/threshold search; A diagnostic threshold0.995, B0.5,10 fixed equal-width bins, logloss epsilon1e-15. За пределами development rank range probability отсутствует и итог C. Probability оценивается только для frozen top1, не для candidate union или всей verse decomposition; вероятности не суммируются и не перемножаются.

Gate сохранён: односторонний confidence95%, required precision lower bound99,5%. 538/538 и892/893 не проходят;539/539 и893/894 проходят только при соответствующей Bernoulli-модели. Зависимые edges одного стиха, shared targets и повторных lexical phenomena не объявлены независимыми trials. Verse/lemma/Strong/target-form connected components — описательная диагностика, их независимость не доказана. Их all-correct bound имеет другой estimand и не сертифицирует edge precision. Даже pooled gold имеет лишь13..97 proven verses/book; все66 обязательных книг underpowered для такой verse-cluster проверки. В validation всего430 reviewed verses. Надёжная Bernoulli/representative sampling модель для edge precision не установлена, поэтому никакая высокая точечная precision не разрешает A_auto. Совместная confidence-гарантия по множеству strata не заявляется; strata после validation не объединялись и не исключались.

Model и весь label-free class payload заморожены до validation3. Validation выполнена ровно один раз, без refit/tuning. Test4 — reused историческая partition; **новый correctness scoring SKIPPED** по заранее заданному NO_GO правилу, labels/metrics7.7 не читались/не вычислялись. Общий annotations JSONL физически проходит для ID/digest/integrity проверок; semantic label fields fold4 не используются и correctness lookup для fold4 не выполняется. Это не новый scoring. Исторические агрегаты7.4/7.6 известны из обязательного чтения и не объявляются untouched holdout.

## Классы на разрешённых scored partitions

| Partition | Class | TP | FP | FN | P denom | Gold denom | Precision | Wilson LB* | Original | Target | Verses | Clusters* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Development 0–2 (in-sample) | A_auto | 0 | 0 | 27462 | 0 | 27462 | — | — | 0 | 0 | 0 | 0 |
| Development 0–2 (in-sample) | B_review | 6002 | 4311 | 21460 | 10313 | 27462 | 0.5819839038107243 | 0.5739745248751777 | 11054 | 11313 | 1291 | 6 |
| Development 0–2 (in-sample) | C_unresolved | 477 | 1471 | 26985 | 1948 | 27462 | 0.24486652977412732 | 0.2292021793199666 | 2719 | 3039 | 971 | 116 |
| Validation 3 (однократно) | A_auto | 0 | 0 | 8541 | 0 | 8541 | — | — | 0 | 0 | 0 | 0 |
| Validation 3 (однократно) | B_review | 1921 | 1335 | 6620 | 3256 | 8541 | 0.589987714987715 | 0.575741018667946 | 3460 | 3557 | 428 | 5 |
| Validation 3 (однократно) | C_unresolved | 161 | 521 | 8380 | 682 | 8541 | 0.23607038123167157 | 0.2103983485602383 | 950 | 1083 | 326 | 64 |

Диагностический high-score bucket (probability≥0.995, итоговый класс C_unresolved):

| Partition | TP | FP | N | Precision | Wilson LB* | Verses | Clusters* |
|---|---|---|---|---|---|---|---|
| Development 0–2 (in-sample) | 61 | 0 | 61 | 1.0 | 0.9575304862433994 | 44 | 8 |
| Validation 3 (однократно) | 22 | 0 | 22 | 1.0 | 0.8904884056032809 | 15 | 6 |

*Wilson LB — описательная односторонняя95% граница, confidence не заменяет required precision99,5%; под зависимостью не является сертификатом. Precision точно задаётся TP/P denominator; FN включает весь eligible gold denominator, включая uncovered/NULL. Компоненты не являются доказанными независимыми units; число доказанных независимых Bernoulli trials не установлено. A_auto с нулевым support имеет undefined precision/LB. High-score bucket `A_proposed` — только диагностический bucket, он отображается в итог C_unresolved. B_review — предложение для проверки; manual overrides/accepted decisions0. Deferred и uncovered — отдельные причины node accounting, не выдуманные assignments.

## Calibration diagnostics

| Partition | Supported | Unsupported | Brier | Log loss | ECE | Edges | Verses | Clusters* |
|---|---|---|---|---|---|---|---|---|
| Development 0–2 (in-sample) | 12261 | 0 | 0.22539496664038536 | 0.638729188279289 | 0.0 | 12261 | 1292 | 4 |
| Validation 3 (однократно) | 3938 | 0 | 0.22175201445791867 | 0.6303765796841344 | 0.008887557621011325 | 3938 | 430 | 2 |

Development diagnostics in-sample, не generalization/OOF estimate. Development bounds также описательны из-за отбора learned high-score bucket на fitting labels; фиксированный заранее probability threshold не делает learned map независимой от этих labels. Максимальный passing bound не искался. Нулевой development ECE — свойство fit на тех же labels, а не доказательство будущей calibration accuracy. Brier/logloss/ECE и reliability bins используют только probability-supported eligible top1 edges; unsupported остаются в correctness/recall accounting. Все bins и знаменатели приведены ниже и в SHA-bound metrics. Test4 diagnostics отсутствуют вследствие predefined skip.

### Development 0–2 (in-sample) — reliability

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 1818 | 388 | 0.21342134213421343 | 0.21342134213421343 |
| 3 | 0 | 0 | — | — |
| 4 | 69 | 28 | 0.4057971014492754 | 0.4057971014492754 |
| 5 | 9739 | 5479 | 0.5625834274566177 | 0.5625834274566177 |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 63 | 53 | 0.8412698412698413 | 0.8412698412698413 |
| 9 | 572 | 531 | 0.9283216783216783 | 0.9283216783216783 |

### Validation 3 (однократно) — reliability

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 635 | 125 | 0.21364026955630344 | 0.1968503937007874 |
| 3 | 0 | 0 | — | — |
| 4 | 25 | 14 | 0.4057435897435897 | 0.56 |
| 5 | 3055 | 1738 | 0.5628751476949441 | 0.5689034369885434 |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 17 | 13 | 0.8412698412698413 | 0.7647058823529411 |
| 9 | 206 | 192 | 0.9283339349837554 | 0.9320388349514563 |

### Calibration diagnostics по итоговым классам

Независимый reporting-only пересчёт использует те же frozen probabilities, fixed10 bins и logloss epsilon; class policy не меняется. [metric_payload_recalculation.v1.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_independent_01/metric_payload_recalculation.v1.json).

| Partition | Class | Edges | Supported | Unsupported | Brier | Log loss | ECE |
|---|---|---|---|---|---|---|---|
| development | A_auto | 0 | 0 | 0 | — | — | — |
| development | B_review | 10313 | 10313 | 0 | 0.23677083248185382 | 0.6634865238653518 | 0.0 |
| development | C_unresolved | 1948 | 1948 | 0 | 0.16516945102279615 | 0.5076601934645735 | 0.0 |
| validation3 | A_auto | 0 | 0 | 0 | — | — | — |
| validation3 | B_review | 3256 | 3256 | 0 | 0.23533875563320614 | 0.6601576264410228 | 0.006290301132334045 |
| validation3 | C_unresolved | 682 | 682 | 0 | 0.15688628239525584 | 0.48819609839318284 | 0.021287362792760903 |

#### development / A_auto

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 0 | 0 | — | — |
| 3 | 0 | 0 | — | — |
| 4 | 0 | 0 | — | — |
| 5 | 0 | 0 | — | — |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 0 | 0 | — | — |
| 9 | 0 | 0 | — | — |

#### development / B_review

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 0 | 0 | — | — |
| 3 | 0 | 0 | — | — |
| 4 | 0 | 0 | — | — |
| 5 | 9739 | 5479 | 0.5625834274566177 | 0.5625834274566177 |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 63 | 53 | 0.8412698412698413 | 0.8412698412698413 |
| 9 | 511 | 470 | 0.9197651663405088 | 0.9197651663405088 |

#### development / C_unresolved

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 1818 | 388 | 0.21342134213421343 | 0.21342134213421343 |
| 3 | 0 | 0 | — | — |
| 4 | 69 | 28 | 0.4057971014492754 | 0.4057971014492754 |
| 5 | 0 | 0 | — | — |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 0 | 0 | — | — |
| 9 | 61 | 61 | 1.0 | 1.0 |

#### validation3 / A_auto

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 0 | 0 | — | — |
| 3 | 0 | 0 | — | — |
| 4 | 0 | 0 | — | — |
| 5 | 0 | 0 | — | — |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 0 | 0 | — | — |
| 9 | 0 | 0 | — | — |

#### validation3 / B_review

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 0 | 0 | — | — |
| 3 | 0 | 0 | — | — |
| 4 | 0 | 0 | — | — |
| 5 | 3055 | 1738 | 0.5628751476949441 | 0.5689034369885434 |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 17 | 13 | 0.8412698412698413 | 0.7647058823529411 |
| 9 | 184 | 170 | 0.9197651663405088 | 0.9239130434782609 |

#### validation3 / C_unresolved

| Bin | N | Correct | Mean probability | Observed precision |
|---|---|---|---|---|
| 0 | 0 | 0 | — | — |
| 1 | 0 | 0 | — | — |
| 2 | 635 | 125 | 0.21364026955630344 | 0.1968503937007874 |
| 3 | 0 | 0 | — | — |
| 4 | 25 | 14 | 0.4057435897435897 | 0.56 |
| 5 | 0 | 0 | — | — |
| 6 | 0 | 0 | — | — |
| 7 | 0 | 0 | — | — |
| 8 | 0 | 0 | — | — |
| 9 | 22 | 22 | 1.0 | 1.0 |

## Применение ко всем31102 стихам

Полный physical accounting сохранён:678149 original+595077 target=1273226 узлов,401983 frozen candidate edges,297767 top1 edges,155246 n-best decompositions. Поиск 7.6 остаётся approximate beam32 / n-best5 / top12; доказанного global optimum нет. Candidate channels, модели, генераторы, ranking weights, search limits и decomposition не менялись. Все296 deferred candidate edges исключены целиком до semantic/feature/label/statistics; invalid/dangling/cross-verse/duplicates проверены раньше exclusion. Нет trimming endpoints, pairwise expansion, reciprocal support inflation, invented NULL или нового Strong. Outside-gold mask absence не создаёт labels. Full top1 original334211/target346822 nodes — гипотезы, не принятие.

| Scope | Verses | A_auto edges | B_review edges | C_unresolved edges | B orig | B target | B verses | B clusters* | C orig | C target | C verses | C clusters* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 31102 | 0 | 254074 | 43693 | 273057 | 278371 | 31051 | 17 | 61154 | 68451 | 22429 | 270 |
| fold:0 | 6231 | 0 | 51092 | 8658 | 54875 | 55957 | 6229 | 16 | 12250 | 13701 | 4488 | 223 |
| fold:1 | 6231 | 0 | 50622 | 8758 | 54380 | 55561 | 6218 | 7 | 12261 | 13655 | 4511 | 243 |
| fold:2 | 6105 | 0 | 49809 | 8567 | 53460 | 54509 | 6095 | 13 | 11993 | 13448 | 4367 | 202 |
| fold:3 | 6238 | 0 | 50920 | 8831 | 54736 | 55623 | 6226 | 6 | 12292 | 13762 | 4501 | 201 |
| fold:4 | 6297 | 0 | 51631 | 8879 | 55606 | 56721 | 6283 | 9 | 12358 | 13885 | 4562 | 219 |

Полный high-score diagnostic bucket: 1126 edges; это label-free число предложений, оно не увеличивает число correctness trials. Все они остаются C_unresolved при NO_GO.

| Scope | Original status counts | Target status counts |
|---|---|---|
| all | {"C_unresolved_unselected": 89637, "candidate_selected": 334211, "deferred_strong_unassigned": 240, "unresolved_only_deferred_candidates": 169, "unresolved_uncovered": 253892} | {"C_unresolved_unselected": 68797, "candidate_selected": 346822, "deferred_strong_unassigned": 290, "unresolved_only_deferred_candidates": 190, "unresolved_uncovered": 178978} |
| fold:0 | {"C_unresolved_unselected": 17970, "candidate_selected": 67125, "deferred_strong_unassigned": 45, "unresolved_only_deferred_candidates": 42, "unresolved_uncovered": 50811} | {"C_unresolved_unselected": 13780, "candidate_selected": 69658, "deferred_strong_unassigned": 67, "unresolved_only_deferred_candidates": 41, "unresolved_uncovered": 35816} |
| fold:1 | {"C_unresolved_unselected": 17869, "candidate_selected": 66641, "deferred_strong_unassigned": 28, "unresolved_only_deferred_candidates": 25, "unresolved_uncovered": 51230} | {"C_unresolved_unselected": 13756, "candidate_selected": 69216, "deferred_strong_unassigned": 48, "unresolved_only_deferred_candidates": 20, "unresolved_uncovered": 35793} |
| fold:2 | {"C_unresolved_unselected": 17416, "candidate_selected": 65453, "deferred_strong_unassigned": 41, "unresolved_only_deferred_candidates": 26, "unresolved_uncovered": 49927} | {"C_unresolved_unselected": 13320, "candidate_selected": 67957, "deferred_strong_unassigned": 59, "unresolved_only_deferred_candidates": 28, "unresolved_uncovered": 35565} |
| fold:3 | {"C_unresolved_unselected": 18166, "candidate_selected": 67028, "deferred_strong_unassigned": 67, "unresolved_only_deferred_candidates": 37, "unresolved_uncovered": 50767} | {"C_unresolved_unselected": 14021, "candidate_selected": 69385, "deferred_strong_unassigned": 62, "unresolved_only_deferred_candidates": 48, "unresolved_uncovered": 35679} |
| fold:4 | {"C_unresolved_unselected": 18216, "candidate_selected": 67964, "deferred_strong_unassigned": 59, "unresolved_only_deferred_candidates": 39, "unresolved_uncovered": 51157} | {"C_unresolved_unselected": 13920, "candidate_selected": 70606, "deferred_strong_unassigned": 54, "unresolved_only_deferred_candidates": 53, "unresolved_uncovered": 36125} |

Fold4 строки этой таблицы — только label-free классификация и physical accounting. TP/FP/FN, precision, Brier и confidence для новых fold4 классов **не оценивались**. Общий account сохраняет каждый узел ровно один раз; class-specific nodes могут пересекаться для доказанного shared-target union, их нельзя механически складывать.

## Утечка, provenance и guards

Единственный feature — frozen rank_score; полный provenance содержит model/version/hash, protocol/input-row/feature digests, training folds, prediction fold, correctness unit и applicability. Raw rank не переименован в probability. [Feature lineage](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/feature_lineage.v1.json) фиксирует upstream development0->[1,2],1->[0,2],2->[0,1], validation3/test4->[0,1,2]. PAVA fit использует все0–2 in-sample. Обычная CV калибратора поверх OOF scores не запускалась: её train features могли бы содержать labels внутреннего held-out fold через upstream prior. Nested views не создавались, claims nested/OOF generalization отсутствуют. Validation/test labels не поступают ни непосредственно, ни через вложенную цепочку в fit/features/thresholds/domain exclusions. Reporting-only vocabulary берётся из KEYS frozen aggregate taxonomy, не из correctness/count values; она не влияет на классы или отбор.

Whole-edge poison, nonrequested-fold label poison, exact null semantics, shared unions Judg.18.24/Mat.5.11/Ruth.2.7, canonical exclusive claims, missing/stale provenance и production spoof проверены автором и независимым reviewer. Детерминизм новых outputs проверен полным frozen-model byte replay; PAVA row permutation проверена на 300 независимых fixture cases. Полные временные копии новых prepared/prediction JSONL с переставленными первыми двумя rows отвергнуты physical SHA consumer. Инвариантность traversal order не заявляется; frozen7.4/7.6 generation/evaluation не запускались. Legacy остаётся zero-vote. Dependency groups, source→target mapping/source selection и source-frequency из frozen source universe сохранены отдельно от reviewed phenomena/OH1988 assignments.

Frozen7.6 сохраняет resolver_eligible=false, calibrated_probability=null, automatic promotions0. Новые artifacts имеют отдельный calibration-only контракт; их resolver_eligible/auto_acceptance false, production_accepted_links0. Production resolver guards не обходились; все B/C outcomes unaccepted.

## Сохранённые references7.6

Следующие числа прочитаны из прежних manifests; это не новый evaluation cycle и не новая test4 оценка7.7. N-best retrieval, candidate union и top1 имеют разные единицы. IBM1 historical7.4 fold4:1675TP/677FP/7860FN, precision1675/2352=0.712159863945578, recall1675/9535=0.175668589407446. Legacy identification в exact hyperedge metrics не включён.

| Historical partition | Mode | TP | FP | FN | P denom | Gold denom | Precision | Recall |
|---|---|---|---|---|---|---|---|---|
| Development0–2 | candidate_union | 7401 | 9208 | 20061 | 16609 | 27462 | 0.44560178216629537 | 0.26949967227441557 |
| Development0–2 | nbest_union | 6795 | 6802 | 20667 | 13597 | 27462 | 0.49974259027726703 | 0.24743281625518898 |
| Development0–2 | top1 | 6479 | 5782 | 20983 | 12261 | 27462 | 0.5284234564880516 | 0.23592600684582332 |
| Validation3 | candidate_union | 2391 | 3002 | 6150 | 5393 | 8541 | 0.44335249397366955 | 0.2799438004917457 |
| Validation3 | nbest_union | 2177 | 2211 | 6364 | 4388 | 8541 | 0.4961257976298997 | 0.2548881863950357 |
| Validation3 | top1 | 2082 | 1856 | 6459 | 3938 | 8541 | 0.5286947689182326 | 0.24376536705303828 |
| Reused test4 | candidate_union | 2716 | 3217 | 6819 | 5933 | 9535 | 0.45777852688353277 | 0.28484530676455166 |
| Reused test4 | nbest_union | 2520 | 2308 | 7015 | 4828 | 9535 | 0.5219552609776305 | 0.26428945988463554 |
| Reused test4 | top1 | 2403 | 1942 | 7132 | 4345 | 9535 | 0.5530494821634062 | 0.2520188778185632 |

## Полные mandatory strata

341 обязательная/отчётная stratum плюс aggregate `all` дают342 metric rows на partition. Book/testament/genre/anomaly/evidence/source-frequency/reviewed/relation строки следуют фиксированному prefit universe; отсутствующие строки остаются явными underpowered/missing. Страты пересекаются; суммы не образуют общий denominator. Для каждой stratum recall denominator — весь eligible gold этой stratum, aggregate `all` включает весь eligible partition. Confidence95% в каждой описательной строке не означает совместную гарантию. Ни одной stratum автоматический класс не разрешён.

### Development 0–2 (in-sample)

| Stratum | Class | TP | FP | FN | P denom | Gold denom | Precision | LB* | Original | Target | Verses | Clusters* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | A_auto | 0 | 0 | 27462 | 0 | 27462 | — | — | 0 | 0 | 0 | 0 |
| all | B_review | 6002 | 4311 | 21460 | 10313 | 27462 | 0.5819839038107243 | 0.5739745248751777 | 11054 | 11313 | 1291 | 6 |
| all | C_unresolved | 477 | 1471 | 26985 | 1948 | 27462 | 0.24486652977412732 | 0.2292021793199666 | 2719 | 3039 | 971 | 116 |
| anomaly:explicit_conflict | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:explicit_conflict | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:explicit_conflict | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:missing | A_auto | 0 | 0 | 26303 | 0 | 26303 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:missing | B_review | 6002 | 4311 | 20301 | 10313 | 26303 | 0.5819839038107243 | 0.5739745248751777 | 11054 | 11313 | 1291 | 6 |
| anomaly:mapping:missing | C_unresolved | 477 | 1471 | 25826 | 1948 | 26303 | 0.24486652977412732 | 0.2292021793199666 | 2719 | 3039 | 971 | 116 |
| anomaly:mapping:other | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:other | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:other | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | A_auto | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | B_review | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | C_unresolved | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:primary | A_auto | 0 | 0 | 26303 | 0 | 26303 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:primary | B_review | 6002 | 4311 | 20301 | 10313 | 26303 | 0.5819839038107243 | 0.5739745248751777 | 11054 | 11313 | 1291 | 6 |
| anomaly:reading:primary | C_unresolved | 477 | 1471 | 25826 | 1948 | 26303 | 0.24486652977412732 | 0.2292021793199666 | 2719 | 3039 | 971 | 116 |
| anomaly:textual_alternative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:textual_alternative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:textual_alternative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| book:1Chr | A_auto | 0 | 0 | 442 | 0 | 442 | — | — | 0 | 0 | 0 | 0 |
| book:1Chr | B_review | 112 | 72 | 330 | 184 | 442 | 0.6086956521739131 | 0.5483496778293945 | 205 | 204 | 22 | 2 |
| book:1Chr | C_unresolved | 0 | 14 | 442 | 14 | 442 | 0.0 | 0.0 | 18 | 21 | 9 | 7 |
| book:1Cor | A_auto | 0 | 0 | 255 | 0 | 255 | — | — | 0 | 0 | 0 | 0 |
| book:1Cor | B_review | 63 | 60 | 192 | 123 | 255 | 0.5121951219512195 | 0.43860063406636185 | 134 | 134 | 18 | 2 |
| book:1Cor | C_unresolved | 10 | 13 | 245 | 23 | 255 | 0.43478260869565216 | 0.2806738753056511 | 28 | 31 | 13 | 10 |
| book:1John | A_auto | 0 | 0 | 248 | 0 | 248 | — | — | 0 | 0 | 0 | 0 |
| book:1John | B_review | 84 | 35 | 164 | 119 | 248 | 0.7058823529411765 | 0.6332157305197359 | 124 | 128 | 13 | 1 |
| book:1John | C_unresolved | 7 | 12 | 241 | 19 | 248 | 0.3684210526315789 | 0.21372891262643998 | 27 | 23 | 9 | 3 |
| book:1Kgs | A_auto | 0 | 0 | 488 | 0 | 488 | — | — | 0 | 0 | 0 | 0 |
| book:1Kgs | B_review | 87 | 139 | 401 | 226 | 488 | 0.38495575221238937 | 0.33337583716561636 | 252 | 257 | 21 | 1 |
| book:1Kgs | C_unresolved | 2 | 22 | 486 | 24 | 488 | 0.08333333333333333 | 0.027970944246688827 | 35 | 38 | 16 | 11 |
| book:1Pet | A_auto | 0 | 0 | 309 | 0 | 309 | — | — | 0 | 0 | 0 | 0 |
| book:1Pet | B_review | 86 | 51 | 223 | 137 | 309 | 0.6277372262773723 | 0.5579460178830649 | 143 | 144 | 18 | 1 |
| book:1Pet | C_unresolved | 12 | 20 | 297 | 32 | 309 | 0.375 | 0.24922285741369088 | 50 | 50 | 17 | 8 |
| book:1Sam | A_auto | 0 | 0 | 396 | 0 | 396 | — | — | 0 | 0 | 0 | 0 |
| book:1Sam | B_review | 88 | 74 | 308 | 162 | 396 | 0.5432098765432098 | 0.4786528415536487 | 179 | 181 | 17 | 1 |
| book:1Sam | C_unresolved | 3 | 24 | 393 | 27 | 396 | 0.1111111111111111 | 0.04528847190347794 | 37 | 41 | 13 | 6 |
| book:1Thess | A_auto | 0 | 0 | 336 | 0 | 336 | — | — | 0 | 0 | 0 | 0 |
| book:1Thess | B_review | 109 | 62 | 227 | 171 | 336 | 0.6374269005847953 | 0.5752507094254959 | 174 | 183 | 19 | 1 |
| book:1Thess | C_unresolved | 17 | 13 | 319 | 30 | 336 | 0.5666666666666667 | 0.41851992055777143 | 38 | 36 | 14 | 10 |
| book:1Tim | A_auto | 0 | 0 | 317 | 0 | 317 | — | — | 0 | 0 | 0 | 0 |
| book:1Tim | B_review | 110 | 62 | 207 | 172 | 317 | 0.6395348837209303 | 0.5775849772117627 | 178 | 177 | 21 | 2 |
| book:1Tim | C_unresolved | 9 | 14 | 308 | 23 | 317 | 0.391304347826087 | 0.24399899068559985 | 36 | 36 | 12 | 8 |
| book:2Chr | A_auto | 0 | 0 | 753 | 0 | 753 | — | — | 0 | 0 | 0 | 0 |
| book:2Chr | B_review | 152 | 115 | 601 | 267 | 753 | 0.5692883895131086 | 0.518993011780865 | 294 | 294 | 24 | 1 |
| book:2Chr | C_unresolved | 5 | 30 | 748 | 35 | 753 | 0.14285714285714285 | 0.07130870042140164 | 55 | 52 | 17 | 4 |
| book:2Cor | A_auto | 0 | 0 | 348 | 0 | 348 | — | — | 0 | 0 | 0 | 0 |
| book:2Cor | B_review | 88 | 69 | 260 | 157 | 348 | 0.5605095541401274 | 0.49487619527896703 | 169 | 171 | 21 | 2 |
| book:2Cor | C_unresolved | 21 | 27 | 327 | 48 | 348 | 0.4375 | 0.3261955350196099 | 61 | 64 | 20 | 8 |
| book:2John | A_auto | 0 | 0 | 154 | 0 | 154 | — | — | 0 | 0 | 0 | 0 |
| book:2John | B_review | 46 | 28 | 108 | 74 | 154 | 0.6216216216216216 | 0.5261472625790398 | 79 | 77 | 9 | 1 |
| book:2John | C_unresolved | 6 | 5 | 148 | 11 | 154 | 0.5454545454545454 | 0.3150681426585182 | 18 | 17 | 8 | 7 |
| book:2Kgs | A_auto | 0 | 0 | 593 | 0 | 593 | — | — | 0 | 0 | 0 | 0 |
| book:2Kgs | B_review | 132 | 100 | 461 | 232 | 593 | 0.5689655172413793 | 0.5149948381349672 | 249 | 249 | 21 | 1 |
| book:2Kgs | C_unresolved | 7 | 29 | 586 | 36 | 593 | 0.19444444444444445 | 0.10900815688556029 | 48 | 58 | 16 | 6 |
| book:2Pet | A_auto | 0 | 0 | 379 | 0 | 379 | — | — | 0 | 0 | 0 | 0 |
| book:2Pet | B_review | 101 | 55 | 278 | 156 | 379 | 0.6474358974358975 | 0.5824913894636286 | 160 | 173 | 20 | 2 |
| book:2Pet | C_unresolved | 17 | 37 | 362 | 54 | 379 | 0.3148148148148148 | 0.22181776052357297 | 76 | 85 | 19 | 7 |
| book:2Sam | A_auto | 0 | 0 | 575 | 0 | 575 | — | — | 0 | 0 | 0 | 0 |
| book:2Sam | B_review | 132 | 91 | 443 | 223 | 575 | 0.5919282511210763 | 0.5370055223265653 | 238 | 241 | 21 | 3 |
| book:2Sam | C_unresolved | 3 | 26 | 572 | 29 | 575 | 0.10344827586206896 | 0.04210607554625538 | 35 | 42 | 14 | 4 |
| book:2Thess | A_auto | 0 | 0 | 338 | 0 | 338 | — | — | 0 | 0 | 0 | 0 |
| book:2Thess | B_review | 106 | 49 | 232 | 155 | 338 | 0.6838709677419355 | 0.6197340925199292 | 164 | 163 | 18 | 1 |
| book:2Thess | C_unresolved | 25 | 22 | 313 | 47 | 338 | 0.5319148936170213 | 0.4137499240771648 | 61 | 64 | 17 | 7 |
| book:2Tim | A_auto | 0 | 0 | 384 | 0 | 384 | — | — | 0 | 0 | 0 | 0 |
| book:2Tim | B_review | 117 | 52 | 267 | 169 | 384 | 0.6923076923076923 | 0.6312630695970732 | 179 | 180 | 24 | 1 |
| book:2Tim | C_unresolved | 13 | 25 | 371 | 38 | 384 | 0.34210526315789475 | 0.22984146852193424 | 61 | 61 | 21 | 16 |
| book:3John | A_auto | 0 | 0 | 97 | 0 | 97 | — | — | 0 | 0 | 0 | 0 |
| book:3John | B_review | 26 | 21 | 71 | 47 | 97 | 0.5531914893617021 | 0.43426933460614886 | 50 | 50 | 6 | 1 |
| book:3John | C_unresolved | 3 | 8 | 94 | 11 | 97 | 0.2727272727272727 | 0.11469412885053899 | 14 | 16 | 5 | 4 |
| book:Acts | A_auto | 0 | 0 | 416 | 0 | 416 | — | — | 0 | 0 | 0 | 0 |
| book:Acts | B_review | 118 | 68 | 298 | 186 | 416 | 0.6344086021505376 | 0.5747836609443028 | 190 | 190 | 22 | 1 |
| book:Acts | C_unresolved | 13 | 37 | 403 | 50 | 416 | 0.26 | 0.17217863209934098 | 68 | 74 | 19 | 6 |
| book:Amos | A_auto | 0 | 0 | 422 | 0 | 422 | — | — | 0 | 0 | 0 | 0 |
| book:Amos | B_review | 76 | 54 | 346 | 130 | 422 | 0.5846153846153846 | 0.5125063489703865 | 136 | 144 | 17 | 1 |
| book:Amos | C_unresolved | 8 | 21 | 414 | 29 | 422 | 0.27586206896551724 | 0.16303316642707164 | 44 | 48 | 11 | 5 |
| book:Col | A_auto | 0 | 0 | 313 | 0 | 313 | — | — | 0 | 0 | 0 | 0 |
| book:Col | B_review | 97 | 49 | 216 | 146 | 313 | 0.6643835616438356 | 0.5976291503342452 | 151 | 154 | 20 | 1 |
| book:Col | C_unresolved | 9 | 19 | 304 | 28 | 313 | 0.32142857142857145 | 0.19764236424994422 | 40 | 47 | 15 | 7 |
| book:Dan | A_auto | 0 | 0 | 481 | 0 | 481 | — | — | 0 | 0 | 0 | 0 |
| book:Dan | B_review | 51 | 57 | 430 | 108 | 481 | 0.4722222222222222 | 0.39485380776914697 | 118 | 120 | 18 | 1 |
| book:Dan | C_unresolved | 8 | 30 | 473 | 38 | 481 | 0.21052631578947367 | 0.12291522540306497 | 53 | 57 | 15 | 6 |
| book:Deut | A_auto | 0 | 0 | 337 | 0 | 337 | — | — | 0 | 0 | 0 | 0 |
| book:Deut | B_review | 73 | 45 | 264 | 118 | 337 | 0.6186440677966102 | 0.5432168819505232 | 123 | 132 | 16 | 3 |
| book:Deut | C_unresolved | 5 | 16 | 332 | 21 | 337 | 0.23809523809523808 | 0.12102558686031813 | 30 | 34 | 11 | 9 |
| book:Eccl | A_auto | 0 | 0 | 503 | 0 | 503 | — | — | 0 | 0 | 0 | 0 |
| book:Eccl | B_review | 79 | 68 | 424 | 147 | 503 | 0.5374149659863946 | 0.4697069558564061 | 160 | 159 | 20 | 1 |
| book:Eccl | C_unresolved | 3 | 37 | 500 | 40 | 503 | 0.075 | 0.030370252611739 | 63 | 62 | 19 | 11 |
| book:Eph | A_auto | 0 | 0 | 326 | 0 | 326 | — | — | 0 | 0 | 0 | 0 |
| book:Eph | B_review | 79 | 52 | 247 | 131 | 326 | 0.6030534351145038 | 0.5313389530853987 | 136 | 141 | 20 | 1 |
| book:Eph | C_unresolved | 7 | 24 | 319 | 31 | 326 | 0.22580645161290322 | 0.12732924808224702 | 53 | 47 | 18 | 11 |
| book:Esth | A_auto | 0 | 0 | 639 | 0 | 639 | — | — | 0 | 0 | 0 | 0 |
| book:Esth | B_review | 118 | 97 | 521 | 215 | 639 | 0.5488372093023256 | 0.49275405623438057 | 239 | 237 | 20 | 1 |
| book:Esth | C_unresolved | 6 | 33 | 633 | 39 | 639 | 0.15384615384615385 | 0.08170176634205892 | 59 | 67 | 17 | 4 |
| book:Exod | A_auto | 0 | 0 | 487 | 0 | 487 | — | — | 0 | 0 | 0 | 0 |
| book:Exod | B_review | 117 | 76 | 370 | 193 | 487 | 0.6062176165803109 | 0.5472833403122879 | 207 | 209 | 20 | 1 |
| book:Exod | C_unresolved | 3 | 19 | 484 | 22 | 487 | 0.13636363636363635 | 0.05584132113802161 | 28 | 32 | 14 | 11 |
| book:Ezek | A_auto | 0 | 0 | 427 | 0 | 427 | — | — | 0 | 0 | 0 | 0 |
| book:Ezek | B_review | 75 | 56 | 352 | 131 | 427 | 0.5725190839694656 | 0.5006633828895553 | 145 | 150 | 17 | 1 |
| book:Ezek | C_unresolved | 9 | 23 | 418 | 32 | 427 | 0.28125 | 0.17161564817209635 | 40 | 45 | 15 | 10 |
| book:Ezra | A_auto | 0 | 0 | 446 | 0 | 446 | — | — | 0 | 0 | 0 | 0 |
| book:Ezra | B_review | 82 | 69 | 364 | 151 | 446 | 0.543046357615894 | 0.47619411481573065 | 164 | 168 | 17 | 1 |
| book:Ezra | C_unresolved | 4 | 17 | 442 | 21 | 446 | 0.19047619047619047 | 0.08852026505608854 | 25 | 26 | 10 | 6 |
| book:Gal | A_auto | 0 | 0 | 289 | 0 | 289 | — | — | 0 | 0 | 0 | 0 |
| book:Gal | B_review | 75 | 67 | 214 | 142 | 289 | 0.528169014084507 | 0.4593806115729639 | 158 | 154 | 18 | 1 |
| book:Gal | C_unresolved | 8 | 16 | 281 | 24 | 289 | 0.3333333333333333 | 0.19922671510154388 | 31 | 33 | 14 | 13 |
| book:Gen | A_auto | 0 | 0 | 383 | 0 | 383 | — | — | 0 | 0 | 0 | 0 |
| book:Gen | B_review | 85 | 61 | 298 | 146 | 383 | 0.5821917808219178 | 0.5141545324742915 | 159 | 160 | 16 | 1 |
| book:Gen | C_unresolved | 4 | 27 | 379 | 31 | 383 | 0.12903225806451613 | 0.05927250137645876 | 38 | 50 | 14 | 4 |
| book:Hab | A_auto | 0 | 0 | 513 | 0 | 513 | — | — | 0 | 0 | 0 | 0 |
| book:Hab | B_review | 68 | 80 | 445 | 148 | 513 | 0.4594594594594595 | 0.3934103764004767 | 162 | 173 | 21 | 2 |
| book:Hab | C_unresolved | 4 | 24 | 509 | 28 | 513 | 0.14285714285714285 | 0.06579216216010401 | 44 | 45 | 15 | 10 |
| book:Hag | A_auto | 0 | 0 | 588 | 0 | 588 | — | — | 0 | 0 | 0 | 0 |
| book:Hag | B_review | 105 | 90 | 483 | 195 | 588 | 0.5384615384615384 | 0.4796152975921421 | 214 | 220 | 20 | 1 |
| book:Hag | C_unresolved | 6 | 25 | 582 | 31 | 588 | 0.1935483870967742 | 0.10354254954292576 | 46 | 48 | 18 | 7 |
| book:Heb | A_auto | 0 | 0 | 289 | 0 | 289 | — | — | 0 | 0 | 0 | 0 |
| book:Heb | B_review | 74 | 46 | 215 | 120 | 289 | 0.6166666666666667 | 0.541853199221546 | 125 | 131 | 18 | 2 |
| book:Heb | C_unresolved | 9 | 15 | 280 | 24 | 289 | 0.375 | 0.23305153214508628 | 35 | 35 | 14 | 9 |
| book:Hos | A_auto | 0 | 0 | 402 | 0 | 402 | — | — | 0 | 0 | 0 | 0 |
| book:Hos | B_review | 87 | 64 | 315 | 151 | 402 | 0.5761589403973509 | 0.5092422303216346 | 156 | 163 | 21 | 2 |
| book:Hos | C_unresolved | 1 | 19 | 401 | 20 | 402 | 0.05 | 0.011234816850851653 | 27 | 39 | 12 | 12 |
| book:Isa | A_auto | 0 | 0 | 438 | 0 | 438 | — | — | 0 | 0 | 0 | 0 |
| book:Isa | B_review | 81 | 71 | 357 | 152 | 438 | 0.5328947368421053 | 0.46633845803282087 | 165 | 168 | 22 | 2 |
| book:Isa | C_unresolved | 7 | 23 | 431 | 30 | 438 | 0.23333333333333334 | 0.1317602445380376 | 39 | 43 | 16 | 15 |
| book:Jas | A_auto | 0 | 0 | 250 | 0 | 250 | — | — | 0 | 0 | 0 | 0 |
| book:Jas | B_review | 79 | 32 | 171 | 111 | 250 | 0.7117117117117117 | 0.6366210109035939 | 114 | 115 | 17 | 1 |
| book:Jas | C_unresolved | 13 | 19 | 237 | 32 | 250 | 0.40625 | 0.27623579752744953 | 45 | 51 | 16 | 11 |
| book:Jer | A_auto | 0 | 0 | 659 | 0 | 659 | — | — | 0 | 0 | 0 | 0 |
| book:Jer | B_review | 122 | 107 | 537 | 229 | 659 | 0.5327510917030568 | 0.4784540806721604 | 263 | 256 | 24 | 2 |
| book:Jer | C_unresolved | 3 | 29 | 656 | 32 | 659 | 0.09375 | 0.038091372834826186 | 42 | 55 | 14 | 8 |
| book:Job | A_auto | 0 | 0 | 241 | 0 | 241 | — | — | 0 | 0 | 0 | 0 |
| book:Job | B_review | 28 | 45 | 213 | 73 | 241 | 0.3835616438356164 | 0.295705399622824 | 78 | 86 | 17 | 4 |
| book:Job | C_unresolved | 0 | 14 | 241 | 14 | 241 | 0.0 | 0.0 | 20 | 26 | 11 | 10 |
| book:Joel | A_auto | 0 | 0 | 401 | 0 | 401 | — | — | 0 | 0 | 0 | 0 |
| book:Joel | B_review | 76 | 51 | 325 | 127 | 401 | 0.5984251968503937 | 0.5255419012095935 | 137 | 135 | 16 | 1 |
| book:Joel | C_unresolved | 0 | 15 | 401 | 15 | 401 | 0.0 | 1.175715490783574e-17 | 23 | 25 | 11 | 11 |
| book:John | A_auto | 0 | 0 | 386 | 0 | 386 | — | — | 0 | 0 | 0 | 0 |
| book:John | B_review | 129 | 59 | 257 | 188 | 386 | 0.6861702127659575 | 0.6281935065140004 | 195 | 203 | 23 | 1 |
| book:John | C_unresolved | 23 | 22 | 363 | 45 | 386 | 0.5111111111111111 | 0.39143582443975855 | 58 | 63 | 18 | 9 |
| book:Jonah | A_auto | 0 | 0 | 566 | 0 | 566 | — | — | 0 | 0 | 0 | 0 |
| book:Jonah | B_review | 128 | 77 | 438 | 205 | 566 | 0.624390243902439 | 0.5674749069208713 | 224 | 228 | 22 | 1 |
| book:Jonah | C_unresolved | 9 | 30 | 557 | 39 | 566 | 0.23076923076923078 | 0.1395110336826601 | 56 | 62 | 19 | 8 |
| book:Josh | A_auto | 0 | 0 | 470 | 0 | 470 | — | — | 0 | 0 | 0 | 0 |
| book:Josh | B_review | 79 | 100 | 391 | 179 | 470 | 0.441340782122905 | 0.3816175252164714 | 205 | 207 | 18 | 1 |
| book:Josh | C_unresolved | 1 | 19 | 469 | 20 | 470 | 0.05 | 0.011234816850851653 | 27 | 30 | 10 | 5 |
| book:Jude | A_auto | 0 | 0 | 237 | 0 | 237 | — | — | 0 | 0 | 0 | 0 |
| book:Jude | B_review | 63 | 38 | 174 | 101 | 237 | 0.6237623762376238 | 0.5422201179511167 | 105 | 104 | 13 | 1 |
| book:Jude | C_unresolved | 10 | 14 | 227 | 24 | 237 | 0.4166666666666667 | 0.26796186712437636 | 35 | 37 | 11 | 7 |
| book:Judg | A_auto | 0 | 0 | 630 | 0 | 630 | — | — | 0 | 0 | 0 | 0 |
| book:Judg | B_review | 144 | 118 | 486 | 262 | 630 | 0.549618320610687 | 0.498808766591696 | 287 | 295 | 23 | 1 |
| book:Judg | C_unresolved | 2 | 20 | 628 | 22 | 630 | 0.09090909090909091 | 0.03055415224149295 | 31 | 36 | 16 | 10 |
| book:Lam | A_auto | 0 | 0 | 404 | 0 | 404 | — | — | 0 | 0 | 0 | 0 |
| book:Lam | B_review | 55 | 55 | 349 | 110 | 404 | 0.5 | 0.42253159356547026 | 115 | 124 | 22 | 4 |
| book:Lam | C_unresolved | 2 | 22 | 402 | 24 | 404 | 0.08333333333333333 | 0.027970944246688827 | 33 | 44 | 14 | 9 |
| book:Lev | A_auto | 0 | 0 | 402 | 0 | 402 | — | — | 0 | 0 | 0 | 0 |
| book:Lev | B_review | 70 | 59 | 332 | 129 | 402 | 0.5426356589147286 | 0.4703524225183007 | 141 | 147 | 16 | 2 |
| book:Lev | C_unresolved | 3 | 28 | 399 | 31 | 402 | 0.0967741935483871 | 0.039341718026033055 | 41 | 50 | 14 | 11 |
| book:Luke | A_auto | 0 | 0 | 304 | 0 | 304 | — | — | 0 | 0 | 0 | 0 |
| book:Luke | B_review | 92 | 42 | 212 | 134 | 304 | 0.6865671641791045 | 0.6175103033874207 | 139 | 141 | 20 | 2 |
| book:Luke | C_unresolved | 7 | 18 | 297 | 25 | 304 | 0.28 | 0.15953836195207008 | 42 | 42 | 16 | 10 |
| book:Mal | A_auto | 0 | 0 | 491 | 0 | 491 | — | — | 0 | 0 | 0 | 0 |
| book:Mal | B_review | 75 | 74 | 416 | 149 | 491 | 0.5033557046979866 | 0.43652500474521594 | 166 | 172 | 18 | 1 |
| book:Mal | C_unresolved | 4 | 26 | 487 | 30 | 491 | 0.13333333333333333 | 0.06129713455799518 | 45 | 51 | 15 | 7 |
| book:Mark | A_auto | 0 | 0 | 487 | 0 | 487 | — | — | 0 | 0 | 0 | 0 |
| book:Mark | B_review | 121 | 96 | 366 | 217 | 487 | 0.5576036866359447 | 0.5017740681022433 | 231 | 238 | 28 | 1 |
| book:Mark | C_unresolved | 20 | 28 | 467 | 48 | 487 | 0.4166666666666667 | 0.3071451154863139 | 62 | 66 | 20 | 7 |
| book:Mat | A_auto | 0 | 0 | 345 | 0 | 345 | — | — | 0 | 0 | 0 | 0 |
| book:Mat | B_review | 114 | 45 | 231 | 159 | 345 | 0.7169811320754716 | 0.6549702732144435 | 166 | 165 | 20 | 1 |
| book:Mat | C_unresolved | 13 | 26 | 332 | 39 | 345 | 0.3333333333333333 | 0.22359246204838437 | 54 | 56 | 16 | 7 |
| book:Mic | A_auto | 0 | 0 | 415 | 0 | 415 | — | — | 0 | 0 | 0 | 0 |
| book:Mic | B_review | 62 | 64 | 353 | 126 | 415 | 0.49206349206349204 | 0.4197458402517953 | 133 | 150 | 17 | 2 |
| book:Mic | C_unresolved | 2 | 31 | 413 | 33 | 415 | 0.06060606060606061 | 0.02026262035520702 | 48 | 59 | 14 | 11 |
| book:Nah | A_auto | 0 | 0 | 378 | 0 | 378 | — | — | 0 | 0 | 0 | 0 |
| book:Nah | B_review | 55 | 59 | 323 | 114 | 378 | 0.4824561403508772 | 0.40677939975709043 | 118 | 121 | 19 | 2 |
| book:Nah | C_unresolved | 4 | 21 | 374 | 25 | 378 | 0.16 | 0.07392513321006355 | 34 | 46 | 15 | 10 |
| book:Neh | A_auto | 0 | 0 | 339 | 0 | 339 | — | — | 0 | 0 | 0 | 0 |
| book:Neh | B_review | 95 | 43 | 244 | 138 | 339 | 0.6884057971014492 | 0.6204582516412736 | 144 | 146 | 16 | 3 |
| book:Neh | C_unresolved | 3 | 13 | 336 | 16 | 339 | 0.1875 | 0.07752937709440155 | 21 | 19 | 11 | 10 |
| book:Num | A_auto | 0 | 0 | 610 | 0 | 610 | — | — | 0 | 0 | 0 | 0 |
| book:Num | B_review | 107 | 103 | 503 | 210 | 610 | 0.5095238095238095 | 0.45302202205129966 | 231 | 249 | 24 | 2 |
| book:Num | C_unresolved | 0 | 19 | 610 | 19 | 610 | 0.0 | 1.2147955148237664e-17 | 30 | 38 | 10 | 4 |
| book:Obad | A_auto | 0 | 0 | 275 | 0 | 275 | — | — | 0 | 0 | 0 | 0 |
| book:Obad | B_review | 53 | 43 | 222 | 96 | 275 | 0.5520833333333334 | 0.4683134724777761 | 103 | 105 | 12 | 2 |
| book:Obad | C_unresolved | 4 | 16 | 271 | 20 | 275 | 0.2 | 0.09311801658121098 | 25 | 31 | 8 | 7 |
| book:Phil | A_auto | 0 | 0 | 336 | 0 | 336 | — | — | 0 | 0 | 0 | 0 |
| book:Phil | B_review | 103 | 51 | 233 | 154 | 336 | 0.6688311688311688 | 0.6040078171466852 | 163 | 171 | 23 | 1 |
| book:Phil | C_unresolved | 15 | 17 | 321 | 32 | 336 | 0.46875 | 0.33183380229313175 | 46 | 51 | 19 | 15 |
| book:Phlm | A_auto | 0 | 0 | 177 | 0 | 177 | — | — | 0 | 0 | 0 | 0 |
| book:Phlm | B_review | 70 | 22 | 107 | 92 | 177 | 0.7608695652173914 | 0.6809367473917836 | 97 | 98 | 12 | 2 |
| book:Phlm | C_unresolved | 5 | 6 | 172 | 11 | 177 | 0.45454545454545453 | 0.24210496514211077 | 13 | 17 | 9 | 9 |
| book:Prov | A_auto | 0 | 0 | 234 | 0 | 234 | — | — | 0 | 0 | 0 | 0 |
| book:Prov | B_review | 40 | 41 | 194 | 81 | 234 | 0.49382716049382713 | 0.40414149391743565 | 86 | 88 | 19 | 5 |
| book:Prov | C_unresolved | 0 | 15 | 234 | 15 | 234 | 0.0 | 1.175715490783574e-17 | 21 | 30 | 11 | 10 |
| book:Ps | A_auto | 0 | 0 | 1099 | 0 | 1099 | — | — | 0 | 0 | 0 | 0 |
| book:Ps | B_review | 112 | 99 | 987 | 211 | 1099 | 0.5308056872037915 | 0.4742625498179664 | 230 | 241 | 53 | 7 |
| book:Ps | C_unresolved | 8 | 47 | 1091 | 55 | 1099 | 0.14545454545454545 | 0.08394908204781595 | 75 | 109 | 33 | 18 |
| book:Rev | A_auto | 0 | 0 | 613 | 0 | 613 | — | — | 0 | 0 | 0 | 0 |
| book:Rev | B_review | 212 | 78 | 401 | 290 | 613 | 0.7310344827586207 | 0.6862141828978007 | 303 | 308 | 23 | 1 |
| book:Rev | C_unresolved | 19 | 42 | 594 | 61 | 613 | 0.3114754098360656 | 0.223711126222984 | 91 | 91 | 21 | 3 |
| book:Rom | A_auto | 0 | 0 | 240 | 0 | 240 | — | — | 0 | 0 | 0 | 0 |
| book:Rom | B_review | 84 | 51 | 156 | 135 | 240 | 0.6222222222222222 | 0.5518201712141746 | 137 | 141 | 15 | 1 |
| book:Rom | C_unresolved | 9 | 11 | 231 | 20 | 240 | 0.45 | 0.2841234912890313 | 24 | 26 | 11 | 8 |
| book:Ruth | A_auto | 0 | 0 | 550 | 0 | 550 | — | — | 0 | 0 | 0 | 0 |
| book:Ruth | B_review | 102 | 88 | 448 | 190 | 550 | 0.5368421052631579 | 0.47723884668237343 | 202 | 209 | 20 | 1 |
| book:Ruth | C_unresolved | 3 | 36 | 547 | 39 | 550 | 0.07692307692307693 | 0.03115972335092813 | 52 | 59 | 16 | 4 |
| book:Song | A_auto | 0 | 0 | 419 | 0 | 419 | — | — | 0 | 0 | 0 | 0 |
| book:Song | B_review | 55 | 60 | 364 | 115 | 419 | 0.4782608695652174 | 0.4030254275410077 | 124 | 130 | 23 | 6 |
| book:Song | C_unresolved | 1 | 29 | 418 | 30 | 419 | 0.03333333333333333 | 0.007471878764942328 | 44 | 56 | 18 | 9 |
| book:Titus | A_auto | 0 | 0 | 295 | 0 | 295 | — | — | 0 | 0 | 0 | 0 |
| book:Titus | B_review | 105 | 38 | 190 | 143 | 295 | 0.7342657342657343 | 0.6695666581598553 | 147 | 148 | 20 | 2 |
| book:Titus | C_unresolved | 16 | 10 | 279 | 26 | 295 | 0.6153846153846154 | 0.4547551614886022 | 33 | 34 | 15 | 12 |
| book:Zech | A_auto | 0 | 0 | 645 | 0 | 645 | — | — | 0 | 0 | 0 | 0 |
| book:Zech | B_review | 115 | 105 | 530 | 220 | 645 | 0.5227272727272727 | 0.4673972694221221 | 242 | 252 | 24 | 1 |
| book:Zech | C_unresolved | 2 | 38 | 643 | 40 | 645 | 0.05 | 0.016686282214939493 | 54 | 63 | 17 | 7 |
| book:Zeph | A_auto | 0 | 0 | 453 | 0 | 453 | — | — | 0 | 0 | 0 | 0 |
| book:Zeph | B_review | 78 | 63 | 375 | 141 | 453 | 0.5531914893617021 | 0.4839662776153679 | 149 | 161 | 18 | 2 |
| book:Zeph | C_unresolved | 2 | 24 | 451 | 26 | 453 | 0.07692307692307693 | 0.02579056210119658 | 33 | 49 | 15 | 11 |
| evidence:lexical_description | A_auto | 0 | 0 | 473 | 0 | 473 | — | — | 0 | 0 | 0 | 0 |
| evidence:lexical_description | B_review | 435 | 156 | 38 | 591 | 473 | 0.7360406091370558 | 0.705190443202456 | 591 | 591 | 310 | 79 |
| evidence:lexical_description | C_unresolved | 13 | 0 | 460 | 13 | 473 | 1.0 | 0.8277332164911549 | 13 | 13 | 11 | 5 |
| evidence:missing | A_auto | 0 | 0 | 20061 | 0 | 20061 | — | — | 0 | 0 | 0 | 0 |
| evidence:missing | B_review | 0 | 0 | 20061 | 0 | 20061 | — | — | 0 | 0 | 0 | 0 |
| evidence:missing | C_unresolved | 0 | 0 | 20061 | 0 | 20061 | — | — | 0 | 0 | 0 | 0 |
| evidence:multilingual_contextual | A_auto | 0 | 0 | 2918 | 0 | 2918 | — | — | 0 | 0 | 0 | 0 |
| evidence:multilingual_contextual | B_review | 2404 | 2494 | 514 | 4898 | 2918 | 0.490812576561862 | 0.47907152232927186 | 5137 | 5506 | 1237 | 34 |
| evidence:multilingual_contextual | C_unresolved | 400 | 1424 | 2518 | 1824 | 2918 | 0.21929824561403508 | 0.20378453258656332 | 2588 | 2907 | 932 | 105 |
| evidence:parallel_translation | A_auto | 0 | 0 | 4691 | 0 | 4691 | — | — | 0 | 0 | 0 | 0 |
| evidence:parallel_translation | B_review | 3830 | 1703 | 861 | 5533 | 4691 | 0.6922103741189228 | 0.6819116156992716 | 6036 | 5925 | 1243 | 23 |
| evidence:parallel_translation | C_unresolved | 96 | 47 | 4595 | 143 | 4691 | 0.6713286713286714 | 0.6040598217879964 | 150 | 151 | 128 | 78 |
| evidence:transliteration | A_auto | 0 | 0 | 435 | 0 | 435 | — | — | 0 | 0 | 0 | 0 |
| evidence:transliteration | B_review | 388 | 45 | 47 | 433 | 435 | 0.8960739030023095 | 0.8694417878041248 | 433 | 433 | 265 | 118 |
| evidence:transliteration | C_unresolved | 0 | 0 | 435 | 0 | 435 | — | — | 0 | 0 | 0 | 0 |
| genre:acts_narrative | A_auto | 0 | 0 | 416 | 0 | 416 | — | — | 0 | 0 | 0 | 0 |
| genre:acts_narrative | B_review | 118 | 68 | 298 | 186 | 416 | 0.6344086021505376 | 0.5747836609443028 | 190 | 190 | 22 | 1 |
| genre:acts_narrative | C_unresolved | 13 | 37 | 403 | 50 | 416 | 0.26 | 0.17217863209934098 | 68 | 74 | 19 | 6 |
| genre:apocalyptic | A_auto | 0 | 0 | 613 | 0 | 613 | — | — | 0 | 0 | 0 | 0 |
| genre:apocalyptic | B_review | 212 | 78 | 401 | 290 | 613 | 0.7310344827586207 | 0.6862141828978007 | 303 | 308 | 23 | 1 |
| genre:apocalyptic | C_unresolved | 19 | 42 | 594 | 61 | 613 | 0.3114754098360656 | 0.223711126222984 | 91 | 91 | 21 | 3 |
| genre:epistle | A_auto | 0 | 0 | 5917 | 0 | 5917 | — | — | 0 | 0 | 0 | 0 |
| genre:epistle | B_review | 1765 | 990 | 4152 | 2755 | 5917 | 0.6406533575317604 | 0.6254860226683842 | 2887 | 2937 | 363 | 2 |
| genre:epistle | C_unresolved | 241 | 347 | 5676 | 588 | 5917 | 0.4098639455782313 | 0.3769900605831819 | 825 | 861 | 297 | 55 |
| genre:gospel_narrative | A_auto | 0 | 0 | 1522 | 0 | 1522 | — | — | 0 | 0 | 0 | 0 |
| genre:gospel_narrative | B_review | 456 | 242 | 1066 | 698 | 1522 | 0.6532951289398281 | 0.6231243907109257 | 731 | 747 | 91 | 1 |
| genre:gospel_narrative | C_unresolved | 63 | 94 | 1459 | 157 | 1522 | 0.4012738853503185 | 0.339127239534793 | 216 | 227 | 70 | 17 |
| genre:historical_prose | A_auto | 0 | 0 | 6321 | 0 | 6321 | — | — | 0 | 0 | 0 | 0 |
| genre:historical_prose | B_review | 1323 | 1106 | 4998 | 2429 | 6321 | 0.5446685878962536 | 0.5280075869240051 | 2658 | 2688 | 240 | 4 |
| genre:historical_prose | C_unresolved | 39 | 283 | 6282 | 322 | 6321 | 0.12111801242236025 | 0.09432623838281469 | 443 | 489 | 165 | 27 |
| genre:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:poetry_wisdom | A_auto | 0 | 0 | 2496 | 0 | 2496 | — | — | 0 | 0 | 0 | 0 |
| genre:poetry_wisdom | B_review | 314 | 313 | 2182 | 627 | 2496 | 0.5007974481658692 | 0.46802013484491306 | 678 | 704 | 132 | 7 |
| genre:poetry_wisdom | C_unresolved | 12 | 142 | 2484 | 154 | 2496 | 0.07792207792207792 | 0.04924254824757258 | 223 | 283 | 92 | 36 |
| genre:prophetic | A_auto | 0 | 0 | 7958 | 0 | 7958 | — | — | 0 | 0 | 0 | 0 |
| genre:prophetic | B_review | 1362 | 1170 | 6596 | 2532 | 7958 | 0.5379146919431279 | 0.5215856643952209 | 2746 | 2842 | 328 | 2 |
| genre:prophetic | C_unresolved | 75 | 417 | 7883 | 492 | 7958 | 0.1524390243902439 | 0.1276899741668702 | 686 | 810 | 244 | 42 |
| genre:torah_prose_law | A_auto | 0 | 0 | 2219 | 0 | 2219 | — | — | 0 | 0 | 0 | 0 |
| genre:torah_prose_law | B_review | 452 | 344 | 1767 | 796 | 2219 | 0.5678391959798995 | 0.5387768455313628 | 861 | 897 | 92 | 2 |
| genre:torah_prose_law | C_unresolved | 15 | 109 | 2204 | 124 | 2219 | 0.12096774193548387 | 0.08072835179157978 | 167 | 204 | 63 | 19 |
| relation:grouped_expression | A_auto | 0 | 0 | 20 | 0 | 20 | — | — | 0 | 0 | 0 | 0 |
| relation:grouped_expression | B_review | 0 | 0 | 20 | 0 | 20 | — | — | 0 | 0 | 0 | 0 |
| relation:grouped_expression | C_unresolved | 0 | 0 | 20 | 0 | 20 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_many | A_auto | 0 | 0 | 269 | 0 | 269 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_many | B_review | 0 | 310 | 269 | 310 | 269 | 0.0 | 0.0 | 653 | 677 | 260 | 75 |
| relation:many_to_many | C_unresolved | 0 | 396 | 269 | 396 | 269 | 0.0 | 0.0 | 967 | 1044 | 352 | 51 |
| relation:many_to_one | A_auto | 0 | 0 | 792 | 0 | 792 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_one | B_review | 3 | 361 | 789 | 364 | 792 | 0.008241758241758242 | 0.003298473506343208 | 762 | 364 | 303 | 92 |
| relation:many_to_one | C_unresolved | 3 | 181 | 789 | 184 | 792 | 0.016304347826086956 | 0.00653433060479876 | 384 | 184 | 174 | 66 |
| relation:one_to_many | A_auto | 0 | 0 | 2018 | 0 | 2018 | — | — | 0 | 0 | 0 | 0 |
| relation:one_to_many | B_review | 27 | 573 | 1991 | 600 | 2018 | 0.045 | 0.033003746167576016 | 600 | 1233 | 469 | 59 |
| relation:one_to_many | C_unresolved | 18 | 357 | 2000 | 375 | 2018 | 0.048 | 0.03285816923634124 | 375 | 818 | 327 | 90 |
| relation:one_to_one | A_auto | 0 | 0 | 18025 | 0 | 18025 | — | — | 0 | 0 | 0 | 0 |
| relation:one_to_one | B_review | 5972 | 3067 | 12053 | 9039 | 18025 | 0.6606925544861157 | 0.6524540545265339 | 9039 | 9039 | 1287 | 13 |
| relation:one_to_one | C_unresolved | 456 | 537 | 17569 | 993 | 18025 | 0.459214501510574 | 0.43334849975581463 | 993 | 993 | 668 | 245 |
| relation:original_omitted | A_auto | 0 | 0 | 5179 | 0 | 5179 | — | — | 0 | 0 | 0 | 0 |
| relation:original_omitted | B_review | 0 | 0 | 5179 | 0 | 5179 | — | — | 0 | 0 | 0 | 0 |
| relation:original_omitted | C_unresolved | 0 | 0 | 5179 | 0 | 5179 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | A_auto | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | B_review | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | C_unresolved | 0 | 0 | 1159 | 0 | 1159 | — | — | 0 | 0 | 0 | 0 |
| reviewed:addition | A_auto | 0 | 0 | 1013 | 0 | 1013 | — | — | 0 | 0 | 0 | 0 |
| reviewed:addition | B_review | 6 | 165 | 1007 | 171 | 1013 | 0.03508771929824561 | 0.018250591776146668 | 184 | 231 | 146 | 30 |
| reviewed:addition | C_unresolved | 0 | 86 | 1013 | 86 | 1013 | 0.0 | 0.0 | 136 | 192 | 79 | 21 |
| reviewed:adjectival_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_rendering | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_rendering | B_review | 0 | 5 | 7 | 5 | 7 | 0.0 | 0.0 | 5 | 8 | 3 | 3 |
| reviewed:adjectival_rendering | C_unresolved | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:age_idiom | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:age_idiom | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:age_idiom | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:alignment_counterexample | A_auto | 0 | 0 | 22 | 0 | 22 | — | — | 0 | 0 | 0 | 0 |
| reviewed:alignment_counterexample | B_review | 3 | 0 | 19 | 3 | 22 | 1.0 | 0.5258044258424873 | 3 | 4 | 1 | 1 |
| reviewed:alignment_counterexample | C_unresolved | 1 | 3 | 21 | 4 | 22 | 0.25 | 0.05790732119985868 | 7 | 6 | 1 | 1 |
| reviewed:analytic_future | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_future | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_future | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_tense | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_tense | B_review | 0 | 3 | 5 | 3 | 5 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:analytic_tense | C_unresolved | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:anaphoric_expansion | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_expansion | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:anaphoric_expansion | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | B_review | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_genitive_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_genitive_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_genitive_group | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 3 | 5 | 1 | 1 |
| reviewed:article_lexical_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_lexical_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_lexical_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:article_noun_group | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_noun_group | B_review | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_noun_group | C_unresolved | 0 | 3 | 5 | 3 | 5 | 0.0 | 0.0 | 7 | 6 | 2 | 2 |
| reviewed:aspectual_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:aspectual_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:aspectual_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:blind_semantic_review | A_auto | 0 | 0 | 1377 | 0 | 1377 | — | — | 0 | 0 | 0 | 0 |
| reviewed:blind_semantic_review | B_review | 261 | 222 | 1116 | 483 | 1377 | 0.5403726708074534 | 0.5029516070854536 | 528 | 554 | 56 | 3 |
| reviewed:blind_semantic_review | C_unresolved | 7 | 73 | 1370 | 80 | 1377 | 0.0875 | 0.04813564152266386 | 108 | 137 | 38 | 9 |
| reviewed:body_part_change | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:body_part_change | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:body_part_change | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_government | A_auto | 0 | 0 | 11 | 0 | 11 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_government | B_review | 0 | 7 | 11 | 7 | 11 | 0.0 | 0.0 | 10 | 9 | 4 | 4 |
| reviewed:case_government | C_unresolved | 0 | 4 | 11 | 4 | 11 | 0.0 | 0.0 | 5 | 8 | 4 | 4 |
| reviewed:case_realization | A_auto | 0 | 0 | 26 | 0 | 26 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_realization | B_review | 1 | 22 | 25 | 23 | 26 | 0.043478260869565216 | 0.009760191526756024 | 27 | 29 | 13 | 13 |
| reviewed:case_realization | C_unresolved | 0 | 4 | 26 | 4 | 26 | 0.0 | 0.0 | 4 | 6 | 4 | 4 |
| reviewed:case_restructuring | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_restructuring | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_restructuring | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causal_connective | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causal_connective | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causal_connective | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_motion_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_motion_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_motion_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_particle_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_particle_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:cohortative_particle_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_clause | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_clause | B_review | 0 | 2 | 3 | 2 | 3 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:comparative_clause | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparison | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparison | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:comparison | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 3 | 1 | 1 |
| reviewed:compositional_alignment | A_auto | 0 | 0 | 24 | 0 | 24 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compositional_alignment | B_review | 0 | 16 | 24 | 16 | 24 | 0.0 | 0.0 | 20 | 17 | 9 | 5 |
| reviewed:compositional_alignment | C_unresolved | 0 | 6 | 24 | 6 | 24 | 0.0 | 0.0 | 9 | 11 | 5 | 4 |
| reviewed:compound | A_auto | 0 | 0 | 415 | 0 | 415 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound | B_review | 20 | 222 | 395 | 242 | 415 | 0.08264462809917356 | 0.05794143237850184 | 277 | 286 | 172 | 80 |
| reviewed:compound | C_unresolved | 8 | 82 | 407 | 90 | 415 | 0.08888888888888889 | 0.05081175342978662 | 151 | 172 | 81 | 63 |
| reviewed:compound_numeral | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_numeral | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_numeral | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_particle_repetition | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_particle_repetition | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_particle_repetition | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| reviewed:contextual_addressee_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_addressee_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_addressee_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_lexical_choice | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_lexical_choice | B_review | 0 | 4 | 7 | 4 | 7 | 0.0 | 0.0 | 4 | 4 | 4 | 4 |
| reviewed:contextual_lexical_choice | C_unresolved | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:contextual_location_addition | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_location_addition | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:contextual_location_addition | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:copular_construction | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_construction | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_construction | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_expression | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_expression | B_review | 1 | 1 | 3 | 2 | 4 | 0.5 | 0.12086631942227365 | 2 | 3 | 2 | 2 |
| reviewed:copular_expression | C_unresolved | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_relative | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_relative | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:copular_relative | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:correlative_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:correlative_expansion | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:correlative_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:dative_copular_expansion | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_copular_expansion | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:dative_copular_expansion | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:dative_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_possessive_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_possessive_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_possessive_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:definiteness | A_auto | 0 | 0 | 15 | 0 | 15 | — | — | 0 | 0 | 0 | 0 |
| reviewed:definiteness | B_review | 2 | 8 | 13 | 10 | 15 | 0.2 | 0.06855798773753206 | 11 | 15 | 6 | 3 |
| reviewed:definiteness | C_unresolved | 0 | 3 | 15 | 3 | 15 | 0.0 | 0.0 | 3 | 4 | 2 | 2 |
| reviewed:deictic_expression | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_expression | B_review | 0 | 3 | 1 | 3 | 1 | 0.0 | 0.0 | 3 | 5 | 1 | 1 |
| reviewed:deictic_expression | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_subject | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_subject | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:deictic_subject | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_time | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_time | B_review | 0 | 3 | 2 | 3 | 2 | 0.0 | 0.0 | 4 | 3 | 2 | 1 |
| reviewed:deictic_time | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivation | A_auto | 0 | 0 | 31 | 0 | 31 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivation | B_review | 3 | 9 | 28 | 12 | 31 | 0.25 | 0.10465256557048917 | 18 | 15 | 9 | 7 |
| reviewed:derivation | C_unresolved | 0 | 2 | 31 | 2 | 31 | 0.0 | 0.0 | 4 | 3 | 2 | 2 |
| reviewed:derivational_rendering | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivational_rendering | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:derivational_rendering | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_lexical | A_auto | 0 | 0 | 212 | 0 | 212 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_lexical | B_review | 62 | 33 | 150 | 95 | 212 | 0.6526315789473685 | 0.5690611272146345 | 101 | 113 | 43 | 18 |
| reviewed:direct_lexical | C_unresolved | 1 | 12 | 211 | 13 | 212 | 0.07692307692307693 | 0.017352312196041646 | 19 | 31 | 12 | 10 |
| reviewed:direct_object_marker_not_overt | A_auto | 0 | 0 | 9 | 0 | 9 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_object_marker_not_overt | B_review | 0 | 3 | 9 | 3 | 9 | 0.0 | 0.0 | 3 | 5 | 3 | 1 |
| reviewed:direct_object_marker_not_overt | C_unresolved | 0 | 1 | 9 | 1 | 9 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:directional_place | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_place | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:directional_place | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_suffix | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_suffix | B_review | 0 | 8 | 7 | 8 | 7 | 0.0 | 0.0 | 10 | 12 | 4 | 4 |
| reviewed:directional_suffix | C_unresolved | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discontinuous_rendering | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discontinuous_rendering | B_review | 0 | 3 | 2 | 3 | 2 | 0.0 | 0.0 | 4 | 5 | 2 | 2 |
| reviewed:discontinuous_rendering | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_restructuring | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_restructuring | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:discourse_restructuring | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:duration_phrase | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:duration_phrase | B_review | 1 | 0 | 2 | 1 | 3 | 1.0 | 0.2698659487840541 | 1 | 1 | 1 | 1 |
| reviewed:duration_phrase | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:elliptical_predicate_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:elliptical_predicate_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:elliptical_predicate_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:emphasis | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:emphasis | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:emphasis | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_original_null | A_auto | 0 | 0 | 297 | 0 | 297 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_original_null | B_review | 0 | 51 | 297 | 51 | 297 | 0.0 | 0.0 | 62 | 56 | 34 | 19 |
| reviewed:explicit_original_null | C_unresolved | 0 | 31 | 297 | 31 | 297 | 0.0 | 0.0 | 52 | 53 | 21 | 7 |
| reviewed:explicit_source_null | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_source_null | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_source_null | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_subject | A_auto | 0 | 0 | 9 | 0 | 9 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_subject | B_review | 0 | 4 | 9 | 4 | 9 | 0.0 | 0.0 | 4 | 4 | 4 | 4 |
| reviewed:explicit_subject | C_unresolved | 0 | 3 | 9 | 3 | 9 | 0.0 | 0.0 | 4 | 6 | 3 | 3 |
| reviewed:explicit_target_function | A_auto | 0 | 0 | 10 | 0 | 10 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_function | B_review | 0 | 1 | 10 | 1 | 10 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:explicit_target_function | C_unresolved | 0 | 0 | 10 | 0 | 10 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_null | A_auto | 0 | 0 | 59 | 0 | 59 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_null | B_review | 0 | 32 | 59 | 32 | 59 | 0.0 | 0.0 | 36 | 48 | 21 | 13 |
| reviewed:explicit_target_null | C_unresolved | 0 | 10 | 59 | 10 | 59 | 0.0 | 0.0 | 13 | 22 | 7 | 4 |
| reviewed:explicitation | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicitation | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:explicitation | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:fawn_deer_lexical_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:fawn_deer_lexical_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:fawn_deer_lexical_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:function_token | A_auto | 0 | 0 | 60 | 0 | 60 | — | — | 0 | 0 | 0 | 0 |
| reviewed:function_token | B_review | 0 | 28 | 60 | 28 | 60 | 0.0 | 0.0 | 31 | 40 | 18 | 11 |
| reviewed:function_token | C_unresolved | 0 | 10 | 60 | 10 | 60 | 0.0 | 0.0 | 13 | 23 | 7 | 5 |
| reviewed:genitive_group | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_group | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:genitive_group | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| reviewed:genitive_lexical_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_lexical_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_lexical_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:gentilic_recasting | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:gentilic_recasting | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:gentilic_recasting | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government | B_review | 0 | 3 | 5 | 3 | 5 | 0.0 | 0.0 | 5 | 8 | 3 | 2 |
| reviewed:government | C_unresolved | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:government_shift | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government_shift | B_review | 2 | 3 | 5 | 5 | 7 | 0.4 | 0.14270647201921308 | 5 | 5 | 2 | 2 |
| reviewed:government_shift | C_unresolved | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_expansion | A_auto | 0 | 0 | 25 | 0 | 25 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_expansion | B_review | 1 | 20 | 24 | 21 | 25 | 0.047619047619047616 | 0.010696136643627141 | 26 | 25 | 13 | 8 |
| reviewed:grammatical_expansion | C_unresolved | 0 | 4 | 25 | 4 | 25 | 0.0 | 0.0 | 4 | 8 | 4 | 3 |
| reviewed:grammatical_function | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:grammatical_function | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function_not_overt | A_auto | 0 | 0 | 169 | 0 | 169 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function_not_overt | B_review | 0 | 30 | 169 | 30 | 169 | 0.0 | 6.364878706553033e-18 | 35 | 34 | 25 | 11 |
| reviewed:grammatical_function_not_overt | C_unresolved | 0 | 29 | 169 | 29 | 169 | 0.0 | 0.0 | 48 | 52 | 25 | 12 |
| reviewed:grouped_expression | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grouped_expression | B_review | 0 | 4 | 7 | 4 | 7 | 0.0 | 0.0 | 5 | 5 | 4 | 4 |
| reviewed:grouped_expression | C_unresolved | 0 | 3 | 7 | 3 | 7 | 0.0 | 0.0 | 4 | 5 | 3 | 3 |
| reviewed:idiom | A_auto | 0 | 0 | 15 | 0 | 15 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiom | B_review | 0 | 15 | 15 | 15 | 15 | 0.0 | 1.175715490783574e-17 | 16 | 17 | 11 | 10 |
| reviewed:idiom | C_unresolved | 0 | 2 | 15 | 2 | 15 | 0.0 | 0.0 | 2 | 3 | 2 | 2 |
| reviewed:idiomatic_armory_rendering | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_armory_rendering | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_armory_rendering | C_unresolved | 0 | 2 | 1 | 2 | 1 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| reviewed:idiomatic_degree | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_degree | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_degree | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_fullness | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_fullness | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:idiomatic_fullness | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_object_explication | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_object_explication | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:idiomatic_object_explication | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_paraphrase | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_paraphrase | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| reviewed:idiomatic_paraphrase | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_rendering | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_rendering | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:idiomatic_rendering | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:idiomatic_smooth_speech | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_smooth_speech | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_smooth_speech | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_translation | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_translation | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:idiomatic_translation | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:impersonal_voice | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:impersonal_voice | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:impersonal_voice | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:implicit_destination_relation | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:implicit_destination_relation | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:implicit_destination_relation | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:kinship | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:kinship | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:kinship | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_alignment | A_auto | 0 | 0 | 366 | 0 | 366 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_alignment | B_review | 131 | 68 | 235 | 199 | 366 | 0.6582914572864321 | 0.6011977570468073 | 210 | 215 | 21 | 3 |
| reviewed:lexical_alignment | C_unresolved | 3 | 24 | 363 | 27 | 366 | 0.1111111111111111 | 0.04528847190347794 | 33 | 40 | 14 | 4 |
| reviewed:lexical_context | A_auto | 0 | 0 | 147 | 0 | 147 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_context | B_review | 29 | 34 | 118 | 63 | 147 | 0.4603174603174603 | 0.3607979798615799 | 67 | 74 | 22 | 9 |
| reviewed:lexical_context | C_unresolved | 0 | 18 | 147 | 18 | 147 | 0.0 | 0.0 | 29 | 40 | 13 | 9 |
| reviewed:lexical_context_equivalence | A_auto | 0 | 0 | 1058 | 0 | 1058 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_context_equivalence | B_review | 261 | 219 | 797 | 480 | 1058 | 0.54375 | 0.5062144230430494 | 524 | 551 | 56 | 3 |
| reviewed:lexical_context_equivalence | C_unresolved | 7 | 73 | 1051 | 80 | 1058 | 0.0875 | 0.04813564152266386 | 108 | 137 | 38 | 9 |
| reviewed:lexical_derivation | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_derivation | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:lexical_derivation | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_divergence | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_divergence | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:lexical_divergence | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_expansion | A_auto | 0 | 0 | 17 | 0 | 17 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_expansion | B_review | 1 | 8 | 16 | 9 | 17 | 0.1111111111111111 | 0.025191472713156977 | 10 | 14 | 5 | 5 |
| reviewed:lexical_expansion | C_unresolved | 0 | 2 | 17 | 2 | 17 | 0.0 | 0.0 | 4 | 5 | 2 | 2 |
| reviewed:lexical_generalization | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_generalization | B_review | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_generalization | C_unresolved | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| reviewed:lexical_mismatch | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_mismatch | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:lexical_mismatch | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_rendering | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_rendering | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:lexical_rendering | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_shift | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_shift | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:lexical_shift | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:lexical_substitution | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_substitution | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:lexical_substitution | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_uncertainty | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_uncertainty | B_review | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:lexical_uncertainty | C_unresolved | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 1 | 3 | 1 | 1 |
| reviewed:location_expression | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:location_expression | B_review | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:location_expression | C_unresolved | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 1 | 3 | 1 | 1 |
| reviewed:locative_case | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_case | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_case | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | C_unresolved | 0 | 2 | 1 | 2 | 1 | 0.0 | 0.0 | 2 | 3 | 1 | 1 |
| reviewed:manual_adjudication | A_auto | 0 | 0 | 1827 | 0 | 1827 | — | — | 0 | 0 | 0 | 0 |
| reviewed:manual_adjudication | B_review | 188 | 395 | 1639 | 583 | 1827 | 0.32246998284734135 | 0.29151097750896676 | 674 | 668 | 160 | 21 |
| reviewed:manual_adjudication | C_unresolved | 4 | 129 | 1823 | 133 | 1827 | 0.03007518796992481 | 0.013572280050309263 | 207 | 217 | 86 | 19 |
| reviewed:manual_semantic_alignment | A_auto | 0 | 0 | 2222 | 0 | 2222 | — | — | 0 | 0 | 0 | 0 |
| reviewed:manual_semantic_alignment | B_review | 518 | 388 | 1704 | 906 | 2222 | 0.5717439293598234 | 0.5445292003271646 | 980 | 1005 | 129 | 5 |
| reviewed:manual_semantic_alignment | C_unresolved | 23 | 143 | 2199 | 166 | 2222 | 0.13855421686746988 | 0.10021758685420316 | 235 | 266 | 93 | 38 |
| reviewed:many_to_many | A_auto | 0 | 0 | 8 | 0 | 8 | — | — | 0 | 0 | 0 | 0 |
| reviewed:many_to_many | B_review | 0 | 8 | 8 | 8 | 8 | 0.0 | 0.0 | 9 | 13 | 5 | 5 |
| reviewed:many_to_many | C_unresolved | 0 | 2 | 8 | 2 | 8 | 0.0 | 0.0 | 3 | 2 | 2 | 2 |
| reviewed:many_to_one | A_auto | 0 | 0 | 25 | 0 | 25 | — | — | 0 | 0 | 0 | 0 |
| reviewed:many_to_one | B_review | 0 | 10 | 25 | 10 | 25 | 0.0 | 0.0 | 12 | 12 | 9 | 9 |
| reviewed:many_to_one | C_unresolved | 0 | 8 | 25 | 8 | 25 | 0.0 | 0.0 | 10 | 11 | 7 | 6 |
| reviewed:measure_explication | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:measure_explication | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:measure_explication | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:merge_split | A_auto | 0 | 0 | 4408 | 0 | 4408 | — | — | 0 | 0 | 0 | 0 |
| reviewed:merge_split | B_review | 289 | 2048 | 4119 | 2337 | 4408 | 0.12366281557552418 | 0.11289511521909916 | 2599 | 2771 | 912 | 67 |
| reviewed:merge_split | C_unresolved | 39 | 762 | 4369 | 801 | 4408 | 0.04868913857677903 | 0.03762937863262981 | 1217 | 1470 | 561 | 114 |
| reviewed:missing_whitespace | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:missing_whitespace | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:missing_whitespace | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_contraction | A_auto | 0 | 0 | 15 | 0 | 15 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_contraction | B_review | 0 | 10 | 15 | 10 | 15 | 0.0 | 0.0 | 11 | 10 | 7 | 6 |
| reviewed:morphosyntactic_contraction | C_unresolved | 0 | 2 | 15 | 2 | 15 | 0.0 | 0.0 | 2 | 3 | 1 | 1 |
| reviewed:morphosyntactic_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:multiple_strong | A_auto | 0 | 0 | 440 | 0 | 440 | — | — | 0 | 0 | 0 | 0 |
| reviewed:multiple_strong | B_review | 29 | 202 | 411 | 231 | 440 | 0.12554112554112554 | 0.09396386424783075 | 266 | 274 | 114 | 45 |
| reviewed:multiple_strong | C_unresolved | 1 | 78 | 439 | 79 | 440 | 0.012658227848101266 | 0.0028290364276782527 | 135 | 156 | 67 | 36 |
| reviewed:named_entity | A_auto | 0 | 0 | 1532 | 0 | 1532 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_entity | B_review | 683 | 389 | 849 | 1072 | 1532 | 0.6371268656716418 | 0.6126538738795513 | 1143 | 1139 | 545 | 77 |
| reviewed:named_entity | C_unresolved | 24 | 77 | 1508 | 101 | 1532 | 0.2376237623762376 | 0.17538154691343996 | 162 | 178 | 93 | 33 |
| reviewed:named_measure | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_measure | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_measure | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation | A_auto | 0 | 0 | 13 | 0 | 13 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation | B_review | 3 | 5 | 10 | 8 | 13 | 0.375 | 0.16117233776067347 | 11 | 10 | 6 | 1 |
| reviewed:negation | C_unresolved | 0 | 1 | 13 | 1 | 13 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:negation_compound | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation_compound | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:negation_compound | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:negative_purpose | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_purpose | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:negative_purpose | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_quantification | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_quantification | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:negative_quantification | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:nominalization | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominalization | B_review | 0 | 3 | 6 | 3 | 6 | 0.0 | 0.0 | 3 | 3 | 3 | 3 |
| reviewed:nominalization | C_unresolved | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nonlexical_source_marker | A_auto | 0 | 0 | 85 | 0 | 85 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nonlexical_source_marker | B_review | 0 | 15 | 85 | 15 | 85 | 0.0 | 1.175715490783574e-17 | 19 | 17 | 13 | 12 |
| reviewed:nonlexical_source_marker | C_unresolved | 0 | 5 | 85 | 5 | 85 | 0.0 | 0.0 | 9 | 7 | 5 | 3 |
| reviewed:number_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_expansion | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:number_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:omission | A_auto | 0 | 0 | 4928 | 0 | 4928 | — | — | 0 | 0 | 0 | 0 |
| reviewed:omission | B_review | 24 | 911 | 4904 | 935 | 4928 | 0.025668449197860963 | 0.018432805272539887 | 1119 | 1030 | 662 | 144 |
| reviewed:omission | C_unresolved | 0 | 475 | 4928 | 475 | 4928 | 0.0 | 0.0 | 840 | 778 | 376 | 56 |
| reviewed:one_to_many | A_auto | 0 | 0 | 22 | 0 | 22 | — | — | 0 | 0 | 0 | 0 |
| reviewed:one_to_many | B_review | 0 | 15 | 22 | 15 | 22 | 0.0 | 1.175715490783574e-17 | 16 | 19 | 9 | 7 |
| reviewed:one_to_many | C_unresolved | 0 | 5 | 22 | 5 | 22 | 0.0 | 0.0 | 6 | 6 | 5 | 5 |
| reviewed:one_to_one | A_auto | 0 | 0 | 181 | 0 | 181 | — | — | 0 | 0 | 0 | 0 |
| reviewed:one_to_one | B_review | 69 | 31 | 112 | 100 | 181 | 0.69 | 0.6097635121266138 | 112 | 112 | 16 | 2 |
| reviewed:one_to_one | C_unresolved | 3 | 15 | 178 | 18 | 181 | 0.16666666666666666 | 0.06864078827907072 | 27 | 30 | 9 | 5 |
| reviewed:orthography | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:orthography | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:orthography | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:overt_subject | A_auto | 0 | 0 | 36 | 0 | 36 | — | — | 0 | 0 | 0 | 0 |
| reviewed:overt_subject | B_review | 0 | 23 | 36 | 23 | 36 | 0.0 | 0.0 | 25 | 30 | 13 | 9 |
| reviewed:overt_subject | C_unresolved | 0 | 6 | 36 | 6 | 36 | 0.0 | 0.0 | 8 | 9 | 5 | 3 |
| reviewed:participial_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:participial_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:participial_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle | A_auto | 0 | 0 | 6627 | 0 | 6627 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle | B_review | 1584 | 1685 | 5043 | 3269 | 6627 | 0.4845518507188743 | 0.4701930976385873 | 3555 | 3747 | 1030 | 22 |
| reviewed:particle | C_unresolved | 87 | 645 | 6540 | 732 | 6627 | 0.11885245901639344 | 0.10056785683515743 | 1112 | 1289 | 487 | 49 |
| reviewed:particle_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:passive_voice | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:passive_voice | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:passive_voice | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:person_number | A_auto | 0 | 0 | 8 | 0 | 8 | — | — | 0 | 0 | 0 | 0 |
| reviewed:person_number | B_review | 0 | 2 | 8 | 2 | 8 | 0.0 | 0.0 | 2 | 2 | 2 | 2 |
| reviewed:person_number | C_unresolved | 0 | 2 | 8 | 2 | 8 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:polarity | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:polarity | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polysemy | A_auto | 0 | 0 | 2201 | 0 | 2201 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polysemy | B_review | 270 | 703 | 1931 | 973 | 2201 | 0.2774922918807811 | 0.25452280116114956 | 1097 | 1150 | 547 | 105 |
| reviewed:polysemy | C_unresolved | 44 | 372 | 2157 | 416 | 2201 | 0.10576923076923077 | 0.08346408097588927 | 676 | 776 | 335 | 113 |
| reviewed:possessive | A_auto | 0 | 0 | 62 | 0 | 62 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive | B_review | 14 | 18 | 48 | 32 | 62 | 0.4375 | 0.3037776070112922 | 38 | 38 | 14 | 8 |
| reviewed:possessive | C_unresolved | 0 | 4 | 62 | 4 | 62 | 0.0 | 0.0 | 6 | 7 | 4 | 4 |
| reviewed:possessive_derivation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_derivation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_derivation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:predicate_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:predicate_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:predicate_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_complement | A_auto | 0 | 0 | 37 | 0 | 37 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_complement | B_review | 2 | 19 | 35 | 21 | 37 | 0.09523809523809523 | 0.032033402063969534 | 22 | 26 | 11 | 9 |
| reviewed:pronominal_complement | C_unresolved | 0 | 4 | 37 | 4 | 37 | 0.0 | 0.0 | 5 | 6 | 3 | 3 |
| reviewed:pronominal_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_subject | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_subject | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_subject | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronoun_repetition | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronoun_repetition | B_review | 1 | 0 | 0 | 1 | 1 | 1.0 | 0.2698659487840541 | 1 | 2 | 1 | 1 |
| reviewed:pronoun_repetition | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:purpose_clause | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:purpose_clause | B_review | 0 | 2 | 5 | 2 | 5 | 0.0 | 0.0 | 2 | 3 | 2 | 2 |
| reviewed:purpose_clause | C_unresolved | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reciprocal_target_accounting | A_auto | 0 | 0 | 19 | 0 | 19 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reciprocal_target_accounting | B_review | 3 | 4 | 16 | 7 | 19 | 0.42857142857142855 | 0.18644319036395607 | 7 | 8 | 5 | 5 |
| reviewed:reciprocal_target_accounting | C_unresolved | 0 | 4 | 19 | 4 | 19 | 0.0 | 0.0 | 7 | 13 | 3 | 1 |
| reviewed:referent_explication | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:referent_explication | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:referent_explication | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive | B_review | 0 | 1 | 6 | 1 | 6 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:reflexive | C_unresolved | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:reflexive_possessive | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_possessive | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_possessive | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_clause | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_clause | B_review | 0 | 3 | 5 | 3 | 5 | 0.0 | 0.0 | 4 | 5 | 3 | 2 |
| reviewed:relative_clause | C_unresolved | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:relative_expansion | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_expansion | B_review | 0 | 2 | 5 | 2 | 5 | 0.0 | 0.0 | 3 | 4 | 1 | 1 |
| reviewed:relative_expansion | C_unresolved | 0 | 2 | 5 | 2 | 5 | 0.0 | 0.0 | 3 | 6 | 2 | 2 |
| reviewed:relative_participle_expansion | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_participle_expansion | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 2 | 5 | 1 | 1 |
| reviewed:relative_participle_expansion | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 3 | 5 | 1 | 1 |
| reviewed:relative_subject | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_subject | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:relative_subject | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reorder | A_auto | 0 | 0 | 5004 | 0 | 5004 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reorder | B_review | 1269 | 1297 | 3735 | 2566 | 5004 | 0.4945440374123149 | 0.4783236794833441 | 2817 | 2878 | 870 | 57 |
| reviewed:reorder | C_unresolved | 95 | 513 | 4909 | 608 | 5004 | 0.15625 | 0.13355763956712455 | 949 | 1092 | 418 | 102 |
| reviewed:repetition | A_auto | 0 | 0 | 149 | 0 | 149 | — | — | 0 | 0 | 0 | 0 |
| reviewed:repetition | B_review | 12 | 86 | 137 | 98 | 149 | 0.12244897959183673 | 0.07791347770495 | 117 | 132 | 69 | 28 |
| reviewed:repetition | C_unresolved | 2 | 20 | 147 | 22 | 149 | 0.09090909090909091 | 0.03055415224149295 | 35 | 44 | 18 | 16 |
| reviewed:resultative | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resultative | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:resultative | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_restructuring_requires_second_pass | A_auto | 0 | 0 | 23 | 0 | 23 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_restructuring_requires_second_pass | B_review | 0 | 6 | 23 | 6 | 23 | 0.0 | 0.0 | 6 | 6 | 4 | 4 |
| reviewed:semantic_restructuring_requires_second_pass | C_unresolved | 0 | 7 | 23 | 7 | 23 | 0.0 | 0.0 | 10 | 18 | 6 | 6 |
| reviewed:semantic_uncertainty | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_uncertainty | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:semantic_uncertainty | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_grammar | A_auto | 0 | 0 | 47 | 0 | 47 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_grammar | B_review | 0 | 7 | 47 | 7 | 47 | 0.0 | 0.0 | 9 | 9 | 6 | 2 |
| reviewed:source_grammar | C_unresolved | 0 | 6 | 47 | 6 | 47 | 0.0 | 0.0 | 11 | 9 | 6 | 5 |
| reviewed:source_idiom | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_idiom | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:source_idiom | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_marker | A_auto | 0 | 0 | 157 | 0 | 157 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_marker | B_review | 0 | 39 | 157 | 39 | 157 | 0.0 | 6.4887504115668775e-18 | 47 | 41 | 35 | 33 |
| reviewed:source_marker | C_unresolved | 0 | 15 | 157 | 15 | 157 | 0.0 | 1.175715490783574e-17 | 27 | 27 | 14 | 11 |
| reviewed:source_merge_or_compound | A_auto | 0 | 0 | 108 | 0 | 108 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_merge_or_compound | B_review | 8 | 51 | 100 | 59 | 108 | 0.13559322033898305 | 0.07812455086250891 | 72 | 70 | 31 | 18 |
| reviewed:source_merge_or_compound | C_unresolved | 0 | 23 | 108 | 23 | 108 | 0.0 | 0.0 | 36 | 50 | 16 | 8 |
| reviewed:source_tag_uncertainty | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_tag_uncertainty | B_review | 0 | 2 | 1 | 2 | 1 | 0.0 | 0.0 | 4 | 2 | 1 | 1 |
| reviewed:source_tag_uncertainty | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:source_text_not_rendered | A_auto | 0 | 0 | 235 | 0 | 235 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_text_not_rendered | B_review | 0 | 42 | 235 | 42 | 235 | 0.0 | 0.0 | 53 | 45 | 34 | 29 |
| reviewed:source_text_not_rendered | C_unresolved | 0 | 18 | 235 | 18 | 235 | 0.0 | 0.0 | 33 | 28 | 16 | 7 |
| reviewed:speaker_attribution_addition | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:speaker_attribution_addition | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:speaker_attribution_addition | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_absorption | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_absorption | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_absorption | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_clause | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_clause | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:subject_clause | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_expansion | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_expansion | B_review | 0 | 3 | 7 | 3 | 7 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:subject_expansion | C_unresolved | 0 | 2 | 7 | 2 | 7 | 0.0 | 0.0 | 3 | 6 | 2 | 2 |
| reviewed:subject_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subordinator_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subordinator_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 1 | 1 | 1 |
| reviewed:subordinator_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_anomaly | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_anomaly | B_review | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:target_anomaly | C_unresolved | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_split_or_expansion | A_auto | 0 | 0 | 110 | 0 | 110 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_split_or_expansion | B_review | 14 | 48 | 96 | 62 | 110 | 0.22580645161290322 | 0.15100934777641498 | 71 | 85 | 30 | 12 |
| reviewed:target_split_or_expansion | C_unresolved | 0 | 20 | 110 | 20 | 110 | 0.0 | 0.0 | 31 | 50 | 15 | 10 |
| reviewed:temporal_addition | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_addition | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_addition | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_clause | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_clause | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:temporal_clause | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:tense_aspect | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:tense_aspect | B_review | 0 | 2 | 1 | 2 | 1 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:tense_aspect | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant | A_auto | 0 | 0 | 1567 | 0 | 1567 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant | B_review | 428 | 329 | 1139 | 757 | 1567 | 0.5653896961690885 | 0.5355738367258589 | 809 | 826 | 237 | 30 |
| reviewed:textual_variant | C_unresolved | 51 | 149 | 1516 | 200 | 1567 | 0.255 | 0.20780897925384803 | 306 | 346 | 129 | 49 |
| reviewed:textual_variant_divergence | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant_divergence | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant_divergence | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_addition | A_auto | 0 | 0 | 18 | 0 | 18 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_addition | B_review | 0 | 5 | 18 | 5 | 18 | 0.0 | 0.0 | 6 | 9 | 5 | 5 |
| reviewed:translation_addition | C_unresolved | 0 | 3 | 18 | 3 | 18 | 0.0 | 0.0 | 8 | 7 | 3 | 3 |
| reviewed:translation_choice | A_auto | 0 | 0 | 19 | 0 | 19 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_choice | B_review | 5 | 3 | 14 | 8 | 19 | 0.625 | 0.3479914384047327 | 8 | 8 | 1 | 1 |
| reviewed:translation_choice | C_unresolved | 1 | 0 | 18 | 1 | 19 | 1.0 | 0.2698659487840541 | 1 | 1 | 1 | 1 |
| reviewed:translation_omission | A_auto | 0 | 0 | 15 | 0 | 15 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_omission | B_review | 0 | 1 | 15 | 1 | 15 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| reviewed:translation_omission | C_unresolved | 0 | 1 | 15 | 1 | 15 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:translation_paraphrase | A_auto | 0 | 0 | 10 | 0 | 10 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_paraphrase | B_review | 0 | 3 | 10 | 3 | 10 | 0.0 | 0.0 | 3 | 4 | 3 | 3 |
| reviewed:translation_paraphrase | C_unresolved | 0 | 0 | 10 | 0 | 10 | — | — | 0 | 0 | 0 | 0 |
| reviewed:unclassified | A_auto | 0 | 0 | 6425 | 0 | 6425 | — | — | 0 | 0 | 0 | 0 |
| reviewed:unclassified | B_review | 2053 | 1383 | 4372 | 3436 | 6425 | 0.5974970896391153 | 0.5836644824797264 | 3755 | 3872 | 939 | 33 |
| reviewed:unclassified | C_unresolved | 209 | 569 | 6216 | 778 | 6425 | 0.2686375321336761 | 0.24333344750713057 | 1177 | 1298 | 516 | 128 |
| reviewed:vocative_particle | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_particle | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_particle | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:vocative_split | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_split | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:vocative_split | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:volitive | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:volitive_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:frequent_1000_plus | A_auto | 0 | 0 | 7514 | 0 | 7514 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:frequent_1000_plus | B_review | 1963 | 1428 | 5551 | 3391 | 7514 | 0.578885284576821 | 0.564881487352223 | 3824 | 3784 | 1124 | 1 |
| source_frequency:frequent_1000_plus | C_unresolved | 89 | 430 | 7425 | 519 | 7514 | 0.17148362235067438 | 0.14598972290599962 | 873 | 861 | 399 | 5 |
| source_frequency:mid | A_auto | 0 | 0 | 10236 | 0 | 10236 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:mid | B_review | 2979 | 1488 | 7257 | 4467 | 10236 | 0.6668905305574211 | 0.6551930609964983 | 4758 | 4773 | 1209 | 28 |
| source_frequency:mid | C_unresolved | 261 | 420 | 9975 | 681 | 10236 | 0.3832599118942731 | 0.3531346513309841 | 1024 | 1094 | 463 | 148 |
| source_frequency:rare_1_to_5 | A_auto | 0 | 0 | 1006 | 0 | 1006 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:rare_1_to_5 | B_review | 195 | 108 | 811 | 303 | 1006 | 0.6435643564356436 | 0.5972188899625351 | 323 | 324 | 226 | 191 |
| source_frequency:rare_1_to_5 | C_unresolved | 52 | 112 | 954 | 164 | 1006 | 0.3170731707317073 | 0.26068620046047203 | 260 | 291 | 138 | 110 |
| source_frequency:unclassified | A_auto | 0 | 0 | 8885 | 0 | 8885 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:unclassified | B_review | 866 | 1378 | 8019 | 2244 | 8885 | 0.3859180035650624 | 0.36916151057172064 | 2340 | 2557 | 749 | 42 |
| source_frequency:unclassified | C_unresolved | 76 | 676 | 8809 | 752 | 8885 | 0.10106382978723404 | 0.08439057323878696 | 1001 | 1179 | 466 | 76 |
| testament:NT | A_auto | 0 | 0 | 8468 | 0 | 8468 | — | — | 0 | 0 | 0 | 0 |
| testament:NT | B_review | 2551 | 1378 | 5917 | 3929 | 8468 | 0.6492746245864087 | 0.6366534928371479 | 4111 | 4182 | 499 | 2 |
| testament:NT | C_unresolved | 336 | 520 | 8132 | 856 | 8468 | 0.3925233644859813 | 0.36545030370324916 | 1200 | 1253 | 407 | 59 |
| testament:OT | A_auto | 0 | 0 | 18994 | 0 | 18994 | — | — | 0 | 0 | 0 | 0 |
| testament:OT | B_review | 3451 | 2933 | 15543 | 6384 | 18994 | 0.5405701754385965 | 0.5302958781248912 | 6943 | 7131 | 792 | 5 |
| testament:OT | C_unresolved | 141 | 951 | 18853 | 1092 | 18994 | 0.12912087912087913 | 0.11334154467781275 | 1519 | 1786 | 564 | 70 |
| testament:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| testament:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| testament:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |

Missing/zero-prediction strata: `anomaly:explicit_conflict`, `anomaly:mapping:1:1`, `anomaly:mapping:merge`, `anomaly:mapping:other`, `anomaly:mapping:split`, `anomaly:none`, `anomaly:reading:missing`, `anomaly:reading:nonprimary_or_unresolved`, `anomaly:textual_alternative`, `evidence:missing`, `genre:missing`, `relation:grouped_expression`, `relation:original_omitted`, `relation:textual_alternative`, `relation:translation_addition`, `reviewed:adjectival_explication`, `reviewed:adjectival_restructuring`, `reviewed:analytic_future`, `reviewed:anaphoric_explication`, `reviewed:aspectual_expansion`, `reviewed:case_restructuring`, `reviewed:causal_connective`, `reviewed:causative_recasting`, `reviewed:clause_coordination`, `reviewed:clause_relation`, `reviewed:clause_restructuring`, `reviewed:cohortative_motion_expansion`, `reviewed:comparative_frame`, `reviewed:compound_numeral`, `reviewed:compound_time`, `reviewed:conditional_expansion`, `reviewed:contextual_addressee_addition`, `reviewed:contextual_demonstrative_addition`, `reviewed:contextual_possessor_addition`, `reviewed:contextual_private_speech_addition`, `reviewed:coordination`, `reviewed:copular_construction`, `reviewed:dative_expansion`, `reviewed:dative_possessive_group`, `reviewed:directional_pr_pronominal`, `reviewed:discourse_particle`, `reviewed:discourse_particle_omission`, `reviewed:distributive`, `reviewed:elliptical_predicate_explication`, `reviewed:emphasis`, `reviewed:existential_restructuring`, `reviewed:existential_to_indefinite`, `reviewed:explicit_object`, `reviewed:explicit_source_null`, `reviewed:fawn_deer_lexical_group`, `reviewed:frequent_lemma`, `reviewed:genitive_lexical_expansion`, `reviewed:idiomatic_degree`, `reviewed:idiomatic_reflexive_particle`, `reviewed:idiomatic_smooth_speech`, `reviewed:idiomatic_wine_house_rendering`, `reviewed:implicit_destination_relation`, `reviewed:inchoative_aspect`, `reviewed:infinitive`, `reviewed:infinitive_group`, `reviewed:instrumental_group`, `reviewed:interrogative`, `reviewed:locative_case`, `reviewed:measure_explication`, `reviewed:morphosyntactic_shift`, `reviewed:named_measure`, `reviewed:negative_concord`, `reviewed:negative_coordination`, `reviewed:negative_copula`, `reviewed:number_shift`, `reviewed:numeral_mismatch`, `reviewed:oath_formula_addition`, `reviewed:orthography`, `reviewed:participial_rendering`, `reviewed:particle_expansion`, `reviewed:polarity_anomaly`, `reviewed:polarity_recasting`, `reviewed:possessive_derivation`, `reviewed:possessive_shift`, `reviewed:predicate_restructuring`, `reviewed:prepositional_expansion`, `reviewed:prepositional_restructuring`, `reviewed:pronominal_expansion`, `reviewed:pronominal_explication`, `reviewed:pronominal_subject`, `reviewed:proper_name_component_omission`, `reviewed:proper_name_group`, `reviewed:proper_place_mismatch`, `reviewed:rare_lemma`, `reviewed:reflexive_possessive`, `reviewed:resumptive_object`, `reviewed:rhetorical_question`, `reviewed:semantic_recasting`, `reviewed:source_component_not_overt`, `reviewed:subject_absorption`, `reviewed:subject_shift`, `reviewed:temporal_addition`, `reviewed:temporal_connective`, `reviewed:textual_variant_divergence`, `reviewed:vocative_superlative`, `reviewed:word_split`, `testament:missing`.

### Validation 3 (однократно)

| Stratum | Class | TP | FP | FN | P denom | Gold denom | Precision | LB* | Original | Target | Verses | Clusters* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | A_auto | 0 | 0 | 8541 | 0 | 8541 | — | — | 0 | 0 | 0 | 0 |
| all | B_review | 1921 | 1335 | 6620 | 3256 | 8541 | 0.589987714987715 | 0.575741018667946 | 3460 | 3557 | 428 | 5 |
| all | C_unresolved | 161 | 521 | 8380 | 682 | 8541 | 0.23607038123167157 | 0.2103983485602383 | 950 | 1083 | 326 | 64 |
| anomaly:explicit_conflict | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:explicit_conflict | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:explicit_conflict | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:1:1 | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:merge | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:missing | A_auto | 0 | 0 | 8173 | 0 | 8173 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:missing | B_review | 1921 | 1335 | 6252 | 3256 | 8173 | 0.589987714987715 | 0.575741018667946 | 3460 | 3557 | 428 | 5 |
| anomaly:mapping:missing | C_unresolved | 161 | 521 | 8012 | 682 | 8173 | 0.23607038123167157 | 0.2103983485602383 | 950 | 1083 | 326 | 64 |
| anomaly:mapping:other | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:other | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:other | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:mapping:split | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | A_auto | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | B_review | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| anomaly:none | C_unresolved | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:nonprimary_or_unresolved | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:primary | A_auto | 0 | 0 | 8173 | 0 | 8173 | — | — | 0 | 0 | 0 | 0 |
| anomaly:reading:primary | B_review | 1921 | 1335 | 6252 | 3256 | 8173 | 0.589987714987715 | 0.575741018667946 | 3460 | 3557 | 428 | 5 |
| anomaly:reading:primary | C_unresolved | 161 | 521 | 8012 | 682 | 8173 | 0.23607038123167157 | 0.2103983485602383 | 950 | 1083 | 326 | 64 |
| anomaly:textual_alternative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:textual_alternative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| anomaly:textual_alternative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| book:1Chr | A_auto | 0 | 0 | 93 | 0 | 93 | — | — | 0 | 0 | 0 | 0 |
| book:1Chr | B_review | 22 | 13 | 71 | 35 | 93 | 0.6285714285714286 | 0.4895860801068812 | 40 | 39 | 4 | 2 |
| book:1Chr | C_unresolved | 1 | 5 | 92 | 6 | 93 | 0.16666666666666666 | 0.03810557007934284 | 10 | 8 | 2 | 2 |
| book:1Cor | A_auto | 0 | 0 | 75 | 0 | 75 | — | — | 0 | 0 | 0 | 0 |
| book:1Cor | B_review | 17 | 11 | 58 | 28 | 75 | 0.6071428571428571 | 0.452423995707315 | 31 | 29 | 6 | 3 |
| book:1Cor | C_unresolved | 0 | 7 | 75 | 7 | 75 | 0.0 | 0.0 | 14 | 13 | 4 | 3 |
| book:1John | A_auto | 0 | 0 | 172 | 0 | 172 | — | — | 0 | 0 | 0 | 0 |
| book:1John | B_review | 54 | 34 | 118 | 88 | 172 | 0.6136363636363636 | 0.5260847572729532 | 94 | 99 | 9 | 1 |
| book:1John | C_unresolved | 5 | 8 | 167 | 13 | 172 | 0.38461538461538464 | 0.20159260258306824 | 19 | 17 | 7 | 4 |
| book:1Kgs | A_auto | 0 | 0 | 128 | 0 | 128 | — | — | 0 | 0 | 0 | 0 |
| book:1Kgs | B_review | 22 | 39 | 106 | 61 | 128 | 0.36065573770491804 | 0.2674384770051503 | 68 | 65 | 5 | 1 |
| book:1Kgs | C_unresolved | 2 | 10 | 126 | 12 | 128 | 0.16666666666666666 | 0.0567805527494444 | 17 | 16 | 4 | 2 |
| book:1Pet | A_auto | 0 | 0 | 125 | 0 | 125 | — | — | 0 | 0 | 0 | 0 |
| book:1Pet | B_review | 30 | 14 | 95 | 44 | 125 | 0.6818181818181818 | 0.5586897706163608 | 46 | 48 | 7 | 2 |
| book:1Pet | C_unresolved | 8 | 10 | 117 | 18 | 125 | 0.4444444444444444 | 0.2719364054526546 | 22 | 26 | 6 | 5 |
| book:1Sam | A_auto | 0 | 0 | 289 | 0 | 289 | — | — | 0 | 0 | 0 | 0 |
| book:1Sam | B_review | 73 | 55 | 216 | 128 | 289 | 0.5703125 | 0.4976203761634306 | 138 | 136 | 11 | 1 |
| book:1Sam | C_unresolved | 4 | 10 | 285 | 14 | 289 | 0.2857142857142857 | 0.13533400388166497 | 15 | 21 | 7 | 4 |
| book:1Thess | A_auto | 0 | 0 | 152 | 0 | 152 | — | — | 0 | 0 | 0 | 0 |
| book:1Thess | B_review | 64 | 22 | 88 | 86 | 152 | 0.7441860465116279 | 0.6601752394646292 | 87 | 88 | 10 | 1 |
| book:1Thess | C_unresolved | 4 | 6 | 148 | 10 | 152 | 0.4 | 0.1942269918768033 | 13 | 10 | 6 | 5 |
| book:1Tim | A_auto | 0 | 0 | 51 | 0 | 51 | — | — | 0 | 0 | 0 | 0 |
| book:1Tim | B_review | 14 | 8 | 37 | 22 | 51 | 0.6363636363636364 | 0.4615411118288446 | 23 | 22 | 3 | 1 |
| book:1Tim | C_unresolved | 1 | 4 | 50 | 5 | 51 | 0.2 | 0.04596245388060396 | 6 | 8 | 2 | 2 |
| book:2Chr | A_auto | 0 | 0 | 138 | 0 | 138 | — | — | 0 | 0 | 0 | 0 |
| book:2Chr | B_review | 30 | 20 | 108 | 50 | 138 | 0.6 | 0.48375270593523306 | 54 | 52 | 6 | 2 |
| book:2Chr | C_unresolved | 0 | 9 | 138 | 9 | 138 | 0.0 | 0.0 | 13 | 14 | 6 | 5 |
| book:2Cor | A_auto | 0 | 0 | 45 | 0 | 45 | — | — | 0 | 0 | 0 | 0 |
| book:2Cor | B_review | 14 | 8 | 31 | 22 | 45 | 0.6363636363636364 | 0.4615411118288446 | 23 | 23 | 4 | 1 |
| book:2Cor | C_unresolved | 0 | 2 | 45 | 2 | 45 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| book:2John | A_auto | 0 | 0 | 86 | 0 | 86 | — | — | 0 | 0 | 0 | 0 |
| book:2John | B_review | 35 | 18 | 51 | 53 | 86 | 0.660377358490566 | 0.5479285581201709 | 56 | 58 | 4 | 1 |
| book:2John | C_unresolved | 3 | 1 | 83 | 4 | 86 | 0.75 | 0.3561680085985064 | 4 | 4 | 3 | 3 |
| book:2Kgs | A_auto | 0 | 0 | 146 | 0 | 146 | — | — | 0 | 0 | 0 | 0 |
| book:2Kgs | B_review | 34 | 16 | 112 | 50 | 146 | 0.68 | 0.5646681873987485 | 57 | 58 | 5 | 1 |
| book:2Kgs | C_unresolved | 2 | 4 | 144 | 6 | 146 | 0.3333333333333333 | 0.1172760941022896 | 7 | 7 | 3 | 3 |
| book:2Pet | A_auto | 0 | 0 | 139 | 0 | 139 | — | — | 0 | 0 | 0 | 0 |
| book:2Pet | B_review | 29 | 24 | 110 | 53 | 139 | 0.5471698113207547 | 0.43515487381827395 | 55 | 57 | 8 | 1 |
| book:2Pet | C_unresolved | 6 | 14 | 133 | 20 | 139 | 0.3 | 0.16385941535194348 | 29 | 35 | 7 | 5 |
| book:2Sam | A_auto | 0 | 0 | 133 | 0 | 133 | — | — | 0 | 0 | 0 | 0 |
| book:2Sam | B_review | 28 | 23 | 105 | 51 | 133 | 0.5490196078431373 | 0.43483896052204846 | 53 | 54 | 4 | 2 |
| book:2Sam | C_unresolved | 2 | 6 | 131 | 8 | 133 | 0.25 | 0.08651484419906225 | 11 | 11 | 4 | 2 |
| book:2Thess | A_auto | 0 | 0 | 72 | 0 | 72 | — | — | 0 | 0 | 0 | 0 |
| book:2Thess | B_review | 14 | 17 | 58 | 31 | 72 | 0.45161290322580644 | 0.31444855707060776 | 32 | 33 | 4 | 1 |
| book:2Thess | C_unresolved | 4 | 7 | 68 | 11 | 72 | 0.36363636363636365 | 0.1751367285207303 | 13 | 14 | 4 | 4 |
| book:2Tim | A_auto | 0 | 0 | 88 | 0 | 88 | — | — | 0 | 0 | 0 | 0 |
| book:2Tim | B_review | 30 | 11 | 58 | 41 | 88 | 0.7317073170731707 | 0.6061962950059531 | 42 | 41 | 5 | 2 |
| book:2Tim | C_unresolved | 2 | 7 | 86 | 9 | 88 | 0.2222222222222222 | 0.07649473755439642 | 13 | 14 | 4 | 2 |
| book:3John | A_auto | 0 | 0 | 69 | 0 | 69 | — | — | 0 | 0 | 0 | 0 |
| book:3John | B_review | 19 | 11 | 50 | 30 | 69 | 0.6333333333333333 | 0.48326356968012874 | 32 | 32 | 5 | 1 |
| book:3John | C_unresolved | 3 | 4 | 66 | 7 | 69 | 0.42857142857142855 | 0.18644319036395607 | 13 | 13 | 4 | 3 |
| book:Acts | A_auto | 0 | 0 | 257 | 0 | 257 | — | — | 0 | 0 | 0 | 0 |
| book:Acts | B_review | 71 | 38 | 186 | 109 | 257 | 0.6513761467889908 | 0.5734566953644078 | 114 | 117 | 14 | 1 |
| book:Acts | C_unresolved | 10 | 28 | 247 | 38 | 257 | 0.2631578947368421 | 0.16428751834910818 | 48 | 54 | 14 | 7 |
| book:Amos | A_auto | 0 | 0 | 79 | 0 | 79 | — | — | 0 | 0 | 0 | 0 |
| book:Amos | B_review | 16 | 13 | 63 | 29 | 79 | 0.5517241379310345 | 0.401967487034627 | 31 | 30 | 4 | 3 |
| book:Amos | C_unresolved | 1 | 8 | 78 | 9 | 79 | 0.1111111111111111 | 0.025191472713156977 | 12 | 16 | 4 | 4 |
| book:Col | A_auto | 0 | 0 | 95 | 0 | 95 | — | — | 0 | 0 | 0 | 0 |
| book:Col | B_review | 30 | 10 | 65 | 40 | 95 | 0.75 | 0.6240270595401831 | 43 | 43 | 7 | 1 |
| book:Col | C_unresolved | 2 | 8 | 93 | 10 | 95 | 0.2 | 0.06855798773753206 | 15 | 14 | 5 | 4 |
| book:Dan | A_auto | 0 | 0 | 162 | 0 | 162 | — | — | 0 | 0 | 0 | 0 |
| book:Dan | B_review | 25 | 16 | 137 | 41 | 162 | 0.6097560975609756 | 0.48140347697882474 | 42 | 44 | 7 | 2 |
| book:Dan | C_unresolved | 3 | 11 | 159 | 14 | 162 | 0.21428571428571427 | 0.08906777124970816 | 20 | 25 | 7 | 6 |
| book:Deut | A_auto | 0 | 0 | 280 | 0 | 280 | — | — | 0 | 0 | 0 | 0 |
| book:Deut | B_review | 51 | 56 | 229 | 107 | 280 | 0.4766355140186916 | 0.39877489953443074 | 118 | 126 | 10 | 1 |
| book:Deut | C_unresolved | 0 | 9 | 280 | 9 | 280 | 0.0 | 0.0 | 12 | 16 | 6 | 5 |
| book:Eccl | A_auto | 0 | 0 | 138 | 0 | 138 | — | — | 0 | 0 | 0 | 0 |
| book:Eccl | B_review | 16 | 20 | 122 | 36 | 138 | 0.4444444444444444 | 0.31689530204252975 | 41 | 40 | 7 | 2 |
| book:Eccl | C_unresolved | 1 | 10 | 137 | 11 | 138 | 0.09090909090909091 | 0.02054953121924344 | 18 | 15 | 6 | 5 |
| book:Eph | A_auto | 0 | 0 | 106 | 0 | 106 | — | — | 0 | 0 | 0 | 0 |
| book:Eph | B_review | 38 | 19 | 68 | 57 | 106 | 0.6666666666666666 | 0.558481254814099 | 58 | 62 | 6 | 1 |
| book:Eph | C_unresolved | 4 | 6 | 102 | 10 | 106 | 0.4 | 0.1942269918768033 | 11 | 11 | 4 | 3 |
| book:Esth | A_auto | 0 | 0 | 143 | 0 | 143 | — | — | 0 | 0 | 0 | 0 |
| book:Esth | B_review | 21 | 27 | 122 | 48 | 143 | 0.4375 | 0.3261955350196099 | 54 | 54 | 4 | 1 |
| book:Esth | C_unresolved | 2 | 9 | 141 | 11 | 143 | 0.18181818181818182 | 0.06211525251916969 | 17 | 20 | 4 | 3 |
| book:Exod | A_auto | 0 | 0 | 103 | 0 | 103 | — | — | 0 | 0 | 0 | 0 |
| book:Exod | B_review | 29 | 19 | 74 | 48 | 103 | 0.6041666666666666 | 0.4855094429373269 | 52 | 52 | 5 | 1 |
| book:Exod | C_unresolved | 2 | 0 | 101 | 2 | 103 | 1.0 | 0.42503060900634637 | 2 | 2 | 1 | 1 |
| book:Ezek | A_auto | 0 | 0 | 147 | 0 | 147 | — | — | 0 | 0 | 0 | 0 |
| book:Ezek | B_review | 33 | 24 | 114 | 57 | 147 | 0.5789473684210527 | 0.4702078201392749 | 60 | 64 | 6 | 1 |
| book:Ezek | C_unresolved | 4 | 3 | 143 | 7 | 147 | 0.5714285714285714 | 0.28947709101359287 | 7 | 9 | 5 | 5 |
| book:Ezra | A_auto | 0 | 0 | 240 | 0 | 240 | — | — | 0 | 0 | 0 | 0 |
| book:Ezra | B_review | 28 | 32 | 212 | 60 | 240 | 0.4666666666666667 | 0.3644669308556731 | 62 | 67 | 8 | 1 |
| book:Ezra | C_unresolved | 2 | 19 | 238 | 21 | 240 | 0.09523809523809523 | 0.032033402063969534 | 32 | 33 | 6 | 4 |
| book:Gal | A_auto | 0 | 0 | 119 | 0 | 119 | — | — | 0 | 0 | 0 | 0 |
| book:Gal | B_review | 32 | 29 | 87 | 61 | 119 | 0.5245901639344263 | 0.420624557022952 | 61 | 65 | 8 | 1 |
| book:Gal | C_unresolved | 6 | 8 | 113 | 14 | 119 | 0.42857142857142855 | 0.24064970440458236 | 18 | 23 | 7 | 7 |
| book:Gen | A_auto | 0 | 0 | 155 | 0 | 155 | — | — | 0 | 0 | 0 | 0 |
| book:Gen | B_review | 23 | 35 | 132 | 58 | 155 | 0.39655172413793105 | 0.29778726885155166 | 64 | 66 | 7 | 3 |
| book:Gen | C_unresolved | 2 | 6 | 153 | 8 | 155 | 0.25 | 0.08651484419906225 | 11 | 14 | 5 | 4 |
| book:Hab | A_auto | 0 | 0 | 99 | 0 | 99 | — | — | 0 | 0 | 0 | 0 |
| book:Hab | B_review | 14 | 10 | 85 | 24 | 99 | 0.5833333333333334 | 0.41774350354288503 | 26 | 29 | 5 | 5 |
| book:Hab | C_unresolved | 1 | 5 | 98 | 6 | 99 | 0.16666666666666666 | 0.03810557007934284 | 7 | 10 | 4 | 4 |
| book:Hag | A_auto | 0 | 0 | 141 | 0 | 141 | — | — | 0 | 0 | 0 | 0 |
| book:Hag | B_review | 20 | 24 | 121 | 44 | 141 | 0.45454545454545453 | 0.3373070740505237 | 49 | 51 | 5 | 1 |
| book:Hag | C_unresolved | 0 | 6 | 141 | 6 | 141 | 0.0 | 0.0 | 12 | 12 | 4 | 3 |
| book:Heb | A_auto | 0 | 0 | 109 | 0 | 109 | — | — | 0 | 0 | 0 | 0 |
| book:Heb | B_review | 27 | 20 | 82 | 47 | 109 | 0.574468085106383 | 0.4549918214284115 | 50 | 51 | 6 | 1 |
| book:Heb | C_unresolved | 0 | 12 | 109 | 12 | 109 | 0.0 | 0.0 | 19 | 21 | 5 | 5 |
| book:Hos | A_auto | 0 | 0 | 129 | 0 | 129 | — | — | 0 | 0 | 0 | 0 |
| book:Hos | B_review | 24 | 21 | 105 | 45 | 129 | 0.5333333333333333 | 0.41261987422574065 | 45 | 46 | 7 | 2 |
| book:Hos | C_unresolved | 0 | 7 | 129 | 7 | 129 | 0.0 | 0.0 | 8 | 12 | 4 | 4 |
| book:Isa | A_auto | 0 | 0 | 127 | 0 | 127 | — | — | 0 | 0 | 0 | 0 |
| book:Isa | B_review | 24 | 15 | 103 | 39 | 127 | 0.6153846153846154 | 0.48376040809425297 | 39 | 41 | 6 | 2 |
| book:Isa | C_unresolved | 2 | 7 | 125 | 9 | 127 | 0.2222222222222222 | 0.07649473755439642 | 13 | 16 | 4 | 4 |
| book:Jas | A_auto | 0 | 0 | 147 | 0 | 147 | — | — | 0 | 0 | 0 | 0 |
| book:Jas | B_review | 45 | 18 | 102 | 63 | 147 | 0.7142857142857143 | 0.6133682363579077 | 64 | 67 | 9 | 1 |
| book:Jas | C_unresolved | 4 | 16 | 143 | 20 | 147 | 0.2 | 0.09311801658121098 | 27 | 36 | 9 | 9 |
| book:Jer | A_auto | 0 | 0 | 82 | 0 | 82 | — | — | 0 | 0 | 0 | 0 |
| book:Jer | B_review | 13 | 15 | 69 | 28 | 82 | 0.4642857142857143 | 0.3193594682143511 | 30 | 32 | 3 | 2 |
| book:Jer | C_unresolved | 0 | 2 | 82 | 2 | 82 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| book:Job | A_auto | 0 | 0 | 82 | 0 | 82 | — | — | 0 | 0 | 0 | 0 |
| book:Job | B_review | 12 | 13 | 70 | 25 | 82 | 0.48 | 0.32581809779808024 | 25 | 29 | 7 | 5 |
| book:Job | C_unresolved | 1 | 6 | 81 | 7 | 82 | 0.14285714285714285 | 0.03254380205478664 | 10 | 15 | 4 | 4 |
| book:Joel | A_auto | 0 | 0 | 228 | 0 | 228 | — | — | 0 | 0 | 0 | 0 |
| book:Joel | B_review | 46 | 35 | 182 | 81 | 228 | 0.5679012345679012 | 0.47662043040443397 | 85 | 86 | 10 | 2 |
| book:Joel | C_unresolved | 1 | 11 | 227 | 12 | 228 | 0.08333333333333333 | 0.018816049516361844 | 18 | 17 | 9 | 8 |
| book:John | A_auto | 0 | 0 | 102 | 0 | 102 | — | — | 0 | 0 | 0 | 0 |
| book:John | B_review | 38 | 19 | 64 | 57 | 102 | 0.6666666666666666 | 0.558481254814099 | 61 | 60 | 7 | 2 |
| book:John | C_unresolved | 2 | 5 | 100 | 7 | 102 | 0.2857142857142857 | 0.09956584356228707 | 9 | 11 | 4 | 4 |
| book:Jonah | A_auto | 0 | 0 | 114 | 0 | 114 | — | — | 0 | 0 | 0 | 0 |
| book:Jonah | B_review | 23 | 14 | 91 | 37 | 114 | 0.6216216216216216 | 0.48646503369246774 | 39 | 41 | 5 | 3 |
| book:Jonah | C_unresolved | 2 | 7 | 112 | 9 | 114 | 0.2222222222222222 | 0.07649473755439642 | 13 | 20 | 4 | 3 |
| book:Josh | A_auto | 0 | 0 | 92 | 0 | 92 | — | — | 0 | 0 | 0 | 0 |
| book:Josh | B_review | 29 | 15 | 63 | 44 | 92 | 0.6590909090909091 | 0.5354168360627467 | 47 | 51 | 5 | 1 |
| book:Josh | C_unresolved | 1 | 5 | 91 | 6 | 92 | 0.16666666666666666 | 0.03810557007934284 | 9 | 6 | 2 | 2 |
| book:Jude | A_auto | 0 | 0 | 101 | 0 | 101 | — | — | 0 | 0 | 0 | 0 |
| book:Jude | B_review | 26 | 21 | 75 | 47 | 101 | 0.5531914893617021 | 0.43426933460614886 | 50 | 51 | 5 | 2 |
| book:Jude | C_unresolved | 4 | 9 | 97 | 13 | 101 | 0.3076923076923077 | 0.14641538530333972 | 15 | 20 | 5 | 3 |
| book:Judg | A_auto | 0 | 0 | 94 | 0 | 94 | — | — | 0 | 0 | 0 | 0 |
| book:Judg | B_review | 15 | 17 | 79 | 32 | 94 | 0.46875 | 0.33183380229313175 | 33 | 34 | 3 | 1 |
| book:Judg | C_unresolved | 0 | 6 | 94 | 6 | 94 | 0.0 | 0.0 | 10 | 14 | 3 | 3 |
| book:Lam | A_auto | 0 | 0 | 72 | 0 | 72 | — | — | 0 | 0 | 0 | 0 |
| book:Lam | B_review | 8 | 14 | 64 | 22 | 72 | 0.36363636363636365 | 0.2186806375734043 | 22 | 23 | 5 | 3 |
| book:Lam | C_unresolved | 0 | 4 | 72 | 4 | 72 | 0.0 | 0.0 | 7 | 10 | 2 | 1 |
| book:Lev | A_auto | 0 | 0 | 122 | 0 | 122 | — | — | 0 | 0 | 0 | 0 |
| book:Lev | B_review | 22 | 23 | 100 | 45 | 122 | 0.4888888888888889 | 0.3704738999421948 | 51 | 53 | 6 | 1 |
| book:Lev | C_unresolved | 1 | 7 | 121 | 8 | 122 | 0.125 | 0.028399323737810202 | 14 | 18 | 5 | 5 |
| book:Luke | A_auto | 0 | 0 | 130 | 0 | 130 | — | — | 0 | 0 | 0 | 0 |
| book:Luke | B_review | 40 | 20 | 90 | 60 | 130 | 0.6666666666666666 | 0.561292592786729 | 63 | 63 | 9 | 1 |
| book:Luke | C_unresolved | 4 | 8 | 126 | 12 | 130 | 0.3333333333333333 | 0.15948534492584052 | 20 | 24 | 8 | 6 |
| book:Mal | A_auto | 0 | 0 | 151 | 0 | 151 | — | — | 0 | 0 | 0 | 0 |
| book:Mal | B_review | 33 | 18 | 118 | 51 | 151 | 0.6470588235294118 | 0.53213411538532 | 54 | 54 | 6 | 1 |
| book:Mal | C_unresolved | 0 | 9 | 151 | 9 | 151 | 0.0 | 0.0 | 19 | 20 | 3 | 3 |
| book:Mark | A_auto | 0 | 0 | 40 | 0 | 40 | — | — | 0 | 0 | 0 | 0 |
| book:Mark | B_review | 13 | 3 | 27 | 16 | 40 | 0.8125 | 0.6121302575521457 | 19 | 18 | 3 | 3 |
| book:Mark | C_unresolved | 1 | 4 | 39 | 5 | 40 | 0.2 | 0.04596245388060396 | 8 | 6 | 2 | 2 |
| book:Mat | A_auto | 0 | 0 | 204 | 0 | 204 | — | — | 0 | 0 | 0 | 0 |
| book:Mat | B_review | 62 | 26 | 142 | 88 | 204 | 0.7045454545454546 | 0.6194113819406312 | 93 | 101 | 11 | 1 |
| book:Mat | C_unresolved | 4 | 13 | 200 | 17 | 204 | 0.23529411764705882 | 0.1103148536765237 | 27 | 25 | 8 | 4 |
| book:Mic | A_auto | 0 | 0 | 232 | 0 | 232 | — | — | 0 | 0 | 0 | 0 |
| book:Mic | B_review | 53 | 28 | 179 | 81 | 232 | 0.654320987654321 | 0.5636844899255222 | 84 | 87 | 11 | 1 |
| book:Mic | C_unresolved | 1 | 17 | 231 | 18 | 232 | 0.05555555555555555 | 0.012493195762984893 | 25 | 34 | 8 | 3 |
| book:Nah | A_auto | 0 | 0 | 109 | 0 | 109 | — | — | 0 | 0 | 0 | 0 |
| book:Nah | B_review | 16 | 12 | 93 | 28 | 109 | 0.5714285714285714 | 0.4181035538853205 | 30 | 33 | 6 | 3 |
| book:Nah | C_unresolved | 2 | 9 | 107 | 11 | 109 | 0.18181818181818182 | 0.06211525251916969 | 12 | 17 | 6 | 6 |
| book:Neh | A_auto | 0 | 0 | 76 | 0 | 76 | — | — | 0 | 0 | 0 | 0 |
| book:Neh | B_review | 26 | 9 | 50 | 35 | 76 | 0.7428571428571429 | 0.6070661495747554 | 38 | 40 | 7 | 4 |
| book:Neh | C_unresolved | 0 | 1 | 76 | 1 | 76 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| book:Num | A_auto | 0 | 0 | 67 | 0 | 67 | — | — | 0 | 0 | 0 | 0 |
| book:Num | B_review | 18 | 13 | 49 | 31 | 67 | 0.5806451612903226 | 0.4342169483345065 | 35 | 33 | 4 | 4 |
| book:Num | C_unresolved | 1 | 4 | 66 | 5 | 67 | 0.2 | 0.04596245388060396 | 7 | 6 | 3 | 3 |
| book:Obad | A_auto | 0 | 0 | 173 | 0 | 173 | — | — | 0 | 0 | 0 | 0 |
| book:Obad | B_review | 31 | 19 | 142 | 50 | 173 | 0.62 | 0.5036944596784989 | 56 | 62 | 7 | 2 |
| book:Obad | C_unresolved | 1 | 13 | 172 | 14 | 173 | 0.07142857142857142 | 0.016099895800737347 | 20 | 25 | 6 | 5 |
| book:Phil | A_auto | 0 | 0 | 80 | 0 | 80 | — | — | 0 | 0 | 0 | 0 |
| book:Phil | B_review | 16 | 13 | 64 | 29 | 80 | 0.5517241379310345 | 0.401967487034627 | 31 | 33 | 4 | 1 |
| book:Phil | C_unresolved | 2 | 11 | 78 | 13 | 80 | 0.15384615384615385 | 0.052290440446758214 | 17 | 17 | 4 | 2 |
| book:Phlm | A_auto | 0 | 0 | 129 | 0 | 129 | — | — | 0 | 0 | 0 | 0 |
| book:Phlm | B_review | 48 | 18 | 81 | 66 | 129 | 0.7272727272727273 | 0.6294929693512521 | 71 | 71 | 9 | 1 |
| book:Phlm | C_unresolved | 9 | 6 | 120 | 15 | 129 | 0.6 | 0.3926063693439542 | 16 | 18 | 7 | 7 |
| book:Prov | A_auto | 0 | 0 | 99 | 0 | 99 | — | — | 0 | 0 | 0 | 0 |
| book:Prov | B_review | 21 | 20 | 78 | 41 | 99 | 0.5121951219512195 | 0.3870724444597019 | 44 | 47 | 8 | 2 |
| book:Prov | C_unresolved | 1 | 6 | 98 | 7 | 99 | 0.14285714285714285 | 0.03254380205478664 | 7 | 10 | 5 | 3 |
| book:Ps | A_auto | 0 | 0 | 378 | 0 | 378 | — | — | 0 | 0 | 0 | 0 |
| book:Ps | B_review | 29 | 36 | 349 | 65 | 378 | 0.4461538461538462 | 0.34891301331067903 | 70 | 71 | 18 | 7 |
| book:Ps | C_unresolved | 2 | 27 | 376 | 29 | 378 | 0.06896551724137931 | 0.0230907224042537 | 42 | 57 | 16 | 6 |
| book:Rev | A_auto | 0 | 0 | 186 | 0 | 186 | — | — | 0 | 0 | 0 | 0 |
| book:Rev | B_review | 58 | 28 | 128 | 86 | 186 | 0.6744186046511628 | 0.5870896777832659 | 91 | 89 | 7 | 1 |
| book:Rev | C_unresolved | 9 | 9 | 177 | 18 | 186 | 0.5 | 0.3192601388872444 | 25 | 25 | 7 | 5 |
| book:Rom | A_auto | 0 | 0 | 119 | 0 | 119 | — | — | 0 | 0 | 0 | 0 |
| book:Rom | B_review | 30 | 25 | 89 | 55 | 119 | 0.5454545454545454 | 0.4354855351623055 | 59 | 66 | 7 | 1 |
| book:Rom | C_unresolved | 3 | 2 | 116 | 5 | 119 | 0.6 | 0.2724831718661928 | 7 | 5 | 4 | 4 |
| book:Ruth | A_auto | 0 | 0 | 98 | 0 | 98 | — | — | 0 | 0 | 0 | 0 |
| book:Ruth | B_review | 16 | 17 | 82 | 33 | 98 | 0.48484848484848486 | 0.3484198152256923 | 33 | 34 | 4 | 1 |
| book:Ruth | C_unresolved | 4 | 5 | 94 | 9 | 98 | 0.4444444444444444 | 0.21804705127977433 | 11 | 12 | 4 | 3 |
| book:Song | A_auto | 0 | 0 | 83 | 0 | 83 | — | — | 0 | 0 | 0 | 0 |
| book:Song | B_review | 9 | 13 | 74 | 22 | 83 | 0.4090909090909091 | 0.2560374350265464 | 24 | 26 | 4 | 3 |
| book:Song | C_unresolved | 3 | 5 | 80 | 8 | 83 | 0.375 | 0.16117233776067347 | 9 | 12 | 3 | 3 |
| book:Titus | A_auto | 0 | 0 | 72 | 0 | 72 | — | — | 0 | 0 | 0 | 0 |
| book:Titus | B_review | 21 | 9 | 51 | 30 | 72 | 0.7 | 0.5506175038264008 | 30 | 30 | 6 | 1 |
| book:Titus | C_unresolved | 5 | 4 | 67 | 9 | 72 | 0.5555555555555556 | 0.30347666024424585 | 13 | 15 | 5 | 4 |
| book:Zech | A_auto | 0 | 0 | 105 | 0 | 105 | — | — | 0 | 0 | 0 | 0 |
| book:Zech | B_review | 29 | 18 | 76 | 47 | 105 | 0.6170212765957447 | 0.4970600701885879 | 48 | 49 | 4 | 1 |
| book:Zech | C_unresolved | 0 | 4 | 105 | 4 | 105 | 0.0 | 0.0 | 6 | 6 | 3 | 2 |
| book:Zeph | A_auto | 0 | 0 | 144 | 0 | 144 | — | — | 0 | 0 | 0 | 0 |
| book:Zeph | B_review | 24 | 14 | 120 | 38 | 144 | 0.631578947368421 | 0.49816459978363886 | 40 | 41 | 6 | 1 |
| book:Zeph | C_unresolved | 4 | 10 | 140 | 14 | 144 | 0.2857142857142857 | 0.13533400388166497 | 18 | 19 | 5 | 3 |
| evidence:lexical_description | A_auto | 0 | 0 | 167 | 0 | 167 | — | — | 0 | 0 | 0 | 0 |
| evidence:lexical_description | B_review | 161 | 42 | 6 | 203 | 167 | 0.7931034482758621 | 0.7426323012101972 | 203 | 203 | 123 | 43 |
| evidence:lexical_description | C_unresolved | 3 | 0 | 164 | 3 | 167 | 1.0 | 0.5258044258424873 | 3 | 3 | 3 | 3 |
| evidence:missing | A_auto | 0 | 0 | 6150 | 0 | 6150 | — | — | 0 | 0 | 0 | 0 |
| evidence:missing | B_review | 0 | 0 | 6150 | 0 | 6150 | — | — | 0 | 0 | 0 | 0 |
| evidence:missing | C_unresolved | 0 | 0 | 6150 | 0 | 6150 | — | — | 0 | 0 | 0 | 0 |
| evidence:multilingual_contextual | A_auto | 0 | 0 | 939 | 0 | 939 | — | — | 0 | 0 | 0 | 0 |
| evidence:multilingual_contextual | B_review | 776 | 774 | 163 | 1550 | 939 | 0.5006451612903225 | 0.47977260025233703 | 1626 | 1746 | 406 | 27 |
| evidence:multilingual_contextual | C_unresolved | 128 | 505 | 811 | 633 | 939 | 0.20221169036334913 | 0.1772457251903011 | 899 | 1033 | 314 | 62 |
| evidence:parallel_translation | A_auto | 0 | 0 | 1532 | 0 | 1532 | — | — | 0 | 0 | 0 | 0 |
| evidence:parallel_translation | B_review | 1220 | 535 | 312 | 1755 | 1532 | 0.6951566951566952 | 0.6767931317743188 | 1883 | 1860 | 410 | 18 |
| evidence:parallel_translation | C_unresolved | 38 | 16 | 1494 | 54 | 1532 | 0.7037037037037037 | 0.5937714175704719 | 56 | 55 | 47 | 35 |
| evidence:transliteration | A_auto | 0 | 0 | 127 | 0 | 127 | — | — | 0 | 0 | 0 | 0 |
| evidence:transliteration | B_review | 119 | 11 | 8 | 130 | 127 | 0.9153846153846154 | 0.8662852740822247 | 130 | 130 | 72 | 39 |
| evidence:transliteration | C_unresolved | 1 | 0 | 126 | 1 | 127 | 1.0 | 0.2698659487840541 | 1 | 1 | 1 | 1 |
| genre:acts_narrative | A_auto | 0 | 0 | 257 | 0 | 257 | — | — | 0 | 0 | 0 | 0 |
| genre:acts_narrative | B_review | 71 | 38 | 186 | 109 | 257 | 0.6513761467889908 | 0.5734566953644078 | 114 | 117 | 14 | 1 |
| genre:acts_narrative | C_unresolved | 10 | 28 | 247 | 38 | 257 | 0.2631578947368421 | 0.16428751834910818 | 48 | 54 | 14 | 7 |
| genre:apocalyptic | A_auto | 0 | 0 | 186 | 0 | 186 | — | — | 0 | 0 | 0 | 0 |
| genre:apocalyptic | B_review | 58 | 28 | 128 | 86 | 186 | 0.6744186046511628 | 0.5870896777832659 | 91 | 89 | 7 | 1 |
| genre:apocalyptic | C_unresolved | 9 | 9 | 177 | 18 | 186 | 0.5 | 0.3192601388872444 | 25 | 25 | 7 | 5 |
| genre:epistle | A_auto | 0 | 0 | 2151 | 0 | 2151 | — | — | 0 | 0 | 0 | 0 |
| genre:epistle | B_review | 633 | 360 | 1518 | 993 | 2151 | 0.6374622356495468 | 0.6120268275383912 | 1038 | 1069 | 132 | 2 |
| genre:epistle | C_unresolved | 75 | 152 | 2076 | 227 | 2151 | 0.3303964757709251 | 0.2813082975377202 | 307 | 337 | 104 | 26 |
| genre:gospel_narrative | A_auto | 0 | 0 | 476 | 0 | 476 | — | — | 0 | 0 | 0 | 0 |
| genre:gospel_narrative | B_review | 153 | 68 | 323 | 221 | 476 | 0.6923076923076923 | 0.6391715243480973 | 236 | 242 | 30 | 1 |
| genre:gospel_narrative | C_unresolved | 11 | 30 | 465 | 41 | 476 | 0.2682926829268293 | 0.1714688325741911 | 64 | 66 | 22 | 9 |
| genre:historical_prose | A_auto | 0 | 0 | 1670 | 0 | 1670 | — | — | 0 | 0 | 0 | 0 |
| genre:historical_prose | B_review | 344 | 283 | 1326 | 627 | 1670 | 0.5486443381180224 | 0.515816211320723 | 677 | 684 | 66 | 2 |
| genre:historical_prose | C_unresolved | 20 | 89 | 1650 | 109 | 1670 | 0.1834862385321101 | 0.13042806552398534 | 154 | 166 | 46 | 7 |
| genre:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| genre:poetry_wisdom | A_auto | 0 | 0 | 780 | 0 | 780 | — | — | 0 | 0 | 0 | 0 |
| genre:poetry_wisdom | B_review | 87 | 102 | 693 | 189 | 780 | 0.4603174603174603 | 0.40166311142749983 | 204 | 213 | 44 | 6 |
| genre:poetry_wisdom | C_unresolved | 8 | 54 | 772 | 62 | 780 | 0.12903225806451613 | 0.07426068242789266 | 86 | 109 | 34 | 9 |
| genre:prophetic | A_auto | 0 | 0 | 2294 | 0 | 2294 | — | — | 0 | 0 | 0 | 0 |
| genre:prophetic | B_review | 432 | 310 | 1862 | 742 | 2294 | 0.5822102425876011 | 0.5521828848002076 | 780 | 813 | 103 | 5 |
| genre:prophetic | C_unresolved | 22 | 133 | 2272 | 155 | 2294 | 0.14193548387096774 | 0.10195761344818137 | 220 | 270 | 79 | 30 |
| genre:torah_prose_law | A_auto | 0 | 0 | 727 | 0 | 727 | — | — | 0 | 0 | 0 | 0 |
| genre:torah_prose_law | B_review | 143 | 146 | 584 | 289 | 727 | 0.49480968858131485 | 0.4467072245707152 | 320 | 330 | 32 | 1 |
| genre:torah_prose_law | C_unresolved | 6 | 26 | 721 | 32 | 727 | 0.1875 | 0.10019349618866828 | 46 | 56 | 20 | 11 |
| relation:grouped_expression | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| relation:grouped_expression | B_review | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| relation:grouped_expression | C_unresolved | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_many | A_auto | 0 | 0 | 96 | 0 | 96 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_many | B_review | 0 | 86 | 96 | 86 | 96 | 0.0 | 0.0 | 183 | 187 | 72 | 33 |
| relation:many_to_many | C_unresolved | 0 | 149 | 96 | 149 | 96 | 0.0 | 0.0 | 342 | 393 | 124 | 34 |
| relation:many_to_one | A_auto | 0 | 0 | 264 | 0 | 264 | — | — | 0 | 0 | 0 | 0 |
| relation:many_to_one | B_review | 0 | 102 | 264 | 102 | 264 | 0.0 | 0.0 | 209 | 102 | 90 | 44 |
| relation:many_to_one | C_unresolved | 0 | 68 | 264 | 68 | 264 | 0.0 | 0.0 | 143 | 68 | 64 | 37 |
| relation:one_to_many | A_auto | 0 | 0 | 676 | 0 | 676 | — | — | 0 | 0 | 0 | 0 |
| relation:one_to_many | B_review | 9 | 179 | 667 | 188 | 676 | 0.047872340425531915 | 0.028060811531244963 | 188 | 388 | 151 | 30 |
| relation:one_to_many | C_unresolved | 3 | 136 | 673 | 139 | 676 | 0.02158273381294964 | 0.008657678550151543 | 139 | 296 | 119 | 41 |
| relation:one_to_one | A_auto | 0 | 0 | 5594 | 0 | 5594 | — | — | 0 | 0 | 0 | 0 |
| relation:one_to_one | B_review | 1912 | 968 | 3682 | 2880 | 5594 | 0.6638888888888889 | 0.6492626646673758 | 2880 | 2880 | 428 | 9 |
| relation:one_to_one | C_unresolved | 158 | 168 | 5436 | 326 | 5594 | 0.48466257668711654 | 0.43944782630503354 | 326 | 326 | 214 | 111 |
| relation:original_omitted | A_auto | 0 | 0 | 1538 | 0 | 1538 | — | — | 0 | 0 | 0 | 0 |
| relation:original_omitted | B_review | 0 | 0 | 1538 | 0 | 1538 | — | — | 0 | 0 | 0 | 0 |
| relation:original_omitted | C_unresolved | 0 | 0 | 1538 | 0 | 1538 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:textual_alternative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | A_auto | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | B_review | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| relation:translation_addition | C_unresolved | 0 | 0 | 368 | 0 | 368 | — | — | 0 | 0 | 0 | 0 |
| reviewed:addition | A_auto | 0 | 0 | 331 | 0 | 331 | — | — | 0 | 0 | 0 | 0 |
| reviewed:addition | B_review | 1 | 51 | 330 | 52 | 331 | 0.019230769230769232 | 0.004301992430414864 | 56 | 77 | 43 | 14 |
| reviewed:addition | C_unresolved | 0 | 41 | 331 | 41 | 331 | 0.0 | 0.0 | 65 | 102 | 38 | 18 |
| reviewed:adjectival_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:adjectival_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:age_idiom | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:age_idiom | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:age_idiom | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:alignment_counterexample | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:alignment_counterexample | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:alignment_counterexample | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_future | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_future | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_future | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_tense | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:analytic_tense | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:analytic_tense | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:anaphoric_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:anaphoric_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_genitive_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_genitive_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:article_genitive_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_lexical_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_lexical_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_lexical_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_noun_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_noun_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:article_noun_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:aspectual_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:aspectual_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:aspectual_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:blind_semantic_review | A_auto | 0 | 0 | 336 | 0 | 336 | — | — | 0 | 0 | 0 | 0 |
| reviewed:blind_semantic_review | B_review | 62 | 71 | 274 | 133 | 336 | 0.46616541353383456 | 0.39639957868754616 | 149 | 151 | 17 | 3 |
| reviewed:blind_semantic_review | C_unresolved | 3 | 17 | 333 | 20 | 336 | 0.15 | 0.06158241047736831 | 31 | 37 | 12 | 9 |
| reviewed:body_part_change | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:body_part_change | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:body_part_change | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_government | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_government | B_review | 0 | 2 | 3 | 2 | 3 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:case_government | C_unresolved | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:case_realization | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_realization | B_review | 0 | 5 | 5 | 5 | 5 | 0.0 | 0.0 | 5 | 5 | 2 | 2 |
| reviewed:case_realization | C_unresolved | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:case_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:case_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causal_connective | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causal_connective | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:causal_connective | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:causative_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_relation | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_restructuring | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:clause_restructuring | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:clause_restructuring | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:cohortative_motion_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_motion_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_motion_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_particle_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_particle_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:cohortative_particle_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_clause | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_clause | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_clause | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparative_frame | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparison | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:comparison | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:comparison | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compositional_alignment | A_auto | 0 | 0 | 12 | 0 | 12 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compositional_alignment | B_review | 0 | 6 | 12 | 6 | 12 | 0.0 | 0.0 | 6 | 7 | 4 | 4 |
| reviewed:compositional_alignment | C_unresolved | 0 | 3 | 12 | 3 | 12 | 0.0 | 0.0 | 4 | 4 | 3 | 3 |
| reviewed:compound | A_auto | 0 | 0 | 147 | 0 | 147 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound | B_review | 7 | 73 | 140 | 80 | 147 | 0.0875 | 0.04813564152266386 | 90 | 94 | 51 | 39 |
| reviewed:compound | C_unresolved | 0 | 37 | 147 | 37 | 147 | 0.0 | 6.466076323609322e-18 | 62 | 84 | 28 | 23 |
| reviewed:compound_numeral | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_numeral | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_numeral | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | B_review | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:compound_time | C_unresolved | 0 | 1 | 4 | 1 | 4 | 0.0 | 0.0 | 3 | 2 | 1 | 1 |
| reviewed:conditional_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:conditional_particle_repetition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_particle_repetition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:conditional_particle_repetition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_addressee_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_addressee_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_addressee_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_demonstrative_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_lexical_choice | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_lexical_choice | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:contextual_lexical_choice | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_location_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_location_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_location_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_possessor_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:contextual_private_speech_addition | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_adjectival_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_construction | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_construction | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_construction | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_expression | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_expression | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_expression | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_relative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_relative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:copular_relative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:correlative_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:correlative_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:correlative_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_copular_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_copular_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_copular_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_expansion | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:dative_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_possessive_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_possessive_group | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:dative_possessive_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:dative_pronominal_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:definiteness | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:definiteness | B_review | 0 | 2 | 1 | 2 | 1 | 0.0 | 0.0 | 2 | 3 | 1 | 1 |
| reviewed:definiteness | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_expression | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_expression | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_expression | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_subject | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_subject | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_subject | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_time | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_time | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:deictic_time | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivation | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivation | B_review | 2 | 0 | 4 | 2 | 6 | 1.0 | 0.42503060900634637 | 2 | 2 | 2 | 2 |
| reviewed:derivation | C_unresolved | 0 | 3 | 6 | 3 | 6 | 0.0 | 0.0 | 8 | 4 | 2 | 2 |
| reviewed:derivational_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivational_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:derivational_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_lexical | A_auto | 0 | 0 | 61 | 0 | 61 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_lexical | B_review | 16 | 9 | 45 | 25 | 61 | 0.64 | 0.47570886420669156 | 26 | 28 | 13 | 8 |
| reviewed:direct_lexical | C_unresolved | 0 | 8 | 61 | 8 | 61 | 0.0 | 0.0 | 11 | 20 | 7 | 6 |
| reviewed:direct_object_marker_not_overt | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_object_marker_not_overt | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:direct_object_marker_not_overt | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_place | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_place | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_place | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_pr_pronominal | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_suffix | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:directional_suffix | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:directional_suffix | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discontinuous_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discontinuous_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discontinuous_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_particle_omission | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:discourse_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:distributive | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:duration_phrase | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:duration_phrase | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:duration_phrase | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:elliptical_predicate_explication | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:elliptical_predicate_explication | B_review | 0 | 2 | 4 | 2 | 4 | 0.0 | 0.0 | 2 | 3 | 1 | 1 |
| reviewed:elliptical_predicate_explication | C_unresolved | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:emphasis | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:emphasis | B_review | 1 | 0 | 2 | 1 | 3 | 1.0 | 0.2698659487840541 | 1 | 1 | 1 | 1 |
| reviewed:emphasis | C_unresolved | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| reviewed:existential_restructuring | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_restructuring | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_restructuring | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:existential_to_indefinite | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_object | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_original_null | A_auto | 0 | 0 | 67 | 0 | 67 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_original_null | B_review | 0 | 15 | 67 | 15 | 67 | 0.0 | 1.175715490783574e-17 | 18 | 16 | 13 | 13 |
| reviewed:explicit_original_null | C_unresolved | 0 | 7 | 67 | 7 | 67 | 0.0 | 0.0 | 15 | 18 | 6 | 5 |
| reviewed:explicit_source_null | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_source_null | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_source_null | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_subject | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_subject | B_review | 0 | 1 | 3 | 1 | 3 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:explicit_subject | C_unresolved | 0 | 2 | 3 | 2 | 3 | 0.0 | 0.0 | 2 | 3 | 2 | 2 |
| reviewed:explicit_target_function | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_function | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_function | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_null | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicit_target_null | B_review | 0 | 4 | 6 | 4 | 6 | 0.0 | 0.0 | 4 | 6 | 3 | 3 |
| reviewed:explicit_target_null | C_unresolved | 0 | 1 | 6 | 1 | 6 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:explicitation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicitation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:explicitation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:fawn_deer_lexical_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:fawn_deer_lexical_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:fawn_deer_lexical_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:frequent_lemma | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:function_token | A_auto | 0 | 0 | 9 | 0 | 9 | — | — | 0 | 0 | 0 | 0 |
| reviewed:function_token | B_review | 0 | 5 | 9 | 5 | 9 | 0.0 | 0.0 | 5 | 7 | 4 | 4 |
| reviewed:function_token | C_unresolved | 0 | 0 | 9 | 0 | 9 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_lexical_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:genitive_lexical_expansion | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:genitive_lexical_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:gentilic_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:gentilic_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:gentilic_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:government_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_expansion | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_expansion | B_review | 0 | 3 | 3 | 3 | 3 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:grammatical_expansion | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function | B_review | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function_not_overt | A_auto | 0 | 0 | 30 | 0 | 30 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grammatical_function_not_overt | B_review | 0 | 1 | 30 | 1 | 30 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:grammatical_function_not_overt | C_unresolved | 0 | 6 | 30 | 6 | 30 | 0.0 | 0.0 | 13 | 14 | 6 | 5 |
| reviewed:grouped_expression | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:grouped_expression | B_review | 0 | 2 | 5 | 2 | 5 | 0.0 | 0.0 | 2 | 2 | 2 | 2 |
| reviewed:grouped_expression | C_unresolved | 0 | 2 | 5 | 2 | 5 | 0.0 | 0.0 | 2 | 3 | 2 | 2 |
| reviewed:idiom | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiom | B_review | 1 | 4 | 5 | 5 | 6 | 0.2 | 0.04596245388060396 | 6 | 6 | 2 | 2 |
| reviewed:idiom | C_unresolved | 0 | 1 | 6 | 1 | 6 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:idiomatic_armory_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_armory_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_armory_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_degree | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_degree | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_degree | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_fullness | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_fullness | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_fullness | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_object_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_object_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_object_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_paraphrase | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_paraphrase | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_paraphrase | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_reflexive_particle | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_rendering | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_rendering | B_review | 0 | 3 | 3 | 3 | 3 | 0.0 | 0.0 | 4 | 4 | 2 | 2 |
| reviewed:idiomatic_rendering | C_unresolved | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_smooth_speech | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_smooth_speech | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_smooth_speech | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_translation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_translation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_translation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:idiomatic_wine_house_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:impersonal_voice | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:impersonal_voice | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:impersonal_voice | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:implicit_destination_relation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:implicit_destination_relation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:implicit_destination_relation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:inchoative_aspect | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:infinitive_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:instrumental_group | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:interrogative | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:kinship | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:kinship | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:kinship | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_alignment | A_auto | 0 | 0 | 91 | 0 | 91 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_alignment | B_review | 28 | 16 | 63 | 44 | 91 | 0.6363636363636364 | 0.5124163638068504 | 46 | 46 | 4 | 2 |
| reviewed:lexical_alignment | C_unresolved | 2 | 5 | 89 | 7 | 91 | 0.2857142857142857 | 0.09956584356228707 | 10 | 10 | 4 | 2 |
| reviewed:lexical_context | A_auto | 0 | 0 | 34 | 0 | 34 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_context | B_review | 6 | 5 | 28 | 11 | 34 | 0.5454545454545454 | 0.3150681426585182 | 12 | 13 | 4 | 3 |
| reviewed:lexical_context | C_unresolved | 3 | 2 | 31 | 5 | 34 | 0.6 | 0.2724831718661928 | 5 | 7 | 2 | 2 |
| reviewed:lexical_context_equivalence | A_auto | 0 | 0 | 266 | 0 | 266 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_context_equivalence | B_review | 62 | 70 | 204 | 132 | 266 | 0.4696969696969697 | 0.3995726907234285 | 148 | 150 | 17 | 3 |
| reviewed:lexical_context_equivalence | C_unresolved | 3 | 17 | 263 | 20 | 266 | 0.15 | 0.06158241047736831 | 31 | 37 | 12 | 9 |
| reviewed:lexical_derivation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_derivation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_derivation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_divergence | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_divergence | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_divergence | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_expansion | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_expansion | B_review | 1 | 2 | 4 | 3 | 5 | 0.3333333333333333 | 0.0782657263337284 | 3 | 3 | 1 | 1 |
| reviewed:lexical_expansion | C_unresolved | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_generalization | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_generalization | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_generalization | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_mismatch | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_mismatch | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_mismatch | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_substitution | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_substitution | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_substitution | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_uncertainty | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_uncertainty | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:lexical_uncertainty | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:location_expression | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:location_expression | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:location_expression | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_case | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_case | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_case | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:locative_idiom | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:manual_adjudication | A_auto | 0 | 0 | 409 | 0 | 409 | — | — | 0 | 0 | 0 | 0 |
| reviewed:manual_adjudication | B_review | 32 | 84 | 377 | 116 | 409 | 0.27586206896551724 | 0.2133016707203926 | 130 | 133 | 35 | 9 |
| reviewed:manual_adjudication | C_unresolved | 2 | 42 | 407 | 44 | 409 | 0.045454545454545456 | 0.015157576670885766 | 71 | 73 | 26 | 15 |
| reviewed:manual_semantic_alignment | A_auto | 0 | 0 | 894 | 0 | 894 | — | — | 0 | 0 | 0 | 0 |
| reviewed:manual_semantic_alignment | B_review | 216 | 176 | 678 | 392 | 894 | 0.5510204081632653 | 0.5094890624234256 | 428 | 440 | 54 | 2 |
| reviewed:manual_semantic_alignment | C_unresolved | 11 | 44 | 883 | 55 | 894 | 0.2 | 0.12631883901358953 | 76 | 92 | 31 | 11 |
| reviewed:many_to_many | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:many_to_many | B_review | 0 | 2 | 4 | 2 | 4 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:many_to_many | C_unresolved | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:many_to_one | A_auto | 0 | 0 | 17 | 0 | 17 | — | — | 0 | 0 | 0 | 0 |
| reviewed:many_to_one | B_review | 0 | 14 | 17 | 14 | 17 | 0.0 | 0.0 | 16 | 16 | 8 | 7 |
| reviewed:many_to_one | C_unresolved | 0 | 4 | 17 | 4 | 17 | 0.0 | 0.0 | 5 | 6 | 4 | 3 |
| reviewed:measure_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:measure_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:measure_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:merge_split | A_auto | 0 | 0 | 1359 | 0 | 1359 | — | — | 0 | 0 | 0 | 0 |
| reviewed:merge_split | B_review | 70 | 628 | 1289 | 698 | 1359 | 0.10028653295128939 | 0.08310098498509946 | 769 | 816 | 301 | 62 |
| reviewed:merge_split | C_unresolved | 9 | 281 | 1350 | 290 | 1359 | 0.03103448275862069 | 0.018142910723239897 | 447 | 548 | 193 | 59 |
| reviewed:missing_whitespace | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:missing_whitespace | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:missing_whitespace | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_contraction | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_contraction | B_review | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:morphosyntactic_contraction | C_unresolved | 0 | 1 | 7 | 1 | 7 | 0.0 | 0.0 | 2 | 2 | 1 | 1 |
| reviewed:morphosyntactic_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:morphosyntactic_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:multiple_strong | A_auto | 0 | 0 | 124 | 0 | 124 | — | — | 0 | 0 | 0 | 0 |
| reviewed:multiple_strong | B_review | 4 | 82 | 120 | 86 | 124 | 0.046511627906976744 | 0.021050067420064298 | 94 | 93 | 43 | 28 |
| reviewed:multiple_strong | C_unresolved | 0 | 26 | 124 | 26 | 124 | 0.0 | 6.284892038016744e-18 | 41 | 45 | 20 | 15 |
| reviewed:named_entity | A_auto | 0 | 0 | 486 | 0 | 486 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_entity | B_review | 221 | 126 | 265 | 347 | 486 | 0.6368876080691642 | 0.5935165141478507 | 362 | 359 | 181 | 43 |
| reviewed:named_entity | C_unresolved | 9 | 34 | 477 | 43 | 486 | 0.20930232558139536 | 0.12604830014849006 | 63 | 74 | 38 | 16 |
| reviewed:named_measure | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_measure | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:named_measure | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation | B_review | 1 | 0 | 0 | 1 | 1 | 1.0 | 0.2698659487840541 | 1 | 1 | 1 | 1 |
| reviewed:negation | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation_compound | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation_compound | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negation_compound | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_concord | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_coordination | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_copula | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_predicate | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_purpose | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_purpose | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_purpose | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_quantification | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_quantification | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:negative_quantification | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominal_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominalization | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominalization | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nominalization | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nonlexical_source_marker | A_auto | 0 | 0 | 17 | 0 | 17 | — | — | 0 | 0 | 0 | 0 |
| reviewed:nonlexical_source_marker | B_review | 0 | 3 | 17 | 3 | 17 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:nonlexical_source_marker | C_unresolved | 0 | 2 | 17 | 2 | 17 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:number_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:number_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:numeral_mismatch | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:oath_formula_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:omission | A_auto | 0 | 0 | 1432 | 0 | 1432 | — | — | 0 | 0 | 0 | 0 |
| reviewed:omission | B_review | 3 | 277 | 1429 | 280 | 1432 | 0.010714285714285714 | 0.004289843441564408 | 328 | 302 | 209 | 58 |
| reviewed:omission | C_unresolved | 0 | 153 | 1432 | 153 | 1432 | 0.0 | 0.0 | 271 | 252 | 124 | 37 |
| reviewed:one_to_many | A_auto | 0 | 0 | 14 | 0 | 14 | — | — | 0 | 0 | 0 | 0 |
| reviewed:one_to_many | B_review | 1 | 6 | 13 | 7 | 14 | 0.14285714285714285 | 0.03254380205478664 | 7 | 10 | 4 | 3 |
| reviewed:one_to_many | C_unresolved | 0 | 2 | 14 | 2 | 14 | 0.0 | 0.0 | 2 | 5 | 2 | 2 |
| reviewed:one_to_one | A_auto | 0 | 0 | 120 | 0 | 120 | — | — | 0 | 0 | 0 | 0 |
| reviewed:one_to_one | B_review | 54 | 19 | 66 | 73 | 120 | 0.7397260273972602 | 0.6477679258247637 | 79 | 77 | 11 | 1 |
| reviewed:one_to_one | C_unresolved | 4 | 7 | 116 | 11 | 120 | 0.36363636363636365 | 0.1751367285207303 | 12 | 17 | 7 | 4 |
| reviewed:orthography | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:orthography | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:orthography | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:overt_subject | A_auto | 0 | 0 | 6 | 0 | 6 | — | — | 0 | 0 | 0 | 0 |
| reviewed:overt_subject | B_review | 1 | 2 | 5 | 3 | 6 | 0.3333333333333333 | 0.0782657263337284 | 3 | 3 | 2 | 2 |
| reviewed:overt_subject | C_unresolved | 0 | 2 | 6 | 2 | 6 | 0.0 | 0.0 | 3 | 5 | 1 | 1 |
| reviewed:participial_rendering | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:participial_rendering | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:participial_rendering | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle | A_auto | 0 | 0 | 2066 | 0 | 2066 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle | B_review | 481 | 527 | 1585 | 1008 | 2066 | 0.4771825396825397 | 0.4514011828086513 | 1073 | 1138 | 338 | 11 |
| reviewed:particle | C_unresolved | 36 | 234 | 2030 | 270 | 2066 | 0.13333333333333333 | 0.10291709982671662 | 398 | 471 | 167 | 34 |
| reviewed:particle_expansion | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:particle_expansion | B_review | 0 | 3 | 2 | 3 | 2 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:particle_expansion | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:passive_voice | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:passive_voice | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:passive_voice | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:person_number | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:person_number | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:person_number | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_anomaly | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polarity_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polysemy | A_auto | 0 | 0 | 740 | 0 | 740 | — | — | 0 | 0 | 0 | 0 |
| reviewed:polysemy | B_review | 108 | 212 | 632 | 320 | 740 | 0.3375 | 0.2955443525248828 | 356 | 369 | 171 | 47 |
| reviewed:polysemy | C_unresolved | 15 | 144 | 725 | 159 | 740 | 0.09433962264150944 | 0.06271353275501099 | 255 | 299 | 110 | 54 |
| reviewed:possessive | A_auto | 0 | 0 | 11 | 0 | 11 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive | B_review | 3 | 4 | 8 | 7 | 11 | 0.42857142857142855 | 0.18644319036395607 | 7 | 8 | 3 | 2 |
| reviewed:possessive | C_unresolved | 0 | 2 | 11 | 2 | 11 | 0.0 | 0.0 | 4 | 2 | 1 | 1 |
| reviewed:possessive_derivation | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_derivation | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_derivation | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:possessive_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:predicate_restructuring | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:predicate_restructuring | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:predicate_restructuring | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:prepositional_expansion | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_expansion | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:prepositional_expansion | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:prepositional_restructuring | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_complement | A_auto | 0 | 0 | 7 | 0 | 7 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_complement | B_review | 1 | 2 | 6 | 3 | 7 | 0.3333333333333333 | 0.0782657263337284 | 3 | 3 | 1 | 1 |
| reviewed:pronominal_complement | C_unresolved | 0 | 2 | 7 | 2 | 7 | 0.0 | 0.0 | 3 | 5 | 1 | 1 |
| reviewed:pronominal_expansion | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_expansion | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:pronominal_expansion | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_subject | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronominal_subject | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:pronominal_subject | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:pronoun_repetition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronoun_repetition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:pronoun_repetition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_component_omission | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_name_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:proper_place_mismatch | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:purpose_clause | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:purpose_clause | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:purpose_clause | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rare_lemma | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reciprocal_target_accounting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reciprocal_target_accounting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reciprocal_target_accounting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:referent_explication | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:referent_explication | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:referent_explication | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_possessive | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reflexive_possessive | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:reflexive_possessive | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_clause | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_clause | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_clause | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_conception_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_expansion | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_expansion | B_review | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:relative_expansion | C_unresolved | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_participle_expansion | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_participle_expansion | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_participle_expansion | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_subject | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_subject | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:relative_subject | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reorder | A_auto | 0 | 0 | 1729 | 0 | 1729 | — | — | 0 | 0 | 0 | 0 |
| reviewed:reorder | B_review | 454 | 453 | 1275 | 907 | 1729 | 0.5005512679162073 | 0.4732820495660474 | 985 | 1007 | 290 | 38 |
| reviewed:reorder | C_unresolved | 24 | 190 | 1705 | 214 | 1729 | 0.11214953271028037 | 0.08140258085952776 | 325 | 393 | 154 | 59 |
| reviewed:repetition | A_auto | 0 | 0 | 51 | 0 | 51 | — | — | 0 | 0 | 0 | 0 |
| reviewed:repetition | B_review | 7 | 27 | 44 | 34 | 51 | 0.20588235294117646 | 0.11566389757386858 | 36 | 46 | 22 | 16 |
| reviewed:repetition | C_unresolved | 1 | 12 | 50 | 13 | 51 | 0.07692307692307693 | 0.017352312196041646 | 19 | 23 | 12 | 12 |
| reviewed:resultative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resultative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resultative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:resumptive_object | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:rhetorical_question | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_recasting | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_restructuring_requires_second_pass | A_auto | 0 | 0 | 2 | 0 | 2 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_restructuring_requires_second_pass | B_review | 0 | 2 | 2 | 2 | 2 | 0.0 | 0.0 | 3 | 3 | 1 | 1 |
| reviewed:semantic_restructuring_requires_second_pass | C_unresolved | 0 | 1 | 2 | 1 | 2 | 0.0 | 0.0 | 3 | 4 | 1 | 1 |
| reviewed:semantic_uncertainty | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_uncertainty | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:semantic_uncertainty | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_component_not_overt | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_grammar | A_auto | 0 | 0 | 14 | 0 | 14 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_grammar | B_review | 0 | 1 | 14 | 1 | 14 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:source_grammar | C_unresolved | 0 | 5 | 14 | 5 | 14 | 0.0 | 0.0 | 12 | 7 | 4 | 3 |
| reviewed:source_idiom | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_idiom | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_idiom | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_marker | A_auto | 0 | 0 | 46 | 0 | 46 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_marker | B_review | 0 | 10 | 46 | 10 | 46 | 0.0 | 0.0 | 13 | 12 | 9 | 9 |
| reviewed:source_marker | C_unresolved | 0 | 5 | 46 | 5 | 46 | 0.0 | 0.0 | 9 | 6 | 4 | 4 |
| reviewed:source_merge_or_compound | A_auto | 0 | 0 | 29 | 0 | 29 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_merge_or_compound | B_review | 1 | 23 | 28 | 24 | 29 | 0.041666666666666664 | 0.009351070046073277 | 30 | 29 | 10 | 9 |
| reviewed:source_merge_or_compound | C_unresolved | 0 | 5 | 29 | 5 | 29 | 0.0 | 0.0 | 11 | 12 | 3 | 3 |
| reviewed:source_tag_uncertainty | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_tag_uncertainty | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_tag_uncertainty | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_target_surface_issue | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_text_not_rendered | A_auto | 0 | 0 | 52 | 0 | 52 | — | — | 0 | 0 | 0 | 0 |
| reviewed:source_text_not_rendered | B_review | 0 | 17 | 52 | 17 | 52 | 0.0 | 0.0 | 20 | 18 | 15 | 15 |
| reviewed:source_text_not_rendered | C_unresolved | 0 | 5 | 52 | 5 | 52 | 0.0 | 0.0 | 10 | 9 | 5 | 4 |
| reviewed:speaker_attribution_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:speaker_attribution_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:speaker_attribution_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_absorption | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_absorption | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:subject_absorption | C_unresolved | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_clause | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_clause | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_clause | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_expansion | A_auto | 0 | 0 | 3 | 0 | 3 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_expansion | B_review | 0 | 3 | 3 | 3 | 3 | 0.0 | 0.0 | 3 | 4 | 1 | 1 |
| reviewed:subject_expansion | C_unresolved | 0 | 2 | 3 | 2 | 3 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| reviewed:subject_shift | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_shift | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subject_shift | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subordinator_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subordinator_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:subordinator_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_anomaly | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_anomaly | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_anomaly | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_split_or_expansion | A_auto | 0 | 0 | 20 | 0 | 20 | — | — | 0 | 0 | 0 | 0 |
| reviewed:target_split_or_expansion | B_review | 1 | 16 | 19 | 17 | 20 | 0.058823529411764705 | 0.0132343756497352 | 20 | 20 | 9 | 8 |
| reviewed:target_split_or_expansion | C_unresolved | 0 | 5 | 20 | 5 | 20 | 0.0 | 0.0 | 11 | 12 | 3 | 3 |
| reviewed:temporal_addition | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_addition | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_addition | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_clause | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_clause | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_clause | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_connective | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:temporal_subordinator | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:tense_aspect | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:tense_aspect | B_review | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:tense_aspect | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 2 | 4 | 1 | 1 |
| reviewed:textual_variant | A_auto | 0 | 0 | 519 | 0 | 519 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant | B_review | 142 | 113 | 377 | 255 | 519 | 0.5568627450980392 | 0.5053633433370303 | 281 | 279 | 74 | 27 |
| reviewed:textual_variant | C_unresolved | 18 | 49 | 501 | 67 | 519 | 0.26865671641791045 | 0.18984770738835224 | 91 | 111 | 40 | 26 |
| reviewed:textual_variant_divergence | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant_divergence | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:textual_variant_divergence | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_addition | A_auto | 0 | 0 | 5 | 0 | 5 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_addition | B_review | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:translation_addition | C_unresolved | 0 | 1 | 5 | 1 | 5 | 0.0 | 0.0 | 1 | 2 | 1 | 1 |
| reviewed:translation_choice | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_choice | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_choice | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_omission | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_omission | B_review | 0 | 1 | 4 | 1 | 4 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:translation_omission | C_unresolved | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_paraphrase | A_auto | 0 | 0 | 4 | 0 | 4 | — | — | 0 | 0 | 0 | 0 |
| reviewed:translation_paraphrase | B_review | 0 | 3 | 4 | 3 | 4 | 0.0 | 0.0 | 3 | 3 | 2 | 2 |
| reviewed:translation_paraphrase | C_unresolved | 0 | 1 | 4 | 1 | 4 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:unclassified | A_auto | 0 | 0 | 1905 | 0 | 1905 | — | — | 0 | 0 | 0 | 0 |
| reviewed:unclassified | B_review | 626 | 392 | 1279 | 1018 | 1905 | 0.6149312377210217 | 0.5895717590017733 | 1092 | 1136 | 317 | 29 |
| reviewed:unclassified | C_unresolved | 64 | 188 | 1841 | 252 | 1905 | 0.25396825396825395 | 0.21164383255920588 | 394 | 446 | 177 | 67 |
| reviewed:vocative_particle | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_particle | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_particle | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_split | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_split | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_split | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:vocative_superlative | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive | A_auto | 0 | 0 | 1 | 0 | 1 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive | B_review | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:volitive | C_unresolved | 0 | 1 | 1 | 1 | 1 | 0.0 | 0.0 | 1 | 1 | 1 | 1 |
| reviewed:volitive_group | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive_group | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:volitive_group | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| reviewed:word_split | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:frequent_1000_plus | A_auto | 0 | 0 | 2364 | 0 | 2364 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:frequent_1000_plus | B_review | 636 | 406 | 1728 | 1042 | 2364 | 0.6103646833013435 | 0.5852599397322308 | 1159 | 1149 | 353 | 1 |
| source_frequency:frequent_1000_plus | C_unresolved | 29 | 155 | 2335 | 184 | 2364 | 0.15760869565217392 | 0.11842781895485231 | 295 | 286 | 132 | 4 |
| source_frequency:mid | A_auto | 0 | 0 | 3293 | 0 | 3293 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:mid | B_review | 974 | 492 | 2319 | 1466 | 3293 | 0.6643929058663028 | 0.6438208815887178 | 1555 | 1570 | 401 | 36 |
| source_frequency:mid | C_unresolved | 89 | 183 | 3204 | 272 | 3293 | 0.3272058823529412 | 0.2823131683433643 | 401 | 440 | 181 | 87 |
| source_frequency:rare_1_to_5 | A_auto | 0 | 0 | 343 | 0 | 343 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:rare_1_to_5 | B_review | 61 | 47 | 282 | 108 | 343 | 0.5648148148148148 | 0.4857090891461987 | 114 | 115 | 82 | 73 |
| source_frequency:rare_1_to_5 | C_unresolved | 14 | 41 | 329 | 55 | 343 | 0.2545454545454545 | 0.17103247784451941 | 96 | 108 | 46 | 38 |
| source_frequency:unclassified | A_auto | 0 | 0 | 2599 | 0 | 2599 | — | — | 0 | 0 | 0 | 0 |
| source_frequency:unclassified | B_review | 250 | 420 | 2349 | 670 | 2599 | 0.373134328358209 | 0.34296885289693707 | 696 | 763 | 225 | 23 |
| source_frequency:unclassified | C_unresolved | 29 | 207 | 2570 | 236 | 2599 | 0.1228813559322034 | 0.09194362411379595 | 317 | 387 | 148 | 43 |
| testament:NT | A_auto | 0 | 0 | 3070 | 0 | 3070 | — | — | 0 | 0 | 0 | 0 |
| testament:NT | B_review | 915 | 494 | 2155 | 1409 | 3070 | 0.6493967352732435 | 0.6282194255671159 | 1479 | 1517 | 183 | 1 |
| testament:NT | C_unresolved | 105 | 219 | 2965 | 324 | 3070 | 0.32407407407407407 | 0.28291477655206887 | 444 | 482 | 147 | 33 |
| testament:OT | A_auto | 0 | 0 | 5471 | 0 | 5471 | — | — | 0 | 0 | 0 | 0 |
| testament:OT | B_review | 1006 | 841 | 4465 | 1847 | 5471 | 0.5446670276123443 | 0.5255554820212466 | 1981 | 2040 | 245 | 5 |
| testament:OT | C_unresolved | 56 | 302 | 5415 | 358 | 5471 | 0.1564245810055866 | 0.12743578721354878 | 506 | 601 | 179 | 36 |
| testament:missing | A_auto | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| testament:missing | B_review | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |
| testament:missing | C_unresolved | 0 | 0 | 0 | 0 | 0 | — | — | 0 | 0 | 0 | 0 |

Missing/zero-prediction strata: `anomaly:explicit_conflict`, `anomaly:mapping:1:1`, `anomaly:mapping:merge`, `anomaly:mapping:other`, `anomaly:mapping:split`, `anomaly:none`, `anomaly:reading:missing`, `anomaly:reading:nonprimary_or_unresolved`, `anomaly:textual_alternative`, `evidence:missing`, `genre:missing`, `relation:grouped_expression`, `relation:original_omitted`, `relation:textual_alternative`, `relation:translation_addition`, `reviewed:adjectival_explication`, `reviewed:adjectival_rendering`, `reviewed:adjectival_restructuring`, `reviewed:age_idiom`, `reviewed:alignment_counterexample`, `reviewed:analytic_future`, `reviewed:anaphoric_expansion`, `reviewed:anaphoric_explication`, `reviewed:article_lexical_expansion`, `reviewed:article_noun_group`, `reviewed:aspectual_expansion`, `reviewed:body_part_change`, `reviewed:case_restructuring`, `reviewed:causative_recasting`, `reviewed:clause_coordination`, `reviewed:clause_relation`, `reviewed:cohortative_motion_expansion`, `reviewed:cohortative_particle_group`, `reviewed:comparative_clause`, `reviewed:comparative_frame`, `reviewed:compound_numeral`, `reviewed:conditional_particle_repetition`, `reviewed:contextual_addressee_addition`, `reviewed:contextual_demonstrative_addition`, `reviewed:contextual_location_addition`, `reviewed:contextual_possessor_addition`, `reviewed:contextual_private_speech_addition`, `reviewed:coordination`, `reviewed:copular_adjectival_expansion`, `reviewed:copular_construction`, `reviewed:copular_expression`, `reviewed:copular_relative`, `reviewed:correlative_expansion`, `reviewed:dative_copular_expansion`, `reviewed:dative_group`, `reviewed:dative_pronominal_group`, `reviewed:deictic_expression`, `reviewed:deictic_subject`, `reviewed:deictic_time`, `reviewed:derivational_rendering`, `reviewed:direct_object_marker_not_overt`, `reviewed:directional_place`, `reviewed:directional_pr_pronominal`, `reviewed:discontinuous_rendering`, `reviewed:discourse_particle`, `reviewed:discourse_particle_omission`, `reviewed:discourse_restructuring`, `reviewed:distributive`, `reviewed:duration_phrase`, `reviewed:existential_restructuring`, `reviewed:existential_to_indefinite`, `reviewed:explicit_object`, `reviewed:explicit_source_null`, `reviewed:explicit_target_function`, `reviewed:explicitation`, `reviewed:fawn_deer_lexical_group`, `reviewed:frequent_lemma`, `reviewed:genitive_group`, `reviewed:gentilic_recasting`, `reviewed:government`, `reviewed:government_shift`, `reviewed:grammatical_function`, `reviewed:idiomatic_armory_rendering`, `reviewed:idiomatic_degree`, `reviewed:idiomatic_fullness`, `reviewed:idiomatic_object_explication`, `reviewed:idiomatic_paraphrase`, `reviewed:idiomatic_reflexive_particle`, `reviewed:idiomatic_smooth_speech`, `reviewed:idiomatic_translation`, `reviewed:idiomatic_wine_house_rendering`, `reviewed:impersonal_voice`, `reviewed:implicit_destination_relation`, `reviewed:inchoative_aspect`, `reviewed:infinitive`, `reviewed:infinitive_group`, `reviewed:instrumental_group`, `reviewed:interrogative`, `reviewed:kinship`, `reviewed:lexical_derivation`, `reviewed:lexical_divergence`, `reviewed:lexical_generalization`, `reviewed:lexical_mismatch`, `reviewed:lexical_rendering`, `reviewed:lexical_shift`, `reviewed:lexical_substitution`, `reviewed:lexical_uncertainty`, `reviewed:location_expression`, `reviewed:locative_case`, `reviewed:locative_idiom`, `reviewed:measure_explication`, `reviewed:missing_whitespace`, `reviewed:morphosyntactic_shift`, `reviewed:named_measure`, `reviewed:negation_compound`, `reviewed:negative_concord`, `reviewed:negative_coordination`, `reviewed:negative_copula`, `reviewed:negative_predicate`, `reviewed:negative_purpose`, `reviewed:negative_quantification`, `reviewed:nominal_group`, `reviewed:nominalization`, `reviewed:number_expansion`, `reviewed:number_shift`, `reviewed:numeral_mismatch`, `reviewed:oath_formula_addition`, `reviewed:orthography`, `reviewed:participial_rendering`, `reviewed:passive_voice`, `reviewed:person_number`, `reviewed:polarity`, `reviewed:polarity_anomaly`, `reviewed:polarity_recasting`, `reviewed:possessive_derivation`, `reviewed:possessive_shift`, `reviewed:prepositional_restructuring`, `reviewed:pronominal_explication`, `reviewed:pronoun_repetition`, `reviewed:proper_name_component_omission`, `reviewed:proper_name_group`, `reviewed:proper_place_mismatch`, `reviewed:purpose_clause`, `reviewed:rare_lemma`, `reviewed:reciprocal_target_accounting`, `reviewed:referent_explication`, `reviewed:reflexive`, `reviewed:reflexive_group`, `reviewed:relative_clause`, `reviewed:relative_conception_expansion`, `reviewed:relative_participle_expansion`, `reviewed:relative_subject`, `reviewed:resultative`, `reviewed:resumptive_object`, `reviewed:rhetorical_question`, `reviewed:semantic_recasting`, `reviewed:semantic_uncertainty`, `reviewed:source_component_not_overt`, `reviewed:source_idiom`, `reviewed:source_tag_uncertainty`, `reviewed:source_target_surface_issue`, `reviewed:speaker_attribution_addition`, `reviewed:subject_clause`, `reviewed:subject_shift`, `reviewed:subordinator_group`, `reviewed:target_anomaly`, `reviewed:temporal_addition`, `reviewed:temporal_clause`, `reviewed:temporal_connective`, `reviewed:temporal_subordinator`, `reviewed:textual_variant_divergence`, `reviewed:translation_choice`, `reviewed:vocative_particle`, `reviewed:vocative_split`, `reviewed:vocative_superlative`, `reviewed:volitive_group`, `reviewed:word_split`, `testament:missing`.

## Проверки, роли и artifacts

539 Python tests PASS:457 Bible+26 consensus76+26 calibration77+30 Content Tool. Независимый reviewer не наследовал авторскую историю, не писал producer и не проверял собственную реализацию:32 собственные canary groups,300 PAVA oracle cases, raw payload/metrics recount и frozen-model replay. Все конкретные результаты и ограничения — в [независимом отчёте](calibration77_independent_validation.v1.ru.md).

Фактические роли: `/root/calibration_author` — новый package/tests и единственный producer fit/validation; `/root/independent_review77` (`fork_turns=none`) — независимый source/raw QC и собственные auditors; `/root` — orchestration/preflight/docs/checks, не independent QC; `/root/inventory_writer77` — отдельный writer existing helper после остальных записей. [Роли](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_root_01/roles.v1.json).

Flutter format/analyze/test/smoke N/A: изменены только отдельный Python stdlib tooling, calibration evidence и content docs; lib/test Dart, UI/navigation/startup, dependencies/localization/release и platform/DB/web DB не менялись. Approved RU/EN architecture/testing pairs не затронуты. Flutter-bundled Dart по абсолютному пути используется для docs-sync и forbidden-pattern checks. Окончательные stage/SHA/public gold/docs/navigation/diff receipts и отдельный writer отражены в [validation log](calibration77_validation_log.v1.md) и [актуальном HANDOFF](HANDOFF.ru.md); последние post-inventory receipts записываются только в исключённый HANDOFF.

[inputs.v1.lock.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/inputs.v1.lock.json), [source.v1.lock.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/source.v1.lock.json), [runtime.v1.lock.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/runtime.v1.lock.json), [pipeline.v1.lock.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/pipeline.v1.lock.json), [model.v1.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/build.v1/model.v1.json), [development.metrics.v1.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/build.v1/development.metrics.v1.json), [validation3.v1.manifest.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/validation3.v1/validation3.v1.manifest.json), [test4.skipped.v1.json](../../work/ukrainian_stage_7_20260801/session_calibration77_20261017_author_01/test4.skipped.v1.json).

Результат относится к этой frozen policy и не доказывает отсутствие любого возможного точного subclass. Новых исследований отсрочек/Strong assignments, iterative ledger/bootstrap/self-training, stage8, production acceptance/promotions, commit/push не было. Единственный OH1988 registry и все frozen artifacts сохранены.

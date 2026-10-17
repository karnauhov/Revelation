# Этап 7.4 — глобальный gold и фиксированная baseline-оценка, 2026-10-17

Gold-пакет завершён с проверенными зарегистрированными отсрочками. Этап 7 целиком остаётся открытым: калибровка, production Strong и этап 8 не выполнялись.

Завершено **66/66** книг: **38** строго приняты, **28** завершены как `completed_with_registered_deferrals`. Отсрочки не превращены в strict acceptance.

Full-grid: **2171 стихов / 87638 node decisions**, включая 45831 original и 41807 target. Eligible: **2171 стихов / 87108 node decisions**, из них **45591 original link/null decisions**. Исключены **530** present-but-deferred nodes. Минимумы 2000 стихов и 25000 original решений пройдены после исключений; target rows, hyperedges и negative annotations в минимум не включены.

Serialized annotation record types: `{'deferred_original_decision': 240, 'deferred_target_accounting': 290, 'hyperedge': 45538, 'original_decision': 45591, 'target_accounting': 41517}`. SHA256 маски: `d99436f6dedb48c6d7ec99acbaf4631fc009723fdc411851e2dc587e84f844db`. SHA256 annotations: `547c67517fa466682b5cfe602cc669fa35f3a0420d813bad3a41670d0e880d67`.

## Контракты и доказательства

[Final lock](gold_alignment.finalized.v2.lock.json), [final manifest](gold_alignment.finalized.v2.manifest.json), [активный registry source](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/gold_finalization_registry.candidate.v11.json) и [byte-identical Git mirror](gold_finalization_registry.v7.manifest.json), [annotations](../../work/ukrainian_stage_7_20260801/gold_alignment.annotations.v2.jsonl), [eligibility mask](../../work/ukrainian_stage_7_20260801/gold_alignment.eligibility.v2.jsonl), [единый OH1988 реестр](oh88_strongs_issue_inventory.ru.md#registry-records), [независимая проверка](gold_global_independent_validation.v1.ru.md).

Маска выведена из текущих completion/correction/source/QC chains, policy и общего реестра до оценки методов. Exact-once accounting сохраняет каждый original и target узел. Отложенные узлы остаются явно present, без Strong, вымышленных NULL или недоказанных ребёр. Исключения замкнуты по reciprocal/many-to-many компонентам; остальные доказанные решения сохранены. Zeph.2.14 включает точную пару отложенных узлов.

Допустимые пересекающиеся target-связи в Judg.18.24, Mat.5.11 и Ruth.2.7 сохраняют отдельные declared hyperedges. Единственная reciprocal target row содержит точный union связанных originals; это не дублирование physical node и не повод сливать gold edges. Evaluation-loader и legacy identification проверены на этой структуре отдельными regression и независимыми probes.

`ukrainian_stage_7_gold_v2 build-registry → finalize → check-final` использует отдельную версионированную цепочку. Старый strict workflow и его отказы сохранены. Check-final проверяет physical SHA/bytes, актуальный roster overlays, исходные provenance/QC, полный packet accounting и заново воспроизводит exact annotations и mask. Историческая mutable ancestry доступна только через явные exact SHA bridges; она не объявлена live accepted QC.

Исторический strict acceptance использует исходные bounded QC-контракты: 1Kgs 503 unique reviewed IDs, 1Sam 319, 2Sam 306; mandatory adjudication subsets и stratified samples проверены в их фактическом объёме. Это не новый full-grid content QC. Для Dan/Isa отдельный root-authored adapter проверяет старые aggregate/agreed error classes, exact correction scope, supersedes, авторство и весь последующий independent final-QC payload. Старые public strict validators сохраняют прежние отказы. Остальные филологические passes не переоткрывались. Реальные роли и границы независимости сохранены в [session roles](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/roles.v2.json) и независимом отчёте.

## Full, eligible и exclusions

Страты могут пересекаться; их строки нельзя складывать. Proven verse требует хотя бы одного eligible original решения внутри данной группы. Deferred-only и target-only присутствие не выдаётся за доказанное оценочное покрытие.

### book

| Группа | Full verses | Proven verses | Deferred-only | Full original | Eligible original | Full target | Eligible target | Excluded nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1Chr | 32 | 32 | 0 | 699 | 699 | 565 | 565 | 0 |
| 1Cor | 33 | 33 | 0 | 471 | 469 | 481 | 477 | 6 |
| 1John | 33 | 33 | 0 | 689 | 677 | 605 | 586 | 31 |
| 1Kgs | 33 | 33 | 0 | 947 | 947 | 806 | 806 | 0 |
| 1Pet | 32 | 32 | 0 | 548 | 529 | 554 | 531 | 42 |
| 1Sam | 35 | 35 | 0 | 964 | 964 | 829 | 829 | 0 |
| 1Thess | 32 | 32 | 0 | 531 | 514 | 506 | 502 | 21 |
| 1Tim | 33 | 33 | 0 | 483 | 477 | 530 | 521 | 15 |
| 2Chr | 34 | 34 | 0 | 1026 | 1026 | 816 | 816 | 0 |
| 2Cor | 34 | 34 | 0 | 540 | 533 | 543 | 529 | 21 |
| 2John | 13 | 13 | 0 | 245 | 237 | 246 | 236 | 18 |
| 2Kgs | 32 | 32 | 0 | 950 | 950 | 768 | 768 | 0 |
| 2Pet | 32 | 32 | 0 | 605 | 582 | 613 | 594 | 42 |
| 2Sam | 33 | 33 | 0 | 951 | 951 | 777 | 777 | 0 |
| 2Thess | 32 | 32 | 0 | 603 | 593 | 597 | 575 | 32 |
| 2Tim | 32 | 32 | 0 | 513 | 510 | 507 | 502 | 8 |
| 3John | 14 | 14 | 0 | 219 | 211 | 227 | 222 | 13 |
| Acts | 39 | 39 | 0 | 720 | 712 | 716 | 707 | 17 |
| Amos | 32 | 32 | 0 | 779 | 779 | 690 | 690 | 0 |
| Col | 33 | 33 | 0 | 526 | 519 | 491 | 484 | 14 |
| Dan | 32 | 32 | 0 | 844 | 844 | 721 | 721 | 0 |
| Deut | 33 | 33 | 0 | 852 | 852 | 710 | 710 | 0 |
| Eccl | 32 | 32 | 0 | 780 | 780 | 625 | 625 | 0 |
| Eph | 32 | 32 | 0 | 530 | 524 | 460 | 451 | 15 |
| Esth | 32 | 32 | 0 | 1083 | 1083 | 855 | 855 | 0 |
| Exod | 32 | 32 | 0 | 754 | 754 | 628 | 628 | 0 |
| Ezek | 32 | 32 | 0 | 845 | 845 | 717 | 717 | 0 |
| Ezra | 32 | 32 | 0 | 906 | 906 | 695 | 695 | 0 |
| Gal | 32 | 32 | 0 | 499 | 493 | 556 | 546 | 16 |
| Gen | 33 | 33 | 0 | 809 | 809 | 698 | 698 | 0 |
| Hab | 32 | 32 | 0 | 707 | 707 | 703 | 703 | 0 |
| Hag | 32 | 32 | 0 | 901 | 901 | 694 | 694 | 0 |
| Heb | 32 | 32 | 0 | 508 | 499 | 531 | 518 | 22 |
| Hos | 32 | 32 | 0 | 615 | 615 | 588 | 588 | 0 |
| Isa | 34 | 34 | 0 | 716 | 716 | 649 | 649 | 0 |
| Jas | 32 | 32 | 0 | 505 | 491 | 503 | 484 | 33 |
| Jer | 32 | 32 | 0 | 946 | 946 | 773 | 773 | 0 |
| Job | 32 | 32 | 0 | 435 | 435 | 435 | 435 | 0 |
| Joel | 32 | 32 | 0 | 745 | 745 | 644 | 644 | 0 |
| John | 36 | 36 | 0 | 593 | 588 | 577 | 576 | 6 |
| Jonah | 32 | 32 | 0 | 831 | 831 | 696 | 696 | 0 |
| Josh | 32 | 32 | 0 | 874 | 874 | 692 | 692 | 0 |
| Jude | 25 | 25 | 0 | 462 | 456 | 472 | 466 | 12 |
| Judg | 33 | 33 | 0 | 971 | 971 | 778 | 778 | 0 |
| Lam | 32 | 32 | 0 | 538 | 538 | 515 | 515 | 0 |
| Lev | 32 | 32 | 0 | 760 | 760 | 635 | 635 | 0 |
| Luke | 39 | 39 | 0 | 606 | 600 | 604 | 597 | 13 |
| Mal | 32 | 32 | 0 | 855 | 855 | 758 | 758 | 0 |
| Mark | 40 | 40 | 0 | 681 | 679 | 647 | 645 | 4 |
| Mat | 39 | 39 | 0 | 691 | 685 | 667 | 658 | 15 |
| Mic | 32 | 32 | 0 | 761 | 761 | 725 | 725 | 0 |
| Nah | 32 | 32 | 0 | 604 | 604 | 593 | 593 | 0 |
| Neh | 32 | 32 | 0 | 621 | 621 | 485 | 485 | 0 |
| Num | 33 | 33 | 0 | 812 | 812 | 684 | 684 | 0 |
| Obad | 21 | 21 | 0 | 498 | 498 | 478 | 478 | 0 |
| Phil | 32 | 32 | 0 | 499 | 495 | 536 | 526 | 14 |
| Phlm | 25 | 25 | 0 | 338 | 329 | 358 | 346 | 21 |
| Prov | 32 | 32 | 0 | 424 | 424 | 389 | 389 | 0 |
| Ps | 97 | 97 | 0 | 1399 | 1399 | 1862 | 1862 | 0 |
| Rev | 35 | 35 | 0 | 922 | 899 | 847 | 832 | 38 |
| Rom | 33 | 33 | 0 | 520 | 516 | 536 | 524 | 16 |
| Ruth | 32 | 32 | 0 | 851 | 851 | 734 | 734 | 0 |
| Song | 32 | 32 | 0 | 623 | 623 | 577 | 577 | 0 |
| Titus | 32 | 32 | 0 | 460 | 451 | 473 | 459 | 23 |
| Zech | 32 | 32 | 0 | 861 | 861 | 745 | 745 | 0 |
| Zeph | 32 | 32 | 0 | 787 | 786 | 692 | 691 | 2 |

### fold

| Группа | Full verses | Proven verses | Deferred-only | Full original | Eligible original | Full target | Eligible target | Excluded nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 449 | 449 | 0 | 9383 | 9338 | 8617 | 8550 | 112 |
| 1 | 397 | 397 | 0 | 8544 | 8516 | 7647 | 7599 | 76 |
| 2 | 446 | 446 | 0 | 9698 | 9657 | 8833 | 8774 | 100 |
| 3 | 430 | 430 | 0 | 8653 | 8586 | 7967 | 7905 | 129 |
| 4 | 449 | 449 | 0 | 9553 | 9494 | 8743 | 8689 | 113 |

### selection_stratum

| Группа | Full verses | Proven verses | Deferred-only | Full original | Eligible original | Full target | Eligible target | Excluded nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| genre:acts_narrative | 39 | 39 | 0 | 720 | 712 | 716 | 707 | 17 |
| genre:apocalyptic | 35 | 35 | 0 | 922 | 899 | 847 | 832 | 38 |
| genre:epistle | 628 | 628 | 0 | 10294 | 10105 | 10325 | 10079 | 435 |
| genre:gospel_narrative | 154 | 154 | 0 | 2571 | 2552 | 2495 | 2476 | 38 |
| genre:historical_prose | 392 | 392 | 0 | 10843 | 10843 | 8800 | 8800 | 0 |
| genre:poetry_wisdom | 225 | 225 | 0 | 3661 | 3661 | 3888 | 3888 | 0 |
| genre:prophetic | 535 | 535 | 0 | 12833 | 12832 | 11381 | 11380 | 2 |
| genre:torah_prose_law | 163 | 163 | 0 | 3987 | 3987 | 3355 | 3355 | 0 |
| mapping_operation:1:1 | 2095 | 2095 | 0 | 44674 | 44434 | 40166 | 39878 | 528 |
| mapping_operation:merge | 68 | 68 | 0 | 1068 | 1068 | 1557 | 1555 | 2 |
| mapping_operation:split | 8 | 8 | 0 | 89 | 89 | 84 | 84 | 0 |
| original_frequency_bands:frequent_1000_plus | 2058 | 2058 | 0 | 43979 | 43739 | 40200 | 39910 | 530 |
| original_frequency_bands:mid_frequency | 2162 | 2162 | 0 | 45737 | 45497 | 41746 | 41456 | 530 |
| original_frequency_bands:rare_1_to_5 | 938 | 938 | 0 | 19840 | 19691 | 18422 | 18236 | 335 |
| original_selection_rule:component_specific_unresolved_choice+post_candidate_manual_textual_overlay | 5 | 5 | 0 | 120 | 114 | 108 | 104 | 10 |
| original_selection_rule:resolved_primary_original_layer | 2118 | 2118 | 0 | 44852 | 44625 | 40900 | 40617 | 510 |
| original_selection_rule:selected_only_begotten_son_surface_alternative | 1 | 1 | 0 | 16 | 14 | 15 | 14 | 3 |
| original_selection_rule:selected_primary_component_layer | 26 | 26 | 0 | 539 | 535 | 490 | 490 | 4 |
| original_selection_rule:selected_primary_plus_traditional_expansion | 4 | 4 | 0 | 71 | 71 | 70 | 70 | 0 |
| original_selection_rule:selected_singular_lot_surface_alternative | 1 | 1 | 0 | 19 | 19 | 20 | 20 | 0 |
| original_selection_rule:selected_tagnt_silas_clause_plus_d05_long_clause_and_versional_addition | 1 | 1 | 0 | 10 | 9 | 10 | 8 | 3 |
| original_selection_rule:selected_tahot_column6_pierced_surface_alternative | 1 | 1 | 0 | 15 | 15 | 15 | 15 | 0 |
| original_selection_rule:selected_traditional_complete_component_layer | 14 | 14 | 0 | 189 | 189 | 179 | 179 | 0 |
| testament:NT | 856 | 856 | 0 | 14507 | 14268 | 14383 | 14094 | 528 |
| testament:OT | 1315 | 1315 | 0 | 31324 | 31323 | 27424 | 27423 | 2 |
| textual_fingerprint_locus:False | 2118 | 2118 | 0 | 44852 | 44625 | 40900 | 40617 | 510 |
| textual_fingerprint_locus:True | 53 | 53 | 0 | 979 | 966 | 907 | 900 | 20 |

### stratum

| Группа | Full verses | Proven verses | Deferred-only | Full original | Eligible original | Full target | Eligible target | Excluded nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| addition | 819 | 28 | 0 | 61 | 61 | 1926 | 1792 | 134 |
| adjectival_explication | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| adjectival_rendering | 5 | 5 | 0 | 7 | 7 | 5 | 5 | 0 |
| adjectival_restructuring | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| age_idiom | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| alignment_counterexample | 1 | 1 | 0 | 22 | 22 | 23 | 23 | 0 |
| analytic_future | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| analytic_tense | 4 | 4 | 0 | 7 | 7 | 14 | 14 | 0 |
| anaphoric_expansion | 2 | 2 | 0 | 3 | 3 | 7 | 7 | 0 |
| anaphoric_explication | 2 | 0 | 0 | 0 | 0 | 3 | 3 | 0 |
| article_genitive_group | 2 | 2 | 0 | 2 | 2 | 0 | 0 | 0 |
| article_lexical_expansion | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| article_noun_group | 6 | 6 | 0 | 9 | 9 | 0 | 0 | 0 |
| aspectual_expansion | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| blind_semantic_review | 98 | 98 | 0 | 2312 | 2312 | 1944 | 1944 | 0 |
| body_part_change | 1 | 1 | 0 | 3 | 3 | 3 | 3 | 0 |
| case_government | 11 | 10 | 0 | 31 | 31 | 20 | 20 | 0 |
| case_realization | 22 | 22 | 0 | 75 | 75 | 44 | 44 | 0 |
| case_restructuring | 2 | 2 | 0 | 3 | 3 | 1 | 1 | 0 |
| causal_connective | 2 | 2 | 0 | 3 | 3 | 5 | 5 | 0 |
| causative_recasting | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| clause_coordination | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| clause_relation | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| clause_restructuring | 1 | 1 | 0 | 4 | 4 | 4 | 4 | 0 |
| cohortative_motion_expansion | 1 | 1 | 0 | 1 | 1 | 4 | 4 | 0 |
| cohortative_particle_group | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| comparative_clause | 1 | 1 | 0 | 3 | 3 | 5 | 5 | 0 |
| comparative_frame | 1 | 1 | 0 | 2 | 2 | 3 | 3 | 0 |
| comparison | 3 | 3 | 0 | 6 | 6 | 5 | 5 | 0 |
| compositional_alignment | 24 | 24 | 0 | 85 | 85 | 46 | 46 | 0 |
| compound | 457 | 440 | 1 | 1044 | 1043 | 1033 | 1032 | 2 |
| compound_numeral | 2 | 2 | 0 | 4 | 4 | 2 | 2 | 0 |
| compound_time | 1 | 1 | 0 | 7 | 7 | 2 | 2 | 0 |
| conditional_expansion | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| conditional_particle_repetition | 1 | 1 | 0 | 1 | 1 | 3 | 3 | 0 |
| contextual_addressee_addition | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| contextual_demonstrative_addition | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| contextual_lexical_choice | 8 | 7 | 0 | 10 | 10 | 12 | 12 | 0 |
| contextual_location_addition | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| contextual_possessor_addition | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| contextual_private_speech_addition | 1 | 0 | 0 | 0 | 0 | 2 | 2 | 0 |
| coordination | 1 | 1 | 0 | 4 | 4 | 5 | 5 | 0 |
| copular_adjectival_expansion | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| copular_construction | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| copular_expression | 2 | 2 | 0 | 2 | 2 | 4 | 4 | 0 |
| copular_relative | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| correlative_expansion | 2 | 2 | 0 | 2 | 2 | 4 | 4 | 0 |
| dative_copular_expansion | 1 | 0 | 0 | 0 | 0 | 3 | 3 | 0 |
| dative_expansion | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| dative_group | 2 | 2 | 0 | 4 | 4 | 2 | 2 | 0 |
| dative_possessive_group | 1 | 1 | 0 | 3 | 3 | 2 | 2 | 0 |
| dative_pronominal_group | 2 | 2 | 0 | 4 | 4 | 2 | 2 | 0 |
| definiteness | 9 | 9 | 0 | 18 | 18 | 18 | 18 | 0 |
| deictic_expression | 3 | 3 | 0 | 10 | 10 | 10 | 10 | 0 |
| deictic_subject | 2 | 2 | 0 | 2 | 2 | 4 | 4 | 0 |
| deictic_time | 3 | 3 | 0 | 14 | 14 | 7 | 7 | 0 |
| derivation | 19 | 19 | 0 | 43 | 43 | 41 | 41 | 0 |
| derivational_rendering | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| direct_lexical | 94 | 94 | 0 | 364 | 364 | 364 | 364 | 0 |
| direct_object_marker_not_overt | 14 | 14 | 0 | 16 | 16 | 0 | 0 | 0 |
| directional_place | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| directional_pr_pronominal | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| directional_suffix | 6 | 6 | 0 | 18 | 18 | 16 | 16 | 0 |
| discontinuous_rendering | 2 | 2 | 0 | 2 | 2 | 5 | 5 | 0 |
| discourse_particle | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 0 |
| discourse_particle_omission | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| discourse_restructuring | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| distributive | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| duration_phrase | 1 | 1 | 0 | 2 | 2 | 3 | 3 | 0 |
| elliptical_predicate_explication | 2 | 0 | 0 | 0 | 0 | 4 | 4 | 0 |
| emphasis | 1 | 1 | 0 | 5 | 5 | 8 | 8 | 0 |
| existential_restructuring | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| existential_to_indefinite | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| explicit_object | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| explicit_original_null | 98 | 98 | 0 | 463 | 463 | 0 | 0 | 0 |
| explicit_source_null | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| explicit_subject | 13 | 12 | 0 | 12 | 12 | 25 | 25 | 0 |
| explicit_target_function | 12 | 0 | 0 | 0 | 0 | 14 | 14 | 0 |
| explicit_target_null | 43 | 0 | 0 | 0 | 0 | 83 | 83 | 0 |
| explicitation | 1 | 1 | 0 | 2 | 2 | 4 | 4 | 0 |
| fawn_deer_lexical_group | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| function_token | 54 | 0 | 0 | 0 | 0 | 92 | 92 | 0 |
| genitive_group | 2 | 2 | 0 | 2 | 2 | 0 | 0 | 0 |
| genitive_lexical_expansion | 1 | 1 | 0 | 1 | 1 | 3 | 3 | 0 |
| gentilic_recasting | 1 | 1 | 0 | 3 | 3 | 2 | 2 | 0 |
| government | 3 | 1 | 0 | 2 | 2 | 5 | 5 | 0 |
| government_shift | 2 | 2 | 0 | 6 | 6 | 5 | 5 | 0 |
| grammatical_expansion | 23 | 23 | 0 | 36 | 36 | 78 | 78 | 0 |
| grammatical_function | 4 | 4 | 0 | 5 | 5 | 0 | 0 | 0 |
| grammatical_function_not_overt | 99 | 99 | 0 | 239 | 239 | 0 | 0 | 0 |
| grouped_expression | 12 | 12 | 0 | 35 | 35 | 30 | 30 | 0 |
| idiom | 22 | 22 | 0 | 82 | 82 | 53 | 53 | 0 |
| idiomatic_armory_rendering | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| idiomatic_degree | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| idiomatic_fullness | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| idiomatic_object_explication | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| idiomatic_paraphrase | 2 | 2 | 0 | 3 | 3 | 4 | 4 | 0 |
| idiomatic_reflexive_particle | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| idiomatic_rendering | 4 | 4 | 0 | 7 | 7 | 11 | 11 | 0 |
| idiomatic_smooth_speech | 1 | 1 | 0 | 2 | 2 | 0 | 0 | 0 |
| idiomatic_translation | 1 | 1 | 0 | 5 | 5 | 2 | 2 | 0 |
| idiomatic_wine_house_rendering | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| impersonal_voice | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| implicit_destination_relation | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| inchoative_aspect | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| infinitive | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| infinitive_group | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| instrumental_group | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| interrogative | 2 | 2 | 0 | 3 | 3 | 2 | 2 | 0 |
| kinship | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| lexical_alignment | 33 | 33 | 0 | 566 | 566 | 607 | 607 | 0 |
| lexical_context | 32 | 32 | 0 | 211 | 211 | 214 | 214 | 0 |
| lexical_context_equivalence | 98 | 98 | 0 | 1850 | 1850 | 1861 | 1861 | 0 |
| lexical_derivation | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| lexical_divergence | 4 | 4 | 0 | 4 | 4 | 7 | 7 | 0 |
| lexical_expansion | 14 | 14 | 0 | 24 | 24 | 42 | 42 | 0 |
| lexical_generalization | 3 | 3 | 0 | 3 | 3 | 4 | 4 | 0 |
| lexical_mismatch | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| lexical_rendering | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| lexical_shift | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| lexical_substitution | 1 | 1 | 0 | 3 | 3 | 3 | 3 | 0 |
| lexical_uncertainty | 2 | 2 | 0 | 9 | 9 | 9 | 9 | 0 |
| location_expression | 1 | 1 | 0 | 5 | 5 | 6 | 6 | 0 |
| locative_case | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| locative_idiom | 1 | 1 | 0 | 3 | 3 | 2 | 2 | 0 |
| manual_adjudication | 278 | 277 | 0 | 2931 | 2931 | 1656 | 1656 | 0 |
| manual_semantic_alignment | 235 | 235 | 0 | 4160 | 4160 | 3832 | 3832 | 0 |
| many_to_many | 11 | 11 | 0 | 37 | 37 | 36 | 36 | 0 |
| many_to_one | 29 | 29 | 0 | 95 | 95 | 46 | 46 | 0 |
| measure_explication | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| merge_split | 1907 | 1855 | 6 | 8632 | 8586 | 11382 | 11309 | 119 |
| missing_whitespace | 2 | 2 | 0 | 5 | 5 | 3 | 3 | 0 |
| morphosyntactic_contraction | 15 | 15 | 0 | 51 | 51 | 25 | 25 | 0 |
| morphosyntactic_shift | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| multiple_strong | 292 | 288 | 0 | 1244 | 1244 | 859 | 859 | 0 |
| named_entity | 1081 | 1073 | 0 | 2656 | 2653 | 2591 | 2581 | 13 |
| named_measure | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| negation | 9 | 9 | 0 | 16 | 16 | 16 | 16 | 0 |
| negation_compound | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| negative_concord | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| negative_coordination | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| negative_copula | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| negative_predicate | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| negative_purpose | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| negative_quantification | 2 | 2 | 0 | 7 | 7 | 8 | 8 | 0 |
| nominal_group | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| nominalization | 3 | 3 | 0 | 9 | 9 | 9 | 9 | 0 |
| nonlexical_source_marker | 33 | 33 | 0 | 136 | 136 | 0 | 0 | 0 |
| number_expansion | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| number_shift | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| numeral_mismatch | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| oath_formula_addition | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| omission | 1936 | 1928 | 8 | 8169 | 8067 | 155 | 155 | 102 |
| one_to_many | 28 | 25 | 0 | 43 | 43 | 99 | 99 | 0 |
| one_to_one | 35 | 35 | 0 | 395 | 395 | 396 | 396 | 0 |
| orthography | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 0 |
| overt_subject | 25 | 25 | 0 | 56 | 56 | 97 | 97 | 0 |
| participial_rendering | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| particle | 1847 | 1830 | 1 | 11233 | 11211 | 10161 | 10138 | 45 |
| particle_expansion | 1 | 1 | 0 | 2 | 2 | 4 | 4 | 0 |
| passive_voice | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| person_number | 2 | 2 | 0 | 8 | 8 | 15 | 15 | 0 |
| polarity | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| polarity_anomaly | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| polarity_recasting | 1 | 1 | 0 | 4 | 4 | 4 | 4 | 0 |
| polysemy | 1326 | 1284 | 11 | 3936 | 3893 | 4662 | 4606 | 99 |
| possessive | 29 | 29 | 0 | 105 | 105 | 97 | 97 | 0 |
| possessive_derivation | 2 | 2 | 0 | 4 | 4 | 4 | 4 | 0 |
| possessive_shift | 2 | 2 | 0 | 4 | 4 | 5 | 5 | 0 |
| predicate_restructuring | 2 | 2 | 0 | 2 | 2 | 4 | 4 | 0 |
| prepositional_expansion | 2 | 2 | 0 | 2 | 2 | 5 | 5 | 0 |
| prepositional_restructuring | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| pronominal_complement | 21 | 21 | 0 | 77 | 77 | 70 | 70 | 0 |
| pronominal_expansion | 1 | 1 | 0 | 1 | 1 | 3 | 3 | 0 |
| pronominal_explication | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| pronominal_subject | 1 | 1 | 0 | 3 | 3 | 1 | 1 | 0 |
| pronoun_repetition | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| proper_name_component_omission | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| proper_name_group | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| proper_place_mismatch | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| purpose_clause | 4 | 4 | 0 | 8 | 8 | 8 | 8 | 0 |
| rare_lemma | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 0 |
| reciprocal_target_accounting | 8 | 0 | 0 | 0 | 0 | 24 | 24 | 0 |
| referent_explication | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| reflexive | 3 | 3 | 0 | 12 | 12 | 8 | 8 | 0 |
| reflexive_group | 2 | 2 | 0 | 4 | 4 | 2 | 2 | 0 |
| reflexive_possessive | 5 | 5 | 0 | 15 | 15 | 14 | 14 | 0 |
| relative_clause | 4 | 3 | 0 | 5 | 5 | 8 | 8 | 0 |
| relative_conception_expansion | 1 | 1 | 0 | 1 | 1 | 5 | 5 | 0 |
| relative_expansion | 5 | 5 | 0 | 7 | 7 | 16 | 16 | 0 |
| relative_participle_expansion | 2 | 2 | 0 | 2 | 2 | 6 | 6 | 0 |
| relative_subject | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| reorder | 1679 | 1667 | 0 | 8955 | 8928 | 9755 | 9722 | 60 |
| repetition | 183 | 144 | 2 | 259 | 255 | 438 | 427 | 15 |
| resultative | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| resumptive_object | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| rhetorical_question | 1 | 1 | 0 | 4 | 4 | 4 | 4 | 0 |
| semantic_recasting | 1 | 1 | 0 | 4 | 4 | 3 | 3 | 0 |
| semantic_restructuring_requires_second_pass | 18 | 17 | 0 | 46 | 46 | 60 | 60 | 0 |
| semantic_uncertainty | 2 | 2 | 0 | 4 | 4 | 4 | 4 | 0 |
| source_component_not_overt | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| source_grammar | 25 | 25 | 0 | 70 | 70 | 0 | 0 | 0 |
| source_idiom | 1 | 1 | 0 | 5 | 5 | 2 | 2 | 0 |
| source_marker | 96 | 96 | 0 | 240 | 240 | 0 | 0 | 0 |
| source_merge_or_compound | 68 | 68 | 0 | 318 | 318 | 226 | 226 | 0 |
| source_tag_uncertainty | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| source_target_surface_issue | 2 | 2 | 0 | 4 | 4 | 2 | 2 | 0 |
| source_text_not_rendered | 132 | 132 | 0 | 368 | 368 | 0 | 0 | 0 |
| speaker_attribution_addition | 1 | 0 | 0 | 0 | 0 | 2 | 2 | 0 |
| subject_absorption | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| subject_clause | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| subject_expansion | 7 | 7 | 0 | 11 | 11 | 22 | 22 | 0 |
| subject_shift | 1 | 1 | 0 | 4 | 4 | 3 | 3 | 0 |
| subordinator_group | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| target_anomaly | 5 | 5 | 0 | 8 | 8 | 7 | 7 | 0 |
| target_split_or_expansion | 61 | 61 | 0 | 218 | 218 | 288 | 288 | 0 |
| temporal_addition | 2 | 0 | 0 | 0 | 0 | 4 | 4 | 0 |
| temporal_clause | 1 | 1 | 0 | 3 | 3 | 3 | 3 | 0 |
| temporal_connective | 2 | 2 | 0 | 2 | 2 | 3 | 3 | 0 |
| temporal_subordinator | 1 | 1 | 0 | 2 | 2 | 1 | 1 | 0 |
| tense_aspect | 4 | 2 | 0 | 3 | 3 | 4 | 4 | 0 |
| textual_variant | 565 | 524 | 24 | 2678 | 2582 | 2581 | 2467 | 210 |
| textual_variant_divergence | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| translation_addition | 26 | 0 | 0 | 0 | 0 | 29 | 29 | 0 |
| translation_choice | 1 | 1 | 0 | 22 | 22 | 19 | 19 | 0 |
| translation_omission | 14 | 14 | 0 | 22 | 22 | 0 | 0 | 0 |
| translation_paraphrase | 14 | 13 | 0 | 19 | 19 | 18 | 18 | 0 |
| unclassified | 1723 | 1723 | 0 | 10839 | 10816 | 10175 | 10157 | 41 |
| vocative_particle | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| vocative_split | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |
| vocative_superlative | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| volitive | 2 | 2 | 0 | 3 | 3 | 6 | 6 | 0 |
| volitive_group | 1 | 1 | 0 | 2 | 2 | 2 | 2 | 0 |
| word_split | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 0 |

### testament

| Группа | Full verses | Proven verses | Deferred-only | Full original | Eligible original | Full target | Eligible target | Excluded nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NT | 856 | 856 | 0 | 14507 | 14268 | 14383 | 14094 | 528 |
| OT | 1315 | 1315 | 0 | 31324 | 31323 | 27424 | 27423 | 2 |

### Source-frequency strata

Обязательная частотная страта проверена отдельным token-level доказательством из frozen original universe: только primary non-unresolved readings, rare ≤5 и frequent ≥1000 по исходному Strong classic. Используются exact selected original IDs; это исходная частотная характеристика, а не назначение Strong или gold-derived lexical training. Исходные reviewed phenomena не изменены. В частности, отсутствовавший reviewed tag frequent_lemma не добавлялся вручную. Deferred-only строки не входят в proven coverage.

| Band | Full verses | Proven verses | Deferred-only verses | Full original | Eligible original | Deferred original |
|---|---:|---:|---:|---:|---:|---:|
| frequent_1000_plus | 2058 | 2058 | 0 | 12701 | 12611 | 90 |
| mid_frequency | 2162 | 2162 | 0 | 17543 | 17426 | 117 |
| rare_1_to_5 | 938 | 933 | 5 | 1698 | 1678 | 20 |

Per-original source-frequency proof SHA256: `e3ffb38edb6a3b656aac7eae1813152e86cc6edafd3e84e606335ccbe1024c07`.

## Фиксированная оценка

Legacy и фиксированные методы оцениваются раздельно. Folds 0–3 и sealed fold 4 имеют отдельные artifacts; sealed оценивается только после freeze и завершения unsealed predecessor. Текущие модели, candidate files и thresholds не менялись по gold. Обучение, калибровка и promotion не выполнялись.

Общая frozen eligibility mask применяется до membership lookup, gold-derived statistics и метрик. Candidate hyperedge, касающийся deferred endpoint, исключается целиком, без прироста TP/FP/FN/support. Illegal IDs, cross-verse и duplicate IDs остаются ошибками. Legacy считает target/original/Strong identification; остальные методы — уникальные exact hyperedges. Эти единицы различаются.

| Канал | Folds | Метод | TP | FP | FN | Precision denominator | Recall denominator | Precision | Recall |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy | [0, 1, 2, 3] | legacy-zero-vote-v1 | 15520 | 9511 | 10964 | 25031 | 26484 | 62.0031% | 58.6014% |
| legacy | [4] | legacy-zero-vote-v1 | 4146 | 2477 | 2835 | 6623 | 6981 | 62.6000% | 59.3898% |
| fixed | [0, 1, 2, 3] | awesome-align-multilingual-contextual-v1 | 3857 | 7935 | 32146 | 11792 | 36003 | 32.7086% | 10.7130% |
| fixed | [0, 1, 2, 3] | bridge-full-group-surface-v1 | 501 | 1323 | 35502 | 1824 | 36003 | 27.4671% | 1.3916% |
| fixed | [0, 1, 2, 3] | ibm1-bidirectional-oof-v1 | 6019 | 2519 | 29984 | 8538 | 36003 | 70.4966% | 16.7181% |
| fixed | [0, 1, 2, 3] | local-uk-strong-description-lexical-v1 | 640 | 440 | 35363 | 1080 | 36003 | 59.2593% | 1.7776% |
| fixed | [0, 1, 2, 3] | transliteration-named-entity-v1 | 562 | 140 | 35441 | 702 | 36003 | 80.0570% | 1.5610% |
| fixed | [4] | awesome-align-multilingual-contextual-v1 | 1060 | 2091 | 8475 | 3151 | 9535 | 33.6401% | 11.1169% |
| fixed | [4] | bridge-full-group-surface-v1 | 133 | 319 | 9402 | 452 | 9535 | 29.4248% | 1.3949% |
| fixed | [4] | ibm1-bidirectional-oof-v1 | 1675 | 677 | 7860 | 2352 | 9535 | 71.2160% | 17.5669% |
| fixed | [4] | local-uk-strong-description-lexical-v1 | 190 | 122 | 9345 | 312 | 9535 | 60.8974% | 1.9927% |
| fixed | [4] | transliteration-named-entity-v1 | 174 | 47 | 9361 | 221 | 9535 | 78.7330% | 1.8249% |

В таблице legacy precision = unique_exact_precision с указанным TP+FP знаменателем. Дополнительная strict row precision учитывает каждое фактическое вхождение и имеет отдельный знаменатель; обе величины сохранены без смешения.

| Legacy partition | Correct occurrence rows | Eligible occurrence rows | Strict row precision |
|---|---:|---:|---:|
| unsealed | 15558 | 25100 | 61.9841% |
| sealed | 4148 | 6629 | 62.5735% |

### Coverage, exclusions и taxonomy

[legacy_unsealed manifest](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/legacy.evaluation.unsealed.v3/candidate_gold_evaluation.v3.manifest.json) / [details](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/legacy.evaluation.unsealed.v3/candidate_gold_evaluation.v3.jsonl)

Coverage: `{'original_link_null_decisions': {'deferred_excluded': 181, 'eligible_proven': 36097, 'full': 36278, 'proven_coverage': 0.9950107503169965}, 'selected_verse_count': 1722, 'target_accounting': {'deferred_excluded': 236, 'eligible_proven': 32828, 'full': 33064, 'proven_coverage': 0.992862327607065}, 'targets_or_classifiers_inflate_original_decision_count': False}`

Counts: `{'candidate_rows_read': 440280, 'evaluated_candidate_rows': 25100, 'excluded_deferred_candidate_rows': 220, 'outside_frozen_gold_refs': 325333, 'outside_requested_folds': 89627}`

Excluded from all metrics: `{'legacy-zero-vote-v1': {'candidate_rows': 220, 'legacy_strong_occurrences': 220}}`

`legacy-zero-vote-v1` taxonomy: `{'ambiguous': 49, 'correct': 15520, 'incorrect': 9462}`; duplicate semantic rows (separate, no metric inflation): **69**.

[legacy_sealed manifest](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/legacy.evaluation.sealed.v3/candidate_gold_evaluation.v3.manifest.json) / [details](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/legacy.evaluation.sealed.v3/candidate_gold_evaluation.v3.jsonl)

Coverage: `{'original_link_null_decisions': {'deferred_excluded': 59, 'eligible_proven': 9494, 'full': 9553, 'proven_coverage': 0.9938239296556056}, 'selected_verse_count': 449, 'target_accounting': {'deferred_excluded': 54, 'eligible_proven': 8689, 'full': 8743, 'proven_coverage': 0.9938236303328377}, 'targets_or_classifiers_inflate_original_decision_count': False}`

Counts: `{'candidate_rows_read': 440280, 'evaluated_candidate_rows': 6629, 'excluded_deferred_candidate_rows': 47, 'outside_frozen_gold_refs': 82951, 'outside_requested_folds': 350653}`

Excluded from all metrics: `{'legacy-zero-vote-v1': {'candidate_rows': 47, 'legacy_strong_occurrences': 47}}`

`legacy-zero-vote-v1` taxonomy: `{'ambiguous': 13, 'correct': 4146, 'incorrect': 2464}`; duplicate semantic rows (separate, no metric inflation): **6**.

[fixed_unsealed manifest](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/fixed.evaluation.unsealed.v3/candidate_gold_evaluation.v3.manifest.json) / [details](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/fixed.evaluation.unsealed.v3/candidate_gold_evaluation.v3.jsonl)

Coverage: `{'original_link_null_decisions': {'deferred_excluded': 181, 'eligible_proven': 36097, 'full': 36278, 'proven_coverage': 0.9950107503169965}, 'selected_verse_count': 1722, 'target_accounting': {'deferred_excluded': 236, 'eligible_proven': 32828, 'full': 33064, 'proven_coverage': 0.992862327607065}, 'targets_or_classifiers_inflate_original_decision_count': False}`

Counts: `{'candidate_rows_read': 431745, 'evaluated_candidate_rows': 23936, 'excluded_deferred_candidate_rows': 235, 'outside_frozen_gold_refs': 319760, 'outside_requested_folds': 87814}`

Excluded from all metrics: `{'awesome-align-multilingual-contextual-v1': {'candidate_rows': 171, 'legacy_strong_occurrences': 0}, 'bridge-full-group-surface-v1': {'candidate_rows': 22, 'legacy_strong_occurrences': 0}, 'ibm1-bidirectional-oof-v1': {'candidate_rows': 34, 'legacy_strong_occurrences': 0}, 'local-uk-strong-description-lexical-v1': {'candidate_rows': 8, 'legacy_strong_occurrences': 0}}`

`awesome-align-multilingual-contextual-v1` taxonomy: `{'cross_gold_group_endpoints': 7402, 'exact_complete_hyperedge': 3857, 'incomplete_or_wrong_group_endpoints': 533}`; duplicate semantic rows (separate, no metric inflation): **0**.

`bridge-full-group-surface-v1` taxonomy: `{'cross_gold_group_endpoints': 1234, 'exact_complete_hyperedge': 501, 'incomplete_or_wrong_group_endpoints': 89}`; duplicate semantic rows (separate, no metric inflation): **0**.

`ibm1-bidirectional-oof-v1` taxonomy: `{'cross_gold_group_endpoints': 1757, 'exact_complete_hyperedge': 6019, 'incomplete_or_wrong_group_endpoints': 762}`; duplicate semantic rows (separate, no metric inflation): **0**.

`local-uk-strong-description-lexical-v1` taxonomy: `{'cross_gold_group_endpoints': 351, 'exact_complete_hyperedge': 640, 'incomplete_or_wrong_group_endpoints': 89}`; duplicate semantic rows (separate, no metric inflation): **0**.

`transliteration-named-entity-v1` taxonomy: `{'cross_gold_group_endpoints': 107, 'exact_complete_hyperedge': 562, 'incomplete_or_wrong_group_endpoints': 33}`; duplicate semantic rows (separate, no metric inflation): **0**.

[fixed_sealed manifest](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/fixed.evaluation.sealed.v3/candidate_gold_evaluation.v3.manifest.json) / [details](../../work/ukrainian_stage_7_20260801/session_global_20261017_evaluation_author_01/fixed.evaluation.sealed.v3/candidate_gold_evaluation.v3.jsonl)

Coverage: `{'original_link_null_decisions': {'deferred_excluded': 59, 'eligible_proven': 9494, 'full': 9553, 'proven_coverage': 0.9938239296556056}, 'selected_verse_count': 449, 'target_accounting': {'deferred_excluded': 54, 'eligible_proven': 8689, 'full': 8743, 'proven_coverage': 0.9938236303328377}, 'targets_or_classifiers_inflate_original_decision_count': False}`

Counts: `{'candidate_rows_read': 431745, 'evaluated_candidate_rows': 6488, 'excluded_deferred_candidate_rows': 70, 'outside_frozen_gold_refs': 81256, 'outside_requested_folds': 343931}`

Excluded from all metrics: `{'awesome-align-multilingual-contextual-v1': {'candidate_rows': 43, 'legacy_strong_occurrences': 0}, 'bridge-full-group-surface-v1': {'candidate_rows': 5, 'legacy_strong_occurrences': 0}, 'ibm1-bidirectional-oof-v1': {'candidate_rows': 18, 'legacy_strong_occurrences': 0}, 'local-uk-strong-description-lexical-v1': {'candidate_rows': 4, 'legacy_strong_occurrences': 0}}`

`awesome-align-multilingual-contextual-v1` taxonomy: `{'cross_gold_group_endpoints': 1966, 'exact_complete_hyperedge': 1060, 'incomplete_or_wrong_group_endpoints': 125}`; duplicate semantic rows (separate, no metric inflation): **0**.

`bridge-full-group-surface-v1` taxonomy: `{'cross_gold_group_endpoints': 296, 'exact_complete_hyperedge': 133, 'incomplete_or_wrong_group_endpoints': 23}`; duplicate semantic rows (separate, no metric inflation): **0**.

`ibm1-bidirectional-oof-v1` taxonomy: `{'cross_gold_group_endpoints': 456, 'exact_complete_hyperedge': 1675, 'incomplete_or_wrong_group_endpoints': 221}`; duplicate semantic rows (separate, no metric inflation): **0**.

`local-uk-strong-description-lexical-v1` taxonomy: `{'cross_gold_group_endpoints': 99, 'exact_complete_hyperedge': 190, 'incomplete_or_wrong_group_endpoints': 23}`; duplicate semantic rows (separate, no metric inflation): **0**.

`transliteration-named-entity-v1` taxonomy: `{'cross_gold_group_endpoints': 40, 'exact_complete_hyperedge': 174, 'incomplete_or_wrong_group_endpoints': 7}`; duplicate semantic rows (separate, no metric inflation): **0**.

### Candidate eligibility coverage

Знаменатель этой coverage — candidate rows внутри frozen gold refs и данного fold partition до deferral mask. Outside-gold и outside-fold rows показаны отдельно в counts. Это coverage применения маски; recall gold labels имеет собственный знаменатель в основной таблице.

| Канал | Partition | Метод | Внутри full grid | Eligible rows | Excluded whole rows | Eligible coverage |
|---|---|---|---:|---:|---:|---:|
| legacy | unsealed | legacy-zero-vote-v1 | 25320 | 25100 | 220 | 99.1311% |
| legacy | sealed | legacy-zero-vote-v1 | 6676 | 6629 | 47 | 99.2960% |
| fixed | unsealed | awesome-align-multilingual-contextual-v1 | 11963 | 11792 | 171 | 98.5706% |
| fixed | unsealed | bridge-full-group-surface-v1 | 1846 | 1824 | 22 | 98.8082% |
| fixed | unsealed | ibm1-bidirectional-oof-v1 | 8572 | 8538 | 34 | 99.6034% |
| fixed | unsealed | local-uk-strong-description-lexical-v1 | 1088 | 1080 | 8 | 99.2647% |
| fixed | unsealed | transliteration-named-entity-v1 | 702 | 702 | 0 | 100.0000% |
| fixed | sealed | awesome-align-multilingual-contextual-v1 | 3194 | 3151 | 43 | 98.6537% |
| fixed | sealed | bridge-full-group-surface-v1 | 457 | 452 | 5 | 98.9059% |
| fixed | sealed | ibm1-bidirectional-oof-v1 | 2370 | 2352 | 18 | 99.2405% |
| fixed | sealed | local-uk-strong-description-lexical-v1 | 316 | 312 | 4 | 98.7342% |
| fixed | sealed | transliteration-named-entity-v1 | 221 | 221 | 0 | 100.0000% |

### Support редких и частых страт

Поддержка выражена в gold hyperedges для fixed и target/original/Strong triples для legacy; это разные единицы. Reviewed rare_lemma и source-frequency rare_lemma — отдельные страты. Отсутствующая в данном partition страта имеет support 0. Нулевой или малый support сохраняется в метриках и не даёт основания для автоматического назначения Strong.

| Канал | Partition | Метод | Reviewed rare support | Source rare support | Source frequent support |
|---|---|---|---:|---:|---:|
| legacy | unsealed | legacy-zero-vote-v1 | 0 | 1755 | 9176 |
| legacy | sealed | legacy-zero-vote-v1 | 2 | 405 | 2389 |
| fixed | unsealed | awesome-align-multilingual-contextual-v1 | 0 | 1353 | 9878 |
| fixed | unsealed | bridge-full-group-surface-v1 | 0 | 1353 | 9878 |
| fixed | unsealed | ibm1-bidirectional-oof-v1 | 0 | 1353 | 9878 |
| fixed | unsealed | local-uk-strong-description-lexical-v1 | 0 | 1353 | 9878 |
| fixed | unsealed | transliteration-named-entity-v1 | 0 | 1353 | 9878 |
| fixed | sealed | awesome-align-multilingual-contextual-v1 | 2 | 312 | 2627 |
| fixed | sealed | bridge-full-group-surface-v1 | 2 | 312 | 2627 |
| fixed | sealed | ibm1-bidirectional-oof-v1 | 2 | 312 | 2627 |
| fixed | sealed | local-uk-strong-description-lexical-v1 | 2 | 312 | 2627 |
| fixed | sealed | transliteration-named-entity-v1 | 2 | 312 | 2627 |

Недостаточный support и низкие показатели остаются результатом измерения; автоматического назначения Strong нет. Сохранённый global legacy quality report отдельно фиксирует 1457 duplicate original occurrences: эти прежние ошибки не превращены в доказанные labels.

До новой цепочки выполнен полный roster scan report/work: завершённых исторических candidate_gold_evaluation artifacts не найдено; отсутствие записано явно. Старые strict tools, подготовленные frozen fold labels и другие sealed evidence сохранены. Новые manifests содержат explicit supersedes контрактов и sealed→unsealed predecessor links.

## Проверки и воспроизведение

Входной [preflight](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/preflight.v1.json): stage 3 offline / 4 / 5 / 6 / 7 PASS до сборки; 5750 физических SHA/byte entries, mismatches 0. Исходный Git status clean. Stage-6 text/comment, stage-5 mapping, original selection, gold selection/folds и прежние reviewer answers сохраняются.

Независимая проверка использует собственные синтетические/adversarial probes и отдельный packet-derived payload accounting, а не только тесты авторов. Точные финальные regression/stage/docs/inventory/git результаты и их фактические receipts добавляются в HANDOFF после выполнения. Эта запись не объявляет будущие проверки пройденными.

Flutter/runtime, SQLite, working/web DB, dependencies, localization, release version, production Strong, stage 8, commit и push не затронуты. Дополнительная филология уже зарегистрированных deferrals для завершения не требуется.


## Фактически завершённые заключительные проверки до inventory refresh

- Full Python regression: **457 tests PASS**; [receipt](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/final_regression.v5.json), source SHA/bytes всех 25 stage-7 tools неизменны после этого прогона.
- Author finalize/check-final и независимый exact byte reproduction PASS; [author receipt](../../work/ukrainian_stage_7_20260801/session_global_20261017_gold_author_01/gold_author_completion.v1.json), [независимое воспроизведение](../../work/ukrainian_stage_7_20260801/session_global_gold_20261017_independent_01/independent_gold_reproduction.v1.json).
- Independent payload audit: **1 106 708 checks PASS**, полный exact accounting/provenance/reciprocal unions/exclusions/source-frequency proof. Дополнительно actual active-overlay и rehashed deferred-promotion negatives, source-family review и независимый raw-candidate metric recomputation/replay: [независимый итоговый отчёт](gold_global_independent_validation.v1.ru.md).
- Stage 3 offline / 4 / 5 / 6 повторно PASS; [точные команды/логи](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/final_checks.v1.json). Stage 7 входной check PASS до сборки; заключительный readonly check после inventory записывается отдельно в HANDOFF.
- Docs sync, forbidden patterns, navigation, scope/ignored-full-corpus check и git diff check PASS: [receipt](../../work/ukrainian_stage_7_20260801/session_global_20261017_root_01/final_documentation_checks.v2.json). Dart/Flutter format/analyze/test/smoke N/A: изменены только Python tooling, evidence и docs; runtime, dependencies, localization и DB не менялись. Approved RU/EN architecture/testing pairs не изменены.
- Первый post-documentation run v1 сохранил FAIL: Python разрешил bare `dart` в старый Dart 3.5, не поддерживающий language version проекта. Без изменения gates выполнен отдельный v2 run с явным Flutter-bundled Dart 3.13.2, обе проверки PASS; первоначальный receipt и error logs сохранены.

Полный inventory обновляет отдельный `/root/artifact_inventory_writer` после завершения всех записей. Его фактический SHA/byte/roster результат и post-refresh stage-7 / check-final / git checks находятся в последнем HANDOFF; здесь будущий успех не объявлен.

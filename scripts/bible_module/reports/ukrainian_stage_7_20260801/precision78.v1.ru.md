# 7.8 — precision feasibility и подготовка независимого аудита

Doc-Version: `1.0.0`
Last-Updated: `2026-10-17`
Source-Commit: `working-tree`

Результат первого deliverable: **STRUCTURAL_NO_GO при действующем контракте, A_auto=0**.
Feasibility matrix построена до обучения и новой разметки; затем выполнена только
структурная taxonomy ошибок development 0–2. Новый predictor, selector, reranker,
новые labels, acceptance и production Strong не создавались. Весь manual review 7.8,
статистическая сертификация и этап 7 остаются открыты.

## Доказанная причина остановки

В `2John` (13/13 стихов), `3John` (14/14), `Jude` (25/25), `Obad` (21/21)
и `Phlm` (25/25) весь текст уже входит в finalized reviewed frame v2.
После обязательного исключения прежних reviewed verses в каждой из этих пяти
книг **0 новых уникальных audit cases**. Это относится и ко всему saved candidate
union; abstention или выбор другой сохранённой decomposition не создаёт нового стиха.
Отсутствующая/пустая обязательная книга не считается пройденной.
Даже при 0 ошибок невозможно получить 539 допустимых новых наблюдений на книгу.
Этот контрпример достаточен для NO_GO; он не зависит от предположения об iid ошибок.
Новые генераторы также не устраняют отсутствие непросмотренных стихов этих пяти книг
при сохранении фиксированного OH1988-корпуса и нынешнего требования свежести.

Дополнительно **15 книг** и всего **31 observable strata** имеют fresh candidate ceiling <539; ещё 235 reviewed-phenomena rows имеют неизвестную новую membership и не могут сертифицироваться.

| Книга | Top-1 envelope | Fresh top-1 edges | Fresh candidate union edges | Требуется Wilson при0 ошибок |
|---|---:|---:|---:|---:|
| 2John | 142 | 0 | 0 | 539 |
| 2Pet | 613 | 285 | 422 | 539 |
| 2Thess | 478 | 135 | 214 | 539 |
| 3John | 119 | 0 | 0 | 539 |
| Hab | 394 | 155 | 190 | 539 |
| Hag | 413 | 69 | 98 | 539 |
| Joel | 606 | 329 | 423 | 539 |
| Jonah | 491 | 155 | 206 | 539 |
| Jude | 256 | 0 | 0 | 539 |
| Mal | 549 | 236 | 305 | 539 |
| Nah | 351 | 131 | 154 | 539 |
| Obad | 204 | 0 | 0 | 539 |
| Phlm | 215 | 0 | 0 | 539 |
| Titus | 378 | 119 | 160 | 539 |
| Zeph | 474 | 184 | 240 | 539 |

## Популяции и наблюдения

Реальный A_auto сейчас пуст: его precision и confidence bound undefined.
Поскольку новый selector не обучался, размер будущего A неизвестен. Для проверки
достижимости использована заведомо щедрая **верхняя популяция A: все eligible
frozen top-1 hyperedges**, без score/class filtering. Это 297767
уникальных полных semantic edges в 31100 стихах. Отдельный более
широкий envelope для saved-candidate reranker: 401687 edges.
Предложений в фактически замороженном A здесь нет; envelope не является новой policy.

Всего graph содержит 31102 стиха, reviewed frame 2171; вне него 28931 стих.
Новые top-1 audit cases: 277223 edges в 28929 стихах;
новый candidate union ceiling: 373752 edges.
Два стиха без top-1 не становятся NULL и не дают наблюдений precision.
296 candidate edges с любым deferred endpoint исключены целиком до семантики.

Свежесть проверена по union всех refs eligibility mask v2, включая deferred,
а не только по development. Это подтверждённый минимальный exposure exclusion:
неучтённые прежние просмотры могут только уменьшить доступную популяцию.
Числа lexical components — induced connectivity по verse OR original family/lemma
OR Strong atoms OR OH comparison form, как в7.7. Для top-1 envelope компонентов
7, для его fresh subset 7.
Они не объявлены независимыми; их число не подставляется в edge Wilson и не заменяет
estimand edge precision. Many-to-many/shared declarations/multiplicity не раскладываются
на дополнительные наблюдения. Legacy остаётся zero-vote.

## Все обязательные strata

Точный roster: **341 strata 7.7  + global =342**: books 66, testament 3,
genre 9, source_frequency 4, reviewed phenomena 235, relation 8, anomaly 11, evidence 5.
Это overlapping reporting/certification domains; их нельзя складывать или выдавать
за disjoint sampling strata. Missing и нулевые строки сохранены.

В таблице N_top — предполагаемая верхняя популяция A и одновременно число её
уникальных semantic edges; N_union — уникальные edges всего eligible graph.
V/C относятся **только к top-1 envelope**; F_top/F_union — ещё не использованные
cases за пределами reviewed frame; FV/FC — fresh top-1 стихи/компоненты.
W0 — неизменный номинальный support 539 при0 ошибок.
D0 — zero-error минимум exact hypergeometric при alpha=.05/342 **для гипотетического
известного finite frame размера F_top**. Это арифметический ориентир на envelope,
а не рассчитанный бюджет будущего A, sampling plan или доказательство применимости.
Для 235 `reviewed:*` membership нового корпуса unknown до независимой разметки:
числа не заменены нулями или model predictions; общий fresh union ceiling 373752
сохранён отдельно в JSON для каждой такой строки.

Статусы: `NO_GO` — F_union<539; `ceiling` — достаточная верхняя численность,
но сертификация не получена; `unknown` — membership не установлена.
Selector-specific underpower F_top<539 дополнительно записан в JSON.

| Stratum | N_top | N_union | V | C | F_top | F_union | FV | FC | W0 | D0 | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| global | 297767 | 401687 | 31100 | 7 | 277223 | 373752 | 28929 | 7 | 539 | 1755 | ceiling |
| anomaly:explicit_conflict | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:mapping:1:1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:mapping:merge | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:mapping:missing | 297767 | 401687 | 31100 | 7 | 277223 | 373752 | 28929 | 7 | 539 | 1755 | ceiling |
| anomaly:mapping:other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:mapping:split | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:none | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:reading:missing | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:reading:nonprimary_or_unresolved | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| anomaly:reading:primary | 297767 | 401687 | 31100 | 7 | 277223 | 373752 | 28929 | 7 | 539 | 1755 | ceiling |
| anomaly:textual_alternative | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:1Chr | 8901 | 12129 | 942 | 5 | 8597 | 11703 | 910 | 5 | 539 | 1593 | ceiling |
| book:1Cor | 4006 | 5958 | 437 | 1 | 3742 | 5556 | 404 | 1 | 539 | 1388 | ceiling |
| book:1John | 1270 | 1900 | 105 | 1 | 875 | 1305 | 72 | 1 | 539 | 724 | ceiling |
| book:1Kgs | 9565 | 12845 | 816 | 1 | 9163 | 12312 | 783 | 1 | 539 | 1597 | ceiling |
| book:1Pet | 961 | 1392 | 105 | 1 | 668 | 970 | 73 | 1 | 539 | 594 | ceiling |
| book:1Sam | 9947 | 13731 | 810 | 1 | 9528 | 13147 | 775 | 1 | 539 | 1598 | ceiling |
| book:1Thess | 866 | 1264 | 89 | 1 | 554 | 810 | 57 | 1 | 539 | 524 | ceiling |
| book:1Tim | 974 | 1388 | 113 | 1 | 674 | 952 | 80 | 1 | 539 | 599 | ceiling |
| book:2Chr | 9833 | 13167 | 822 | 1 | 9430 | 12634 | 788 | 1 | 539 | 1581 | ceiling |
| book:2Cor | 2577 | 3739 | 257 | 1 | 2274 | 3298 | 223 | 1 | 539 | 1182 | ceiling |
| book:2John | 142 | 204 | 13 | 1 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:2Kgs | 8834 | 11893 | 719 | 1 | 8430 | 11345 | 687 | 1 | 539 | 1562 | ceiling |
| book:2Pet | 613 | 864 | 61 | 1 | 285 | 422 | 29 | 1 | 539 | 282 | NO_GO |
| book:2Sam | 8225 | 11394 | 695 | 5 | 7825 | 10857 | 662 | 5 | 539 | 1547 | ceiling |
| book:2Thess | 478 | 704 | 47 | 1 | 135 | 214 | 15 | 1 | 539 | 135 | NO_GO |
| book:2Tim | 727 | 1012 | 83 | 1 | 439 | 604 | 51 | 1 | 539 | 415 | ceiling |
| book:3John | 119 | 177 | 14 | 1 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:Acts | 10428 | 14620 | 1007 | 1 | 10015 | 14054 | 968 | 1 | 539 | 1589 | ceiling |
| book:Amos | 1408 | 1869 | 146 | 1 | 1093 | 1460 | 114 | 1 | 539 | 841 | ceiling |
| book:Col | 903 | 1268 | 95 | 1 | 613 | 890 | 62 | 1 | 539 | 545 | ceiling |
| book:Dan | 3424 | 4287 | 357 | 1 | 3160 | 3962 | 325 | 1 | 539 | 1338 | ceiling |
| book:Deut | 10172 | 13496 | 959 | 1 | 9836 | 13057 | 926 | 1 | 539 | 1589 | ceiling |
| book:Eccl | 1862 | 2356 | 222 | 1 | 1589 | 2008 | 190 | 1 | 539 | 1060 | ceiling |
| book:Eph | 1410 | 1945 | 155 | 1 | 1120 | 1553 | 123 | 1 | 539 | 862 | ceiling |
| book:Esth | 2055 | 2770 | 167 | 1 | 1650 | 2226 | 135 | 1 | 539 | 1029 | ceiling |
| book:Exod | 12054 | 16127 | 1212 | 2 | 11723 | 15675 | 1180 | 2 | 539 | 1626 | ceiling |
| book:Ezek | 12994 | 17143 | 1273 | 1 | 12660 | 16704 | 1241 | 1 | 539 | 1628 | ceiling |
| book:Ezra | 2606 | 3417 | 280 | 2 | 2273 | 2976 | 248 | 2 | 539 | 1182 | ceiling |
| book:Gal | 1341 | 2008 | 149 | 3 | 1047 | 1567 | 117 | 3 | 539 | 805 | ceiling |
| book:Gen | 15662 | 20895 | 1533 | 1 | 15313 | 20424 | 1500 | 1 | 539 | 1656 | ceiling |
| book:Hab | 394 | 514 | 56 | 2 | 155 | 190 | 24 | 4 | 539 | 155 | NO_GO |
| book:Hag | 413 | 603 | 38 | 1 | 69 | 98 | 6 | 1 | 539 | 69 | NO_GO |
| book:Heb | 2811 | 3926 | 303 | 1 | 2535 | 3532 | 271 | 1 | 539 | 1247 | ceiling |
| book:Hos | 1645 | 2081 | 197 | 2 | 1391 | 1771 | 165 | 2 | 539 | 995 | ceiling |
| book:Isa | 10853 | 13874 | 1292 | 3 | 10580 | 13513 | 1258 | 3 | 539 | 1620 | ceiling |
| book:Jas | 1032 | 1433 | 108 | 1 | 743 | 1052 | 76 | 1 | 539 | 660 | ceiling |
| book:Jer | 14885 | 19859 | 1364 | 1 | 14528 | 19386 | 1332 | 1 | 539 | 1652 | ceiling |
| book:Job | 5600 | 7003 | 1069 | 2 | 5445 | 6810 | 1037 | 1 | 539 | 1470 | ceiling |
| book:Joel | 606 | 792 | 73 | 1 | 329 | 423 | 41 | 1 | 539 | 325 | NO_GO |
| book:John | 9352 | 13562 | 879 | 1 | 8984 | 13036 | 843 | 1 | 539 | 1597 | ceiling |
| book:Jonah | 491 | 623 | 48 | 1 | 155 | 206 | 16 | 1 | 539 | 155 | NO_GO |
| book:Josh | 7421 | 9872 | 658 | 2 | 7060 | 9380 | 626 | 2 | 539 | 1532 | ceiling |
| book:Jude | 256 | 362 | 25 | 1 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:Judg | 7375 | 9890 | 618 | 1 | 6957 | 9327 | 585 | 1 | 539 | 1548 | ceiling |
| book:Lam | 937 | 1176 | 154 | 3 | 749 | 933 | 122 | 3 | 539 | 666 | ceiling |
| book:Lev | 8727 | 11764 | 859 | 1 | 8424 | 11352 | 827 | 1 | 539 | 1560 | ceiling |
| book:Luke | 11465 | 16026 | 1151 | 1 | 11145 | 15572 | 1112 | 1 | 539 | 1622 | ceiling |
| book:Mal | 549 | 722 | 55 | 1 | 236 | 305 | 23 | 1 | 539 | 233 | NO_GO |
| book:Mark | 6824 | 9585 | 678 | 1 | 6437 | 9053 | 638 | 1 | 539 | 1508 | ceiling |
| book:Mat | 10989 | 15481 | 1071 | 1 | 10587 | 14919 | 1032 | 1 | 539 | 1621 | ceiling |
| book:Mic | 949 | 1208 | 105 | 1 | 649 | 826 | 73 | 1 | 539 | 577 | ceiling |
| book:Nah | 351 | 438 | 47 | 2 | 131 | 154 | 15 | 2 | 539 | 131 | NO_GO |
| book:Neh | 4054 | 5330 | 406 | 2 | 3777 | 4979 | 374 | 2 | 539 | 1401 | ceiling |
| book:Num | 12459 | 16540 | 1288 | 1 | 12137 | 16110 | 1255 | 1 | 539 | 1632 | ceiling |
| book:Obad | 204 | 267 | 21 | 1 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:Phil | 981 | 1380 | 104 | 1 | 697 | 1001 | 72 | 1 | 539 | 620 | ceiling |
| book:Phlm | 215 | 311 | 25 | 1 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| book:Prov | 4452 | 5543 | 915 | 2 | 4284 | 5334 | 883 | 2 | 539 | 1413 | ceiling |
| book:Ps | 12590 | 15425 | 2461 | 4 | 12107 | 14835 | 2364 | 4 | 539 | 1628 | ceiling |
| book:Rev | 5673 | 7958 | 404 | 1 | 5156 | 7230 | 369 | 1 | 539 | 1482 | ceiling |
| book:Rom | 4189 | 6030 | 433 | 1 | 3875 | 5581 | 400 | 1 | 539 | 1380 | ceiling |
| book:Ruth | 954 | 1234 | 85 | 1 | 595 | 766 | 53 | 1 | 539 | 563 | ceiling |
| book:Song | 723 | 905 | 117 | 3 | 510 | 634 | 85 | 4 | 539 | 483 | ceiling |
| book:Titus | 378 | 536 | 46 | 1 | 119 | 160 | 14 | 1 | 539 | 119 | NO_GO |
| book:Zech | 2139 | 2843 | 211 | 1 | 1782 | 2359 | 179 | 1 | 539 | 1112 | ceiling |
| book:Zeph | 474 | 629 | 53 | 3 | 184 | 240 | 21 | 3 | 539 | 184 | NO_GO |
| evidence:lexical_description | 9865 | 13227 | 5318 | 162 | 8836 | 11835 | 4762 | 157 | 539 | 1571 | ceiling |
| evidence:missing | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| evidence:multilingual_contextual | 154717 | 207153 | 30620 | 74 | 143457 | 192210 | 28483 | 70 | 539 | 1750 | ceiling |
| evidence:parallel_translation | 142330 | 187024 | 30012 | 25 | 132788 | 174268 | 27910 | 24 | 539 | 1750 | ceiling |
| evidence:transliteration | 14101 | 18212 | 7905 | 221 | 13366 | 17289 | 7462 | 215 | 539 | 1647 | ceiling |
| genre:acts_narrative | 10428 | 14620 | 1007 | 1 | 10015 | 14054 | 968 | 1 | 539 | 1589 | ceiling |
| genre:apocalyptic | 5673 | 7958 | 404 | 1 | 5156 | 7230 | 369 | 1 | 539 | 1482 | ceiling |
| genre:epistle | 26249 | 37801 | 2767 | 1 | 20395 | 29467 | 2139 | 1 | 539 | 1688 | ceiling |
| genre:gospel_narrative | 38630 | 54654 | 3779 | 1 | 37153 | 52580 | 3625 | 1 | 539 | 1719 | ceiling |
| genre:historical_prose | 79770 | 107672 | 7018 | 6 | 75285 | 101652 | 6626 | 6 | 539 | 1739 | ceiling |
| genre:missing | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| genre:poetry_wisdom | 25227 | 31232 | 4784 | 6 | 23935 | 29621 | 4559 | 6 | 539 | 1694 | ceiling |
| genre:prophetic | 52716 | 68928 | 5490 | 1 | 47851 | 62530 | 4955 | 1 | 539 | 1725 | ceiling |
| genre:torah_prose_law | 59074 | 78822 | 5851 | 1 | 57433 | 76618 | 5688 | 1 | 539 | 1730 | ceiling |
| relation:grouped_expression | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| relation:many_to_many | 16700 | 44252 | 12798 | 110 | 15521 | 41077 | 11883 | 114 | 539 | 1658 | ceiling |
| relation:many_to_one | 13631 | 22061 | 10505 | 473 | 12725 | 20541 | 9794 | 473 | 539 | 1636 | ceiling |
| relation:one_to_many | 23154 | 40497 | 16081 | 189 | 21537 | 37716 | 14959 | 199 | 539 | 1687 | ceiling |
| relation:one_to_one | 244282 | 294877 | 31002 | 35 | 227440 | 274418 | 28836 | 34 | 539 | 1754 | ceiling |
| relation:original_omitted | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| relation:textual_alternative | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| relation:translation_addition | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |
| reviewed:addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:adjectival_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:adjectival_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:adjectival_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:age_idiom | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:alignment_counterexample | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:analytic_future | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:analytic_tense | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:anaphoric_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:anaphoric_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:article_genitive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:article_lexical_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:article_noun_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:aspectual_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:blind_semantic_review | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:body_part_change | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:case_government | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:case_realization | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:case_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:causal_connective | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:causative_recasting | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:clause_coordination | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:clause_relation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:clause_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:cohortative_motion_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:cohortative_particle_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:comparative_clause | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:comparative_frame | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:comparison | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:compositional_alignment | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:compound | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:compound_numeral | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:compound_time | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:conditional_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:conditional_particle_repetition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_addressee_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_demonstrative_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_lexical_choice | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_location_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_possessor_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:contextual_private_speech_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:coordination | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:copular_adjectival_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:copular_construction | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:copular_expression | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:copular_relative | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:correlative_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:dative_copular_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:dative_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:dative_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:dative_possessive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:dative_pronominal_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:definiteness | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:deictic_expression | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:deictic_subject | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:deictic_time | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:derivation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:derivational_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:direct_lexical | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:direct_object_marker_not_overt | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:directional_place | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:directional_pr_pronominal | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:directional_suffix | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:discontinuous_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:discourse_particle | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:discourse_particle_omission | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:discourse_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:distributive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:duration_phrase | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:elliptical_predicate_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:emphasis | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:existential_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:existential_to_indefinite | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_object | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_original_null | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_source_null | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_subject | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_target_function | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicit_target_null | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:explicitation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:fawn_deer_lexical_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:frequent_lemma | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:function_token | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:genitive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:genitive_lexical_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:gentilic_recasting | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:government | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:government_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:grammatical_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:grammatical_function | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:grammatical_function_not_overt | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:grouped_expression | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiom | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_armory_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_degree | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_fullness | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_object_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_paraphrase | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_reflexive_particle | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_smooth_speech | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_translation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:idiomatic_wine_house_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:impersonal_voice | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:implicit_destination_relation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:inchoative_aspect | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:infinitive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:infinitive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:instrumental_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:interrogative | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:kinship | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_alignment | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_context | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_context_equivalence | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_derivation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_divergence | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_generalization | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_mismatch | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_substitution | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:lexical_uncertainty | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:location_expression | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:locative_case | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:locative_idiom | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:manual_adjudication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:manual_semantic_alignment | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:many_to_many | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:many_to_one | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:measure_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:merge_split | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:missing_whitespace | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:morphosyntactic_contraction | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:morphosyntactic_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:multiple_strong | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:named_entity | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:named_measure | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negation_compound | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_concord | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_coordination | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_copula | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_predicate | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_purpose | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:negative_quantification | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:nominal_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:nominalization | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:nonlexical_source_marker | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:number_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:number_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:numeral_mismatch | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:oath_formula_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:omission | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:one_to_many | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:one_to_one | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:orthography | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:overt_subject | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:participial_rendering | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:particle | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:particle_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:passive_voice | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:person_number | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:polarity | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:polarity_anomaly | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:polarity_recasting | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:polysemy | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:possessive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:possessive_derivation | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:possessive_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:predicate_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:prepositional_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:prepositional_restructuring | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:pronominal_complement | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:pronominal_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:pronominal_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:pronominal_subject | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:pronoun_repetition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:proper_name_component_omission | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:proper_name_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:proper_place_mismatch | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:purpose_clause | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:rare_lemma | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:reciprocal_target_accounting | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:referent_explication | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:reflexive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:reflexive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:reflexive_possessive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:relative_clause | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:relative_conception_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:relative_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:relative_participle_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:relative_subject | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:reorder | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:repetition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:resultative | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:resumptive_object | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:rhetorical_question | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:semantic_recasting | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:semantic_restructuring_requires_second_pass | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:semantic_uncertainty | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_component_not_overt | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_grammar | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_idiom | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_marker | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_merge_or_compound | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_tag_uncertainty | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_target_surface_issue | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:source_text_not_rendered | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:speaker_attribution_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:subject_absorption | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:subject_clause | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:subject_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:subject_shift | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:subordinator_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:target_anomaly | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:target_split_or_expansion | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:temporal_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:temporal_clause | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:temporal_connective | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:temporal_subordinator | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:tense_aspect | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:textual_variant | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:textual_variant_divergence | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:translation_addition | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:translation_choice | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:translation_omission | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:translation_paraphrase | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:unclassified | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:vocative_particle | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:vocative_split | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:vocative_superlative | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:volitive | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:volitive_group | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| reviewed:word_split | ? | ? | ? | ? | ? | ? | ? | ? | 539 | ? | unknown |
| source_frequency:frequent_1000_plus | 90460 | 138578 | 26934 | 1 | 83932 | 128572 | 25020 | 1 | 539 | 1742 | ceiling |
| source_frequency:mid | 118377 | 163724 | 29519 | 9 | 109591 | 151414 | 27433 | 10 | 539 | 1748 | ceiling |
| source_frequency:rare_1_to_5 | 7959 | 11192 | 5373 | 1253 | 7207 | 10152 | 4862 | 1251 | 539 | 1527 | ceiling |
| source_frequency:unclassified | 85413 | 101027 | 22584 | 117 | 80498 | 95256 | 21295 | 113 | 539 | 1741 | ceiling |
| testament:NT | 80980 | 115033 | 7957 | 1 | 72719 | 103331 | 7101 | 1 | 539 | 1739 | ceiling |
| testament:OT | 216787 | 286654 | 23143 | 7 | 204504 | 270421 | 21828 | 7 | 539 | 1754 | ceiling |
| testament:missing | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 539 | ? | NO_GO |

## Статистический протокол и границы применимости

Номинальный Wilson gate сохраняется: one-sided95% LB≥0.995, не confidence99.5%.
Подтверждены минимумы 539/539 при0 ошибок и893/894 при1 ошибке.
Для342 одновременных Wilson assertions с Bonferroni минимум2611/2611 —
**отдельная более строгая sensitivity**, не автоматически обязательный W0 каждой строки.
В новом протоколе заранее выбран другой состав совместного контроля:
все 342 обязательных claims требуют nominal Wilson gate **и дополнительно**
familywise95% design-based bounds, alpha=.05/342 на claim. Union bound не требует
независимости между overlapping claims. Сам Wilson не объявляется exact или
валидным под произвольной зависимостью; без обоснованной применимости остаётся NO_GO.
Формула и one-sided z согласованы с [NIST](https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

Вероятностный аудит фиксированного корпуса может опираться на случайность отбора,
а не на iid языковых ошибок. Для SRS без повторов по известному замороженному
frame размера N с фиксированным числом ошибок D:

`P_D(X<=e) = sum_x C(D,x) C(N-D,n-x) / C(N,n)`.

Берётся максимальный D с `P_D(X<=e)>alpha`; lower precision = `(N-D)/N`.
Реализована эта консервативная one-sided tail inversion на integer combinations,
а не алгоритм minimum-width intervals из статьи. При n=N результат — точная
доля, но census не отменяет отдельный обязательный Wilson gate.
Распределение и support: [официальная документация R](https://search.r-project.org/R/refmans/stats/html/Hypergeometric.html);
более общий подход к exact hypergeometric confidence intervals:
[Bartroff, Lorden, Wang, v2](https://arxiv.org/abs/2109.05624v2).

Это не утверждает применимость к нашему ещё не созданному sample.
До labels нужны точные frame/domain IDs и digests, положительные известные inclusion
probabilities, fixed sample sizes/seed-generation procedure, sampling manifests,
правила missing и отдельное обоснование inference. Для conditional SRS внутри
overlapping domains должны быть известны domain membership и N_s для всего frame;
235 reviewed phenomena сейчас этому не удовлетворяют. Disproportionate stratified,
unequal-probability или cluster sampling нельзя анализировать одной naive
hypergeometric формулой. Требование согласовать sampling design и inference:
[Statistics Canada, sampling guidelines](https://www150.statcan.gc.ca/n1/pub/12-539-x/steps-etapes/4058330-eng.htm).

Исключение reviewed units даёт им inclusion probability0: fresh-only sample сам по
себе не сертифицирует весь payload, включающий reviewed units. Ограничение estimand
только свежим доменом оставляет пять обязательных книг пустыми. Для другого
estimand/сочетания известных reviewed totals и свежего аудита нужен отдельный
предзаданный протокол; текущий Wilson/freshness contract это не меняет.
Fixed payload certificate не переносится на будущую модель или другой перевод.

Бюджет надо планировать по мощности. При iid p=.999 шанс539/539 =58.3174%.
Это иллюстрация, не power для finite sampling design. По nominal Wilson:

| n | Максимум ошибок для passing | iid power приp=.999 |
|---|---:|---:|
| 539 | 0 | 58.3174% |
| 894 | 1 | 77.4697% |
| 1500 | 3 | 93.4452% |
| 2000 | 4 | 94.7437% |
| 2611 | 7 | 99.4561% |
| 3000 | 8 | 99.6217% |

Конечный sample budget сейчас **не существует**: protocol structural gate уже
непроходим. Нельзя складывать минимумы по overlapping strata и считать это бюджетом.
Для будущего допустимого design потребуются N_s, ожидаемые ошибки/nonresponse,
мощность совместных gates и allocation; minimum passing N этого не заменяет.

## Development и последующие действия

Разбор development0–2 сохранён в [taxonomy](precision78_development_taxonomy.v1.ru.md).
Из завершённого [отчёта7.6](consensus76.v1.ru.md), без нового старого evaluation:
candidate union содержит 7401 правильное ребро против 6479 у top-1;
922 — потенциально доступная разница, совместимость всех одновременно не доказана;
20061 gold edges вообще отсутствует в union. Retrieval coverage генераторов
7401/27462 =26.9500%. Новые precision выбранного подкласса и selection improvement
не измерялись: обучение остановлено structural gate.

Предварительный максимум экспериментов —3 простых evidence-based abstaining
selectors над frozen top-1 и1 reranker над сохранёнными candidates/decompositions;
фактически выполнено0. Цель — coverage при высокой precision. Dependency groups
сохраняют общее происхождение; производные одного источника не дают независимых votes.
Для будущей внутренней проверки held-out labels исключаются одновременно из
upstream prior, counts, feature fitting и reranker training. Старые OOF scores7.6
не дают nested leakage-free CV нового слоя. Допустимый дешёвый вариант — заранее
заданный development split с честным in-sample reporting. Folds3/4 — только history.
Generator changes — отдельная последующая ветка с собственным графом; frozen7.6
не подменяется. Structural NO_GO не запрещает улучшать B_review/manual workflow,
но не разрешает automatic acceptance.

Новая annotation cohort не создана. Если появится допустимый контракт, development
review отделяется от закрытой certification; blind pass1/pass2, adjudicator и QC
имеют разные фактические роли. Initial decisions не показывают confidence/class,
labels содержат полную semantic identity и source evidence. Missing/unresolved
остаются в sample и блокируют соответствующий gate, без замены удобным случаем.
Predictions не становятся labels, зарегистрированные deferrals не переоткрываются.

Порядок будущей окончательной проверки: development selection → freeze predictor,
calibrator/features/domain/thresholds → independent technical gate → closed validation
→ distinct final audit только после passing predecessors. Alpha spending между
validation/audit или final-only claim задаётся до labels. После раскрытия labels
threshold/domain/strata неизменны; optional top-up до passing запрещён без заранее
валидной sequential процедуры. Сейчас эти фазы имеют явный `NOT_STARTED`, а не PASS.

## Evidence chain и воспроизведение

Автор реализации `/root`; отдельный reviewer `/root/precision78_independent` не
пишет author code; inventory writer `/root/precision78_inventory` не автор/QC.
Blind annotators/adjudicator отсутствуют, поскольку новая annotation остановлена.
Reading existing labels означает inspection, не авторство и не новый blind pass.
Frozen7.4/7.6/7.7, gold/mask/folds, старые claims и SHA-bound report/log сохраняются.

[Независимый raw recount и статистический QC](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_independent_01/independent_review.v1.ru.md),
[его SHA-manifest](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_independent_01/independent_validation.v1.manifest.json).

- [Preflight6279/stages3–7](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/preflight.v1.json).

- [Protocol lock](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/protocol.v1.lock.json).

- [Input lock](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/inputs.v1.lock.json).

- [Source/runtime lock](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/source_runtime.v1.lock.json).

- [Полная machine-readable matrix](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/feasibility.v1.json).

- [Unique frame](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/frame.v1.jsonl).

- [Арифметика](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/arithmetic.v1.json).

- [Regression](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/regression.v1.json).

- [Workflow phase statuses](../../work/ukrainian_stage_7_20260801/session_precision78_20261017_root_01/workflow.v1.manifest.json).

Локально из корня репозитория: `python -X utf8 -B -m unittest discover -s scripts/bible_module/precision78/tests -q`.
CLI `preflight → lock → feasibility → taxonomy` пишет эксклюзивно в каноническую
session; повторная запись sealed outputs отвергается. Для независимого воспроизведения
используются отдельные read-only QC scripts/receipts, не повтор старого evaluation.
Полные corpora и технические payload остаются в gitignored work. Новых зависимостей,
DB/runtime/локализации/routes/release changes нет. Применён `.github/change_checklist.md`:
Python regression вместо неприменимых Dart format/analyze/Flutter tests; docs sync,
forbidden patterns и навигация проверяются отдельно. Финальные QC/inventory receipts
и точная последняя последовательность записываются в [HANDOFF](HANDOFF.ru.md).

# LXX_TR: инвентарь оставшегося переноса LXX

Документ для личной работы над оставшимися пустыми OT/LXX ячейками после переноса утверждённых CrossWire LXX правил в `C:\Users\karna\Documents\revelation\db\bible_lxx_tr.sqlite`.

## Текущее состояние БД

- Метаданные БД: `schema_version=2`, `data_version=4`, `date=2026-05-30T17:10:10Z`.
- Покрытие всего модуля: `30819/31102` стихов = `99.090%`.
- Покрытие OT/LXX: `22862/23145` стихов = `98.777%`.
- Осталось пустых OT-ячеек: `283`.
- `verse_key` проверены против `assets/data/bible_verse_map.json`: ключи БД совпадают с 3-символьной base36 KJV/protestant сеткой от `001` до `NZY`.

## Уже применённые входные данные переноса

- `lxx_to_kjv_consolidated_remaining_work.json` -> `projection_inputs.versification_candidate_map`: whole-verse и source-exclusion карта проекции.
- `lxx_to_kjv_consolidated_remaining_work.json` -> `projection_inputs.token_span_rules_generated`: уже применённые exact token-span/merge правила.
- `lxx_to_kjv_consolidated_remaining_work.json` -> `projection_inputs.token_span_rules_manual`: уже применённые ручные правила Daniel Theodotion x-2 и Isaiah canonical-prefix.
- `lxx_to_kjv_consolidated_remaining_work.json` -> `projection_inputs.token_span_rules_unmatched`: оставшиеся случаи, где exact-pass не дал безопасной границы.

## Категории оставшихся мест

- `confirmed_control_absence_or_semantic_difference`: `198` - нет отдельной LXX-семантической строки в проверенных контролях.
  Смысл: Похоже на MT/KJV-семантическую строку без отдельного LXX/OG соответствия в проверенных контролях.
- `token_span_merge_or_placement_required`: `39` - нужно вручную выбрать token-span/merge внутри CrossWire.
  Смысл: Текст, скорее всего, уже находится в CrossWire LXX, но он склеен с соседним материалом, переставлен или требует точного ручного выбора границ токенов.
- `crosswire_specific_omission_present_in_lxx_control`: `24` - нет в CrossWire, но есть в контрольном LXX-свидетеле.
  Смысл: Контрольные LXX-страницы показывают греческий материал, но именно наш CrossWire ZIP не содержит переносимую строку в нужном виде.
- `witness_sensitive_crosswire_omission`: `19` - пропуск зависит от выбранного LXX-свидетеля.
  Смысл: Разные LXX-свидетели расходятся; перед импортом нужно явно выбрать свидетель или текстовую политику.
- `addition_preservation_policy_required`: `2` - нужна политика границы канонического текста и греческого добавления.
  Смысл: Канонический материал связан с греческим добавлением; нужно решить, можно ли отделять канонический префикс от addition-tail.
- `partial_crosswire_source_requires_repair_policy`: `1` - в CrossWire есть только частичный текст, нужна политика восстановления.
  Смысл: CrossWire даёт только частичный фрагмент; нельзя считать его финальным без отдельной политики partial-fill.

## Политика поиска замен и источников

- Для `token_span_merge_or_placement_required` текст, вероятно, уже есть внутри CrossWire LXX. Следующая работа - не поиск нового источника, а ручной выбор границ токенов.
- Для `crosswire_specific_omission_present_in_lxx_control` и `witness_sensitive_crosswire_omission` сначала искать другой LXX-свидетель/издание. Возможные направления: GreekDoc control witnesses, Cambridge/Swete, Rahlfs-Hanhart, Göttingen, CATSS/CCAT и другие лицензируемые морфологически размеченные LXX-датасеты. Импортировать только после проверки лицензии и стратегии Strong-разметки.
- Для `confirmed_control_absence_or_semantic_difference` нельзя молча подставлять соседний LXX-стих. Это похоже на MT/KJV-семантические строки без отдельного LXX/OG эквивалента в проверенных контролях. Консервативная замена - пустая ячейка и обработка в UI. Не-LXX греческая замена требует отдельного решения владельца: например Hexaplaric fragments/Aquila/Symmachus/Theodotion там, где они реально сохранились, поздняя греческая библейская традиция или явно помеченная современная ретроверсия. Всё это нельзя смешивать с LXX без видимого provenance.
- Для `addition_preservation_policy_required` текст связан с греческими добавлениями. Нужно решить, можно ли сохранять канонический префикс и отбрасывать addition-tail.
- Для `partial_crosswire_source_requires_repair_policy` частичный текст нельзя считать финальным без явной политики partial-fill.

## По книгам и главам

- `Gen`: `2` мест(а) (31:1, 35:1)
- `Exod`: `54` мест(а) (25:1, 28:4, 32:1, 35:4, 36:25, 37:12, 38:3, 39:1, 40:3)
- `Num`: `1` мест(а) (6:1)
- `Josh`: `10` мест(а) (6:1, 8:2, 10:2, 13:1, 15:1, 20:3)
- `1Sam`: `39` мест(а) (13:1, 17:26, 18:11, 23:1)
- `1Kgs`: `30` мест(а) (2:1, 4:1, 6:5, 7:1, 9:3, 11:4, 12:1, 13:1, 14:11, 15:2)
- `1Chr`: `15` мест(а) (1:14, 16:1)
- `2Chr`: `1` мест(а) (27:1)
- `Neh`: `14` мест(а) (3:1, 4:1, 11:9, 12:3)
- `Esth`: `5` мест(а) (4:1, 5:2, 9:2)
- `Job`: `1` мест(а) (23:1)
- `Ps`: `6` мест(а) (11:1, 29:1, 116:3, 138:1)
- `Prov`: `27` мест(а) (4:1, 8:1, 11:1, 15:1, 16:7, 18:2, 19:2, 20:9, 21:1, 22:1, 23:1)
- `Isa`: `2` мест(а) (2:1, 56:1)
- `Jer`: `66` мест(а) (7:1, 8:2, 10:4, 11:1, 17:4, 25:1, 27:5, 29:5, 30:4, 33:13, 39:10, 46:2, 48:3, 49:1, 51:4, 52:6)
- `Lam`: `4` мест(а) (3:4)
- `Ezek`: `6` мест(а) (1:1, 10:1, 27:1, 32:1, 33:1, 40:1)

## Подробный список

### Gen

#### Gen 31

- `Gen.31.51` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Gen.31.48.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: CrossWire source Gen.31.48 combines its ordinary heap-witness material with the behold-this-heap-and-pillar clause corresponding to target Gen.31.51. GreekDoc retains numbered 31.51. Token-span extraction is required during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Gen` (projection_inputs.token_span_rules_unmatched).
#### Gen 35

- `Gen.35.21` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire source Gen.35.21 resumes with target 35.22 Reuben/Bilhah content. GreekDoc preserves the journey-and-tent-beyond-tower-of-Edar target 35.21 row in both displayed Greek columns, so this is source-specific.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Gen` (lxx_to_kjv_genesis_remaining_target_resolution.json).
### Exod

#### Exod 25

- `Exod.25.6` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot ex25.html preserves the oil-for-light and spices row in both displayed witnesses. Whole-ZIP search finds no equivalent CrossWire source row; nearby matches are only thematic tabernacle material.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
#### Exod 28

- `Exod.28.23` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.28.23.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Breastplate chain, names, and attachment material is compressed and reordered in one CrossWire source verse.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.28.26` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.28.23.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Breastplate chain, names, and attachment material is compressed and reordered in one CrossWire source verse.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.28.27` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.28.23.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Breastplate chain, names, and attachment material is compressed and reordered in one CrossWire source verse.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.28.28` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.28.23.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Breastplate chain, names, and attachment material is compressed and reordered in one CrossWire source verse.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
#### Exod 32

- `Exod.32.9` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_as_distinct_kjv_semantic_row_in_lxx_control`.
  Исследовательская заметка: GreekDoc ex32.html has Alexandrinus N/A and Vaticanus text repeating the these-are-your-gods clause from the neighboring context, not the stiffnecked-people KJV semantic row.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
#### Exod 35

- `Exod.35.8` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_as_distinct_kjv_semantic_row_in_lxx_control`.
  Исследовательская заметка: GreekDoc ex35.html has Alexandrinus emerald-stones material and Vaticanus N/A, not the oil-for-light and spices KJV semantic row.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.35.17` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.35.11.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Court hangings and pillars occur inside the compressed source inventory.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.35.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_as_distinct_kjv_semantic_row_in_lxx_control`.
  Исследовательская заметка: GreekDoc ex35.html fills the control cells with shifted LXX 35.17 inventory material, not the tabernacle/court pins and cords KJV semantic row.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.35.19` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.35.15.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Holy garments line is present at the start of the compressed source verse.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
#### Exod 36

- `Exod.36.10` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.10 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.11 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.12 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.13` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.13 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.14 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.15 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.16 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.17 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.18 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.19 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.20` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.20 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.21` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.21 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.22` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.22 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.23` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.23 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.24` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.24 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.25` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.25 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.26 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.27` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.27 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.28 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.29` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.29 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.30 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.31` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.31 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.32` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.32 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.33` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.33 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.36.34` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 36.34 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
#### Exod 37

- `Exod.37.4` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.11.
  Статус из исследования: `represented_in_compact_source_requires_token_span_review`.
  Исследовательская заметка: Ark staves are combined with table staves in one source line.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.11` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.9.
  Статус из исследования: `represented_in_compact_source_not_distinct`.
  Исследовательская заметка: Table gold overlay is folded into the same source line as target 37.10.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.12 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.37.14` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.10.
  Статус из исследования: `represented_in_compact_source_not_distinct`.
  Исследовательская заметка: Ring placement for carrying the table is folded into the source line mapped to target 37.13.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.20` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.16.
  Статус из исследования: `represented_in_compact_source_not_distinct`.
  Исследовательская заметка: Lampstand bowl, knop, flower, and branch details are compressed into one source line.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.21` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.16.
  Статус из исследования: `represented_in_compact_source_not_distinct`.
  Исследовательская заметка: Lampstand bowl, knop, flower, and branch details are compressed into one source line.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.22` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.16.
  Статус из исследования: `represented_in_compact_source_not_distinct`.
  Исследовательская заметка: Lampstand bowl, knop, flower, and branch details are compressed into one source line.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.37.24` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.24 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.37.25` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.25 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.37.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.26 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.37.27` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.27 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.37.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 37.28 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
#### Exod 38

- `Exod.38.2` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.38.22.
  Статус из исследования: `represented_in_compact_source_requires_primary_placement`.
  Исследовательская заметка: Bronze altar construction is compressed into one source line spanning target 38.1-2.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
- `Exod.38.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 38.6 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.38.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 38.7 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
#### Exod 39

- `Exod.39.39` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Exod.39.9, Exod.39.15.
  Статус из исследования: `represented_or_partly_represented_requires_token_span_review`.
  Исследовательская заметка: Bronze altar/tool inventory is compressed or partially represented; exact placement requires reviewing source 39.9 and neighboring presentation lines.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (projection_inputs.token_span_rules_unmatched).
#### Exod 40

- `Exod.40.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 40.7 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.40.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 40.11 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
- `Exod.40.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 40.28 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Exod` (lxx_to_kjv_exodus_remaining_target_resolution.json).
### Num

#### Num 6

- `Num.6.27` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Num.6.23.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: CrossWire source Num.6.23 contains its ordinary blessing-introduction material followed by the putting-my-name-and-I-will-bless-them clause corresponding to target Num.6.27. GreekDoc preserves numbered 6.27 separately. Token-span extraction is required during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Num` (projection_inputs.token_span_rules_unmatched).
### Josh

#### Josh 6

- `Josh.6.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_as_distinct_kjv_semantic_row_in_lxx_control`.
  Исследовательская заметка: CrossWire source 6.4 resumes with target 6.5 content. GreekDoc shows either N/A or an opening segment of target 6.5 content under label 6.4, not the KJV 6.4 priests/seventh-day instruction. Related procession narrative occurs later.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
#### Josh 8

- `Josh.8.13` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target 8.13 N/A in the displayed LXX controls. CrossWire source 8.13 resumes with target 8.14 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
- `Josh.8.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target 8.26 N/A in the displayed LXX controls. CrossWire source 8.25 resumes with target 8.27 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
#### Josh 10

- `Josh.10.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the first Gilgal-return row 10.15 N/A in the displayed LXX controls. CrossWire source 10.15 resumes with target 10.16 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
- `Josh.10.43` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the second Gilgal-return row 10.43 N/A in the displayed LXX controls. CrossWire source chapter 10 ends after target 10.42 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
#### Josh 13

- `Josh.13.33` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the Levi-no-inheritance row 13.33 N/A in the displayed LXX controls. CrossWire source chapter 13 ends after target 13.32 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
#### Josh 15

- `Josh.15.59` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Josh.15.59.
  Статус из исследования: `represented_in_composite_source_row_requires_canonical_token_span_split`.
  Исследовательская заметка: CrossWire source Josh.15.59 contains canonical target 15.59 followed by OSIS milestone (59.a), matching GreekDoc 15:59a LXX-only city-list material. Keep target blank until canonical-prefix extraction.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (projection_inputs.token_span_rules_unmatched).
#### Josh 20

- `Josh.20.4` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_witness`.
  Исследовательская заметка: CrossWire omits the city-gate and elders procedure. GreekDoc is witness-sensitive: one displayed Greek column marks 20.4 N/A while another preserves the procedural row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
- `Josh.20.5` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_witness`.
  Исследовательская заметка: CrossWire omits the avenger-of-blood procedure. GreekDoc is witness-sensitive: one displayed Greek column marks 20.5 N/A while another preserves the procedural row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
- `Josh.20.6` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_witness`.
  Исследовательская заметка: CrossWire omits the congregation, high-priest-death, and return procedure. GreekDoc is witness-sensitive: one displayed Greek column marks 20.6 N/A while another preserves the procedural row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Josh` (lxx_to_kjv_joshua_remaining_target_resolution.json).
### 1Sam

#### 1Sam 13

- `1Sam.13.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: CrossWire source 13.1 aligns with KJV 13.2. GreekDoc polyglot 1sam13.html marks the reign-duration line at target 13.1 N/A in both Alexandrinus and Vaticanus controls.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
#### 1Sam 17

- `1Sam.17.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.13` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.20` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.21` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.22` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.23` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.24` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.25` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.27` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.29` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.31` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.41` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.50` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.55` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.56` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.57` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.17.58` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
#### 1Sam 18

- `1Sam.18.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.2` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.3` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.5` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.10` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
- `1Sam.18.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `short_greek_recension_lacks_long_mt_kjv_material`.
  Исследовательская заметка: Known minus in the shorter Greek 1 Samuel 17-18 account followed by CrossWire: do not synthesize the longer MT/KJV material into LXX text.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
#### 1Sam 23

- `1Sam.23.12` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: CrossWire source 23.12 aligns with KJV 23.13. GreekDoc polyglot 1sam23.html marks target 23.12 N/A in Alexandrinus but preserves the second Keilah-delivery question and answer in Vaticanus.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Sam` (lxx_to_kjv_1samuel_remaining_target_resolution.json).
### 1Kgs

#### 1Kgs 2

- `1Kgs.2.35` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `no_anchor`).
  Source refs: 1Kgs.2.35.
  Статус из исследования: `represented_in_composite_source_row_requires_canonical_token_span_split`.
  Исследовательская заметка: Whole-row import is unsafe: CrossWire source 2.35 contains canonical 2.35 opening plus a large appended Solomon supplement. Extract only the approved canonical token span for target 2.35.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
#### 1Kgs 4

- `1Kgs.4.26` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.2.46, 1Kgs.10.26.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: The Solomon horse/stall row occurs inside composite source 2.46 and again as a prefix of composite source 10.26. Select an approved witness span during import; do not place either source row whole.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
#### 1Kgs 6

- `1Kgs.6.11` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot preserves target 6.11 in both displayed Greek witnesses, but no distinct CrossWire source row remains after sequence-aware review.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.6.12` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot preserves target 6.12 in both displayed Greek witnesses, but no distinct CrossWire source row remains after sequence-aware review.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.6.13` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot preserves target 6.13 in both displayed Greek witnesses, but no distinct CrossWire source row remains after sequence-aware review.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.6.14` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot preserves target 6.14 in both displayed Greek witnesses, but no distinct CrossWire source row remains after sequence-aware review.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.6.18` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 6.18 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 7

- `1Kgs.7.31` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 7.31 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 9

- `1Kgs.9.17` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.5.10.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: Pharaoh/Gezer material corresponding to KJV 9.16 and part of 9.17 is embedded inside CrossWire source 5.10.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.9.23` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 9.23 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.9.25` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 9.25 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 11

- `1Kgs.11.3` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.11.1.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: CrossWire source 11.1 combines the KJV strange-women opening with the wives/concubines line.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.11.25` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.11.13, 1Kgs.11.22.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: CrossWire source 11.13 combines Hadad introduction and Rezon adversary material; source 11.22 is an additional compact adversary summary.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.11.39` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 11.39 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.11.43` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.11.39.
  Статус из исследования: `represented_in_composite_source_requires_token_span_split`.
  Исследовательская заметка: CrossWire source 11.39 combines Solomon burial/succession with a moved Jeroboam-return narrative.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
#### 1Kgs 12

- `1Kgs.12.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 12.17 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 13

- `1Kgs.13.27` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 13.27 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 14

- `1Kgs.14.5` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.12.22.
  Статус из исследования: `represented_or_partly_represented_in_long_lxx_supplement_requires_token_span_review`.
  Исследовательская заметка: The long source 12.22 supplement includes parallels to the sick child, wife journey, and Ahijah encounter account.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.14.7` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.7 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.8` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.8 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.9` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.9 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.12` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.12.22.
  Статус из исследования: `represented_or_partly_represented_in_long_lxx_supplement_requires_token_span_review`.
  Исследовательская заметка: The source 12.22 supplement compresses the cut-off-house, dogs/birds, return-home, and mourning lines corresponding to KJV 14.10-13.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.14.13` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Kgs.12.22.
  Статус из исследования: `represented_or_partly_represented_in_long_lxx_supplement_requires_token_span_review`.
  Исследовательская заметка: The source 12.22 supplement compresses the cut-off-house, dogs/birds, return-home, and mourning lines corresponding to KJV 14.10-13.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (projection_inputs.token_span_rules_unmatched).
- `1Kgs.14.14` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.14 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.15` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.15 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.16` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.16 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.19` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.19 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.14.20` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: GreekDoc polyglot preserves target 14.20 in Alexandrinus while Vaticanus is N/A; CrossWire does not retain a distinct row.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
#### 1Kgs 15

- `1Kgs.15.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot marks target 15.6 N/A in both displayed Greek witnesses.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
- `1Kgs.15.32` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc polyglot preserves target 15.32 in both displayed Greek witnesses, but no distinct CrossWire source row remains after sequence-aware review.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Kgs` (lxx_to_kjv_1kings_remaining_target_resolution.json).
### 1Chr

#### 1Chr 1

- `1Chr.1.11` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Mizraim descendants row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.12` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Pathrusim/Casluhim/Caphthorim row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.13` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Canaan/Zidon/Heth row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.14` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Jebusite/Amorite/Girgashite row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.15` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Hivite/Arkite/Sinite row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.16` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Arvadite/Zemarite/Hamathite row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.17` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire has no distinct target 1.17 row. Its later compact target 1.24 material overlaps the Shem list but must not be duplicated into this target. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.18` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire has no distinct Arphaxad/Shelah/Eber genealogy row. Its later compact target 1.24 material contains a Shelah segment but must not be duplicated into this target. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.19` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the Eber/Peleg/Joktan row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.20` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the first Joktan descendants row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.21` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the second Joktan descendants row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.22` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the third Joktan descendants row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.23` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire omits the final Joktan descendants row. GreekDoc retains the LXX row.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
- `1Chr.1.24` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: 1Chr.1.11, 1Chr.1.12.
  Статус из исследования: `represented_in_composite_source_rows_requires_merge`.
  Исследовательская заметка: CrossWire source 1.11 preserves the compact sons-of-Shem list and source 1.12 preserves Shelah. Merge both source rows into target 1.24 during import. GreekDoc displays the same compact Alexandrinus-like list under target 1.24.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (projection_inputs.token_span_rules_unmatched).
#### 1Chr 16

- `1Chr.16.24` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire source and target align through 16.23, then source 16.24 resumes with target 16.25 content. GreekDoc preserves the target 16.24 declare-glory-among-the-nations row in both displayed Greek columns.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.1Chr` (lxx_to_kjv_1chronicles_remaining_target_resolution.json).
### 2Chr

#### 2Chr 27

- `2Chr.27.8` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc shows no distinct Greek text for the KJV 27.8 age/regnal-length statement. The following death-and-burial line is numbered 27.8 in one displayed Greek witness and 27.9 in the other; CrossWire source 27.8 aligns with KJV target 27.9.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.2Chr` (lxx_to_kjv_2chronicles_remaining_target_resolution.json).
### Neh

#### Neh 3

- `Neh.3.7` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: CrossWire compact source 3.7 aligns with KJV 3.8. GreekDoc retains an LXX 3.7 row, so this is specifically a CrossWire source omission rather than a general LXX absence.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
#### Neh 4

- `Neh.4.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.4.6 N/A; CrossWire source 4.1 resumes with KJV 4.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
#### Neh 11

- `Neh.11.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.16 N/A; CrossWire source 11.16 resumes with the Mattaniah line corresponding to target 11.17.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.20` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.20 N/A; CrossWire source proceeds from target 11.19 to target 11.22.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.21` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.21 N/A; CrossWire source proceeds from target 11.19 to target 11.22.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.28 N/A; CrossWire source proceeds from target 11.27 to target 11.30.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.29` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.29 N/A; CrossWire source proceeds from target 11.27 to target 11.30.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.32` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.32 N/A; CrossWire source proceeds from target 11.31 to target 11.36.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.33` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.33 N/A; CrossWire source proceeds from target 11.31 to target 11.36.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.34` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.34 N/A; CrossWire source proceeds from target 11.31 to target 11.36.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.11.35` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.11.35 N/A; CrossWire source proceeds from target 11.31 to target 11.36.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
#### Neh 12

- `Neh.12.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.12.4 N/A; CrossWire source 12.4 resumes with target 12.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.12.5` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.12.5 N/A; CrossWire source 12.4 resumes with target 12.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
- `Neh.12.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Neh.12.6 N/A; CrossWire source 12.4 resumes with target 12.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Neh` (lxx_to_kjv_nehemiah_remaining_target_resolution.json).
### Esth

#### Esth 4

- `Esth.4.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target 4.6 N/A in all displayed controls. CrossWire source 4.6 resumes with target 4.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Esth` (lxx_to_kjv_esther_remaining_target_resolution.json).
#### Esth 5

- `Esth.5.1` - нужна политика границы канонического текста и греческого добавления (`addition_preservation_policy_required`).
  Source refs: Esth.5.1.
  Статус из исследования: `represented_in_expanded_lxx_source_row_requires_addition_policy`.
  Исследовательская заметка: CrossWire source 5.1 preserves an expanded Addition D presentation of Esther approaching the king. Decide whether the canonical grid stores the expanded Greek row or a canonical span before import.
  Следующее действие: Решить, можно ли сохранять канонический префикс внутри греческого добавления или ячейка должна остаться пустой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Esth` (lxx_to_kjv_esther_remaining_target_resolution.json).
- `Esth.5.2` - нужна политика границы канонического текста и греческого добавления (`addition_preservation_policy_required`).
  Source refs: Esth.5.2.
  Статус из исследования: `represented_in_expanded_lxx_source_row_requires_addition_policy`.
  Исследовательская заметка: CrossWire source 5.2 continues the expanded Addition D scene around the king receiving Esther. Decide the canonical-grid representation together with target 5.1 before import.
  Следующее действие: Решить, можно ли сохранять канонический префикс внутри греческого добавления или ячейка должна остаться пустой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Esth` (lxx_to_kjv_esther_remaining_target_resolution.json).
#### Esth 9

- `Esth.9.5` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target 9.5 N/A in all displayed controls. CrossWire source 9.5 resumes with target 9.6 Shushan-five-hundred content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Esth` (lxx_to_kjv_esther_remaining_target_resolution.json).
- `Esth.9.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target 9.30 N/A in all displayed controls. CrossWire source 9.29 resumes with target 9.31 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Esth` (lxx_to_kjv_esther_remaining_target_resolution.json).
### Job

#### Job 23

- `Job.23.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks Job.23.14 N/A. CrossWire compact source Job.23.14 begins with the Therefore/I am troubled line corresponding to KJV Job.23.15, so target 23.14 is not embedded in a neighboring CrossWire row.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Job` (lxx_to_kjv_job_remaining_target_resolution.json).
### Ps

#### Ps 11

- `Ps.11.1` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Ps.10.1.
  Статус из исследования: `represented_in_composite_source_rows_requires_token_span_split_or_merge`.
  Исследовательская заметка: Mechanical DP alignment joins one or more source rows containing a Psalm title or superscription with the KJV-grid canonical verse token span.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (projection_inputs.token_span_rules_unmatched).
#### Ps 29

- `Ps.29.1` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `no_table`).
  Source refs: Ps.28.1.
  Статус из исследования: `represented_in_composite_source_rows_requires_token_span_split_or_merge`.
  Исследовательская заметка: Mechanical DP alignment joins one or more source rows containing a Psalm title or superscription with the KJV-grid canonical verse token span.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (projection_inputs.token_span_rules_unmatched).
#### Ps 116

- `Ps.116.10` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Ps.115.1.
  Статус из исследования: `represented_in_composite_source_rows_requires_token_span_split_or_merge`.
  Исследовательская заметка: Manual control-page review identified an embedded Psalm heading prefix before the canonical verse token span.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (projection_inputs.token_span_rules_unmatched).
- `Ps.116.14` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc Ps.116.14 preserves the vow-paying line, while CrossWire source Ps.115 skips that source row and resumes with target Ps.116.15.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (lxx_to_kjv_psalms_remaining_target_resolution.json).
- `Ps.116.17` - в CrossWire есть только частичный текст, нужна политика восстановления (`partial_crosswire_source_requires_repair_policy`).
  Source refs: Ps.115.7.
  Статус из исследования: `partially_represented_in_crosswire_source_missing_suffix`.
  Исследовательская заметка: CrossWire contains only the opening sacrifice-of-praise clause. GreekDoc Ps.116.17 also contains the call-on-the-name-of-the-Lord clause. Do not import the partial row as a complete target verse.
  Следующее действие: Найти полный одобренный источник или явно разрешить частичное заполнение с маркировкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (lxx_to_kjv_psalms_remaining_target_resolution.json).
#### Ps 138

- `Ps.138.1` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Ps.137.1.
  Статус из исследования: `represented_in_composite_source_rows_requires_token_span_split_or_merge`.
  Исследовательская заметка: Manual control-page review identified an embedded Psalm heading prefix before the canonical verse token span.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ps` (projection_inputs.token_span_rules_unmatched).
### Prov

#### Prov 4

- `Prov.4.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the wisdom-is-principal row 4.7 N/A. CrossWire source 4.7 resumes with target 4.8 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 8

- `Prov.8.33` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_witness`.
  Исследовательская заметка: CrossWire omits the hear-instruction row. GreekDoc is witness-sensitive: one displayed Greek column marks 8.33 N/A while another preserves the instruction. CrossWire source 8.33 instead combines the tail of target 8.32 with target 8.34 content.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 11

- `Prov.11.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the riches-profit-not row 11.4 N/A. CrossWire source 11.4 resumes with target 11.5 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 15

- `Prov.15.31` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the ear-hearing-reproof row 15.31 N/A. CrossWire source 15.31 resumes with target 15.32 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 16

- `Prov.16.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the preparations-of-heart row 16.1 N/A in the displayed LXX controls.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.16.2` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: Prov.16.1.
  Статус из исследования: `unrepresented_as_kjv_semantic_row_lxx_variant_present`.
  Исследовательская заметка: CrossWire source 16.1 and GreekDoc row 16.2 preserve a nearby LXX variant about works being manifest before God and the wicked perishing in an evil day. It is not the KJV-semantic ways-clean-in-own-eyes proverb and must not be imported as target 16.2.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.16.3` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the commit-thy-works row 16.3 N/A in the displayed LXX controls.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.16.6` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.15.27.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The mercy/truth and fear-of-the-Lord segment follows ordinary target 15.27 content inside CrossWire source 15.27. Extract the token span during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
- `Prov.16.7` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.15.28.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The ways-pleasing-the-Lord and enemies-becoming-friends segment follows ordinary target 15.28 content inside CrossWire source 15.28. Extract the token span during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
- `Prov.16.8` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.15.29.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The little-with-righteousness segment follows ordinary target 15.29 content inside CrossWire source 15.29. Extract the token span during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
- `Prov.16.9` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.15.29.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The heart-devising and God-directing-steps segment follows the target 16.8 segment inside CrossWire source 15.29. Extract the token span during import.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
#### Prov 18

- `Prov.18.23` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the poor-using-entreaties row 18.23 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.18.24` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the friend-sticking-closer-than-brother row 18.24 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 19

- `Prov.19.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the poor-walking-in-integrity row 19.1 N/A. CrossWire source 19.1 resumes with target 19.3 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.19.2` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the soul-without-knowledge row 19.2 N/A. CrossWire source 19.1 resumes with target 19.3 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 20

- `Prov.20.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the buyer-saying-naught row 20.14 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the lips-of-knowledge row 20.15 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the garment-for-surety row 20.16 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the bread-of-deceit row 20.17 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the counsel-before-war row 20.18 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the talebearer row 20.19 N/A.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
- `Prov.20.20` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.20.9.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The cursing-father-or-mother segment follows ordinary target 20.9 content inside CrossWire source 20.9. GreekDoc marks target 20.20 N/A as a separate row.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
- `Prov.20.21` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.20.9.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The hastily-gotten-inheritance segment follows the target 20.20 segment inside CrossWire source 20.9. GreekDoc marks target 20.21 N/A as a separate row.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
- `Prov.20.22` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Prov.20.9.
  Статус из исследования: `represented_in_composite_source_row_requires_token_span_split`.
  Исследовательская заметка: The wait-on-the-Lord segment follows the target 20.21 segment inside CrossWire source 20.9. GreekDoc marks target 20.22 N/A as a separate row.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (projection_inputs.token_span_rules_unmatched).
#### Prov 21

- `Prov.21.5` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the thoughts-of-the-diligent row 21.5 N/A. CrossWire source 21.5 resumes with target 21.6 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 22

- `Prov.22.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks the train-up-a-child row 22.6 N/A. CrossWire source 22.6 resumes with target 22.7 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
#### Prov 23

- `Prov.23.23` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_witness`.
  Исследовательская заметка: CrossWire omits the buy-truth row and source 23.23 resumes with target 23.24 content. GreekDoc is witness-sensitive: one displayed Greek column marks 23.23 N/A while another preserves the instruction.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Prov` (lxx_to_kjv_proverbs_remaining_target_resolution.json).
### Isa

#### Isa 2

- `Isa.2.22` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Isa.2.22 N/A in both displayed Greek columns. CrossWire chapter 2 ends after source 2.21, which aligns directly with target 2.21.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Isa` (lxx_to_kjv_isaiah_remaining_target_resolution.json).
#### Isa 56

- `Isa.56.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Isa.56.12 N/A in both displayed Greek columns. CrossWire chapter 56 ends after source 56.11, which aligns directly with target 56.11.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Isa` (lxx_to_kjv_isaiah_remaining_target_resolution.json).
### Jer

#### Jer 7

- `Jer.7.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.7.1 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 8

- `Jer.8.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.8.11 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.8.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.8.12 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 10

- `Jer.10.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.10.6 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.10.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.10.7 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.10.8` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.10.8 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.10.10` - нет в CrossWire, но есть в контрольном LXX-свидетеле (`crosswire_specific_omission_present_in_lxx_control`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control`.
  Исследовательская заметка: GreekDoc preserves target 10.10 Greek text. CrossWire source 10.6 aligns with target 10.9 and source 10.7 resumes with target 10.11, so this is a source-specific omission.
  Следующее действие: Искать другой LXX-свидетель или издание; импортировать только после проверки лицензии и стратегии Strong-разметки.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 11

- `Jer.11.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.11.7 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 17

- `Jer.17.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.17.1 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.17.2` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.17.2 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.17.3` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.17.3 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.17.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.17.4 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 25

- `Jer.25.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.25.14 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 27

- `Jer.27.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.27.1 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.27.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.27.7 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.27.13` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.27.13 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.27.14` - нужно вручную выбрать token-span/merge внутри CrossWire (`token_span_merge_or_placement_required`; статус exact-pass: `not_unique_exact_match`).
  Source refs: Jer.34.10, Jer.34.11, Jer.34.13.
  Статус из исследования: `represented_in_composite_source_rows_requires_token_span_split_or_merge`.
  Исследовательская заметка: CrossWire source 34.10 and the opening of 34.11 form target 27.12; the remainder of 34.11 forms target 27.14. Source 34.13 combines targets 27.16 and 27.17. GreekDoc marks target 27.13 N/A.
  Следующее действие: Вручную проверить указанные source_refs, выбрать точные token_start/token_end, добавить manual-rule в consolidated JSON и пересобрать БД.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (projection_inputs.token_span_rules_unmatched).
- `Jer.27.21` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.27.21 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 29

- `Jer.29.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.29.16 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.29.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.29.17 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.29.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.29.18 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.29.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.29.19 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.29.20` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.29.20 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 30

- `Jer.30.10` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.30.10 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.30.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.30.11 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.30.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.30.15 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.30.22` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.30.22 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 33

- `Jer.33.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.14 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.15 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.16` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.16 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.17` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.17 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.18` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.18 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.19 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.20` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.20 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.21` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.21 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.22` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.22 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.23` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.23 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.24` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.24 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.25` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.25 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.33.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.33.26 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 39

- `Jer.39.4` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.4 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.5` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.5 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.6 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.7` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.7 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.8` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.8 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.9` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.9 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.10` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.10 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.11` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.11 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.12` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.12 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.39.13` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.39.13 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 46

- `Jer.46.1` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.46.1 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.46.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.46.26 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 48

- `Jer.48.45` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.48.45 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.48.46` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.48.46 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.48.47` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.48.47 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 49

- `Jer.49.6` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.49.6 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 51

- `Jer.51.45` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.51.45 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.51.46` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.51.46 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.51.47` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.51.47 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.51.48` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.51.48 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
#### Jer 52

- `Jer.52.2` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.2 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.52.3` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.3 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.52.15` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.15 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.52.28` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.28 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.52.29` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.29 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
- `Jer.52.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Jer.52.30 N/A in the displayed LXX controls. Keep the fixed KJV-grid row blank.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Jer` (lxx_to_kjv_jeremiah_remaining_target_resolution.json).
### Lam

#### Lam 3

- `Lam.3.22` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: CrossWire source Lam.3.22 resumes with target 3.25. GreekDoc shows target 3.22 text in one displayed Greek witness and N/A in the other, so this is a selected-source omission rather than a universal LXX absence.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Lam` (lxx_to_kjv_lamentations_remaining_target_resolution.json).
- `Lam.3.23` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: CrossWire source Lam.3.22 resumes with target 3.25. GreekDoc shows target 3.23 text in one displayed Greek witness and N/A in the other, so this is a selected-source omission rather than a universal LXX absence.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Lam` (lxx_to_kjv_lamentations_remaining_target_resolution.json).
- `Lam.3.24` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: CrossWire source Lam.3.22 resumes with target 3.25. GreekDoc shows target 3.24 text in one displayed Greek witness and N/A in the other, so this is a selected-source omission rather than a universal LXX absence.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Lam` (lxx_to_kjv_lamentations_remaining_target_resolution.json).
- `Lam.3.29` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Lam.3.29 N/A in both displayed Greek witnesses. CrossWire source Lam.3.25 aligns with target 3.28 and source 3.26 with target 3.30.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Lam` (lxx_to_kjv_lamentations_remaining_target_resolution.json).
### Ezek

#### Ezek 1

- `Ezek.1.14` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Ezek.1.14 N/A in both displayed Greek columns. CrossWire source 1.14 resumes with target 1.15 wheel content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).
#### Ezek 10

- `Ezek.10.14` - пропуск зависит от выбранного LXX-свидетеля (`witness_sensitive_crosswire_omission`).
  Source refs: не указаны.
  Статус из исследования: `unrepresented_in_crosswire_source_but_present_in_lxx_control_variant_witness`.
  Исследовательская заметка: CrossWire source 10.14 resumes with target 10.15. GreekDoc shows witness variation: one Greek column marks 10.14 N/A while the other preserves bracketed four-faces text.
  Следующее действие: Сначала выбрать политику свидетеля, затем импортировать только из одобренного источника с понятной лицензией и Strong-разметкой.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).
#### Ezek 27

- `Ezek.27.31` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Ezek.27.31 N/A in both displayed Greek columns. CrossWire source 27.31 resumes with target 27.32 lamentation content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).
#### Ezek 32

- `Ezek.32.19` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Ezek.32.19 N/A in both displayed Greek columns. CrossWire source 32.19 resumes with target 32.20 fallen-by-sword content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).
#### Ezek 33

- `Ezek.33.26` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Ezek.33.26 N/A in both displayed Greek columns. CrossWire source 33.26 resumes with target 33.27 wastes/sword content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).
#### Ezek 40

- `Ezek.40.30` - нет отдельной LXX-семантической строки в проверенных контролях (`confirmed_control_absence_or_semantic_difference`).
  Source refs: не указаны.
  Статус из исследования: `confirmed_unrepresented_in_lxx_control`.
  Исследовательская заметка: GreekDoc marks target Ezek.40.30 N/A in both displayed Greek columns. CrossWire source 40.29 aligns directly with target 40.29, and source 40.30 resumes with target 40.31 content.
  Следующее действие: Пока оставлять пустым. Не подставлять соседний LXX-текст и не смешивать с не-LXX греческой заменой без отдельного решения владельца.
  Где искать детали в объединённом JSON: `remaining_target_resolution_by_book.Ezek` (lxx_to_kjv_ezekiel_remaining_target_resolution.json).

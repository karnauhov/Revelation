# 2Thess.2.4: осмотр corrector и зарегистрированное исключение — v1, 2026-10-10

Отдельный corrector `/root/corrector_1tim` подтвердил основания четырех ошибок переноса source scope по sealed independent blocking QC, существующему bounded research packet и exact token evidence. **Формальная correction 2Thess не выпущена; frozen wrong grid не объявлен исправленным.**

Скан OH1988 лист1460, печатная1456, имеет «сяде, як Бог, і за Бога себе видаватиме». В выбранном TAGNT/UGNT ὅτι ἐστὶν θεός завершает ἀποδεικνύντα ἑαυτόν, соответствуя второму predicate. Comparative як Бог относится к другому clause slot с traditional-only ὡς θεόν, который не входит в selected original grid. Поэтому текущий ὅτι→як переносит content conjunction в comparative clause, а последний θεός→Бог+Бога объединяет разные occurrences. Общая лемма/Strong G2316 не доказывает такую привязку.

| Frozen строка | Verdict сохраняется | Итоговый assignment |
| --- | --- | --- |
| o021 ὅτι → t018 як | error | deferred_strong_unassigned |
| o023 последний θεός → t019 Бог + t022 Бога | error | deferred_strong_unassigned |
| t018 як ← o021 ὅτι | error | deferred_strong_unassigned |
| t019 Бог ← o023 последний θεός | error | deferred_strong_unassigned |
| t022 Бога ← o023 последний θεός | accepted, reciprocal dependency | deferred_strong_unassigned |

Exact source IDs: o021 ὅτι = `tagnt:4cbcef7fbc9921474a0845da725927acf8257979dac0a887b46906b8cf35b22c:c01`; o023 θεός = `tagnt:9c6a641cbe49db9d7c9200d02839e3e84ec97fb0a77fe0c2ab277b0ffc4299ce:c01`. Target IDs/spans: t018 як = `uk7:MW2:018:95:97` (scalar95:97, UTF-8170:174); t019 Бог = `uk7:MW2:019:98:101` (scalar98:101, UTF-8175:181); dependency t022 Бога = `uk7:MW2:022:108:112` (scalar108:112, UTF-8191:199). Cleanup candidate t021 за = `uk7:MW2:021:105:107` не привязан заново.

Grammar cleanup кандидаты ὅτι→за и последний θεός→Бога достаточно объясняют две разные конструкции, но удаление неправильных links оставляет як/Бог без доказанного classifier. Existing strict gold schema допускает target statuses только aligned, translation_addition и function_token. Read-only in-memory check существующим _validate_final_grid отверг нейтральный deferred target status с «Target accounting status is invalid». Новый provisional addition/function classifier не назначен: его доказательство отсутствует, owner это прямо запретил. Traditional IDs/Strong не импортировались, validator не ослаблялся.

Рекомендуется existing completion_v2 с exact closed exclusion пяти keys: четыре original content errors и одна принятая зависимость. Error не переименовывается в uncertain; verdict зависимости остаётся accepted. Effective projection удаляет links/Strong и любые frozen relation/classifier у всех пяти, исключая их из accepted alignment, training, scoring и export. t021 за остаётся frozen function_token вне указанного exclusion; proposed reciprocal mutation не применена и не названа новой отдельной ошибкой.

SHA-256 и bytes QC/source/chain inputs проверены до полного JSONL чтения. Full current grid1200 инспектирован структурно,6 scoped rows изучены,24 scalar/UTF-8 target spans этого стиха совпали. Existing reciprocal_components подтвердил exact exclusion5 и2 excluded hyperedges. [Deferral manifest](gold_group_005_2Thess_2_4.error_deferral.v1.manifest.json) фиксирует роли, доказательства, exact scope и причину отказа от formal correction. Это corrector review, а не независимый QC своих работ; final full-grid/effective projection проверяет отдельный reviewer. Single shared OH1988 issue inventory редактирует root, никаких параллельных working registries здесь не создано. Registered deferral закрывает completion без нового research cycle.

Exact closed exclusion stable keys (four errors and the final accepted dependency):

- `original:gold7:original:8146b1a458398a51b81864413fb2ef9c` — error.
- `original:gold7:original:b0da9c3f4fe033ffb984bd9831a1b0c0` — error.
- `target:gold7:target:12fcac04fa834879859d93a1aa2a88ed` — error.
- `target:gold7:target:8535a0732b53317dafb336782d041c0a` — error.
- `target:gold7:target:d942b43fc6fc7ddd6c4d2033a3d6a8ce` — accepted dependency.

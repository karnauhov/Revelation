# Украинский библейский модуль: этап 5

## Результат

Полная versioned-карта `ohienko_1988` (`OH1988`) из исходной версификации в
нормативную сетку `protestant_66 / kjv_protestant` построена в обе стороны.
Полные JSONL находятся только в gitignored work-каталоге; в Git сохраняются
манифесты, SHA-256, безопасные правила и отчёты.

## Контракт

- `schema_version`: 1;
- `mapping_contract_version`: `oh1988-kjv-protestant-v1`;
- операции: `1:1`, `merge`, `split`, `range_transfer`;
- separator для `merge`: один U+0020 (` `);
- соседний стих не используется как fallback;
- target text, `target_comment`, Strong alignment и SQLite не создаются.

## Покрытие

- source records: 31160 / 31160;
- source segments: 31171 / 31171;
- target positions: 31102 / 31102;
- target keys точно равны baseline: true;
- duplicate target keys: 0;
- необъяснённые пустые target positions: 0;
- forward/reverse consistency: true.
- source-only positions: 1;
- target-only positions: 0;
- targets с формально лучшим соседом, направленные в review: 575;
- автоматические neighbor rebindings: 0;
- проверено границ книг/глав: 66 / 1189.

## Операции

- `1:1`: 31026 правил.
- `merge`: 68 правил.
- `range_transfer`: 1 правил.
- `split`: 4 правил.

Все non-1:1 и все исправления исходного reference context включены в
`manual_review.jsonl` с безопасными идентификаторами, диапазонами, короткими
SHA-256 и минимум двумя источниками доказательств.

### Все non-1:1 правила

- `uk5-d5a81ed1064ef40638df` — `merge`: `Num.25.19; Num.26.1` → `Num.26.1` (`accepted`).
- `uk5-89c5c7bc97a4fa579dc8` — `merge`: `1Sam.20.42; 1Sam.21.1` → `1Sam.20.42` (`accepted`).
- `uk5-c8bf69422fcf4923b8e2` — `merge`: `1Kgs.22.43; 1Kgs.22.44` → `1Kgs.22.43` (`accepted`).
- `uk5-0610ce90421d68ba131f` — `split`: `2Chr.13.23` → `2Chr.13.23; 2Chr.14.1` (`accepted`).
- `uk5-ffa16f2340c8ed90aef7` — `merge`: `Ps.3.1; Ps.3.2` → `Ps.3.1` (`accepted`).
- `uk5-f2953b08cb8cdb236ff0` — `merge`: `Ps.4.1; Ps.4.2` → `Ps.4.1` (`accepted`).
- `uk5-36861ca02fbcb4ad8503` — `merge`: `Ps.5.1; Ps.5.2` → `Ps.5.1` (`accepted`).
- `uk5-d08697987abdec08e6ca` — `merge`: `Ps.6.1; Ps.6.2` → `Ps.6.1` (`accepted`).
- `uk5-546a865b67f0e4d6cb2c` — `merge`: `Ps.7.1; Ps.7.2` → `Ps.7.1` (`accepted`).
- `uk5-4424678d2a33e80ff8e3` — `merge`: `Ps.8.1; Ps.8.2` → `Ps.8.1` (`accepted`).
- `uk5-0e9362e7729a9c10b13b` — `merge`: `Ps.9.1; Ps.9.2` → `Ps.9.1` (`accepted`).
- `uk5-53d76e91e4c2dbba2347` — `merge`: `Ps.11.1; Ps.11.2` → `Ps.12.1` (`accepted`).
- `uk5-ac3515afaadddbb69d01` — `merge`: `Ps.12.1; Ps.12.2` → `Ps.13.1` (`accepted`).
- `uk5-88df09394a8445f2a2cf` — `split`: `Ps.12.6` → `Ps.13.5; Ps.13.6` (`accepted`).
- `uk5-87998cec0485e7597d5e` — `merge`: `Ps.17.1; Ps.17.2` → `Ps.18.1` (`accepted`).
- `uk5-4cc4643ff87e6e1ca501` — `merge`: `Ps.18.1; Ps.18.2` → `Ps.19.1` (`accepted`).
- `uk5-817842299927f8c96ef6` — `merge`: `Ps.19.1; Ps.19.2` → `Ps.20.1` (`accepted`).
- `uk5-b1d33b3ee8e1bd42e180` — `merge`: `Ps.20.1; Ps.20.2` → `Ps.21.1` (`accepted`).
- `uk5-d5142e94f89835fb63a0` — `merge`: `Ps.21.1; Ps.21.2` → `Ps.22.1` (`accepted`).
- `uk5-8a80f7352d672c027f63` — `merge`: `Ps.29.1; Ps.29.2` → `Ps.30.1` (`accepted`).
- `uk5-49aac9a3f7baffc7dc4a` — `merge`: `Ps.30.1; Ps.30.2` → `Ps.31.1` (`accepted`).
- `uk5-78661572a2baeabd77ac` — `merge`: `Ps.33.1; Ps.33.2` → `Ps.34.1` (`accepted`).
- `uk5-4a73fbd98db1c3af7a6a` — `merge`: `Ps.35.1; Ps.35.2` → `Ps.36.1` (`accepted`).
- `uk5-da8e6b74d23222d78e67` — `merge`: `Ps.37.1; Ps.37.2` → `Ps.38.1` (`accepted`).
- `uk5-cc15f27e89d24a27ed89` — `merge`: `Ps.38.1; Ps.38.2` → `Ps.39.1` (`accepted`).
- `uk5-59b8c1a5b408f4909584` — `merge`: `Ps.39.1; Ps.39.2` → `Ps.40.1` (`accepted`).
- `uk5-603f55921e49fa4f3eea` — `merge`: `Ps.40.1; Ps.40.2` → `Ps.41.1` (`accepted`).
- `uk5-5bc9b29f93501c952392` — `merge`: `Ps.41.1; Ps.41.2` → `Ps.42.1` (`accepted`).
- `uk5-96b26750e80073b9bbe7` — `merge`: `Ps.43.1; Ps.43.2` → `Ps.44.1` (`accepted`).
- `uk5-ba2f74f0e3b0ccc479e9` — `merge`: `Ps.44.1; Ps.44.2` → `Ps.45.1` (`accepted`).
- `uk5-0de76f2cfc432cbab4a9` — `merge`: `Ps.45.1; Ps.45.2` → `Ps.46.1` (`accepted`).
- `uk5-61dcf805c2513530d509` — `merge`: `Ps.46.1; Ps.46.2` → `Ps.47.1` (`accepted`).
- `uk5-76bda772c759f84640b5` — `merge`: `Ps.47.1; Ps.47.2` → `Ps.48.1` (`accepted`).
- `uk5-88f35bd7556053369421` — `merge`: `Ps.48.1; Ps.48.2` → `Ps.49.1` (`accepted`).
- `uk5-1e4b5996c1f673332082` — `merge`: `Ps.50.1; Ps.50.2; Ps.50.3` → `Ps.51.1` (`accepted`).
- `uk5-f4d71321241b5e966848` — `merge`: `Ps.51.1; Ps.51.2; Ps.51.3` → `Ps.52.1` (`accepted`).
- `uk5-88d5cb4cec3854447a76` — `merge`: `Ps.52.1; Ps.52.2` → `Ps.53.1` (`accepted`).
- `uk5-56d515ae58b3cc276915` — `merge`: `Ps.53.1; Ps.53.2; Ps.53.3` → `Ps.54.1` (`accepted`).
- `uk5-959f6ed22cfe763a5c46` — `merge`: `Ps.54.1; Ps.54.2` → `Ps.55.1` (`accepted`).
- `uk5-dece5af8040501309b44` — `merge`: `Ps.55.1; Ps.55.2` → `Ps.56.1` (`accepted`).
- `uk5-0b7c2322b330d8adf27c` — `merge`: `Ps.56.1; Ps.56.2` → `Ps.57.1` (`accepted`).
- `uk5-8fe503b11ee92cb2526f` — `merge`: `Ps.57.1; Ps.57.2` → `Ps.58.1` (`accepted`).
- `uk5-ccff227825f754699ff7` — `merge`: `Ps.58.1; Ps.58.2` → `Ps.59.1` (`accepted`).
- `uk5-bf614a58ee3d0dd9ba23` — `merge`: `Ps.59.1; Ps.59.2; Ps.59.3` → `Ps.60.1` (`accepted`).
- `uk5-bf2fe4f2728031b67a3c` — `merge`: `Ps.60.1; Ps.60.2` → `Ps.61.1` (`accepted`).
- `uk5-5eac6da0c5a7ae95fc38` — `merge`: `Ps.61.1; Ps.61.2` → `Ps.62.1` (`accepted`).
- `uk5-cd259cc817a328a0630a` — `merge`: `Ps.62.1; Ps.62.2` → `Ps.63.1` (`accepted`).
- `uk5-741d00cb0c30408c8507` — `merge`: `Ps.63.1; Ps.63.2` → `Ps.64.1` (`accepted`).
- `uk5-af9f19256edbaa1d1958` — `merge`: `Ps.64.1; Ps.64.2` → `Ps.65.1` (`accepted`).
- `uk5-091e3b20cd545a272e09` — `merge`: `Ps.66.1; Ps.66.2` → `Ps.67.1` (`accepted`).
- `uk5-2e3ceedadcc7ab089552` — `merge`: `Ps.67.1; Ps.67.2` → `Ps.68.1` (`accepted`).
- `uk5-28c78f5c1da866b7e64d` — `merge`: `Ps.68.1; Ps.68.2` → `Ps.69.1` (`accepted`).
- `uk5-4fb8e111d5b51aaf0677` — `merge`: `Ps.69.1; Ps.69.2` → `Ps.70.1` (`accepted`).
- `uk5-795b153acde7b145e514` — `merge`: `Ps.74.1; Ps.74.2` → `Ps.75.1` (`accepted`).
- `uk5-2510f6782c73b939f08a` — `merge`: `Ps.75.1; Ps.75.2` → `Ps.76.1` (`accepted`).
- `uk5-2f442a5a9a312fa86ae1` — `merge`: `Ps.76.1; Ps.76.2` → `Ps.77.1` (`accepted`).
- `uk5-3b16add783dd9a788798` — `merge`: `Ps.79.1; Ps.79.2` → `Ps.80.1` (`accepted`).
- `uk5-948794c7e5a816e15392` — `merge`: `Ps.80.1; Ps.80.2` → `Ps.81.1` (`accepted`).
- `uk5-e74746984a51e60b7bdd` — `merge`: `Ps.82.1; Ps.82.2` → `Ps.83.1` (`accepted`).
- `uk5-90144b009e0828ccb8a5` — `merge`: `Ps.83.1; Ps.83.2` → `Ps.84.1` (`accepted`).
- `uk5-0bdf9a0001a4eddb5c5a` — `merge`: `Ps.84.1; Ps.84.2` → `Ps.85.1` (`accepted`).
- `uk5-37efbf5a77cb67890f8a` — `merge`: `Ps.87.1; Ps.87.2` → `Ps.88.1` (`accepted`).
- `uk5-d33092e3db5efb796436` — `merge`: `Ps.88.1; Ps.88.2` → `Ps.89.1` (`accepted`).
- `uk5-444b0d486fd6e0db3abc` — `merge`: `Ps.91.1; Ps.91.2` → `Ps.92.1` (`accepted`).
- `uk5-bee384f5d1d047945b75` — `merge`: `Ps.101.1; Ps.101.2` → `Ps.102.1` (`accepted`).
- `uk5-367eabe0d54ff3f0dad5` — `merge`: `Ps.107.1; Ps.107.2` → `Ps.108.1` (`accepted`).
- `uk5-391b4f2b3e02e6fd088e` — `merge`: `Ps.139.1; Ps.139.2` → `Ps.140.1` (`accepted`).
- `uk5-b88d07daf944036734b5` — `merge`: `Ps.141.1; Ps.141.2` → `Ps.142.1` (`accepted`).
- `uk5-f396c7f9af758d544088` — `split`: `Acts.19.40` → `Acts.19.40; Acts.19.41` (`accepted`).
- `uk5-efbee9e56dfaf4f134ec` — `split`: `2Cor.13.12` → `2Cor.13.12; 2Cor.13.13` (`accepted`).
- `uk5-f93cd5171e3523b410a4` — `merge`: `3John.1.14; 3John.1.15` → `3John.1.14` (`accepted`).
- `uk5-ee0a677049c6f6ae20f3` — `merge`: `Rev.12.18; Rev.13.1` → `Rev.13.1` (`accepted`).
- `uk5-8a849ae7516e1d910cfb` — `range_transfer`: `2Chr.14.14` → `∅` (`accepted`).

## Сноски

- definitions: 1204;
- uses/markers: 1329 / 1329;
- projected: 1318;
- explicit anomalies: 11;
- heading/non-verse: 11;
- target anchors pending: 1318;
- `target_comment` создан: false.

- `1:1`: 1310 projected, 0 anomalies, 1310 total.
- `merge`: 8 projected, 0 anomalies, 8 total.
- `non_verse_source_material`: 0 projected, 11 anomalies, 11 total.
- `range_transfer`: 0 projected, 0 anomalies, 0 total.
- `split`: 0 projected, 0 anomalies, 0 total.

Offsets target не выдумываются: до синтеза target text доказанные назначения
имеют состояние `target_anchor_pending`; неоднозначные split/range anchors
остаются одним explicit anomaly с полным списком кандидатов.

## Границы этапа

Этап 6 не выполнялся. В отчетах нет Strong-выравнивания, результирующего текста
стихов, строки комментария или базы данных.

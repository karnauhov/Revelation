# Этап 4: парсеры и независимая нормализация источников

Статус: **завершён**. Дата доказательств: 2026-08-01.

Этап разобрал все 14 locked machine sources независимыми путями после fail-closed проверки размера и SHA-256. Полные normalized JSONL находятся в gitignored `scripts/bible_module/work/ukrainian_stage_4_20260801/`; в Git сохранены точные manifests, агрегаты, hashes и безопасные расхождения.

Проекция на `kjv_protestant`, `verse_key`, формирование `target_comment`, Strong-выравнивание и SQLite **не выполнялись**. Каждая source-native запись имеет `projection_status=unprojected`.

## Источники

| source_id | records | verses | tokens | Strong | footnote uses | warnings | errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `commons_ohienko_1988_scan` | 1538 | 0 | 148602 | 0 | 0 | 1 | 0 |
| `crosswire_kjv_3_1` | 31102 | 31102 | 355295 | 373501 | 0 | 0 | 0 |
| `internet_archive_ohienko_1988_scan` | 1538 | 0 | 148602 | 0 | 0 | 0 | 0 |
| `openscriptures_oshb_v2_2` | 23213 | 23213 | 311284 | 300007 | 0 | 0 | 0 |
| `step_tagnt_act_rev` | 4170 | 4170 | 74789 | 113174 | 0 | 0 | 0 |
| `step_tagnt_mat_jhn` | 3778 | 3778 | 66931 | 104985 | 0 | 0 | 0 |
| `step_tahot_gen_deu` | 5607 | 5607 | 76490 | 156426 | 0 | 0 | 0 |
| `step_tahot_isa_mal` | 5189 | 5189 | 75051 | 147565 | 0 | 0 | 0 |
| `step_tahot_job_sng` | 3729 | 3729 | 29983 | 56359 | 0 | 0 | 0 |
| `step_tahot_jos_est` | 6653 | 6653 | 102210 | 210825 | 0 | 0 | 0 |
| `step_tvtms` | 28770 | 0 | 0 | 0 | 0 | 0 | 0 |
| `tanach_us_uxlc_2_5_27_6` | 23213 | 23213 | 306782 | 0 | 0 | 0 | 0 |
| `unfoldingword_ugnt_v0_34` | 7958 | 7958 | 137990 | 137990 | 0 | 0 | 0 |
| `wikisource_ohienko_1988_revisions` | 31171 | 31160 | 605969 | 0 | 1329 | 11 | 0 |

Commons является печатным эталоном. Закреплённый Commons DjVu содержит два байт-в-байт одинаковых логических DjVu-контейнера; parser fail-closed проверил это и разобрал один логический набор из 1 538 страниц. Internet Archive совпадает с этим логическим контейнером и учитывается только как зависимый контроль. Wikisource — транскрипция того же Commons-скана, а не независимое издание.

## Сноски

- raw carrier inventory: {'ref_opening': 1329, 'ref_closing': 1204, 'ref_self_closing': 125, 'reflist': 735, 'anchor': 2201}.
- уникальные определения: 1204.
- места использования после разрешения named/self-closing refs: 1329.
- однозначно привязаны к source verse: 1318.
- missing/unresolved/ambiguous: 11/0/0.
- source verses с одной или несколькими сносками: 1222; с несколькими: 90.

Carrier counts не объявляются количеством итоговых сносок. Paired named ref хранит определение и использование, self-closing named ref создаёт только дополнительное use. Текст сносок отсутствует в `source_plain_nfc`; каждый печатный marker сохраняется как page-local `ref` ordinal с carrier provenance. Одиннадцать сносок находятся в заголовочных шаблонах и не имеют verse anchor; они сохранены как `missing` для ручной проверки. Продолжение Иак. 5:5 на границе страницы 1490 удерживается в исходном стихе, без присоединения к соседней книге.

## Сравнения и расхождения

Постиховые сравнения выполнялись по порядку source-native tokens, их digest, raw/normalized Strong sequence и полноте source refs. Для печатных сносок сравнивались page, порядок, digest текста и доступное OCR-доказательство Commons. Производные/зеркальные источники помечены зависимыми и не считаются независимым подтверждением.

Агрегаты сравнений: `{"commons_vs_internet_archive_pages":{"differences":0,"pages_compared":1538,"relation":"same scan; Internet Archive is dependent control"},"oshb_vs_uxlc":{"common_records":23213,"surface_differences":23213},"tagnt_vs_crosswire_kjv":{"common_records":7948,"missing_records":9,"strong_differences":7929},"tagnt_vs_ugnt":{"common_records":7948,"missing_records":10,"strong_differences":7920,"surface_differences":7948},"tahot_vs_oshb":{"common_records":21178,"missing_records":2035,"strong_differences":21178,"surface_differences":21178},"wikisource_footnotes_vs_commons_hidden_ocr":{"exact_normalized_ocr_containment":641,"manual_print_check_needed":149,"partial_ocr_evidence":414}}`.

Полный безопасный список находится в `source_diff.csv`; он содержит identifiers, hashes и counts, но не воспроизводит корпус. Отсутствие точного совпадения с hidden OCR имеет medium/manual-review статус и не означает потерю ref: OCR печатного скана шумный, а provenance каждой сноски сохранён.

## Manual-only источники

Google Books, HathiTrust и Internet Archive access-preview/manual controls из source lock не превращались в machine inputs. На следующих ручных проверках спорный `footnote_id` можно открыть по Commons page/revision provenance и сверить с этими control surfaces; они не меняют автоматически source text или binding.

## Выход

Все machine records учтены как processed либо классифицированные metadata/service/skipped records; ошибок parser contract нет. Все 1 329 `<ref>` carriers структурно потреблены: 1 204 paired definitions/uses и 125 self-closing named uses. Нет нерешённых critical/high дефектов. Missing heading anchors и OCR-review items находятся в явных безопасных списках. Этап 5 разрешён, но не начат.

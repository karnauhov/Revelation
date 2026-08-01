# Журнал проверок этапа 3 украинского библейского модуля

Дата: `2026-08-01`

Рабочий commit до изменений: `3a2f21b` (`Lock Ukrainian module stage 2 contract`)

Статус этапа: `Завершён`

## Объём и границы

Выполнен только этап 3: воспроизводимое получение и фиксация утверждённых
источников. Не реализовывались парсеры этапа 4, карта версификации этапа 5,
Strong-выравнивание, сборщик или итоговый `bible_ohienko_1988.sqlite`.
Runtime/UI/state-management код, маршруты, локализация, существующие SQLite и
`web/db` не изменялись.

Этапы 1–2 подтверждены закрытыми: roadmap до изменений прямо разрешал этап 3,
а stage-2 baseline продолжает фиксировать `bible_ohienko_1988.sqlite`,
`ohienko_1988`, `OH1988`, `uk`, `protestant_66`, `kjv_protestant` и 31 102
целевых ключа.

## Артефакты

- [`source_lock.json`](source_lock.json) — 14 машинных файлов, точные роли,
  страницы и download URL, версии/commit/tag/revision, дата получения, размеры,
  SHA-256, лицензии, точные license URL и зависимости; отдельно описаны два
  ручных контроля, которые не маскируются под независимые машинные входы.
- [`fetch_log.json`](fetch_log.json) — tool versions, timestamps, clean-cache и
  offline runs, все HTTP attempts, TLS certificate summaries, redirect chain,
  ошибки и ограничения.
- [`source_files.csv`](source_files.csv) — стабильная табличная сводка всех
  машинных файлов.
- [`test_ukrainian_stage_3_sources.py`](../../tests/test_ukrainian_stage_3_sources.py)
  — contract и fail-closed тесты.
- [`ukrainian_stage_3_sources.py`](../../ukrainian_stage_3_sources.py) —
  совместимый с существующим `fetch_sources.py` механизм: общий
  `sha256_file`, штатный `source_cache`, JSON lock, проверка перед атомарной
  заменой.

Все 14 файлов занимают в локальном кэше `293 075 184` байта. Полные тексты,
DjVu, ZIP и generated Wikisource bundle находятся только в gitignored
`scripts/bible_module/source_cache`; в Git они не добавлены.

## Разрешённые placeholders

- `commons_scan_sha256`:
  `0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34`;
  размер `83 637 482`, SHA-1 MediaWiki
  `8995dec8cfd20c212dc48e91868f115d3b8d17cc`, 1 538 страниц.
- `wikisource_revision_lock`: `1 540` ревизий — `Біблія=442425`,
  `Індекс:Ivan Ohienko Bible.djvu=960013` и полный список страниц
  `Сторінка:Ivan Ohienko Bible.djvu/1–1538`; SHA-256 канонической
  последовательности revision metadata:
  `ecce2e6d48a07f7baac96b393b1147a4f3b28c5eba6ac757f4de8f5b8a697dc9`.
  Детерминированный content bundle имеет `8 372 816` байт и SHA-256
  `c7bc09ffdb232ded0abae6b631e382d896396750e3d3931ba5ee07e22c3e0702`.

Полный список 1 540 записей находится внутри `source_lock.json`, а полный
защищённый content bundle — только в кэше. Stage-2 template не подменялся
непроверенным кратким диапазоном: в stage-3 evidence сохранены и полный список,
и его digest.

## Зафиксированные наборы и независимость

- Commons — основной печатный эталон точного издания 1988 года.
- Wikisource — производная машинная транскрипция того же Commons-скана, а не
  независимое издание.
- Internet Archive — зависимый контрольный DjVu, SHA-256
  `39d34d366554a2c798e180d0fce05a4ca11fc8c10901c174848e37f30468cee8`;
  зеркало/derivative не считается независимым текстовым источником.
- STEPBible TAHOT (4 файла), TAGNT (2 файла) и TVTMS закреплены commit
  `b9dcc831a98e0fd6f3c7e122be9ff68377c310c0`.
- Open Scriptures Hebrew Bible закреплён tag `v.2.2`, commit
  `6a5db284c715c18b239422e57bb89684e6a19f00`; его общая WLC/OpenScriptures
  линия с TAHOT явно помечена зависимой.
- Tanach.us закреплён как UXLC `2.5`, build `27.6`, text date `2026-04-01`,
  точным размером и SHA-256; это независимый контроль поверхности, не второй
  Strong-слой.
- unfoldingWord UGNT закреплён tag `v0.34`, commit
  `fc95b2b8aad08bb65ab54628ab685413a1139e97`.
- CrossWire KJV `3.1` закреплён commit
  `d490be7e34762deb2c76cb2c1306d4808e27890d` и остаётся только classic-Strong
  аудитом.
- Физический/библиотечный экземпляр издания 1988 года и снимки Ленинградского
  кодекса перечислены отдельно как manual-only controls без фиктивного SHA или
  локального файла.

Поздние редакции УБТ не входят в lock. Validator требует
`translation_id=ohienko_1988`, `edition_year=1988` для каждого украинского
текстового/сканового входа и глобально запрещает редакции после 1990 года.

## Получение, TLS и fail-closed поведение

Clean-cache run `2026-08-01T05:59:18Z`–`06:03:53Z` скачал и проверил 14/14
файлов. Следующий полностью offline run `06:03:53Z`–`06:03:54Z` дал 14/14
`cache_hit` без сетевых attempts. В clean run выполнено 44 HTTPS-запроса:
ошибок 0, TLS verify result везде `0`; единственная цепочка перенаправления —
разрешённый Internet Archive `302` на
`https://dn721308.ca.archive.org/0/items/BibleOhienko/Ohienko_Bible.djvu`.

Получение использует HTTPS-only, отклоняет downgrade, ограничивает redirect
пятью переходами, retry — четырьмя attempts для `429/500/502/503/504` и
сетевых ошибок с backoff `2/4/8` секунд. Размер и SHA-256 проверяются на
временном файле; только затем выполняется атомарная замена. Повреждённый ответ
не может заменить существующий валидный cache. Cache hit также сначала
проверяет размер и SHA-256.

Зафиксированные версии среды:

- Python `3.12.2`, OpenSSL `3.0.13`;
- curl `8.21.0` с Windows Schannel;
- Git `2.45.1.windows.1`;
- Flutter `3.38.9`, framework `67323de285`, Dart `3.10.8`;
- PowerShell `5.1.26100.8972`;
- Windows 11 Home `10.0.26200`.

## Сетевые ошибки и их разрешение

1. Первый bootstrap аварийно завершился до записи lock: bundled
   Python/OpenSSL trust path отклонил новую, фактически действующую цепочку
   Wikimedia. Проверка сертификата не отключалась. Транспорт переведён на уже
   установленный curl/Schannel; итоговый log сохраняет `ssl_verify_result`,
   leaf subject/issuer и сроки сертификатов.
2. Наивная серия title batches Wikisource получила HTTP 429 после примерно
   500 ревизий и также остановилась без неполного lock. Discovery заменён на
   paginated `allpages`, а content получается только по точным `revids` с
   контролируемым интервалом. Плавающие текущие страницы не стали входом.
3. Внешний timeout одного bootstrap-процесса сработал после записи generated
   artifacts. Этот exit не считался PASS; отдельный `--check` затем проверил
   lock и все 14 фактических cache-файлов, а независимый clean-cache run
   повторно скачал весь набор и завершился PASS.

## Автоматические тесты этапа 3

Новые тесты проверяют:

- структуру, полноту, обязательные роли и уникальность `source_id`;
- точные commit/tag/revision и полный digest 1 540 Wikisource revisions;
- заполненные Commons/Wikisource placeholders;
- отказ при неверном размере и SHA-256 до замены валидного cache;
- offline cache hit без обращения к сети;
- bounded retry/backoff и контролируемую 302→200 redirect chain;
- запрет `latest`, `main`, `master`, `HEAD` в download URL;
- запрет поздней/смешанной УБТ и ложной классификации manual controls.

## Выполненные команды

| Команда | Результат |
| --- | --- |
| `python -m scripts.bible_module.ukrainian_stage_3_sources --check` | PASS; lock и 14 cache-файлов совпали по размеру/SHA-256 |
| `verify_source_manifest(manifest_path=.../source_lock.json)` из существующего `fetch_sources.py` | PASS; stage-3 lock совместим с текущей checksum-проверкой |
| `python -m scripts.bible_module.ukrainian_stage_3_sources --verify-clean-cache` | PASS; 14 downloads + 14 offline cache hits |
| `python -m unittest scripts.bible_module.tests.test_sources scripts.bible_module.tests.test_ukrainian_stage_3_sources` | PASS; 13 тестов |
| `python -m unittest discover -s scripts/bible_module/tests` | KNOWN PRE-EXISTING FAILURE; 118 тестов, 1 failure + 2 errors только в старом extended-Strong тесте |
| `python -m unittest discover -s scripts/content_tool/tests` | PASS; 30 тестов |
| `dart format .` | PASS; 475 файлов, 0 изменений |
| `flutter analyze` | PASS; `No issues found`, 203,6 с |
| `flutter test` | PASS; 920 тестов |
| `dart run scripts/check_forbidden_patterns.dart` | PASS |
| `dart run scripts/check_docs_sync.dart` | PASS |
| `flutter test integration_test/smoke/bible_navigation_smoke_test.dart -d windows` | KNOWN PRE-EXISTING FAILURE; тот же finder `bible_module_dropdown`, что в этапе 2 |
| `git diff --check` + проверка whitespace во всех новых файлах | PASS; CSV нормализован на LF |
| Итоговый аудит Git/кэша/секретов | PASS; в change set нет исходных бинарников и высокодостоверных секретов, все 23 payload-файла общего локального кэша игнорируются Git |

## Предсуществующие отклонения

### Python discovery

Результат точно совпал с validation log этапа 2: старый fixture
`test_apply_extended_strong_descriptions.py` использует `G6000` и `G20833`,
тогда как актуальные content-tool ranges заканчиваются на `G5624`. Получены те
же 2 `ValueError` и 1 несовпавшее ожидаемое сообщение. Изменённые stage-3
файлы не импортируются этим старым тестом; все 10 новых тестов прошли.

### Bible smoke

Результат точно совпал с этапом 2: строка 54 ожидает один
`bible_module_dropdown`, неизменённый runtime создаёт два. Этап 3 не меняет
runtime/UI/route/smoke. Этот несвязанный дефект не исправлялся и quality gate
не ослаблялся.

Другой smoke не является релевантным: stage-3 change set содержит только
Python source acquisition, его тесты, machine reports и roadmap. Startup,
route, deep link или пользовательский flow не менялся.

## Ограничения

- `gpg` по-прежнему отсутствует. Новая зависимость не добавлялась: отклонённые
  eBible-кандидаты не являются входами этапа 3, а утверждённые файлы имеют
  точные revision/commit/version, размер и SHA-256.
- Tanach.us публикует текущий UXLC archive по mutable product URL. Версия
  `2.5`, build `27.6`, embedded date, размер и SHA-256 закреплены; любое
  upstream изменение аварийно завершит fetch. Это зафиксированное ограничение,
  а не плавающий `latest`.
- Schannel не отдаёт negotiated cipher через curl write-out; в log сохранены
  TLS verify result, backend, leaf certificate и даты. TLS verification не
  ослаблялась.
- Ручные независимые контроли не превращены в машинные источники. Их
  фактическое применение к спорным чтениям относится к последующим этапам
  разбора/аудита.

Лицензия, версия и происхождение каждого обязательного машинного входа
однозначны. Неприкреплённого `latest` нет; поздней УБТ нет; все обязательные
входы повторно получены и проверены. Критерий выхода этапа 3 выполнен.

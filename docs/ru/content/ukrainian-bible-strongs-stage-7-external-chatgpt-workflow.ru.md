# Внешняя помощь ChatGPT для этапа 7 украинского Strong-модуля

Doc-Version: `1.0.2`
Last-Updated: `2026-08-15`
Source-Commit: `working-tree`

## Назначение

Этот документ описывает, какую ограниченную часть этапа 7 можно передать в
обычный ChatGPT Chat/Project или Deep Research, не ослабляя доказательный
контракт выравнивания и не расходуя лимит Codex. Внешний ответ всегда считается только кандидатом на
evidence или review. Он не становится production link, Strong-маркером,
лицензионным решением или закрытым пунктом дорожной карты до локальной проверки.

Главное правило: ChatGPT не должен «подбирать номер Стронга к украинскому слову».
Сначала должен быть доказан конкретный original token или допустимая textual
alternative group, от которой произошёл украинский token/span. Только Strong
этого original token может попасть в итоговую разметку.

## Что использовать

| Возможность | Подходящие задачи этапа 7 | Не использовать для |
| --- | --- | --- |
| Deep Research | Небольшие source-heavy досье: история редакции, лицензия, один–пять textual loci, поиск scan/page/edition evidence | Массовое token alignment, gold-разметка, калибровка и генерация Strong |
| Обычный ChatGPT Chat | Один answer-free gold book-shard, короткий независимый аудит схемы, 5–25 manual-review случаев, проверка rationale | Доступ одновременно к двум blind-проходам или к candidates/legacy |
| Обычный ChatGPT Project | Общие инструкции и разрешённые загруженные файлы для серии однородных Chat/Deep Research заданий | Общий Project для pass 1 и pass 2: project files могут нарушить blindness |
| ChatGPT Work | Не использовать, если цель — сохранить лимит Codex: Work и Codex имеют общий usage budget | Любая вынесенная работа, предназначенная для экономии Codex |
| Локальный Project/папка | Read-only аудит кода, fixtures и manifests | Blind review всего репозитория: в нём видны candidates и готовые ответы |

## Изоляция от лимита Codex

Официальная страница [OpenAI Pricing](https://learn.chatgpt.com/docs/pricing)
прямо указывает: ChatGPT Work и Codex используют одинаковые credits и usage
limits. Поэтому Work не является внешним
ресурсом для целей этого workflow и далее запрещён. Использовать нужно
`chatgpt.com` в режиме обычного `Chat` либо `Deep Research`, а не `Work`, Codex,
Codex CLI, IDE extension, Codex cloud или локальную папку через Codex.

ChatGPT Project допустим только как контейнер загруженных файлов. Внутри него
каждое задание нужно начинать именно кнопкой/режимом `Chat` или `Deep Research`:
один Project может содержать как обычные Chat, так и Work-чаты, поэтому само
слово Project ещё не гарантирует изоляцию.

Перед каждым внешним запуском:

1. открыть обычный интерфейс ChatGPT на `chatgpt.com`;
2. убедиться, что выбран `Chat` или `Deep Research`, а не `Work`/Codex;
3. не запускать task/goal/agent через Codex и не подключать локальный репозиторий;
4. записать в `receipt.json` отображаемые режим и модель;
5. при изменении интерфейса или тарификации снова проверить официальную страницу
   Pricing; при неоднозначности внешнюю работу не запускать.

OpenAI API также не расходует subscription-квоту Codex, но оплачивается отдельно
по API-токенам, поэтому в данном workflow по умолчанию не используется. Если
нужного режима нет на аккаунте, использовать обычный Chat с прикреплёнными
файлами, а не переходить в Work.

## Неизменяемые границы

- Не загружать секреты, API keys, working DB, SQLite и содержимое `web/db`.
- Не загружать весь gitignored corpus, если достаточно одного минимального
  packet или нескольких loci.
- Для blind gold не давать доступ к `alignment_candidates*`, rejected legacy,
  `strong_alignment*`, completed другому проходу, adjudication или report с
  готовыми решениями.
- Для pass 1 и pass 2 использовать разные чаты, разные reviewer IDs и отдельные
  Projects либо работу без Project. Ни один чат не читает результат другого.
- Deep Research не получает право использовать ESV, CSB, NET, LEB, ULT/UST,
  UD Ukrainian-IU, OpenHebrewBible и случайные Strong-Библии как источник
  production data.
- KJV, TR, RST и переводы могут быть только control/evidence. Один перевод не
  доказывает OH1988 link.
- Запрещены position-only, nearest/neighbor, proportional, verse-bag,
  frequency-only и majority-only решения.
- При недостатке доказательств писать `unresolved`, `null` или `needs_review`,
  а не заполнять пробел правдоподобным предположением.
- Внешний ответ не редактирует stage-6 text/comment, stage-5 mapping, source
  registry, overrides или roadmap.

## Организация внешней работы

### 1. Создать место для результатов

Полный внешний материал хранить только здесь:

```text
scripts/bible_module/work/ukrainian_stage_7_20260801/external_chatgpt/
  <task_id>/
    request.md
    task_manifest.json
    inputs/
    raw_response.md
    result.jsonl
    receipt.json
    local_validation.txt
```

Каталог `work/` gitignored. После локального принятия в Git разрешено добавить
только безопасный manifest/hash, минимальные stable-ID annotations, ссылки,
краткое rationale и лицензионно допустимые выдержки. Если внешняя работа реально
использована, её агрегированный versioned manifest создаётся в:

```text
scripts/bible_module/reports/ukrainian_stage_7_20260801/external_research.manifest.json
```

Не создавайте этот manifest для эксперимента, который был полностью отклонён.

### 2. Создать task manifest до запуска

Минимальные поля `task_manifest.json`:

```json
{
  "schema_version": 1,
  "contract_version": "ukrainian-stage-7-evidence-alignment-v1",
  "task_id": "uk7ext:<kind>:<scope>:<ordinal>",
  "roadmap_items": ["7.4"],
  "mode": "chatgpt_web_chat|deep_research",
  "review_pass": 1,
  "reviewer_id": "external-chatgpt:<account-label>:<unique-run-id>",
  "allowed_inputs": [],
  "forbidden_channels": [],
  "input_sha256": {},
  "expected_outputs": [],
  "acceptance_checks": []
}
```

SHA-256 вычисляется локально, не доверяется значению, которое написал ChatGPT.
В `receipt.json` после запуска сохранить дату, отображаемое название модели,
режим, reviewer ID, идентификатор/ссылку чата при наличии, перечень переданных
файлов и фактические имена скачанных результатов. Ссылка на чат не заменяет
локальные файлы и SHA.

### 3. Один чат — один проверяемый результат

- Один textual research chat: один–пять тесно связанных loci.
- Один gold chat: одна книга, один pass, один frozen shard.
- Один B/C review chat: 5–25 случаев одного типа.
- Один audit chat: одна схема, один manifest или один класс инвариантов.

Не продолжать в том же чате новую независимую проверку: предыдущие ответы будут
скрытым каналом зависимости.

### 4. Локальная приёмка обязательна

Каждый результат проходит последовательно:

1. Сохранить raw response и скачанные файлы без исправления.
2. Вычислить SHA-256 локально и сверить с task manifest.
3. Проверить JSON/JSONL schema, stable IDs, exact target refs и полноту.
4. Для web research открыть каждую реально использованную ссылку; проверить
   автора, издание, страницу/locator, цитату, лицензию и независимость источника.
5. Для gold выполнить `expand`, затем `gold_compact check`.
6. Сравнить с независимым проходом; расхождения не сглаживать, а передать в
   adjudication.
7. Только после принятия импортировать результат в stage-7 workflow и записать
   versioned manifest/hash.

Структурно невалидный или непроверяемый ответ сохраняется как rejected audit и
не влияет на candidates, gold, calibration, overrides или markup.

## Пакет A — Deep Research для 7.0/7.1/7.8

### Когда применять

Только для узкого вопроса, требующего внешних первичных источников: точная
редакция, manuscript/edition reading, издательское примечание, scan page,
лицензия конкретного слоя или источник авторской сноски. Оптимальный размер —
один–пять loci. Завершённый fingerprint OH1988 не открывать повторно без нового
конкретного противоречия.

### Передать

- `ukrainian-bible-strongs-stage-7-alignment-plan.ru.md` — только релевантный
  раздел;
- `source_registry.json`;
- релевантные строки `textual_fingerprint.manifest.json`;
- exact OH1988 verse/comment и scan image/page только исследуемых loci;
- exact original candidate rows со stable IDs;
- краткий список уже проверенных источников, чтобы не считать их независимыми
  второй раз;
- отдельный список разрешённых и запрещённых источников.

Не передавать candidate scores, готовый override или желаемый Strong: это создаёт
confirmation bias.

### Шаблон запроса

```text
Выполни глубокое исследование только для перечисленных loci украинского издания
OH1988. Цель — найти проверяемое evidence о конкретном original reading, а не
подобрать Strong к украинскому слову.

ОБЯЗАТЕЛЬНО:
1. Приоритет: exact scan/edition/manuscript/catalog/publisher и академические
   первичные или критические источники. Переводы — только controls.
2. Для каждого утверждения дай прямой URL, автора/учреждение, точное издание,
   страницу/folio/line/locator, дату доступа и лицензию/rights statement.
3. Разделяй: DIRECT_SOURCE_STATEMENT, TRANSCRIPTION, INFERENCE и UNRESOLVED.
4. Не распространяй вывод одного locus на другие.
5. Не используй position, neighboring word, verse bag, частотность или один
   перевод как доказательство.
6. Не используй запрещённые в приложенном policy источники.
7. Если exact evidence не найдено, явно верни UNRESOLVED; не реконструируй его.
8. Не назначай final Strong и не редактируй stable IDs.

Выход:
- research_report.md с кратким выводом и source-by-source критикой;
- evidence.jsonl: по одной записи на source claim с полями locus, claim_status,
  source_type, exact_url, edition, locator, short_excerpt, inference,
  license_statement, independence_group, supports_ids, contradicts_ids,
  unresolved_reason;
- rejected_sources.csv с причиной отклонения каждого неподходящего источника.
```

### Что это может закрыть

Внешнее исследование может предоставить evidence для локального решения 7.0,
7.1 или отдельного 7.8 case. Само по себе оно не закрывает подпункт: главный
pipeline должен перепроверить источник, лицензию, stable-ID crosswalk и сохранить
решение в fingerprint/manual review/override.

## Пакет B — один внешний blind gold-проход для 7.4

### Рекомендуемая экономия

Наиболее полезный текущий вариант: один проход book-shard выполняет обычный
ChatGPT web Chat с загрузкой answer-free файлов, второй — независимый Codex reviewer. Это примерно вдвое сокращает
внутреннюю reviewer-нагрузку и сохраняет cross-model disagreement signal.

Начать пилотом с `Ruth`, shard `008`: 32 стиха, 851 original decisions и 734
target-accounting decisions на проход. Не передавать сразу несколько книг.

Пилот `Ruth` завершён 15 августа 2026 года. Третья внешняя версия прошла
`expand`/`check` без ошибок и совпала с независимо повторённым blind pass 2 по
84,101% exact link/null semantics (82,139% original и 86,376% target), тогда как
внутренняя база `Gen–Judg` составляет 80,191%. Поэтому обычный ChatGPT Chat
признан пригодным для одного blind-прохода, но только с обязательными вторым
проходом и adjudication. Первые две версии были отклонены: одна из-за metadata,
вторая из-за cardinality двух omission-групп.

### Изоляция

- Создать отдельный Project `OH1988 gold pass 1` или работать без Project.
- Для pass 2 создать другой Project/чат без файлов pass 1.
- В Project загрузить только template, его manifest, prompt и при необходимости
  схему compact review.
- Не подключать весь репозиторий, GitHub или папку stage-7 work.
- Отключить web/deep research для этого задания.

### Файлы для `Ruth` pass 1

```text
scripts/bible_module/work/ukrainian_stage_7_20260801/
  gold_compact_review/pass_1/Ruth/
    review_pass_1.shard_008.compact.template.jsonl
    gold_compact_review.manifest.json
```

Для pass 2 использовать только соответствующие файлы из
`gold_compact_review/pass_2/Ruth/`.

### Шаблон запроса

```text
Ты выполняешь один независимый blind gold-review украинского OH1988.
Работай ТОЛЬКО с приложенным answer-free compact template и manifest.
Web, Deep Research, candidates, legacy assignments, другой review pass и готовые
ответы запрещены.

ЦЕЛЬ:
- связать original token/group только с доказанным украинским token/span того же
  target_ref или поставить явный original null;
- каждый украинский token учесть ровно один раз как aligned, function_token или
  translation_addition;
- поддержать one-to-one, one-to-many, many-to-one, many-to-many,
  grouped_expression и omitted;
- не переносить связь по позиции, соседству, сходному слову или другому стиху.

ПРАВИЛА:
1. Не изменяй metadata, stable IDs, local oNNN/tNNN indices, offsets и строки.
2. Не выдумывай token ID. При сомнении используй null/high и честное rationale.
3. Для каждого group/null заполни evidence, rationale и severity.
4. Обрабатывай внутренне партиями по 4–8 стихов, после каждой партии проверяй
   отсутствие повторов и пропусков, но верни один полный файл всей книги.
5. Не назначай Strong самостоятельно: исходный Strong уже принадлежит original
   token; твоя задача — только link/null decision.
6. Никаких пояснений внутри JSONL и никаких Markdown fences.
7. `original_omitted` содержит ровно один original и ни одного target; несколько
   omissions всегда оформляются отдельными группами.
8. Не поглощай служебную морфему, аффикс, местоименный компонент или пунктуацию в
   широкую группу только ради отсутствия null. Если отдельный вклад не доказан,
   используй явный null.
9. Для реально присутствующего явления заполни `phenomena` одним или несколькими
   значениями из нормативного набора: `textual_variant`, `merge_split`, `reorder`,
   `omission`, `addition`, `repetition`, `named_entity`, `particle`, `compound`,
   `multiple_strong`, `rare_lemma`, `frequent_lemma`, `polysemy`. Пустой список
   допустим только когда ни одно из них не относится к решению.

ВЫХОД:
- один скачиваемый файл review_pass_<N>.shard_008.compact.completed.jsonl;
- короткая отдельная сводка counts, сомнений high и использованного reviewer ID.
Не утверждай, что файл принят: его проверит локальный валидатор.
```

### Локальная проверка

Сохранить файл в новый `completed_external/`, не перезаписывая template. Затем
выполнить `expand` с exact shard manifest и `shard_id`, после чего `check` с теми
же inputs. Пример для pass 1:

```powershell
python -B -m scripts.bible_module.ukrainian_stage_7_gold_compact expand `
  --shard-manifest scripts/bible_module/work/ukrainian_stage_7_20260801/gold_review_shards/pass_1/gold_reviewer_packet_shards.manifest.json `
  --shard-id gold7:p1:shard:008:Ruth-Ruth `
  --template scripts/bible_module/work/ukrainian_stage_7_20260801/gold_compact_review/pass_1/Ruth/review_pass_1.shard_008.compact.template.jsonl `
  --compact-manifest scripts/bible_module/work/ukrainian_stage_7_20260801/gold_compact_review/pass_1/Ruth/gold_compact_review.manifest.json `
  --filled <external-completed.jsonl> `
  --output <external-raw-submission.jsonl>

python -B -m scripts.bible_module.ukrainian_stage_7_gold_compact check `
  --shard-manifest scripts/bible_module/work/ukrainian_stage_7_20260801/gold_review_shards/pass_1/gold_reviewer_packet_shards.manifest.json `
  --shard-id gold7:p1:shard:008:Ruth-Ruth `
  --template scripts/bible_module/work/ukrainian_stage_7_20260801/gold_compact_review/pass_1/Ruth/review_pass_1.shard_008.compact.template.jsonl `
  --compact-manifest scripts/bible_module/work/ukrainian_stage_7_20260801/gold_compact_review/pass_1/Ruth/gold_compact_review.manifest.json `
  --expanded <external-raw-submission.jsonl>
```

PASS означает только структурную пригодность. Семантическая приёмка наступает
после независимого второго прохода и adjudication. Если внешний pass массово
ставит 1:1, избегает null/grouped или совпадает с порядком слов подозрительно
часто, его отклонить независимо от успешного schema check.

### Готовые следующие внешние задания

После успешного пилота подготовлены три независимых gitignored пакета:

```text
scripts/bible_module/work/ukrainian_stage_7_20260801/external_chatgpt/
  uk7ext_gold_1Sam_pass1_009/
  uk7ext_gold_2Sam_pass1_010/
  uk7ext_gold_1Kgs_pass1_011/
```

Каждый каталог содержит `request.md`, предварительный `task_manifest.json`,
`receipt.template.json` и подкаталог `inputs/` с exact compact template,
manifest и готовой `completed_metadata.template.jsonl`. Загружать следует только
три файла из `inputs/`, а полный запрос копировать из `request.md`. Начинать с
`1Sam`; `2Sam` и `1Kgs` запускать в новых отдельных чатах только после сохранения
результата предыдущей книги. Пакеты не являются выполненной разметкой и остаются
в `work/` до возврата и локальной проверки.

## Пакет C — аудит методов 7.5/7.6

### Передать

- один pure module или небольшой diff;
- его CC0 fixtures/tests;
- запрещённые методы и hyperedge schema;
- 20–100 обезличенных candidate rows без gold labels;
- конкретный вопрос: cardinality, verse locality, null accounting, leakage,
  evidence independence или determinism.

### Шаблон запроса

```text
Выполни read-only adversarial audit приложенного stage-7 компонента.
Не предлагай новые production links и не используй gold labels.
Найди только воспроизводимые нарушения: cross-verse/dangling IDs, неверную
cardinality, position/neighbor/proportional/verse-bag transfer, single-translation
proof, leakage, stale digests, недетерминированность и потерю null/alternative.

Для каждого finding верни: severity, exact file/field/record ID, минимальный
контрпример, ожидаемый инвариант, способ локальной проверки и CC0 regression test.
Если доказательства нет, пометь hypothesis, а не defect.
```

Результат помогает 7.5/7.6 только как audit backlog. Код исправляется и тестируется
локально; внешний review не меняет candidate vote или resolver eligibility.

## Пакет D — B/C manual-review для 7.8

Использовать после калибровки, партиями по 5–25 однородных случаев. Для обычного
span/link review подходит обычный Chat без web. Deep Research включать только
когда конкретный case требует нового внешнего primary-source evidence.

Передать exact case packet: target_ref, Ukrainian token IDs/offsets, original IDs,
raw/normalized form, morphology, textual status, разрешённое evidence и input
digests. Candidate score можно скрыть для независимой проверки; запрещённые
источники и другой reviewer answer всегда скрываются.

```text
Проверь только приложенные manual-review cases. Для каждого выбери accepted link,
explicit null или unresolved. Не изменяй IDs/Strong и не создавай новый original
token. Один перевод, позиция, частотность или legacy не являются достаточным
evidence. Для accepted укажи exact Ukrainian span, exact original IDs, evidence и
rationale; для null — тип omission/addition/function; для unresolved — чего именно
не хватает. Critical/high не понижай ради покрытия.
```

Каждый critical/high case требует второго независимого прохода. Локальный import
создаёт override только после проверки current input SHA и supersedes chain.

## Пакет E — независимый аудит 7.7/7.9

### 7.7 calibration

Можно передать формулы, aggregate fold metrics и code/tests для Wilson lower
bound. Нельзя передавать sealed-fold labels для настройки порогов. Просить проверить
confidence interval, sample size, stratification, leakage и правило отключения
`A_auto` в малых/слабых strata. Фактические пороги и метрики вычисляются локально.

### 7.9 final manifest audit

Передать только versioned manifests, reports и safe diffs. Попросить составить
таблицу claim → artifact → field → SHA/test → verdict. ChatGPT может обнаружить
несогласованность, но не может подтвердить byte round-trip, exact 31 102 equality,
отсутствие dangling Strong или детерминизм без локального запуска обязательных
проверок.

## Как владельцу передать результат обратно Codex

Сохраните каталог внешнего задания в указанном gitignored `external_chatgpt/` и
напишите:

```text
Импортируй и независимо проверь внешний stage-7 пакет:
scripts/bible_module/work/ukrainian_stage_7_20260801/external_chatgpt/<task_id>/
Не принимай его выводы без проверки sources, licenses, stable IDs, SHA, schema и
локальных invariants. При rejection сохрани причину; при acceptance обнови только
соответствующий artifact/manifest и пункт roadmap.
```

Если невозможно положить файлы напрямую, передайте:

1. точный исходный prompt;
2. все загруженные файлы или их неизменённую копию;
3. скачанный raw result;
4. название режима и модели, дату, reviewer ID;
5. ссылку на чат как дополнительную, но не единственную provenance;
6. перечень источников, которые ChatGPT фактически использовал.

## Критерии отказа

Внешний пакет отклоняется целиком либо частично, если:

- отсутствует exact prompt или невозможно установить переданные inputs;
- stable IDs/offsets придуманы, изменены или не принадлежат указанному verse;
- нет проверяемого URL/page/locator для source claim;
- источник не имеет закрытой лицензии для фактически используемого слоя;
- output опирается на запрещённый перевод, position, neighbor, verse bag,
  frequency или один bridge;
- blind reviewer видел candidates, legacy или другой pass;
- пропущены null/alternative/grouped состояния;
- локальная schema/SHA/invariant проверка не проходит;
- ChatGPT сообщает уверенный вывод там, где evidence допускает только unresolved.

## Практический порядок применения

1. Пилот: обычный ChatGPT web Chat выполняет только один `Ruth` pass, второй остаётся
   независимому Codex reviewer.
2. Локально проверить и сравнить оба прохода. Оценить structural failure rate,
   disagreement rate и характер position bias.
3. Продолжать внешние gold shards только если пилот не ухудшает качество; одна
   книга за один чат.
4. Параллельно отдавать Deep Research только отдельные unresolved B/C textual
   cases, максимум пять loci за исследование.
5. После finalized gold использовать внешний ChatGPT для read-only аудита
   evaluator/calibration reports, но считать authoritative только локальные
   вычисления.
6. Перед закрытием 7.9 выполнить внешний manifest audit как дополнительный слой,
   затем весь обязательный локальный validation suite.

Такой процесс уменьшает расход основного Codex-контекста, но не переносит наружу
право принимать production Strong decisions.

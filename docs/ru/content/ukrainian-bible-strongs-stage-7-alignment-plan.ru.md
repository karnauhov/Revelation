# План доказательного Strong-выравнивания OH1988

Doc-Version: `1.1.0`
Last-Updated: `2026-08-15`
Source-Commit: `working-tree`

## Статус документа

Это план этапа 7, а не результат его выполнения. Генерация финальной Strong-разметки, принятие автоматических связей и SQLite-сборка в рамках подготовки плана не выполнялись.

## Основное решение

Этап 7 следует строить не как перенос готовых номеров из одного перевода и не как позиционное сопоставление двух последовательностей. Номер Strong обозначает словарную лемму, а не конкретную рукопись; выбор текстовой традиции определяет наличие и форму исходных tokens, после чего нормативный номер берётся только у конкретного древнееврейского, арамейского или греческого token/morpheme утверждённого оригинально-языкового источника. Другие переводы используются как независимые пословные мосты, помогающие доказать, как этот исходный token выражен в OH1988.

Желаемая цепочка доказательства:

`оригинальный token → Strong + lemma + morphology → один или несколько независимо выровненных переводных tokens → украинский token/span OH1988`.

Наличие одинакового Strong где-либо в том же стихе, KJV/TR/RST, другом переводе или соседнем стихе само по себе не доказывает последнюю связь. Простое большинство переводов также не является доказательством, если они зависят от одной разметки или только повторяют verse-level набор номеров.

## Почему сначала нужен текстологический fingerprint

Источниковедческие материалы описывают OT Огиенко как перевод с масоретского древнееврейского текста с контролем греческой традиции, а NT — как перевод с критического издания `Novum Testamentum Graece` Эберхарда Нестле. Этого недостаточно, чтобы молча назначить одну современную цифровую редакцию основой для каждого места OH1988.

До массового выравнивания необходимо:

- проверить титульные листы, предисловия, примечания OH1988, методологическую работу Ивана Огиенко 1927 года, доступные издательские материалы и рецензирование Британского библейского общества;
- собрать различительные места OT для MT/LXX и NT для ранних изданий Nestle, SBLGNT/NA-подобной, Byzantine/TR и иных реально возможных традиций;
- классифицировать фактическое чтение OH1988 по каждому месту и сохранить scan/page/revision evidence;
- назначать основной оригинальный token universe по книге/перикопе/стиху, сохраняя альтернативные чтения отдельно;
- отправлять неразрешённые текстологические случаи в manual review, не подменяя их наиболее близким современным текстом.

Печатные авторские сноски exact OH1988 образуют отдельный первичный
evidence-канал. Все стиховые и заголовочные uses нужно учесть ровно по одному
разу и классифицировать как original-language form/transliteration,
grammar/morphology, lexical semantics, textual variant, cross-reference или
общий комментарий. Упомянутые еврейские и греческие формы можно сопоставлять
только с source-qualified stable IDs того же locus; точный footnote anchor
сохраняется отдельно от украинского текста. Сноска помогает выбрать или
проверить исходное чтение, но не является дополнительным текстом стиха,
translation bridge или самостоятельным доказательством original→OH1988 span.
Она не поступает на вход statistical/contextual aligner, имеет нулевой
автоматический вес, а явный textual-variant note обязательно проходит
component-level manual review до вывода Strong.
Замороженный `target_comment` разрешено показывать blind gold-reviewer как
первичное предкандидатное пояснение переводчика; он не превращается в
независимый witness и не используется для обучения candidate generator.

Например, печатные формы `al pnej/pnei tehom` в сносках к `Gen.1.2`
допускают exact same-locus corroboration `עַל / H5921`, `פְּנֵי / H6440`,
`תְהוֹם / H8415`. Повторяющееся в стихе `עַל־פְּנֵי` остаётся набором
равноправных кандидатов до доказанного span-level решения: marker anchor не
разрешает выбрать ближайший original или украинский token по позиции.

Первичный исторический источник для проверки методологии: [НБУВ — «Методологія перекладу Святого Письма…», 1927](https://irbis-nbuv.gov.ua/ulib/item/ukr0000030085). Современное исследование, которое прямо называет масоретскую основу OT и издание Nestle для NT, должно использоваться как вторичное свидетельство, а не вместо оригинальных документов: [«Особливості паратекстів українських перекладів Святого Письма»](https://www.researchgate.net/publication/382116933_Osoblivosti_paratekstiv_ukrainskih_perekladiv_Svatogo_Pisma).

## Реестр источников-кандидатов

Любой новый корпус принимается только после фиксации точной версии/commit, URL конкретного набора, license file, SHA-256, покрытия, версификации, token IDs и отношения независимости. Исходники хранятся в gitignored cache/work; в Git попадают реестр, manifests, hashes, безопасные fixtures и отчёты.

### Уже утверждённая оригинально-языковая основа

- OT: OSHB/TAHOT как носители Hebrew/Aramaic token, morphology и Strong; UXLC/Tanach как независимый контроль текста и границ.
- NT: TAGNT как основной amalgamated token/variant/Strong источник; UGNT и предусмотренные этапом 4 источники как независимые controls.
- STEPBible-Data опубликован под CC BY 4.0 и документирует TAHOT/TAGNT и backward compatibility Extended Strong с классическими номерами: [официальный репозиторий](https://github.com/STEPBible/STEPBible-Data).
- OSHB фиксирует уникальные исходные word IDs и public-domain WLC text: [официальный репозиторий](https://github.com/openscriptures/morphhb).

Эти источники задают допустимый verse-local набор исходных tokens и Strong. Они не решают автоматически, какой украинский token выражает каждый исходный token.

### Рекомендуемые независимые переводные мосты

1. Russian Synodal Bible, ручное выравнивание BiblioNexus:

   - OT `WLCM-RUSSYN-manual`, NT `SBLGNT-RUSSYN-manual`;
   - alignment metadata — CC BY 4.0, RUSSYN — public domain;
   - [OT manifest](https://raw.githubusercontent.com/Clear-Bible/Alignments/main/data/rus/alignments/RUSSYN/WLCM-RUSSYN-manual.toml), [NT manifest](https://raw.githubusercontent.com/Clear-Bible/Alignments/main/data/rus/alignments/RUSSYN/SBLGNT-RUSSYN-manual.toml), [репозиторий Clear Bible Alignments](https://github.com/Clear-Bible/Alignments).

   Это самый ценный дополнительный мост из-за ручной original→Russian разметки и близости русского и украинского языков. Близость языков повышает качество кандидатов, но не разрешает перенос RUSSYN links на OH1988 без отдельного Russian→Ukrainian token/span evidence. Следует отдельно проверить заявленный `LatinWordTokenizer` в metadata на кириллическом target.

2. Young's Literal Translation, ручное выравнивание Clear Bible:

   - OT `WLC-YLT-manual`, NT `NA27-YLT-manual`;
   - alignment — CC BY 4.0, YLT — public domain;
   - точные строки лицензий и источников находятся в [`data/catalog.tsv`](https://github.com/Clear-Bible/Alignments/blob/main/data/catalog.tsv) того же репозитория.

   YLT полезен как формально близкий английский контроль, независимый от RUSSYN. Он не должен получать больший вес только из-за более похожего порядка слов.

3. Berean/MACULA — контекстный, не самостоятельный решающий мост:

   - Berean Standard Bible объявлена CC0; study apparatus использует STEPBible lexicon: [официальное описание](https://biblicalalignment.org/about);
   - MACULA Greek morphology, senses, frames и mappings опубликованы под CC BY 4.0: [репозиторий и лицензия](https://github.com/Clear-Bible/macula-greek/blob/main/LICENSE.md).

   Разрешается использовать только точно скачиваемый и лицензированный слой. Greek→English gloss не равен пословному выравниванию полного BSB и не может быть представлен как независимое голосование перевода.

### Условные источники, требующие отдельного решения владельца

- ULT/UST дают form-centric и meaning-centric представления и публикуются под CC BY-SA 4.0: [официальный каталог](https://unfoldingword.org/for-translators/content/) и [лицензия](https://unfoldingword.org/about/license/). До использования нужно письменно решить, возникает ли ShareAlike для производного alignment/lexicon и как он совместим с лицензией OH1988 и репозитория.
- UD Ukrainian-IU содержит ручные lemmas/morphology, но имеет CC BY-NC-SA 4.0: [официальный репозиторий](https://github.com/UniversalDependencies/UD_Ukrainian-IU). До включения корпуса или производной модели нужны отдельное подтверждение владельца и план attribution/ShareAlike. OH1988 surface text при этом не должен исправляться по современной морфологии.
- OpenHebrewBible содержит translation mappings, но использует CC BY-NC 4.0 и сложные upstream ограничения BHS/других переводов: [официальный репозиторий](https://github.com/eliranwong/OpenHebrewBible). Без отдельного юридического решения его данные не принимаются и не перераспространяются.

### Не принимать по умолчанию

- ESV, CSB, NET, LEB и другие copyrighted targets из Clear Bible Alignments, даже если сами alignment annotations имеют CC BY 4.0: license target text и право на производный украинский lexicon должны быть доказаны отдельно.
- случайные SWORD/e-Sword/OSIS/JSON выгрузки и сайты с надписью «Strong Bible» без точной редакции, word IDs, provenance и лицензии;
- KJV, TR, RST и существующие проектные БД как независимое подтверждение: они допустимы как контроль/регрессия, но не как источник автоматического binding;
- verse-level Strong bags без token-to-original alignment.

## Модель данных

### 1. Неизменяемый украинский слой

Единственный вход текста — `scripts/bible_module/work/ukrainian_stage_6_20260801/synthesized_text.jsonl` с `output_sha256 = e55156cd4c201077de3c2e1d44b06dd1035a7a8db7c26321869f860768671bcf` из stage-6 manifest. Manifest имеет SHA-256 `75d1f0199a528a662a69d55629ecebafa3264122d1b7b2c8df3e3dc8a92ea4af`.

Stage 7 не пересинтезирует текст из stage 5. Для каждого из 31 102 targets сохраняются точные scalar/byte offsets surface tokens; `target_comment` читается и проверяется, но не изменяется.

### 2. Original token universe

Для каждого target/source span хранится ordered список исходных tokens/morphemes:

- stable source token ID, raw/normalized form, lemma, morphology, Strong и textual witness;
- принадлежность Strong конкретному token/morpheme, а не только стиху;
- primary/alternative reading и основание выбора;
- source→target versification rule этапа 5;
- нулевое соответствие для пропущенного в переводе исходного элемента.

### 3. Украинский token и lexeme ledger

Словарь строится по occurrences, а не как таблица «одно украинское слово = один Strong». Минимальные поля:

- exact surface, normalized comparison form, offsets, verse/book/testament и context digest;
- один или несколько lemma/POS/morphology candidates с указанием метода и confidence;
- candidate Strong с раздельными счётчиками direct-original, RUSSYN, YLT, contextual-gloss, corpus-history и manual evidence;
- принятые, отклонённые и unresolved случаи; примеры контекстов;
- распределение Strong и entropy/polysemy, чтобы частотное значение не подавляло редкое;
- multi-token expressions, one-to-many, many-to-one, many-to-many и multiple-Strong-per-surface группы;
- negative evidence: почему очевидный по частоте кандидат неприменим в данном месте.

Lexeme ledger является обучающим и аудиторским ресурсом. Он не назначает номер сам по себе. Для проверки circular leakage статистика конкретного стиха не может обучать решение для того же стиха; использовать book-held-out или k-fold out-of-fold counts.

### 4. Граф доказательств

Выравнивание представляется двудольным hypergraph:

- слева original tokens/morphemes со Strong;
- справа точные украинские token spans;
- hyperedge допускает `0:n`, `m:0`, `1:n`, `m:1` и `m:n`;
- порядок слов — слабый prior, а не жёсткое ограничение;
- каждое ребро содержит top-k alternatives, независимые evidence components, calibrated score и decision status;
- null nodes обязательны для omissions, additions, articles/particles, implicit subjects и иных реально невыраженных элементов.

## План этапа 7

### 7.0. Заморозка входов и лицензий

- проверить stage 3/4/5/6 `--check` и побайтный SHA stage-6 text/comment;
- создать `source_registry.json` с точными версиями, commits, URL, licenses, digests, coverage и dependency graph;
- принять только RUSSYN/YLT и прочие источники, прошедшие license gate; условные источники не скачивать до решения владельца;
- доказать, что источники независимы на уровне alignment annotations, а не только названий переводов.

### 7.1. Textual fingerprint OH1988

- подготовить вариантную панель OT/NT и источник каждого locus;
- сверить OH1988 по Wikisource и точному Commons scan;
- определить primary/alternative original reading по месту;
- сохранить `oh1988_textual_fingerprint.jsonl`, report и unresolved review;
- не начинать массовое назначение, пока остаётся неизвестным token universe высокорискового места.

### 7.2. Токенизация и украинский лексический инвентарь

- построить exact surface tokens с byte/scalar offsets без изменения строки;
- отдельно получить comparison normalization и lemma/morphology candidates;
- создать частотность surface/lemma/n-gram по книгам, жанрам и Заветам;
- завести пустой `ukrainian_lexeme_strong_ledger.jsonl` и схемы polysemy/multiword;
- доказать plain-text/comment round-trip до добавления Strong.

### 7.3. Original token universe и переводные мосты

- спроецировать OSHB/TAHOT/TAGNT/UGNT tokens через неизменённую карту этапа 5;
- импортировать ручные original→RUSSYN и original→YLT links и отобразить их на те же stable original tokens;
- хранить каждый мост отдельно, не сливая зависимые источники в псевдоконсensus;
- классифицировать omissions/additions/groups и текстовые варианты каждого моста;
- создать полный per-verse candidate inventory Strong до связи с украинскими tokens.

### 7.4. Gold set и baseline-оценка

- сформировать стратифицированный gold set минимум из 2 000 стихов и 25 000 link decisions: OT/NT, все книги, частые/редкие lemmas, polysemy, reorder, omission, repetition, named entities, particles/articles, multiword и textual variants;
- вручную подтвердить original token↔OH1988 span с evidence; критические случаи проверять двумя независимыми проходами;
- прогнать сохранённый старый эксперимент только как baseline и измерить precision/recall/error taxonomy;
- зафиксировать thresholds до обучения/настройки, чтобы не подгонять их к финальному корпусу.

### 7.5. Независимые генераторы кандидатов

- direct multilingual model: OH1988↔original и OH1988↔RUSSYN/YLT;
- статистический bidirectional alignment на parallel verses с симметризацией;
- lexeme ledger out-of-fold;
- lemma/morphology/syntax и named-entity/transliteration rules;
- existing experimental assignments только как отдельный `legacy_baseline` feature с нулевым правом автоматически принять решение.

Допустимые инструменты оцениваются отдельно от их результатов. Например, [`fast_align`](https://github.com/clab/fast_align) имеет Apache 2.0, [`awesome-align`](https://github.com/neulab/awesome-align) — BSD-3-Clause, [SimAlign](https://github.com/cisnlp/simalign) — MIT, а [`bert-base-multilingual-cased`](https://huggingface.co/google-bert/bert-base-multilingual-cased) — Apache 2.0. Ни один model score не является доказательством без калибровки на OH1988 gold set, exact model digest и воспроизводимого CPU/GPU режима.

### 7.6. Constrained consensus

- candidate Strong всегда ограничен доказанным original token universe того же source→target span;
- решатель допускает свободный порядок, null links и hyperedges; positional nearest запрещён;
- source votes учитываются с поправкой на зависимость и тип перевода;
- автоматическое принятие разрешается только для заранее определённого класса A, если его lower-bound precision на замороженном gold set не ниже 99,5% и нет конфликтующего textual/bridge evidence;
- класс B требует ручной проверки; класс C остаётся unresolved high и блокирует закрытие;
- unaligned украинский token и невыраженный original token являются нормальными явными исходами, а не ошибкой, если доказаны.

### 7.7. Итеративный lexeme ledger без утечки

- обновлять surface/lemma→Strong статистику только принятыми A/manual decisions;
- пересчитывать кандидатов out-of-fold и измерять изменение precision отдельно от coverage;
- останавливать bootstrap при падении precision, росте entropy bias или book/testament drift;
- отдельно проверять одинаковые украинские формы с несколькими Strong и разные формы одного Strong;
- не повышать confidence только потому, что система повторяет собственное прежнее решение.

### 7.8. Manual review workbench

Для каждого спорного места показывать рядом:

- точный OH1988 text, source span и Commons page;
- original tokens с lemma/morphology/Strong и textual variants;
- ручные RUSSYN/YLT alignments и допустимые дополнительные controls;
- top-k украинских spans, score decomposition и negative evidence;
- историю того же surface/lemma в других книгах без данных текущего fold;
- proposed decision, reviewer, timestamp, evidence URLs/digests и supersedes chain.

Override хранит решение на stable token/span IDs и digests всех входов. При изменении любого digest override становится stale и не применяется молча.

### 7.9. Финальная сборка Strong-слоя и закрытие

- сгенерировать Strong markup отдельно от plain text;
- сохранить все Strong только рядом с существующим украинским surface token/span;
- выполнить точный strip/round-trip для 31 102 text и побайтное равенство всех comments этапа 6;
- проверить все original tokens: aligned, proven omitted, grouped или textual-alternative; никаких неописанных потерь/дублей;
- проверить invalid/dangling Strong, H/G ranges, extended normalization и multiple Strong;
- выполнить полный audit по OT/NT, книгам, главам, confidence/evidence classes и каждому источнику;
- дважды детерминированно сгенерировать результаты и пройти repository-wide проверки;
- не создавать SQLite и не начинать этап 8.

## Что переиспользуется из старого эксперимента

Снимок сохранён в `scripts/bible_module/reports/ukrainian_stage_7_experiment_20260801/`, код — в `ukrainian_stage_7_experiment*.py`.

Можно переиспользовать после адаптации:

- парсинг уже нормализованных OSHB/TAHOT/TAGNT/UGNT controls и raw→classic Strong normalization;
- exact украинскую токенизацию, markup renderer/stripper и round-trip invariants;
- восемь доказанных control-reference решений версификации;
- CC0 fixtures для reorder/omission/repetition/multiple Strong/invalid/round-trip;
- coverage/report scaffolding, unaligned inventory и четыре ручных контрпримера;
- структурные проверки invalid/dangling/no-neighbor.

Нельзя принимать как готовые решения:

- 440 280 экспериментальных Strong occurrences и 399 645 surface bindings;
- `global_corpus_lexical_assignment`, позиционное назначение и старые high/medium labels;
- experiment-generated Ukrainian text/comment, потому что он повторно синтезирован из stage 5 и не закреплён за published stage-6 output SHA;
- единый unresolved aggregate вместо per-edge review.

Старые assignments разрешено подавать только как baseline/candidate feature. Все они должны быть переоценены новым pipeline; отсутствие изменения не считается подтверждением.

## Обязательные артефакты этапа

Полные производные JSONL хранятся только в gitignored work-каталоге. В Git сохраняются schemas, code, CC0 fixtures, source/license registry, manifests/hashes, gold sample с юридически безопасными минимальными цитатами, overrides, safe diffs и reports.

Минимум:

- `source_registry.json`;
- `textual_fingerprint.manifest.json` и безопасный report;
- `author_comment_evidence.manifest.json`; полный построчный разбор авторских
  сносок хранится только в gitignored work-каталоге;
- `original_token_universe.manifest.json`;
- `parallel_bridge_alignment.manifest.json`;
- `ukrainian_token_inventory.manifest.json`;
- `ukrainian_lexeme_strong_ledger.manifest.json` и aggregate report;
- `gold_alignment.annotations.jsonl` со stable IDs/offsets/labels/evidence без непрерывного текста сторонних корпусов и `gold_alignment.manifest.json`; полный gold corpus хранится в gitignored work-каталоге;
- `alignment_candidates.manifest.json`;
- `strong_alignment.manifest.json`;
- `alignment_overrides.jsonl`;
- `strong_coverage_report.json`;
- `plain_text_preservation_report.json`;
- `evidence_independence_report.json`;
- `manual_review.jsonl`;
- `source_diff.csv`;
- `report.ru.md` и `validation_log.md`.

Каждый artifact имеет schema/contract version, exact input/output SHA-256, deterministic order/serialization, processed/skipped/error counts и статус. Manifests различают surface-token coverage, original-token coverage, Strong occurrence coverage и доказательную precision; один процент не заменяет остальные.

## Критерии выхода

Этап не закрывается, если:

- stage-6 text/comment SHA не совпадает или пересинтезирован из более раннего этапа;
- не определён original token universe для critical/high textual locus;
- хотя бы один финальный Strong не имеет конкретного украинского token/span и конкретного original token evidence;
- решение основано только на порядке, соседстве, verse bag, частотном словаре или одном переводе;
- source token потерян/дублирован и не имеет явного omitted/grouped/alternative статуса;
- gold-set lower-bound precision автоматического класса A ниже 99,5%;
- любой critical/high edge или stale override не разрешён;
- plain-text или comment round-trip расходится;
- forward/reverse mapping этапа 5 изменён;
- лицензия/attribution хотя бы одного реально использованного корпуса не закрыта;
- создан SQLite или начат этап 8.

## Решения, которые владелец должен принять перед запуском

1. Разрешить или отклонить ULT/UST (CC BY-SA 4.0) как производные alignment signals после отдельной оценки ShareAlike.
2. Разрешить или отклонить UD Ukrainian-IU (CC BY-NC-SA 4.0) для lemma/morphology assistance.
3. Определить, допустим ли OpenHebrewBible (CC BY-NC 4.0 со сложными upstream условиями); рекомендуемое значение по умолчанию — не использовать.
4. Утвердить размер gold set, минимальную precision 99,5% и необходимость второго человека для филологической проверки critical/high решений.

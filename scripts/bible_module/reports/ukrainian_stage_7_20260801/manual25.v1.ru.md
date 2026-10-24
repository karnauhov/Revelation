# OH1988: ручная development-проверка 25 случаев B_review

Проверены все **25 случаев в 25 разных стихах**. После независимой проверки обоснованы **37 полных соответствий в 23 случаях**: 28 групп содержат классические номера Strong, остальные 9 относятся к безномерным служебным компонентам. Два случая не получили принятой положительной замены. Все исходные предложения отклонены именно как полные hyperedges; это не означает, что каждое отдельное слово в них неверно.

**Нового покрытия сверх frozen gold не добавлено.** 35 точных identities повторно подтверждают gold; 2 отличаются группировкой уже покрытых компонентов (Joel.2.6 и Phil.1.10). Новых покрытых оригинальных компонентов с classic Strong — 0; новых reviewed verses — 0. Эти группировки не проецируются в декартово произведение пар. A_auto=0, production_acceptance=0, training/threshold changes=0.

Решения находятся в [отдельном JSONL](manual25_decisions.v1.jsonl); [completion manifest](manual25.v1.manifest.json) связывает payload, исходные packet hashes, роли и проверки. Ничего из этого слоя не внесено в finalized gold, frozen graph 7.6, mask/folds, старые policy или экспорт. Остальная часть каждого стиха не объявляется заново размеченной.

Партия выбрана до просмотра исходных packets по SHA256(`manual25-v1|case_id`): 8 случаев с лишними участниками, 8 с неполной группой, 9 смешанных; 13 OT / 12 NT; разные стихи, только development folds 0–2. Замены удобными примерами не производились. Это целевая диагностика ошибок, а не вероятностная выборка и не оценка precision всего корпуса.

Автор `/root` и отдельный агент `/root/manual25_reviewer` сделали source-based разбор. Reviewer получил packets без historical gold и авторских решений и запечатал свои суждения до QC автора. Во время initial review был преждевременно обменян один вывод по Eph.1.18; это исключение зафиксировано в обоих seals. Верхние rank/prior удалены из source view, но provenance содержит исходные некалиброванные generator scores. Человеческих blind-проходов, третьего adjudicator и независимой статистической сертификации эта партия не заменяет.

Из 34 первоначальных авторских групп reviewer подтвердил 29; пять exact forms потребовали изменения или hold. Четыре границы уточнены явно и проверены повторно; Lev.4.12 оставлен без принятой замены. Первоначальные payload/seals сохранены, исправления прослеживаются. Дополнительные reviewer-группы вне согласованного авторского scope не добавлялись ради числа.

Непринятые места: **Eph.1.18** — не доказан допустимый endpoint для «і» в выбранном original universe; **Lev.4.12** — не установлено полное распределение компонентов направительной конструкции для «поза». Также не устанавливается новый NULL для перемещённого «то» в Phil.3.15. Неопределённость не заменена удобным кандидатом. Зарегистрированные deferrals не переоткрывались; общий issue inventory не изменялся. Это решения частичной проверки batch, без переоформления старого gold или его отсрочек.

Для Eph.1.18 выполнен один ограниченный source-check: [первичный TAGNT](https://github.com/STEPBible/STEPBible-Data/blob/master/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Act-Rev%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt) различает edition membership καί. Exact rows, blob/file digests и CC BY 4.0 attribution сохранены в independent evidence. Это не доказывает source omission и не расширяет frozen endpoint universe.

Время измерено по UTC wall clock, без пересчёта в человеко-часы. Начало задачи: **2026-10-18 05:42:16 UTC**. Подготовка до первого авторского source review: **11 мин 48 с**. Авторский initial source-разбор с записью обоснований: **05:54:04–05:59:17, 5 мин 13 с**. Независимый initial review: **05:54:17–06:00:43.963, около 6 мин 27 с**, параллельно автору. Initial QC: **06:01:09–06:03:25, 2 мин 16 с**. Финальная проверка и amendments имеют собственные timestamps в receipts. Эти интервалы частично перекрываются; складывать их как человеческое время нельзя. Подготовка включала физическую SHA/bytes проверку 31 ГБ прежних материалов. Время упаковки до inventory: 2026-10-18T06:08:59Z. Полный elapsed после inventory записан отдельно в HANDOFF.

От первого авторского source review до финального independent PASS: **05:54:04–06:07:17, 13 мин 13 с wall clock**. Final independent QC: **06:05:14–06:07:17, 2 мин 3 с**. От начала задачи до этого PASS — **25 мин 1 с**, затем упаковка/inventory/read-only receipts.

Проверки: исходные 7 671 entries preservation PASS; stage3 offline и stage4–7 `--check` PASS. Raw validator независимо от rationale проверяет cardinality/unique IDs, точные scalar/byte spans, eligibility, отсутствие deferred promotions, несовместимых/shared endpoints и NULL, а также физические SHA gold/mask. Финальный reviewer пересчитывает payload и metrics. Flutter runtime/UI, зависимости и парные RU/EN архитектурные документы не менялись; Dart/Flutter suites к этой data-only партии не запускались. Использован checklist `.github/change_checklist.md` с этой областью применимости.

Таблица показывает целые группы; полные IDs, source commits/digests, morphology, source locators и exact offsets находятся в JSONL и зафиксированных source packets. Номер Strong рядом с группой относится к её исходным компонентам, а не к каждой возможной паре слов.

| № | Стих | Отклонённое полное предложение | Принятые полные группы | Статус |
|---:|---|---|---|---|
| 1 | Hos.2.5 | [וְ] → [та + напо́ї] (one_to_many) | [וְ] → [та] (one_to_one) | Partial repair; остальной стих вне scope |
| 2 | Zech.10.3 | [אֶת + וֹ] → [Свої́м] (many_to_one) | [וֹ] → [Свої́м] (one_to_one) | Partial repair; остальной стих вне scope |
| 3 | 1Chr.6.33 | [בֶּן + בֶּן] → [сина] (many_to_one) | [בֶּן] → [сина] (one_to_one)<br>[בֶּן] → [син] (one_to_one) | Partial repair; остальной стих вне scope |
| 4 | Joel.2.6 | [מִ + ו] → [Наро́ди] (many_to_one) | [עַמִּ֑ים] → [Наро́ди] (one_to_one)<br>[מִ + פָּנָ֖י] → [перед] (many_to_one)<br>[ו] → [ним] (one_to_one) | Partial repair; остальной стих вне scope |
| 5 | Phil.3.15 | [καὶ] → [то] (one_to_one) | [καὶ] → [й] (one_to_one) | Partial repair; остальной стих вне scope; «то» unproved, без NULL |
| 6 | 2John.1.6 | [ἵνα + ἵνα] → [щоб + щоб] (many_to_many) | [ἵνα] → [щоб] (one_to_one)<br>[ἵνα] → [щоб] (one_to_one) | Partial repair; остальной стих вне scope |
| 7 | Eph.1.18 | [αὐτοῦ,] → [і] (one_to_one) | Нет принятой замены | Replacement not proven |
| 8 | Jas.2.12 | [διὰ] → [як + такі] (one_to_many) | [διὰ + νόμου] → [зако́ном] (many_to_one) | Partial repair; остальной стих вне scope |
| 9 | Josh.18.4 | [וְ] → [та] (one_to_one) | [וְ] → [та + й] (one_to_many) | Partial repair; остальной стих вне scope |
| 10 | Joel.2.25 | [שִׁלַּמְתִּ֤י] → [надолу́жу] (one_to_one) | [שִׁלַּמְתִּ֤י] → [надолу́жу + Я] (one_to_many) | Partial repair; остальной стих вне scope |
| 11 | Lev.4.12 | [ח֨וּץ] → [поза] (one_to_one) | Нет принятой замены | Replacement not proven |
| 12 | Josh.21.2 | [תֶת] → [дати] (one_to_one) | [לָֽ + תֶת] → [дати] (many_to_one) | Partial repair; остальной стих вне scope |
| 13 | Rom.11.1 | [γένοιτο.] → [Зо́всім] (one_to_one) | [μὴ + γένοιτο.] → [Зо́всім + ні] (many_to_many) | Partial repair; остальной стих вне scope |
| 14 | Rom.6.4 | [δόξης] → [славою] (one_to_one) | [διὰ + δόξης] → [славою] (many_to_one) | Partial repair; остальной стих вне scope |
| 15 | Phil.1.10 | [τὰ] → [те] (one_to_one) | [τὰ + διαφέροντα,] → [те + що + краще] (many_to_many) | Partial repair; остальной стих вне scope |
| 16 | 3John.1.9 | [ἐκκλησίᾳ·] → [Церкви] (one_to_one) | [ἐκκλησίᾳ·] → [до + Церкви] (one_to_many) | Partial repair; остальной стих вне scope |
| 17 | Jer.39.9 | [ו] → [і] (one_to_one) | [עָלָ֔י] → [до] (one_to_one)<br>[ו] → [нього] (one_to_one) | Partial repair; остальной стих вне scope |
| 18 | Josh.10.11 | [בְּ] → [повмирали] (one_to_one) | [מֵ֙תוּ֙] → [повмирали] (one_to_one)<br>[בְּ] → [від] (one_to_one)<br>[אַבְנֵ֣י] → [каміння] (one_to_one) | Partial repair; остальной стих вне scope |
| 19 | 2Sam.13.37 | [עַל] → [ґешурського] (one_to_one) | [עַל] → [за] (one_to_one)<br>[גְּשׁ֑וּר] → [ґешурського] (one_to_one) | Partial repair; остальной стих вне scope |
| 20 | Zeph.2.13 | [וְ] → [та + й] (one_to_many) | [וְ] → [і] (one_to_one)<br>[וִֽ] → [та + й] (one_to_many) | Partial repair; остальной стих вне scope |
| 21 | Exod.37.10 | [וֹ] → [лікоть] (one_to_one) | [וֹ] → [його] (one_to_one)<br>[אַמָּ֣ה] → [лікоть] (one_to_one) | Partial repair; остальной стих вне scope |
| 22 | Phil.2.30 | [με] → [для] (one_to_one) | [με] → [мене] (one_to_one)<br>[πρός] → [для] (one_to_one) | Partial repair; остальной стих вне scope |
| 23 | 1Tim.4.5 | [γὰρ] → [освячується] (one_to_one) | [γὰρ] → [бо] (one_to_one)<br>[ἁγιάζεται] → [воно + освячується] (one_to_many) | Partial repair; остальной стих вне scope |
| 24 | 2Thess.1.5 | [δικαίας] → [доказ] (one_to_one) | [δικαίας] → [праведного] (one_to_one) | Partial repair; остальной стих вне scope |
| 25 | 1Tim.1.16 | [διὰ] → [для] (one_to_one) | [διὰ + τοῦτο] → [тому́] (many_to_one)<br>[πρὸς] → [для] (one_to_one)<br>[ὑποτύπωσιν] → [при́кладу] (one_to_one) | Partial repair; остальной стих вне scope |

Технические доказательства и журналы доступны через completion manifest; результаты независимой проверки не являются старым gold, переименованным в новую разметку. После всех artifact writes inventory обновляет отдельный writer; затем допускаются только read-only проверки и receipts в HANDOFF.

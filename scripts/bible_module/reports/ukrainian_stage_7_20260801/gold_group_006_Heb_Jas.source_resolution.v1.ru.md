# Group006 OH1988: source-resolution Heb/Jas v1

Дата: 2026-10-10. Фактический автор: `/root/heb_jas_research`; роль — изолированный исследователь источников, не corrector и не независимый QC reviewer.

Проведён один bounded cycle для каждого из 16 уникальных стихов, включая supplement scopes, переданные root после независимого inspection. Точные чтения, lemma/morphology и украинские spans установлены; все остающиеся недоказанные atom/source-choice scopes рекомендованы как `deferred_strong_unassigned`. Доказанные подвыводы перечислены отдельно. Новых accepted Strong, gold corrections и error verdicts здесь нет. Никакой исторический QC не переписан и не присвоен автору этого отчёта.

Проверены 42 SHA/byte locks source/chain/policy **до full JSONL reads**. Root stage3 offline/4/5/6/7 и inventory PASS приняты как предпосылка, не выданы за наши проверки. Независимый native audit этого исследователя: 16 target texts, все scalar/UTF-8 byte spans, exact selected-original template equality и 298 raw TAGNT line digests PASS. 11 OH1988 DjVu pages визуально просмотрены. Синтезированный текст и comments не изменены.

## Контракт и границы

Политика: [group006 v6](gold_group_006_completion_policy.v6.manifest.json). Initial mutable HANDOFF, registry, report, validation log и inventory lock references разрешаются через exact root baseline snapshots и [preserved inputs](gold_group_006_preserved_inputs.v1.manifest.json). Все frozen sources и chains lock напрямую. Чтение answer-free templates — inspection; поля reviewer_answers содержат только пустой scaffold `{groups: [], target_nulls: []}`. Исторические verdicts из residual — исходный scope, не доказательство собственного вывода.

Это versioned source registry/research artifact и technical conclusion snapshot; **не второй рабочий issue registry**. Общий OH1988 registry не редактировался. Root может перенести exact unresolved cases в единственный общий Markdown registry. Registered deferrals удовлетворяют completion; второе исследование для этого не требуется.

## Источники и ограниченные попытки

Primary official [SBLGNT text/apparatus](https://github.com/Faithlife/SBLGNT/tree/c4d241a9c1c479a55b989ba35a4976c1d0b8052c) закреплены commit `c4d241a9c1c479a55b989ba35a4976c1d0b8052c`. Они сравнивают printed editions WH/Treg/NA28/RP; список edition alternatives не является полным manuscript apparatus и не устанавливает личный source экземпляр Огиенко. Текст/apparatus: CC BY 4.0 по exact upstream LICENSE; attribution retained. Это read-only evidence, новая runtime dependency не принята.

Locked TAGNT STEP commit `b9dcc831a98e0fd6f3c7e122be9ff68377c310c0` и locked UGNT v0.34 используются как original/control sources. UGNT zip SHA independently verified. Extended IDs `G15435`, `G33463`, `G08495` сохранены целиком; они не classic `G1543`, `G3346`, `G0849`. TAGNT `G6092`, `G6060`, `G6094` не заменены nearby/classic/traditional candidate.

[William Varner, JGRChJ 10 (2014), 132–137](https://www.jgrchj.net/volume10/JGRChJ10-6_Varner.pdf) — доступная первичная научная аргументация Jas3.3. Её вывод о preferred reading не является доказательством выбора Огиенко. Открытые UBS TIPs публикуют licensed excerpts исходных scholarly handbooks: Ellingworth/Nida 1983 для Heb; Loh/Hatton 1997 для Jas. В отчёте использованы краткие парафразы, не полное воспроизведение комментариев.

Попытки без достаточного usable text: Logeion University of Chicago exact lemma pages (JS/empty tool extraction); CORE scholarly PDF `212874103.pdf` (403); STEP web verse view (tool inaccessible); UBS Heb6.19 web page (challenge). Повторные обходы этих ограничений не выполнялись. Download SBL zip через web parser был unsupported content-type; один обычный HTTPS retrieval official download успешен. Classic Strong scanned/OCR PDF получен как контроль, но noisy Greek/digit OCR отвергнут как authoritative numeric proof; никаких Strong assignments из него нет. Paid expert access не предполагался.

[Машинные cases](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/source_resolution.cases.v1.jsonl), [conclusion map](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/source_resolution.conclusion_map.v1.json), [native proof](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/native_evidence_validation.v1.json), [scan inspection](../../work/ukrainian_stage_7_20260801/session_group6_20261010_heb_jas_research_01/scan_visual_inspection.v1.json).

## Exact cases

### Heb.3.14

OH1988 DjVu page 1475 / печатная 1471; text SHA `ef9fd9c0aa0f45ba17eb9bc66b8e38817cf44b7e005d5fae4ecd34c243b679c1`.

ὑποστάσεως — родительный от ὑπόστασις/G5287, а не название жизни. Закреплённые TAGNT и UGNT согласуют lemma и чтение. UBS Ellingworth/Nida для этого стиха выбирает начальное доверие/уверенность и отвергает перенос философского real being из Heb 1:3. Скан действительно печатает «почате життя». Смысл целой фразы можно обсуждать как интерпретационный пересказ начального христианского существования, но это не доказывает самостоятельный lexical atom ὑπόστασις→«життя».

Недостающая proof: Нет авторского комментария Огиенко или доступного лексикографического доказательства, которое в этом употреблении устанавливает ζωή/життя как точное значение ὑπόστασις. Нет достаточного доказательства выбранного atom без пересказа всей конструкции.

Stable scope:

- `o011` `tagnt:f9d627139fd8571790d3ae05e6e7228e87ea9f7376d3d2bac2083584a7cbcc03:c01`; `gold7:original:04e411412b5eb4e0bd53230f2d8f9207`; ὑποστάσεως / ὑπόστασις / G5287.
- `t009` `uk7:N5M:009:50:55`; `gold7:target:6c43cf9533d286cefcea5500f31cc5eb`; «життя»; scalar [50,55) / UTF-8 bytes [91,101).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Greek lemma G5287 и фактический украинский текст установлены; значение слова життя не превращено в доказанный Strong supplier.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Heb314](https://tips.translation.bible/story/translation-commentary-on-hebrews-314/).

### Heb.6.17

OH1988 DjVu page 1477 / печатная 1473; text SHA `09171301fe9399968cc917b975f3e1adda2619a90125ec94209fdda9c0c48cdb`.

ἐμεσίτευσεν — μεσιτεύω/G3315, аорист активного залога 3 ед.; ὅρκῳ — ὅρκος/G3727, дательный ед. Огиенко печатает «учинив те при помочі клятви». Глагол означает вмешательство/поручительство/подтверждение, а oath-dative выражает средство; UBS допускает широкий пересказ добавления клятвы к обещанию. Для «клятви» supplier ὅρκος доказан; «при помочі» естественно выражает means-dative. Однако «учинив те» отсылает к предыдущей цели показать неизменность; оно не называет mediation/ratification явно. Отдельный verb atom нельзя объявить установленным только из наличия действия в этом стихе.

Недостающая proof: Не доказано точное распределение mediation/confirmation между «учинив те» и целой oath-phrase. Существующий многословный edge следует проверять как композицию; нельзя переносить G3315 на общий глагол действия по позиционному совпадению.

Stable scope:

- `o017` `tagnt:29bc4c5485566b35741454baccee849c0ba59d920238b3d1367234c88d86600b:c01`; `gold7:original:6e43a54bbfdca74c4d276e1b9b01c4d9`; ἐμεσίτευσεν / μεσιτεύω / G3315.
- `o018` `tagnt:a525084e9db8a098dcf5be2ef1b187d4b51a638eb0dbca3ab6675c937196cb4f:c01`; `gold7:original:3903bf3d92f72983bd168ab11c9f20c4`; ὅρκῳ, / ὅρκος / G3727.
- `t012` `uk7:N72:012:87:93`; `gold7:target:c22a08eb33e41a79a25109d6ac4550c3`; «учинив»; scalar [87,93) / UTF-8 bytes [161,173).
- `t013` `uk7:N72:013:94:96`; `gold7:target:35c9ce7679c3607d17103a44f1b201a6`; «те»; scalar [94,96) / UTF-8 bytes [174,178).
- `t014` `uk7:N72:014:97:100`; `gold7:target:77ef3c376f422e3282b52c4bba0d456d`; «при»; scalar [97,100) / UTF-8 bytes [179,185).
- `t015` `uk7:N72:015:101:107`; `gold7:target:a94988068ea21381ce9535203d0c4a5f`; «помочі»; scalar [101,107) / UTF-8 bytes [186,198).
- `t016` `uk7:N72:016:108:114`; `gold7:target:c3b3f917ad6f958b175f428f2d4329db`; «клятви»; scalar [108,114) / UTF-8 bytes [199,211).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: ὅρκος/G3727→клятви — доказанная лексическая часть; решение о whole edge o018 не заменяет независимую QC.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Heb617](https://tips.translation.bible/story/translation-commentary-on-hebrews-617/).

### Heb.6.19

OH1988 DjVu page 1477 / печатная 1473; text SHA `0eb3d0145fe91ad7c3c7e9bfcb008df3070fa81399af5bad67548b480fb648bd`.

Во всех указанных TAGNT изданиях и в UGNT стоит ἔχομεν, ἔχω/G2192, настоящее 1 мн. Скан подтверждает «що вони для душі як котвиця», включая именно «вони». Украинское местоимение имеет 3-е лицо мн., тогда как греческий глагол содержит субъект мы и предикат иметь. В OH изменена конструкция всего относительного предложения; preceding «надію» единственного числа само по себе не доказывает референт plural «вони». Ни одно из доступных чтений не даёт греческого 3-мн. местоимения на месте ἔχομεν.

Недостающая proof: Не установлено точное авторское разложение пересказа и референт вони; нет доказательства source ἔχομεν→вони. Нельзя из этого объявить lexical omission ἔχομεν либо target addition вони доказанными classifiers.

Stable scope:

- `o004` `tagnt:108ff356a12f1815a9ada4f683d41e42eff9529754740da1afb3137d9dafa55f:c01`; `gold7:original:1e9774c9609b5a128db3ef90fbe29f70`; ἔχομεν / ἔχω / G2192.
- `t002` `uk7:N74:002:3:7`; `gold7:target:558b8e5917fa04084581d34ebe3729ae`; «вони»; scalar [3,7) / UTF-8 bytes [5,13).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Форма вони — печатная, не ошибка машинной транскрипции. Greek lemma/morphology также установлены.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

### Heb.7.21

OH1988 DjVu page 1478 / печатная 1474; text SHA `942793cf7d66f0aec53697ae53d01e65bfadb6081e0bd7c964fc3c3d51c40c74`.

Скан подтверждает окончание «за чином Мелхиседековим». TAGNT universe содержит κατὰ τὴν τάξιν Μελχισεδέκ с отдельными stable original IDs, только TR+Byz; SBLGNT apparatus независимо фиксирует длинное окончание RP против краткого WH/Treg/NA28. Украинские слова диагностируют именно наличие extended phrase. В immutable выбранной gold-сетке этих четырёх original components нет. Доказательство длинной фразы не разрешает исследователю дописывать их в selected layer либо назначать Strong на существующих NULL rows.

Недостающая proof: Для accepted reciprocal links нет допустимого выбранного original node и независимо проверенной scoped source-layer correction/overlay. Историческая конкретная редакция Nestle не нужна для регистрации deferral и не запрашивается как условие completion.

Stable scope:

- `t027` `uk7:N7Q:027:151:153`; `gold7:target:30acfbbda203fc0d7da71fc00c0f6be5`; «за»; scalar [151,153) / UTF-8 bytes [273,277).
- `t028` `uk7:N7Q:028:154:159`; `gold7:target:9968315ea2d249f197209b70ab5a6aff`; «чином»; scalar [154,159) / UTF-8 bytes [278,288).
- `t029` `uk7:N7Q:029:160:175`; `gold7:target:b696bdf72478075a20e37b21b58036b9`; «Мелхиседе́ковим»; scalar [160,175) / UTF-8 bytes [289,319).

Universe-only components отсутствуют в selected grid:

- `tagnt:ce0daeeb568dd2a7bce72861dcf6e0cf5180a09a1bcb96c4550e9bbf7d900ab3:c01` κατὰ / κατά / G2596; raw line SHA `774d1b0bbcb38dd8b8732a2fc6cdb362e505908931f4a30630ad103ad305d8e8`.
- `tagnt:7c375e688c34e8335f78bc9468d9217d8f0664b13bb0133f00278d1fbb0d8c20:c01` τὴν / ὁ / G3588; raw line SHA `1cef01ae7b29413827fddca61695dfea15357fd330003f647763f7f5b5537600`.
- `tagnt:bdc798a5bab41e07d4e58f23278bd1b2582a8f88c5e9cad3e8b074bfc3682fec:c01` τάξιν / τάξις / G5010; raw line SHA `bd43b496f673c2a2f0636f9eac86a0eb43b602408c473d02a6556094a93e50ab`.
- `tagnt:7a89163b6b79c902c9b94e74a3de823d6ee4b083e9de0e9fef49cc3f3670211f:c01` Μελχισεδέκ· / Μελχισεδέκ / G3198; raw line SHA `3fa12149680883cfd2ecf65495e5d2825f172b12423b7502169413d377d44c06`.

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Традиционное длинное окончание доказано на уровне source-resolution фразы. G2596/G3588/G5010/G3198 остаются evidence-only; новых accepted Strong нет.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Heb_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Heb.xml).

### Heb.10.6

OH1988 DjVu page 1480 / печатная 1476; text SHA `f92d9e1a839fe0141ecf04248be2674b42feb1b929d27ffa1e545e9529326db0`.

εὐδόκησας — εὐδοκέω/G2106, аорист 2 ед.; source/control согласуются. Скан печатает «Ти не жадав». UBS Ellingworth/Nida объясняет глагол как отсутствие удовольствия/одобрения жертв, а не как простое желание. Общая семантическая область willingness/preference допускает пересказ, поэтому это не доказанная ошибка. Но точное desire atom и здесь не установлен: в том же печатном блоке 10:5 стоит «не схотів», а 10:8 различает «не жадав і Собі не вподобав». Эти контексты видимы в скане, но не используются для Strong transfer.

Недостающая proof: Не хватает контекстно точного доказательства εὐδοκέω→жадати в данном употреблении; общая willingness в словаре и тематический параллелизм не доказывают точный atom.

Stable scope:

- `o006` `tagnt:81d1c3837345b17785120da305dd93f24a5f50a4674f928523c9ee0cd3b9efa7:c01`; `gold7:original:66aac92c6c9a6796728eec0a9d67aacd`; εὐδόκησας· / εὐδοκέω / G2106.
- `t007` `uk7:N98:007:38:43`; `gold7:target:f82cac8405403a3f9808c829e66a3fdb`; «жадав»; scalar [38,43) / UTF-8 bytes [70,80).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Greek supplier G2106 установлен как source lemma; literal pleasure и фактическое жадав сохраняются раздельно.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Heb106](https://tips.translation.bible/story/translation-commentary-on-hebrews-106/).

### Heb.10.12

OH1988 DjVu page 1481 / печатная 1477; text SHA `3733080d9f9c3a04a447570fe10dc007d1a4c40ecb7e9d85d87b4e4ce9955129`.

Первое место: οὗτος/G3778 в критических изданиях и αὐτός/G0846 в TR/Byz/RP; «Він» семантически совместим с обоими. Второе: μίαν — винительный жен. ед. от εἷς/G1520; оно согласовано с θυσίαν, а не является наречием once. OH печатает «приніс жертву один раз». Контраст с повторными жертвами и комментарий UBS подтверждают одну жертву, но сами по себе не устанавливают exact composition adjective→event-count adverbial phrase «один раз». Это допустимый смысловой пересказ, а не автоматически доказанная ошибка.

Недостающая proof: Не выбран конкурирующий pronoun lemma по Він. Для o003→один+раз не доказано точное разложение номинального количества жертвы в число действий; нужна phrase-level independent QC, а не новый поисковый цикл.

Stable scope:

- `o001` `tagnt:45b1a79af3594be1f5df21ac05337febd57063e9545984afcf86c4578038edb8:c01`; `gold7:original:1d630d238c0b57c3dee0478689b04a79`; οὗτος / οὗτος / G3778.
- `t002` `uk7:N9E:002:2:5`; `gold7:target:c7165b57a3d8e64db40857012b30a59f`; «Він»; scalar [2,5) / UTF-8 bytes [3,9).
- `o003` `tagnt:01bc2649c66ab36ae5da13c42b9db6f73a1625c87053c2358d882793e46d799c:c01`; `gold7:original:c21f49670011074c5b2506a90d14bc54`; μίαν / εἷς / G1520.
- `t008` `uk7:N9E:008:35:39`; `gold7:target:f3914b72ae2d252938a9a92a3d501aee`; «один»; scalar [35,39) / UTF-8 bytes [63,71).
- `t009` `uk7:N9E:009:40:43`; `gold7:target:8d4e408b0641ae72ef0be2595f4d8eb9`; «раз»; scalar [40,43) / UTF-8 bytes [72,78).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: μίαν классическое G1520, θυσίαν G2378; числовая one-часть установлена, event-count scope остаётся не доказан.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Heb_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Heb.xml); [ubs_Heb1012](https://tips.translation.bible/story/translation-commentary-on-hebrews-1012/).

### Heb.11.15

OH1988 DjVu page 1482 / печатная 1478; text SHA `e38a837f2ac0ab5d165d321d77d36ad79351476b60cbc2c388fdd7d532385dbd`.

TAGNT выделяет ἐξέβησαν, ἐκβαίνω, extended G6092; классических Strong в source record нет. Альтернатива TR/Byz — ἐξῆλθον, ἐξέρχομαι/G1831. SBLGNT apparatus независимо фиксирует это различие. UGNT имеет ту же lemma ἐκβαίνω, но другую extended систему G15435, что не является classic G1543. OH «вийшли» передаёт общий выход и не различает две lemma. Номер G1831 нельзя брать из traditional alternative для critical node.

Недостающая proof: Нет доказательства точного греческого source lexeme по вийшли и нет authoritative classic identity для ἐκβαίνω. G6092/G15435 — разные extended идентификаторы для контроля, не разрешение назначить classic Strong.

Stable scope:

- `o008` `tagnt:139b4646d316fb0188657b95d6e228f4677f6d1cdeaac00738f1eb3c41369f63:c01`; `gold7:original:cf4fc09a2b9c4d21f00eeeb33c8f2733`; ἐξέβησαν, / ἐκβαίνω / G6092.
- `t008` `uk7:NAK:008:31:37`; `gold7:target:f57f0bd74af3c07b1468ad2d2d1a9077`; «вийшли»; scalar [31,37) / UTF-8 bytes [53,65).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Критическое lemma ἐκβαίνω подтверждено двумя оригинальными datasets; classic supplier не установлен.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Heb_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Heb.xml).

### Heb.13.18

OH1988 DjVu page 1485 / печатная 1481; text SHA `f8e1dc1e17b11e6ec143af812833fb63e3e1806b8cc8e187138032607ac4b09e`.

πειθόμεθα — πείθω/G3982, настоящее middle/passive 1 мн.; traditional πεποίθαμεν сохраняет ту же lemma/G3982, меняя форму на perfect confidence. Скан подтверждает «надіємося, що ми маємо добре сумління». UBS Ellingworth/Nida объясняет исходное утверждение как уверенность в чистой совести. Украинское надіятися может обозначать надежду или доверие; существование общей области trust не доказывает exact persuasion/certainty atom, но и не устанавливает ошибку связи.

Недостающая proof: Не доказано, что в этом украинском употреблении надіємося выражает именно inward certainty/source πείθω, а не ослабляющий hope-пересказ. Требуется independent atom QC; никакой G1679 из общей темы hope не предлагается.

Stable scope:

- `o004` `tagnt:764394ddd00aab7e35580a4e20d087aa8f4547472306d8d18e89f0ae7f3b34b0:c01`; `gold7:original:c561d23b25a92de042f0cef02dfb81d1`; πειθόμεθα / πείθω / G3982.
- `t005` `uk7:NCK:005:20:30`; `gold7:target:cfc0299a9d21fa59ab9aeef08fe3a195`; «наді́ємося»; scalar [20,30) / UTF-8 bytes [35,55).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Textual alternative не создаёт competing Strong: G3982 общий; unresolved остаётся semantic atom.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Heb1318](https://tips.translation.bible/story/translation-commentary-on-hebrews-1318/); [sbl_Heb_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Heb.xml).

### Jas.1.23

OH1988 DjVu page 1487 / печатная 1483; text SHA `6c05aafb0b4216fa47938d30ec839f675998bfacc3cc4e15e323e3b744c281ab`.

γενέσεως — γένεσις/G1078; целая конструкция τὸ πρόσωπον τῆς γενέσεως αὐτοῦ обозначает естественное/врождённое лицо либо лицо своего существования. UBS Loh/Hatton разбирает оба толкования и допускает естественный пересказ как собственное лицо. OH печатает «риси обличчя свого». Смысл whole idiom подтверждён, но риси самостоятельно — features, не birth/nature. Нельзя выводить geneseos→риси только из того, что слово осталось после привязки πρόσωπον к обличчя.

Недостающая proof: Нет достаточной atom decomposition для γένεσις→риси. Возможна whole-phrase functional translation, но буквальный residual matching не доказывает выбранный supplier.

Stable scope:

- `o017` `tagnt:4a3f87eee74853a760229c7aeb08623d5015d327106139ac50cd75c311fad67a:c01`; `gold7:original:a2ce846e1dec27a76705ec7336893c37`; γενέσεως / γένεσις / G1078.
- `t012` `uk7:NDE:012:65:69`; `gold7:target:83a5cd187e71f083c700d46862c314ae`; «риси»; scalar [65,69) / UTF-8 bytes [116,124).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: G1078 и фактический целый idiom установлены; πρόσωπον→обличчя не переоткрывается этим отчётом.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Jas123](https://tips.translation.bible/story/translation-commentary-on-james-123/).

### Jas.2.3

OH1988 DjVu page 1487 / печатная 1483; text SHA `523f7ae9eb93cd0ac4756dc95d1c13f557467401a1a9fc6d900284b65e25a264`.

Начало имеет альтернативные critical ἐπιβλέψητε δέ и Treg/RP/TR/Byz καὶ ἐπιβλέψητε; это подтверждено официальным SBL apparatus, TAGNT memberships и UGNT critical sequence. Выбранная composite grid содержит оба particles, но OH начальное і не доказывает наличие обоих в одном underlying source. Поэтому linked καί не является доказательством omission δέ; accepted opener o001/t001 следует проверить как dependency. Отдельная конструкция: φοροῦντα, φορέω/G5409, present participle «носящего одежду». Украинское «того, хто в шаті блискучій» передаёт wearing аналитическим predicate «хто в [шаті]». Relative хто передаёт грамматическую часть participle, а предикативное в при существующем шаті выражает wearing. Source supplier для phrase group «хто в» доказан на уровне lexical/grammatical composition; isolated group only хто не покрывает predicate. Это рекомендация отдельному corrector, не выполненная correction.

Недостающая proof: Для particles не доказан exact source choice καί/δέ по і, и omission classifier остаётся недоказан. Для wearing необходимо отдельное corrector inspection/correction и независимая reciprocal QC o006/t006/t007; автор этого research не меняет gold.

Stable scope:

- `o003` `tagnt:8b717b9975da7e87df0dfff3b22b54bb0471e4341500c9914367c2f1f1aefb37:c01`; `gold7:original:d2bfb030ea1cbd72c46276a09a8c0514`; δὲ / δέ / G1161.
- `o001` `tagnt:6f763a6ff6402affeb34ded91df7f1eb2af178d4d65407e3649242171620e696:c01`; `gold7:original:3a80985a69309acd737322eea1aa9e51`; καὶ / καί / G2532.
- `t001` `uk7:NDL:001:0:1`; `gold7:target:22acebcbde9e15125086cffb8d8202d1`; «і»; scalar [0,1) / UTF-8 bytes [0,2).
- `o006` `tagnt:c71c9ead4c800a5645f2fbeb41978117509ea60a2fa950a8aa38dd1edd747294:c01`; `gold7:original:f0d4987b2065ad9dbcbebea23e8e1f64`; φοροῦντα / φορέω / G5409.
- `t006` `uk7:NDL:006:25:28`; `gold7:target:967516879a69a070c7a0212ff3b0e2ee`; «хто»; scalar [25,28) / UTF-8 bytes [44,50).
- `t007` `uk7:NDL:007:29:30`; `gold7:target:44757b1226341afedea9702b6b36dddd`; «в»; scalar [29,30) / UTF-8 bytes [51,53).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: G5409 и wearing→хто в [шаті] group подтверждены; recommended_corrector_inspection_only. Source καί/δέ choice остаётся deferred.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Jas_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Jas.xml); [ubs_Jas23](https://tips.translation.bible/story/translation-commentary-on-james-23/).

### Jas.2.8

OH1988 DjVu page 1487 / печатная 1483; text SHA `a265be758a8c0fc9c2b508531d63283b4525c76ddf4d62bf00bc90527ee67292`.

μέντοι/G3305 — усилительно-подтвердительная либо противительная частица, входящая в protasis εἰ μέντοι. UBS Loh/Hatton отмечает оба значения и предпочитает подтверждение. OH имеет условный коррелят «Коли … то ви робите добре». То вводит apodosis и может следовать самой конструкции коли; оно не выражает однозначно действительно/однако. Перестановка discourse marker возможна, но не доказана как exact atom μέντοι→то.

Недостающая proof: Нет достаточного доказательства, что то сохраняет именно affirmative/adversative contribution μέντοι, а не является структурным коррелятом условного предложения. Оба возможных значения частицы проверены; residual matching не принят.

Stable scope:

- `o002` `tagnt:8d002ffb94716afd057806afcf4851aec2fd24fb0a657165996953508a23dd03:c01`; `gold7:original:35d399a2d27ee80e9152b2ad91b67f46`; μέντοι / μέντοι / G3305.
- `t014` `uk7:NDQ:014:92:94`; `gold7:target:69ba7342ff9a1596d99cbe627dbb2cba`; «то»; scalar [92,94) / UTF-8 bytes [169,173).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Greek G3305 и Ukrainian protasis/apodosis structure установлены; Strong или definitive omission/addition не назначены.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Jas28](https://tips.translation.bible/story/translation-commentary-on-james-28/).

### Jas.3.3

OH1988 DjVu page 1488 / печатная 1484; text SHA `f8e83721911f5ed978d5ac118339b667199ce2c11dc93366ae83ea28bff63334`.

Source critical Εἰ δέ/G1487+G1161 конкурирует с TR ἰδού/G2400 и Byz/RP ἴδε/G2396. SBL apparatus и научная статья William Varner, JGRChJ 10 (2014), 132–137 подтверждают реальную проблему. Varner защищает ἴδε по manuscript/context evidence и обсуждает itacism ΕΙΔΕ/ΙΔΕ; UBS Handbook предпочитает conditional reading с C uncertainty. Ни один источник не доказывает, какую exact форму переводил Огиенко. OH «От і» подходит к orienter; оно не выбирает ἰδού против ἴδε. Purpose чтобы/щоб также совместимо с critical εἰς и traditional πρὸς перед infinitive.

Недостающая proof: Нет verse-specific translator source proof для Εἰ δέ/ἰδού/ἴδε и εἰς/πρός. Semantic compatibility и литературное предпочтение Varner не являются доказательством OH source identity.

Stable scope:

- `o001` `tagnt:cf12bb55dfd99c97774bfb906df31bfec7ddcf9b88685933503a95ee7129da24:c01`; `gold7:original:3ab1add6c34ae38e73c9bdddd33d9b97`; Εἰ / εἰ / G1487G.
- `o002` `tagnt:7b7696362fbef06a705110b9e867e24ea85da6cb9189cc35c46c4c8a3b1b5da3:c01`; `gold7:original:118085a66ff86cafb081edc3bf33ef6c`; δὲ / δέ / G1161.
- `o011` `tagnt:5b8585414c6b6989338b50a107718e42bffbbbba976665a4a43bf1a3f5738065:c01`; `gold7:original:f18aefa20d8dad2c6099c9e5bbbd17d0`; εἰς / εἰς / G1519.
- `t001` `uk7:NEB:001:0:2`; `gold7:target:ea8d9525da29d65d6f8beeb030191494`; «От»; scalar [0,2) / UTF-8 bytes [0,4).
- `t002` `uk7:NEB:002:3:4`; `gold7:target:56911ffe59b930cc65c2ec44aef72743`; «і»; scalar [3,4) / UTF-8 bytes [5,7).
- `t008` `uk7:NEB:008:40:43`; `gold7:target:80ff0742bc9aee48eef74e6f697dd032`; «щоб»; scalar [40,43) / UTF-8 bytes [72,78).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Научное несогласие и apparatus учтены; ни committee preference, ни majority manuscript count не голосуют за OH Strong.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Jas_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Jas.xml); [Varner2014](https://www.jgrchj.net/volume10/JGRChJ10-6_Varner.pdf); [ubs_Jas33](https://tips.translation.bible/story/translation-commentary-on-james-33/).

### Jas.3.5

OH1988 DjVu page 1488 / печатная 1484; text SHA `aeb651562d20529dc16efc62f69d89c8934ff3c21b5dec96c8b2029e138bdc3f`.

ἡλίκον/G2245 допускает в этом контрасте малый размер огня; UBS Loh/Hatton прямо объясняет контекстное small значение. Это показывает, почему OH маленький не доказывает traditional ὀλίγον/G3641 и не доказывает exclusive critical lemma. Второй scope: source μεγάλα/G3173 + αὐχεῖ, αὐχέω/extended G6094; traditional μεγαλαυχεῖ — lemma μεγαλαυχέω/G3166. SBL apparatus фиксирует two-word versus compound; TAGNT удерживает compound alternative в raw textual data. UGNT αὐχέω/G08495 — иной extended ID; он не classic G0849. OH «хвалиться вельми» совместимо с обоими composite readings; classic G3166 нельзя назначать source αὐχέω по общему boasting смыслу.

Недостающая proof: Не установлены exclusive ἡλίκος/ὀλίγος и exact two-atom versus compound supplier для хвалиться вельми. У αὐχέω нет доказанной classic identity в locked TAGNT record; supporting extended UGNT не устраняет это.

Stable scope:

- `o012` `tagnt:95f8ce82fef9afdd97dff2d8bcdac0f64165ff3666988d802b053f14762a5c3d:c01`; `gold7:original:ceeb4d4091232bbc06568afd7635f0cf`; ἡλίκον / ἡλίκος / G2245.
- `t011` `uk7:NED:011:59:68`; `gold7:target:962e721f0ca025db23f4b88a5d9b6923`; «маленький»; scalar [59,68) / UTF-8 bytes [105,123).
- `o009` `tagnt:679d9870b9df05f748e296caaf5ce0db3196cf1bdccdc2003e2ffaaa8a9c631c:c01`; `gold7:original:8d56f7ea362568d5ef321122af9ed85e`; μεγάλα / μέγας / G3173.
- `o010` `tagnt:94aaf60ca0ca3a2600f1e718a61c8cec9710190e014667eaff785a985a28a67f:c01`; `gold7:original:20b62301cf685638bb6305889fafef52`; αὐχεῖ. / αὐχέω / G6094.
- `t008` `uk7:NED:008:35:45`; `gold7:target:20e6c2fbd2444b2baf6786944335bfa5`; «хва́литься»; scalar [35,45) / UTF-8 bytes [61,81).
- `t009` `uk7:NED:009:46:53`; `gold7:target:c2530e3944783afafebd712f0a1f7854`; «ве́льми»; scalar [46,53) / UTF-8 bytes [82,96).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Маленький не является доказанной mistranslation ἡλίκος. Nonclassic αὐχέω не превращён в definite selected-layer error.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Jas_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Jas.xml); [ubs_Jas35](https://tips.translation.bible/story/translation-commentary-on-james-35/).

### Jas.3.7

OH1988 DjVu page 1488 / печатная 1484; text SHA `66bdd0c31d451e6b77136214c7f2e39e32da3598872917a433e2f64a15f6894b`.

δεδάμασται — perfect middle/passive indicative 3 ед. от δαμάζω/G1150; locked UGNT также имеет perfect passive. OH печатает «приборкана буде». Лексический supplier δαμάζω→приборкана доказан; различие первой present формы δαμάζεται и второй resultative perfect соответствует двум самостоятельным Ukrainian predicates. UBS Loh/Hatton разбирает perfect как завершённое действие с сохраняющимся значением и допускает риторическую пару present/perfect. Буде фактически даёт future auxiliary, чего Greek perfect не содержит. Аналитический finite passive может быть whole-phrase rendering с tense shift, но это не доказывает отдельный future source contribution.

Недостающая proof: Нет доказательства exact auxiliary/tense contribution для буде. Нужно независимое решение, является ли whole o014→t013+t014 допустимым grammatical transformation edge. Lexical G1150→приборкана доказан; новый G1510 для буде не предлагается.

Stable scope:

- `o014` `tagnt:342261a9e23cac47c74c4f4db5cea498e320ed9e6f389ef2784f8bfaf643e28f:c01`; `gold7:original:6c9175dddea887e8119dfb57aed780bd`; δεδάμασται / δαμάζω / G1150.
- `t013` `uk7:NEF:013:79:90`; `gold7:target:a8315fe20e04739286f089c328b0a623`; «прибо́ркана»; scalar [79,90) / UTF-8 bytes [144,166).
- `t014` `uk7:NEF:014:91:95`; `gold7:target:b3a637a1399f9255ea87f5b82c722d72`; «буде»; scalar [91,95) / UTF-8 bytes [167,175).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: δaμάζω/G1150 lexical part resolved; whole tense composition pending independent QC, не новая lexical ошибка.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [ubs_Jas37](https://tips.translation.bible/story/translation-commentary-on-james-37/).

### Jas.4.9

OH1988 DjVu page 1489 / печатная 1485; text SHA `c632dfd50b166eca5108df8cf80d8b1104ec4f63c95b7a8d5aa2ce449af5c1fe`.

μετατραπήτω — μετατρέπω, extended G6060, aorist passive imperative 3 ед.; alternative μεταστραφήτω — μεταστρέφω/G3344, Tyn/Treg/TR/Byz. SBL apparatus подтверждает WH/NA28 versus Treg/RP. UGNT source-control имеет μετατρέπω/G33463, иной extended ID, не classic G3346. OH «Хай обернеться» верно выражает third-person imperative/passive turning, но оба Greek verbs имеют общий change/turn смысл. Хай — аналитическое выражение imperative, не доказанная addition. Нельзя назначать G3344 критическому μετατρέπω либо G3346 путём обрезания UGNT suffix.

Недостающая proof: Не выбран exact μετατρέπω/μεταστρέφω по Ukrainian phrase и нет authoritative classic supplier для μετατρέπω. Imperative composition доказана на уровне функции, но competing lexical identity остаётся deferred.

Stable scope:

- `o011` `tagnt:27306e84c7b4e3934bbdd7c0aa83f989dab449dfb60467c6ddce053d89ba421d:c01`; `gold7:original:a282348f5b54e0cf8a79f4a7152e5393`; μετατραπήτω / μετατρέπω / G6060.
- `t005` `uk7:NEZ:005:29:32`; `gold7:target:5a3b155ea048720c3e48d35e2433e3fb`; «Хай»; scalar [29,32) / UTF-8 bytes [52,58).
- `t006` `uk7:NEZ:006:33:43`; `gold7:target:296146da9a260f9f6b21a1fd869b83ed`; «обернеться»; scalar [33,43) / UTF-8 bytes [59,79).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Грамматическая imperative функция Хай не является target addition proof; classic assignment отсутствует.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Jas_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Jas.xml); [ubs_Jas49](https://tips.translation.bible/story/translation-commentary-on-james-49/).

### Jas.5.12

OH1988 DjVu page 1490 / печатная 1486; text SHA `828fb8541ec854aae4140adeda0c5c15a60c0f5efb218b5d80c4db7b03c9bebb`.

Критическое ὑπὸ κρίσιν/G5259+G2920 противопоставлено traditional εἰς ὑπόκρισιν/G1519+G5272. TAGNT и официальное SBL apparatus подтверждают различие; UGNT имеет критическое ὑπό + κρίσις. OH печатает «в осуд», а не лицемерство. Поэтому noun judgment-часть поддержана, но украинское в не является однозначной обратной транскрипцией Greek ὑπό. Точность noun не доказывает source preposition в mixed edition translation. Номер G1519 из alternative нельзя присоединять к selected ὑπό; критическое G5259 не разрешается по одному общему sense.

Недостающая proof: Не хватает exact source-preposition evidence ὑπό/εἰς по в. Semantic κρίσις→осуд не устраняет preposition ambiguity. Definitive source omission/addition classifier не установлен.

Stable scope:

- `o030` `tagnt:d52ebe87afaa5c3aec032db5679eabf8cc58d4d860a4c7e0e2d6eb97a1876365:c01`; `gold7:original:2796ff1902ccda120d852a2152bef626`; ὑπὸ / ὑπό / G5259H.
- `t029` `uk7:NFJ:029:148:149`; `gold7:target:8e8503c75113a471eca318052bc4e0e2`; «в»; scalar [148,149) / UTF-8 bytes [263,265).

Рекомендация: `deferred_strong_unassigned` для недоказанного scope; доказанные части: Noun κρίσις/G2920→осуд не переоткрывается как ошибка; deferred preposition сохраняется.

Один цикл завершён. Future follow-up — optional по запросу владельца либо при новой verse-specific proof; completion не требует повторного поиска.

Sources: [sbl_Jas_app](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/xml/Jas.xml); [ubs_Jas512](https://tips.translation.bible/story/translation-commentary-on-james-512/).

## Supersedes, ограничения и валидация

Это первый author research report данной группы Heb/Jas. Он дополняет inherited issue evidence и уточняет source/source-choice и semantic atom причины; historical QC verdicts, rationales, authors и sealed answers не superseded. Early scoped extraction v1 superseded final native/scoped v2: ранний UGNT v1 содержал только verse markers, поэтому не использован как verse text proof. В manifest указан final evidence roster; ранние inspection files остаются технической историей, не рабочими registries.

Jas2.3 analytic wearing group — рекомендация отдельному corrector для concrete scope o006/t006/t007. Исследователь не пишет correction или reciprocal answers. Jas3.7 lexical δαμάζω→приборкана доказано независимо от оставшейся uncertainty auxiliary tense. Heb7.21 extended phrase доказана отдельно от возможности gold source-node overlay. Source resolution не подменяет completion/acceptance или независимое QC.

Checklist: scope source research only; runtime, DB, dependencies, release, locales и approved RU/EN architecture pairs не менялись, поэтому Flutter format/analyze/test и paired-doc sync к этим evidence artifacts не применяются. Выполнены JSON/JSONL parse, exact scopes/IDs, SHA/byte locks, raw-line digests, scalar/byte spans, UTF-8 и local output links. Parent root отвечает за интеграционную navigation ссылку отчёта и общий финальный audit. Другие группы, stage8, global finalize, production Strong markup, DB, commit и push не выполнялись.

# Группа 007: source research 1Pet / 2Pet

**Роль:** `/root/petrine_research`, isolated research author. Не corrector и не independent QC. Дата: 2026-10-10.
**v1 отклонена независимым QC до чтения cases из-за stale physical locks.** Настоящая v2 полностью заменяет её для авторского source research; диагноз и сохранённые v1 digests находятся в invalid_v1_diagnosis.v2.json. V1 не объявляется PASS. Это новая закрытая публикация уже выполненного одного bounded cycle, не новый research cycle.


Один bounded cycle для 25 verse scopes: 12 исторических локусов и 13 новых reviewer scopes, плюс supplemental вопросы внутри прежних локусов. 38 physical SHA256/bytes checks PASS до full work reads; supplemental TBESG lock PASS до dictionary content inspection. Скан OH1988: листья 1491–1498 визуально проверены, target scalar/UTF-8 byte spans проверены. Original universe, selected layer, raw TAGNT и exact locked pass/adjudication/QC chain inspected только в 1Pet/2Pet scope.

**Предложение:** 77 current scoped keys: 72 deferred; 3 current αὐτῷ→тим+самим keys имеют достаточный lexical occurrence proof; 2 source article NULL keys имеют classifier-only correction proposal. Исторические 27 uncertain keys не переименованы и все остаются deferred в авторском предложении. Independent reviewer принимает либо отклоняет proposal; я не изменял QC verdicts или alignment.

Историческое название греческой редакции не является gate. Доказанные alternative lexical bridges сохранены явно: 1Pet.4.1 за нас; 1Pet.5.11 слава та; 2Pet.3.10 вночі; embedded replacement candidates 1Pet.2.21 нас, 2Pet.1.21 святі и 2Pet.2.13 при́ймуть. Но current frozen selected-layer NULL/addition/group rows требуют исполнимой controlled correction, если alternative source будет принят. Unsupported competing-lemma links остаются unassigned. Source IDs для embedded-only alternative не придуманы.

2Pet.2.18 имеет доказанный lexical bridge ὀλίγως→ледве, но classic Strong не доказан: standalone augmented G6067 нельзя заменить на G3641 по знакомой adjective family. 2Pet.2.11 имеет доказанное target segmentation discrepancy несуть + до в скане versus frozen несутьдо; neither frozen tokenization nor historical QC изменены.

Cases JSONL — sealed technical research evidence после связывания manifest, не отдельный editable Strong issue registry. Единственный реестр остаётся `oh88_strongs_issue_inventory.ru.md`; root обновляет его после независимого принятия. Повторный research cycle для зарегистрированных deferrals не требуется.

## Отдельному corrector

Две точные classifier-only proposals находятся в `correction_proposals.v2.json`: 2Pet.3.5 original:gold7:original:0ce8877a263911e6513957b281d6d136 и 2Pet.3.7 original:gold7:original:08bb4bdd1f7207c308f5737ca4efbe8b. Меняется только `null_reason` с `translation_omission` на `grammatical_function_not_overt`; relation=original_omitted и пустые target IDs сохраняются, новые Strong links не создаются. Исследователь не исполнял правки.

Для alternative-source loci machine cases содержат exact native IDs, embedded candidates, target spans и complete current scopes. Corrector может исследовать controlled overlay; если complete source/lemma/Strong/span proof отсутствует, принять exact deferrals достаточно. Frozen files и old QC не редактировать.

| Locus | Historical keys | Supplemental keys | Author outcome |
|---|---:|---:|---|
| 1Pet.1.16 | 3 | 0 | deferred |
| 1Pet.1.7 | 2 | 2 | deferred |
| 1Pet.2.21 | 2 | 5 | deferred |
| 1Pet.3.6 | 0 | 2 | deferred |
| 1Pet.3.7 | 0 | 2 | deferred |
| 1Pet.4.1 | 2 | 0 | deferred |
| 1Pet.4.19 | 0 | 2 | deferred |
| 1Pet.5.10 | 0 | 11 | deferred |
| 1Pet.5.11 | 0 | 2 | deferred |
| 1Pet.5.12 | 0 | 2 | deferred |
| 1Pet.5.13 | 0 | 2 | deferred |
| 1Pet.5.9 | 1 | 2 | deferred |
| 2Pet.1.17 | 1 | 0 | deferred |
| 2Pet.1.21 | 3 | 0 | deferred |
| 2Pet.1.4 | 1 | 0 | deferred |
| 2Pet.1.9 | 0 | 2 | deferred |
| 2Pet.2.11 | 0 | 5 | deferred |
| 2Pet.2.12 | 3 | 0 | deferred |
| 2Pet.2.13 | 2 | 3 | deferred |
| 2Pet.2.18 | 0 | 2 | deferred |
| 2Pet.2.6 | 3 | 0 | deferred |
| 2Pet.3.10 | 4 | 0 | deferred |
| 2Pet.3.18 | 0 | 1 | deferred |
| 2Pet.3.5 | 0 | 1 | 1 classifier proposal |
| 2Pet.3.7 | 0 | 4 | 3 existing lexical keys proved; 1 classifier proposal |

## 1Pet.1.16

**Exact OH1988:** бо написано: „Будьте святі, — Я бо святий“!

Printed «бо написано: Будьте святі, — Я бо святий». First ὅτι после γέγραπται конкурирует с отсутствием; это не последнее причинное ὅτι. Future ἔσεσθε/G1510 допускает command force, традиционные γένεσθε/γίνεσθε/G1096 тоже дают Будьте. Императив перевода не является уникальным индикатором G1096, и пунктуация не доказывает omission первого ὅτι.

**Проверенные альтернативы:** Проверены first-ὅτι presence/absence, future-as-command и two imperative forms; latter causal token сохранён как отдельный контроль.

**Missing proof:** Нет occurrence-specific source/lemma disambiguation G1510 versus G1096 или доказательства NULL-classifier для first ὅτι.

**Scan:** leaf 1491 / printed 1487

**Current target spans:** Будьте `uk7:NG7:003:14:20` scalars[14,20), bytes[26,38)

**Current scoped keys:** `original:gold7:original:4cdd37468e378f001e7c57ee4b101b74`, `original:gold7:original:6deeb7cfcf26e71f448e4697a5c28e15`, `target:gold7:target:6a277de6330ccc237c9605711a1394b7`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=1&verse=16).

## 1Pet.1.7

**Exact OH1988:** щоб досвідчення вашої віри було дорогоцінніше за золото, яке гине, хоч і огнем випробо́вується, на похвалу́, і честь, і славу при з'я́вленні Ісуса Христа.

Скан имеет «було дорогоцінніше» и «на похвалу». Compound πολυτιμότερον/G4186 и split πολὺ τιμιώτερον/G4183+G5093 подтверждены аппаратами. Target сравнительная степень не различает эти lexical identities. Shared εὑρεθῇ/G2147 — единственный finite purpose predicate; NET occurrence note рассматривает его result function. Однако было может обслуживать recast comparative predication, а εὑρεθῇ — result predicate «на похвалу». Полная фразовая связь вероятна, распределение G2147 на один t005 не доказано.

**Проверенные альтернативы:** Проверены single compound, two-word comparative, recast εὑρεθῇ→було и predicate-group alternative; другой стих или словарная возможность не использованы как proof occurrence.

**Missing proof:** Нет доказательства выбора G4186 versus G4183+G5093 и точного atom allocation G2147→було; оба supplemental ключа и comparative pair требуют deferral.

**Scan:** leaf 1491 / printed 1487

**Current target spans:** було `uk7:NFY:005:27:31` scalars[27,31), bytes[50,58); дорогоцінніше `uk7:NFY:006:32:45` scalars[32,45), bytes[59,85)

**Current scoped keys:** `original:gold7:original:4c56da2fd9bb2c0f556cad8584fb56a0`, `original:gold7:original:f16d7ec79bb4a628b1d503519f877a58`, `target:gold7:target:13b9649c4f1819ae6143f644e4d9063a`, `target:gold7:target:4237128b045f3e9e39ca4fbd5c6b771d`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=1&verse=7).

## 1Pet.2.21

**Exact OH1988:** Бо на це ви покликані. Бо й Христос постраждав за нас, і залиши́в нам при́клада, щоб пішли ми сліда́ми Його.

Printed за нас, нам, пішли ми; selected ὑμῶν/ὑμῖν и second-person ἐπακολουθήσητε. Apparatus подтверждает alternative ἡμῶν именно после ὑπέρ. Narrow source bridge ἡμῶν→нас установлен, но original alternative embedded in TAGNT имеет conventional candidate G2257 и не является выбранным token. Для нам и ми в exact raw control нет самостоятельного traditional first-person token: их нельзя переносить из единственного доказанного ἡμῶν. Current ὑμῖν→нам и ἐπακολουθήσητε→пішли+ми не доказываются одним общим смыслом.

**Проверенные альтернативы:** Проверены each pronoun occurrence, second-person verb morphology, inclusive-person translation shift и hypothetical first-person exemplar; latter не утверждается.

**Missing proof:** Для current critical pronoun edge требуется controlled alternative overlay; для дополнительных first-person spans не доказано, source variant это или translation shift и как ограничить reciprocal verb group.

**Scan:** leaf 1492 / printed 1488

**Current target spans:** нас `uk7:NH1:011:50:53` scalars[50,53), bytes[89,95); нам `uk7:NH1:014:66:69` scalars[66,69), bytes[117,123); пішли `uk7:NH1:017:85:90` scalars[85,90), bytes[151,161); ми `uk7:NH1:018:91:93` scalars[91,93), bytes[162,166)

**Current scoped keys:** `original:gold7:original:679f24865afa97c6d0d841fca424dda5`, `original:gold7:original:e41a220e2f95c5a0bbfef266367dc451`, `original:gold7:original:e79da2dcaa5ae00a8825f51698b841aa`, `target:gold7:target:2f1082f881667027a32dd476e6c1724f`, `target:gold7:target:890c8b00ed5b0fd540002ad317694292`, `target:gold7:target:8efa7bd94b6e2ef26412ea751372f8be`, `target:gold7:target:fbd1eb4f47945c069f23e7745e977979`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 1Pet.3.6

**Exact OH1988:** Так Сара корилась Авраамові, і паном його називала. А ви — її діти, коли добро робите та не лякаєтесь жа́дного стра́ху.

Printed «А ви — її діти». Shared ἐγενήθητε/G1096 имеет lexical became и 2P morphology; pronoun ви выражает subject morphology, dash — zero copula. NET exact occurrence подтверждает become predicate. Current one-to-one только на ви сохраняет лицо, но не демонстрирует, что именно lexical G1096 допустимо на местоимении без предикативного group. Не присоединять діти автоматически: оно уже реализует τέκνα/G5043.

**Проверенные альтернативы:** Проверены morphology-only pronoun mapping, zero-copula predicate and many-to-many predicate scope; lexical subject suffix не выдан за самостоятельный become lexeme.

**Missing proof:** Нет fully proved reciprocal atom/group contract для G1096 в zero-copula clause; обе current linked rows deferred.

**Scan:** leaf 1493 / printed 1489

**Current target spans:** ви `uk7:NHB:010:54:56` scalars[54,56), bytes[97,101)

**Current scoped keys:** `original:gold7:original:09fb0e6bdf943a76c160920a5d3c604c`, `target:gold7:target:d91ce43e8307fc6f86b007df8045f3e7`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=3&verse=6).

## 1Pet.3.7

**Exact OH1988:** Чоловіки, — так само живіть ра́зом із дружи́нами за розумом, як зо слабішою жіночою посудиною, і виявляйте їм честь, бо й вони є співспадкоє́миці благода́ті життя, щоб не спинялися ваші моли́тви.

Printed спинялися; selected ἐγκόπτεσθαι/G1465 hindered versus embedded TR ἐκκόπτεσθαι/G1581 cut off. Exact raw occurrence confirms two lemmas, despite selected metadata primary_shared_reading. Both can be paraphrased as stopped prayers; target is not a unique source-lemma selector. SBL apparatus omission of a TR-only variant does not invalidate recorded TAGNT alternative.

**Проверенные альтернативы:** Проверены hinder/block versus cut-off senses, prayer complement and exact raw TR alternative; source-family metadata не выдано за absence of lexical competition.

**Missing proof:** Нет unique occurrence lemma/Strong proof G1465 versus G1581; current linked pair deferred.

**Scan:** leaf 1493 / printed 1489

**Current target spans:** спинялися `uk7:NHC:028:171:180` scalars[171,180), bytes[310,328)

**Current scoped keys:** `original:gold7:original:0a9e7e904d30e0cce882ff1878d4fc0c`, `target:gold7:target:32e5d985c05aa55f9ae28280d0c98de3`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 1Pet.4.1

**Exact OH1988:** Отож, коли тілом Христос постраждав за нас, то озбройтеся й ви тією самою думкою, бо хто тілом постраждав, той перестав грішити,

Printed «Христос постраждав за нас». Native universe содержит two exact traditional-only source IDs ὑπέρ/G5228 и ἡμῶν/raw G3165 с TR+Byz witnesses; selected layer не содержит их. Occurrence-local beneficiary phrase uniquely supplies за and нас. Narrow source/lemma/raw-Strong/span bridges доказаны; это не требует historical Greek edition name. Current two source-NULL target-addition records нельзя превратить в accepted alternative links без отдельного controlled source overlay.

**Проверенные альтернативы:** Проверены selected absence, exact native alternative rows, phrase semantics и distinction raw TAGNT G3165 versus conventional inflected G2257.

**Missing proof:** Не создан и не проверен executable source-selection overlay: current keys остаются deferred до корректной authored correction и independent QC; сам historical edition name не является missing proof.

**Scan:** leaf 1494 / printed 1490

**Current target spans:** за `uk7:NHS:006:36:38` scalars[36,38), bytes[66,70); нас `uk7:NHS:007:39:42` scalars[39,42), bytes[71,77)

**Current scoped keys:** `target:gold7:target:cafcbfa4e515e3e345d0c195a379bd85`, `target:gold7:target:d35443acc593ec227a73bb827cd31711`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 1Pet.4.19

**Exact OH1988:** Тому й ті, хто з Божої волі страждає, нехай душі свої віддадуть в доброчинстві Йому, як Створителю вірному.

Printed душі свої. Selected αὐτῶν/G846 and TR ἑαυτῶν/G1438 refer to the sufferers own souls. Ukrainian reflexive possessive naturally serves both subject-coreferential readings. Coreference proves narrow referent but not which Greek possessive lemma supplies this word. Target свої cannot establish reflexive Greek source by itself.

**Проверенные альтернативы:** Проверены ordinary genitive possessive, explicit reflexive Greek form, Ukrainian subject-coreference and exact native alternative.

**Missing proof:** Нет unique G846 versus G1438 identity proof for current source/target pair.

**Scan:** leaf 1494 / printed 1490

**Current target spans:** свої `uk7:NIA:011:49:53` scalars[49,53), bytes[86,94)

**Current scoped keys:** `original:gold7:original:727b4c617d6973de4ac1d83a891f80ff`, `target:gold7:target:ea7ae3e21e619c345c3d52d17635d08d`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 1Pet.5.10

**Exact OH1988:** А Бог усякої благодаті, що покликав вас до вічної слави Своєї в Христі, нехай Сам удоскона́лить вас, хто трохи поте́рпів, хай упе́внить, зміцни́ть, уґрунтує.

Printed «в Христі», «нехай Сам удосконалить», «хай упевнить, зміцнить, уґрунтує». Ἰησοῦ source token restricted to NA27/Treg/TR/Byz; NET documents disputed expansion. Four future verbs and optative variants share respective lemmas/Strongs G2675/G4741/G4599/G2311. Narrow lexical cores transparent, but current groups include wish auxiliaries and exact future/optative choice is not uniquely recoverable. Common Strong does not prove auxiliary span allocation or source NULL for disputed Jesus.

**Проверенные альтернативы:** Проверены name inclusion/absence, each future/optative form, shared lexical meanings и placement нехай/хай; lexical verbs не смешаны с independently inferred auxiliaries.

**Missing proof:** Нет proof current first grouped auxiliary semantics and exact omission classifier for Ἰησοῦ; no source-form certainty manufactured from common lemma.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** нехай `uk7:NIK:014:72:77` scalars[72,77), bytes[129,139); удоскона́лить `uk7:NIK:016:82:95` scalars[82,95), bytes[147,173); хай `uk7:NIK:021:122:125` scalars[122,125), bytes[220,226); упе́внить `uk7:NIK:022:126:135` scalars[126,135), bytes[227,245); зміцни́ть `uk7:NIK:023:137:146` scalars[137,146), bytes[247,265); уґрунтує `uk7:NIK:024:148:156` scalars[148,156), bytes[267,283)

**Current scoped keys:** `original:gold7:original:3d7aa2e0b55cdb550703c2009b970234`, `original:gold7:original:4db837161cb26fa7d6b634c16c9acddd`, `original:gold7:original:552c4d0cc96dc06ce3b6828b6ba31422`, `original:gold7:original:b61f21b9f70913df3bed7934e27ff777`, `original:gold7:original:fd092676e1130ae727e317066f67f101`, `target:gold7:target:09ade40ffbb5ba4a1228b19a840df079`, `target:gold7:target:4803e8b22966b57888c5e6e6c570835c`, `target:gold7:target:4e3b0df0cae89201a99d7a176464be52`, `target:gold7:target:9b29cad3c7402ec4e3b82374894c7a90`, `target:gold7:target:9b61ca39131dadc91022a73833439eda`, `target:gold7:target:e5077e16cf6e21074db403ca07d55fac`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=5&verse=10).

## 1Pet.5.11

**Exact OH1988:** Йому слава та вла́да на вічні віки, амі́нь.

Printed «Йому слава та влада». Exact universe alternative δόξα/G1391 and καί/G2532 with native IDs independently account for слава and та; selected layer has neither. Both narrow traditional lexical bridges proved, without requiring identification of the translators edition. Current unlinked target records still need executable source-layer/full-grid correction before alternative Strong is accepted.

**Проверенные альтернативы:** Проверены two precise native addition occurrences and shared κράτος control; no G1391 transferred from another doxology.

**Missing proof:** Нет validated controlled overlay for two added source atoms; current target keys deferred pending distinct corrector/QC.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** слава `uk7:NIL:002:5:10` scalars[5,10), bytes[9,19); та `uk7:NIL:003:11:13` scalars[11,13), bytes[20,24)

**Current scoped keys:** `target:gold7:target:81b90f3444cdaad8ed9a704088191e7d`, `target:gold7:target:c4022fbc39e3166dda83fe88ad8a5136`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 1Pet.5.12

**Exact OH1988:** Я коротко вам написав через Силуя́на, як гада́ю — вірного брата. Закликаю та свідчу, що це Божа благода́ть правдива, що ви в ній стоїте́.

Printed «що ви в ній стоїте». Selected στῆτε is aorist imperative; traditional ἑστήκατε perfect indicative. Both G2476, target present indicative fits latter but can be a rendering recast of exhortation. SBL exact apparatus confirms forms; NET explains imperative clause. Common stand meaning is narrow proof, not full current mood/span proof.

**Проверенные альтернативы:** Проверены imperative, indicative, Ukrainian finite-person morphology and paraphrastic recast.

**Missing proof:** Нет unique proof current selected imperative→indicative verb occurrence contract; linked pair deferred without historical-name gate.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** ви `uk7:NIM:020:120:122` scalars[120,122), bytes[217,221); стоїте́ `uk7:NIM:023:129:136` scalars[129,136), bytes[232,246)

**Current scoped keys:** `original:gold7:original:69577c90082c7855269c8a3701d0c493`, `target:gold7:target:be29e95f0b0e977b8cbb121b665d68b8`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=5&verse=12).

## 1Pet.5.13

**Exact OH1988:** Вітає вас ра́зом ви́брана Церква в Вавилоні, і Ма́рко, мій син.

Printed Церква italicized. Shared feminine article ἡ substantivizes the elected subject but does not contain lexical ἐκκλησία/G1577. NET exact note recognizes woman/church interpretation. Context supports church as supplied referent, not the claim that G3588 lexically means Church. Current article-only→Церква edge not fully proved; no G1577 invented.

**Проверенные альтернативы:** Проверены feminine substantivized phrase, female individual interpretation, church ellipse and translator italic typography.

**Missing proof:** Нет exact atom accounting separating substantive grammatical article from supplied lexical church; linked pair deferred.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** Церква `uk7:NIN:005:26:32` scalars[26,32), bytes[48,60)

**Current scoped keys:** `original:gold7:original:f3082d32acee4b12966cac552864b553`, `target:gold7:target:9258252dd438b5e0c42784564f26209c`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=1Pe&chapter=5&verse=13).

## 1Pet.5.9

**Exact OH1988:** Противтесь йому́, тверді в вірі, знавши, що ті самі му́ки трапляються й вашому братству по світу.

Printed «тверді в вірі» и «по світу». First shared τῇ agrees with πίστει; current τῇ→в выводится из dative construction, не из lexical article meaning. Instrumental/respect phrase доказан целиком, но isolated article-only allocation preposition в не уникален. Later τῷ before κόσμῳ присутствует в WH/Treg/NA27 и отсутствует в NA28/RP; target по світу этого не различает. Не путать две статьи и два разных scopes.

**Проверенные альтернативы:** Проверены shared faith article/dative phrase, later world article presence/absence и grammar-not-overt alternative; sequential articles не взаимозаменяются.

**Missing proof:** Нет isolated τῇ→в proof и exact source-presence proof later τῷ; historical NULL key и supplemental linked pair deferred.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** в `uk7:NIJ:004:25:26` scalars[25,26), bytes[46,48)

**Current scoped keys:** `original:gold7:original:3d9b5f8537850a3337d535045783c980`, `original:gold7:original:93e9ce5bc02302051ba7cd9402efd266`, `target:gold7:target:b0dd22353332615d4c3fe341fd46baa7`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Pet.txt).

## 2Pet.1.17

**Exact OH1988:** Бо Він честь та славу прийняв від Бога Отця, як до Нього прийшов від величної слави голос такий: „Це Син Мій Улю́блений, що Його Я вподо́бав!“

Printed «Це Син Мій Улюблений» with one Мій. Selected text contains second μου after ἀγαπητός; apparatus contrasts full two-possessive versus one-possessive order. The one overt Мій may realize first possessive or merge both; it does not prove exact second-token omission or source absence. Its Strong cannot be transferred from adjacent μου.

**Проверенные альтернативы:** Проверены both possessive occurrences, order variant, one-word merger and omission alternatives.

**Missing proof:** Нет exact occurrence allocation/NULL classifier for second μου; no duplication of target Мій for coverage.

**Scan:** leaf 1496 / printed 1492

**Current target spans:** original-only NULL scope; exact full verse retained in machine evidence

**Current scoped keys:** `original:gold7:original:c512d4238819a48c95c88c9db2a1fa23`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.1.21

**Exact OH1988:** Бо проро́цтва ніко́ли не було з волі лю́дської, а звіщали його святі Божі му́жі, прова́джені Духом Святим.

Printed святі Божі; selected ἀπὸ θεοῦ. Apparatus confirms replacement ἀπό/G575 by ἅγιοι/G40 while θεοῦ/G2316 stays shared. Narrow holy→святі and God-genitive→Божі facts clear. Current Божі link includes G575: adjectival Божі does not demonstrate separate origin-from relation. Embedded alternative holy lacks an independent accepted source atom; old group cannot be released merely by dropping G575 in prose.

**Проверенные альтернативы:** Проверены critical from-God group, traditional holy-God phrase, stable shared θεοῦ occurrence and replacement versus addition.

**Missing proof:** Нет validated three-key reciprocal correction separating shared God from replaced from/holy source atom.

**Scan:** leaf 1496 / printed 1492

**Current target spans:** святі `uk7:NJ9:012:63:68` scalars[63,68), bytes[114,124); Божі `uk7:NJ9:013:69:73` scalars[69,73), bytes[125,133)

**Current scoped keys:** `original:gold7:original:d04ef744952c658301b17054332a152a`, `target:gold7:target:1147027597baa4cfca17fdf8a9e41ccb`, `target:gold7:target:276afd9d81ff588336912adc6de4772b`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.1.4

**Exact OH1988:** Через них даро́вані нам цінні та великі обі́тниці, щоб ними ви стали уча́сниками Божої Істо́ти, утікаючи від пожадливого світового тління.

Printed «пожадливого світового тління». Selected article τῷ before κόσμῳ versus RP absence confirmed by exact apparatus. Adjectival Ukrainian recast removes standalone in-the-world words; it cannot attest this article. Semantic similarity of world adjective does not establish translator-source presence.

**Проверенные альтернативы:** Проверены article presence/absence and adjectival genitive recast.

**Missing proof:** Нет evidence for exact τῷ occurrence presence and its current NULL accounting; article remains unassigned.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** original-only NULL scope; exact full verse retained in machine evidence

**Current scoped keys:** `original:gold7:original:4599e0c4fb3b4dca98a6ec60e6b053b8`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.1.9

**Exact OH1988:** А хто цього не має, той сліпий, короткозо́рий, він забув про очи́щення з своїх давніх гріхів.

Printed давніх гріхів; selected ἁμαρτιῶν/G266 and SBL/Treg ἁμαρτημάτων/G265 both sins nouns with different lemmas. Exact apparatus documents noun replacement. Source gender and nominal derivation are not preserved in target гріхів. Shared sin sense is a narrow finding, not an occurrence-specific Strong selector.

**Проверенные альтернативы:** Проверены both Greek sin nouns, genitive plural morphology, cleansing clause and current one-to-one narrowing; no number transfer from generic sins gloss.

**Missing proof:** Нет proof selecting G266 versus G265 for exact target гріхів; current reciprocal pair deferred.

**Scan:** leaf 1495 / printed 1491

**Current target spans:** гріхів `uk7:NIX:016:86:92` scalars[86,92), bytes[154,166)

**Current scoped keys:** `original:gold7:original:80314f51e490f2e707b9ec67639dafd4`, `target:gold7:target:f93dd78b00153a74fd34cffa7cc3fc84`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.2.11

**Exact OH1988:** хоч анголи́, бувши міццю та силою більші за них, не несутьдо Господа знева́жливого суду на них.

Frozen target has несутьдо; scan leaf1496 ends несуть and leaf1497 starts до Господа, proving a separate-word segmentation discrepancy at page boundary. Selected παρὰ κυρίου uses NA27 genitive from-the-Lord; dative κυρίῳ before-the-Lord is embedded alternative, and SBL omits the phrase. Current group φέρουσιν+παρά→несутьдо with isolated κυρίου→Господа mixes fused target and source-case semantics. Lexical bring and Lord cores clear; they do not prove the complete directional/from/before allocation.

**Проверенные альтернативы:** Проверены exact two scan leaves, fused scalar/byte token, genitive/dative/phrase-absence controls and current two-source fused-token group.

**Missing proof:** Нет controlled target-segmentation/source-case correction preserving exact contracts; current closed five-key scope deferred. Frozen stage6 and inventory must not be silently rewritten.

**Scan:** leaf 1496 / printed 1492

**Current target spans:** несутьдо `uk7:NJK:011:52:60` scalars[52,60), bytes[92,108); Господа `uk7:NJK:012:61:68` scalars[61,68), bytes[109,123)

**Current scoped keys:** `original:gold7:original:38d9fd453467aa25917b1e835163cbac`, `original:gold7:original:ad3f050225f02dbb06326c09d8266ef7`, `original:gold7:original:bfb38f54a276ab30e3f16b82606408e1`, `target:gold7:target:7126b28d7dc9b0bf485d2f0de9d59a5a`, `target:gold7:target:c3db8a7d0221e5c70b5408c7f9b25f01`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.2.12

**Exact OH1988:** Вони, немов звірина́ нерозумна, зроджена природою на зло́влення та загибіль, зневажають те, чого не розуміють, і в тлінні своїм будуть знищені,

Printed «будуть знищені». Selected φθαρήσονται/G5351 and alternative καταφθαρήσονται/G2704 both future passive destruction verbs. Prefix may intensify, while target does not overtly specify utter destruction. Neither generic gloss nor Ukrainian auxiliary proves the chosen lexeme.

**Проверенные альтернативы:** Проверены simple/prefixed destruction forms, future passive splitting and apparatus phrase καὶ φθαρήσονται versus καταφθαρήσονται.

**Missing proof:** Нет source lexeme distinction G5351 versus G2704 for this exact target span.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** будуть `uk7:NJL:020:128:134` scalars[128,134), bytes[232,244); знищені `uk7:NJL:021:135:142` scalars[135,142), bytes[245,259)

**Current scoped keys:** `original:gold7:original:0ecb246201fbcfca18d2487924d3a4bb`, `target:gold7:target:01af5e2fbe3e95d646ea3d249f5e6168`, `target:gold7:target:578db72e2554b828c1825cd66a335813`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt).

## 2Pet.2.13

**Exact OH1988:** і при́ймуть запла́ту за лихі вчинки. Вони повсякденну розпусту вважають за ро́зкіш; самі бруд та неслава, вони насолоджуються своїми оманами, бенкету́ючи з вами.

Printed при́ймуть and повсякденну. Selected ἀδικούμενοι/G91 denotes suffering harm; alternative κομιούμενοι/G2865 receiving, with occurrence-specific apparatus and scholarly NET wordplay note. Receive→при́ймуть narrow alternative bridge clear, but current alternative atom is embedded rather than an accepted selected ID. Shared ἐν ἡμέρᾳ/G1722+G2250 means in daytime; Ukrainian повсякденну normally expresses daily/everyday. Neither morphology nor a general day dictionary entry uniquely proves exact combined daytime→daily allocation.

**Проверенные альтернативы:** Проверены suffering-harm versus receiving, wordplay context, daytime versus habitual daily interpretation; supplementary three keys inspected once within this same locus.

**Missing proof:** Нет controlled source replacement for current receive addition, and no uniquely supported exact ἐν ἡμέρᾳ→повсякденну temporal scope; five keys deferred.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** при́ймуть `uk7:NJM:002:2:11` scalars[2,11), bytes[3,21); повсякденну `uk7:NJM:008:42:53` scalars[42,53), bytes[76,98)

**Current scoped keys:** `original:gold7:original:0d92f6c280f4fcc79d4e2b14feb4d1cd`, `original:gold7:original:294100b301dd2eb0fb4bbabcadbd8e8f`, `original:gold7:original:a0acce2454fcbcbcd16e8b681a10e8e5`, `target:gold7:target:979013de7327ae0f367c89c279f7dd0b`, `target:gold7:target:a6aba66b476f19a5d42901215d49cded`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=2&verse=13).

## 2Pet.2.18

**Exact OH1988:** Бо, висло́влюючи марне́ базі́кання, вони зваблюють пожадливістю ті́ла й розпустою тих, хто ледве втік від тих, хто живе в розпусті.

Printed ледве; exact selected ὀλίγως means scarcely/barely, unlike alternative ὄντως truly. Source/lemma/target occurrence bridge uniquely proved. Raw G6067 has strong_status=out_of_classic_range and strong_classic=[]. Physically verified TBESG row5854 is standalone G6067, not Form-of G3641; its same-verse note reports some manuscript systems listing ὀλίγος/G3641, not an identity equality. Mounce oligos/G3641 concordance lacks the exact 2Pet2:18 ὀλίγως form; dictionary-only other occurrences are insufficient. Classic G3641 and alternative G3689 stay unassigned.

**Проверенные альтернативы:** Проверены scarcely versus truly, exact TBESG system relation and same-verse note, both Mounce oligos concordance pages and bounded exact-form search; NET2:18 unavailable. One bounded cycle complete.

**Missing proof:** Lexical bridge fully proved, but no exact conventional classic Strong bridge for standalone augmented G6067; current pair is deferred_strong_unassigned for classic alignment/export, without negating proven lexical finding.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** ледве `uk7:NJR:013:91:96` scalars[91,96), bytes[167,177)

**Current scoped keys:** `original:gold7:original:9d76ceceb38b2d5a79862e26e79fbcf6`, `target:gold7:target:b2d6397ce93326f03dbff9ea3f242858`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://github.com/STEPBible/STEPBible-Data/blob/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt#L5854), [exact primary apparatus or scholarly note](https://www.billmounce.com/greek-dictionary/oligos), [exact primary apparatus or scholarly note](https://www.billmounce.com/greek-dictionary/oligos?page=1).

## 2Pet.2.6

**Exact OH1988:** і міста́ Содо́м і Гомо́рру спопели́в, засудивши на зни́щення, і дав при́клада для майбутніх безбожників,

Printed для майбутніх безбожників. Selected adjective ἀσεβέσιν/G765 and alternative infinitive ἀσεβεῖν/G764 remain equally compatible after μέλλοντων. Exact apparatus and NET occurrence note show two syntactic interpretations of coming ungodly people/ages. Nominal Ukrainian outcome does not establish source part-of-speech or Strong.

**Проверенные альтернативы:** Проверены dative adjective, infinitive complement and genitive participle syntax in the exact verse; no lemma choice inferred from isolated безбожників.

**Missing proof:** Нет unique source lemma/Strong disambiguation for current G765 versus alternative G764 group.

**Scan:** leaf 1496 / printed 1492

**Current target spans:** для `uk7:NJF:013:78:81` scalars[78,81), bytes[142,148); безбожників `uk7:NJF:015:92:103` scalars[92,103), bytes[168,190)

**Current scoped keys:** `original:gold7:original:b770578e60d5b56f445de267b4f3d802`, `target:gold7:target:024648cfae77c3bca90ced2a5c2ef795`, `target:gold7:target:428d71e0997e88cd83c0f0260e3f4aa1`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=2&verse=6).

## 2Pet.3.10

**Exact OH1988:** День же Господній прибу́де, як злодій вночі, коли з гу́ркотом небо мине, а стихі́ї, розпе́чені, ру́нуть, а земля та діла, що на ній, погорять.

Printed вночі and погорять. Exact native alternative IDs ἐν/G1722 and νυκτί/G3571 supply night phrase; no selected counterpart. Embedded κατακαήσεται/G2618 matches burning, while frozen οὐχ εὑρεθήσεται/G3756+G2147 does not. NET treats end-of-verse as major textual problem; SBL apparatus labels NA28 negative reading emendation. Burning context cannot turn G2147 into G2618 or prove historical source omission. Narrow traditional bridges documented; current keys need controlled alternative source atoms/full-grid correction.

**Проверенные альтернативы:** Проверены night addition, exposed/found, negative not-found and burned-up alternatives with exact verse evidence; no conjecture promoted.

**Missing proof:** Нет executed controlled source overlay for night and embedded burn replacement or validated dispositions of both current negative/find source IDs.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** вночі `uk7:NK5:007:38:43` scalars[38,43), bytes[69,79); погорять `uk7:NK5:024:133:141` scalars[133,141), bytes[235,251)

**Current scoped keys:** `original:gold7:original:295e96ca91c203a6082b024a95c60eb6`, `original:gold7:original:8d38ea9c6d42b604140e2edfcb31683d`, `target:gold7:target:6316883d0af834bb9852d1ed020ccd16`, `target:gold7:target:7f41ff5186cc0396bca853bdb9d8c684`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=3&verse=10).

## 2Pet.3.18

**Exact OH1988:** але щоб зростали в благода́ті й пізна́нні Господа нашого й Спасителя Ісуса Христа. Йому слава і тепер, і дня вічного! Амі́нь.

Printed «і тепер, і дня вічного». Shared εἰς ἡμέραν αἰῶνος gives temporal on/until/into-day relation; NET exact note allows on versus until. Ukrainian temporal genitive дня carries time without overt preposition. Therefore current translation_omission classification cannot be inferred merely from missing standalone to/on. Group temporal paraphrase is clear, but exact allocation of G1519 to дня versus zero grammar is not proved.

**Проверенные альтернативы:** Проверены on/until interpretations, Ukrainian temporal genitive, implicit preposition and grouped time expression; adjacent Amen not reopened as separate scope.

**Missing proof:** Нет fully proved atom/group or NULL-classifier contract for εἰς in genitive time phrase; one source key deferred.

**Scan:** leaf 1498 / printed 1494

**Current target spans:** original-only NULL scope; exact full verse retained in machine evidence

**Current scoped keys:** `original:gold7:original:ffc631859727d5bd86d8e93ac7033f6c`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=3&verse=18).

## 2Pet.3.5

**Exact OH1988:** Бо сховане від тих, хто хоче цього, що небо було напоча́тку, а земля із води та водою скла́дена словом Божим,

Printed «словом Божим». Shared τῷ τοῦ θεοῦ λόγῳ has instrumental dative noun phrase. Article τῷ agrees with λόγῳ, no separate Ukrainian article lexeme is present. Instrumental relation remains in словом, so treating the article as a lexical translation omission overstates the evidence. A classifier-only grammatical_function_not_overt proposal preserves original NULL and all noun/God links; it assigns no Strong to словом from article.

**Проверенные альтернативы:** Проверены article agreement, shared reading across witnesses, overt instrumental noun and lexical omission versus unexpressed grammatical article distinction.

**Missing proof:** Для proposed classifier-only correction philological missing proof отсутствует; нужен distinct corrector и independent QC. Direct article→словом allocation is not proposed.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** original-only NULL scope; exact full verse retained in machine evidence

**Current scoped keys:** `original:gold7:original:0ce8877a263911e6513957b281d6d136`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=3&verse=5).

## 2Pet.3.7

**Exact OH1988:** А теперішні небо й земля заховані тим самим словом, і зберігаються для огню на день суду й загибелі безбожних людей.

Printed «тим самим словом». Selected τῷ αὐτῷ λόγῳ has dative same-word construction. Article agrees grammatically; NULL lexical translation_omission is proposed to become grammatical_function_not_overt only. Adjectival αὐτῷ/G846 exactly supplies тим самим; whole closed current one-to-many group has unique same meaning, case agreement and source ID. Alternative αὐτοῦ means his and is semantically distinguished by target самим. This proves the existing three reciprocal keys without identifying a historical edition.

**Проверенные альтернативы:** Проверены article+same construction, alternative possessive αὐτοῦ, independent same-word target phrase and both reciprocal target spans.

**Missing proof:** Для existing αὐτῷ group philological missing proof отсутствует; это author proposal for independent acceptance. Article classifier-only change requires distinct corrector/QC.

**Scan:** leaf 1497 / printed 1493

**Current target spans:** тим `uk7:NK2:007:34:37` scalars[34,37), bytes[62,68); самим `uk7:NK2:008:38:43` scalars[38,43), bytes[69,79)

**Current scoped keys:** `original:gold7:original:08bb4bdd1f7207c308f5737ca4efbe8b`, `original:gold7:original:42f7b633483424f1585df271f539210f`, `target:gold7:target:6ea77422c36ce1993ab3c306b93f8af3`, `target:gold7:target:7729a8a6426ca144b80d0622085788b7`

**Evidence:** [exact primary apparatus or scholarly note](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Pet.txt), [exact primary apparatus or scholarly note](https://classic.net.bible.org/verse.php?book=2Pe&chapter=3&verse=7).

## Role attestation and validation

Автор лично просмотрел exact сканы и occurrence controls; reviewed artifacts прочитаны как inspection. Shared registry, source registry, frozen inputs, prior sealed ledger, runtime, DB, stage8, other book workflows, global finalize, commit/push не изменены. No independent QC role claimed. `.github/change_checklist.md` применён: runtime/test/localization/dependency/RU-EN architecture gates N/A для research evidence only; SHA/bytes, JSON schema, stable IDs, reciprocal closure и spans проверяются author validation. Навигацию из root HANDOFF обновляет root.

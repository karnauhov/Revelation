# Группа 005: исследование 1Tim и 2Tim — предложения автора

**Роль:** `/root/tim_research`; researcher, не corrector и не independent QC. Дата: 2026-10-10.

Один bounded cycle завершён для каждого из 10 исторических и 6 новых questioned loci. До полного чтения проверены 24 exact chain locks и 10 shared-source locks; отдельный UGNT zip lock и официальный TBESG lock также совпали. Изменений frozen/sealed inputs, registry, runtime, DB, commit/push нет. Исходные QC verdicts и все current payloads сохранены как история. Словарная семантика другого стиха нигде не выдаётся за occurrence proof.

**Предложение до каких-либо corrections:** 37 scoped labels = 12 proven existing proposals + 25 deferred current labels. Исторические 23 labels: 3 release / 20 defer; новые 14 labels: 9 release / 5 defer. Три отдельные correction proposals охватывают 9 rows, включая два уже accepted соседних labels в 1Tim1.13. Они не применены и не включены в released count.

Current exclusions остаются `deferred_strong_unassigned`, без недоказанных Strong/NULL/addition classifiers и вне accepted alignment/training/scoring/export. Зарегистрированная отсрочка достаточна для завершения; второй research cycle не требуется. Root/corrector может отдельно adjudicate предложенные corrections и затем distinct reviewer проверить их.

Машинное доказательство: `scripts/bible_module/work/ukrainian_stage_7_20260801/session_group5_20261010_tim_research_01/source_resolution.cases.v1.jsonl`; each row содержит exact source/target IDs, scalar/byte spans, current selected payloads, source URLs/files, missing proof, released/deferred keys и exact correction scope. `conclusions.v1.json` — immutable техническая by-ref projection, не editable issue registry.

| Locus | Existing release | Current defer | Proposal |
|---|---:|---:|---|
| 1Tim.5.16 | 0 | 2 | registered deferral |
| 1Tim.5.21 | 0 | 2 | registered deferral |
| 1Tim.6.3 | 0 | 3 | separate correction |
| 1Tim.6.10 | 0 | 2 | separate correction |
| 1Tim.6.21 | 0 | 3 | registered deferral |
| 2Tim.1.5 | 3 | 0 | retain current mapping |
| 2Tim.2.16 | 0 | 2 | registered deferral |
| 2Tim.3.8 | 0 | 2 | registered deferral |
| 2Tim.4.14 | 0 | 3 | registered deferral |
| 2Tim.4.22 | 0 | 1 | registered deferral |
| 1Tim.1.13 | 0 | 2 | separate correction |
| 1Tim.1.16 | 2 | 0 | retain current mapping |
| 1Tim.2.3 | 0 | 1 | registered deferral |
| 1Tim.6.11 | 0 | 2 | registered deferral |
| 2Tim.2.14 | 4 | 0 | retain current mapping |
| 2Tim.3.15 | 3 | 0 | retain current mapping |

## 1Tim.5.16

**Exact OH1988:** А коли має вдів який вірний, нехай їх утримує, а Церква нехай не обтяжується, щоб могла вона втримувати вдів правдивих.

В скане печатается «який вірний», masculine generic believer. Selected πιστὴ — feminine πιστός/G4103, но TAGNT universe и официальный SBL apparatus сохраняют отдельное TR/RP πιστὸς ἢ перед πιστὴ. Это два возможных same-lemma occurrences, а не только вариант окончания одного слова. Уникальный selected feminine ID не доказан для единственного украинского вірний. NET same-verse textual note подтверждает длинное man-or-woman reading; Mounce подтверждает feminine selected occurrence. Одинаковый G4103 не устраняет конкуренцию occurrence identity.

**Scan:** DjVu leaf 1465 / печатная стр. 1461.

**Exact target spans:** вірний `uk7:MZ8:006:21:27` scalars[21,27), bytes[37,49).

**Original IDs:** πιστὴ `tagnt:eb175462291236bd7f46aba82ec1381432bcef6b8420059b71acf6e5a5dc7394:c01` lemma πιστός source raw ['G4103'] classic ['G4103'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Не установлено, передаёт ли единственный generic masculine target selected πιστὴ или включает отдельное traditional πιστὸς. Нет controlled same-occurrence decomposition между двумя исходными believer occurrences и одним target.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:e1e967c21eaa5a00dd616b20387dec54`, `target:gold7:target:99c3389bfc4bcb98211970c41c57fa45`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/pistos), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=5&verse=16).

## 1Tim.5.21

**Exact OH1988:** Заклинаю тебе перед Богом й Ісусом Христом та ви́браними а́нголами, щоб ти заховав це без лицемі́рства, нічого не ро́блячи з упере́дженням.

Selected προκρίματος/πρόκριμα/G4299 — pre-judgment, preference/partiality в admonition about impartial discipline. OH точно имеет «без лицемі́рства», а следующая clause «з упере́дженням» соответствует отдельному πρόσκλισιν. Mounce и NET отображают именно 1Tim5.21 и различают обе Greek nouns. Эти occurrence proofs не дают достаточного семантического моста от hypocrisy к pre-judgment. Нельзя перенести G4299 на более похожее следующее упередження, уже принадлежащее другому occurrence. Нельзя признать исходное original_omitted/translation_addition механизмом только из lexical mismatch.

**Scan:** DjVu leaf 1465 / печатная стр. 1461.

**Exact target spans:** лицемі́рства `uk7:MZD:016:90:102` scalars[90,102), bytes[164,188).

**Original IDs:** προκρίματος `tagnt:404d5b70cc07e9b9353f86446146bfc7044069ecd46ab5ac678d2fc5f2d4ded2:c01` lemma πρόκριμα source raw ['G4299'] classic ['G4299'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Не найден occurrence-specific авторский/филологический proof, что лицемірство здесь реализует именно предварительное пристрастное суждение; точный classifier omission/addition также не доказан.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:3e9af351d8017688f0f2f60227f35b17`, `target:gold7:target:127252414580cdfa1bd45fe616756da2`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/prokrima), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=5&verse=21).

## 1Tim.6.3

**Exact OH1988:** А коли хто навчає інакше, і не приступає до здорових слів Господа нашого Ісуса Христа та до науки, що вона за правдивою вірою, —

Exact source — εὐσέβειαν/εὐσέβεια/G2150 в τῇ κατ᾽ εὐσέβειαν διδασκαλίᾳ; exact target — «до науки, що вона за правдивою вірою». Greek κατ᾽ и Ukrainian за задают один standard-of-teaching role, весь религиозный standard выражен target phrase правдивою вірою; отдельного πίστις или adjective true в этой clause нет. Locked UGNT, TAGNT и SBL подтверждают единственное εὐσέβειαν в этой роли. Mounce даёт общий religion/piety semantic range и отдельно отображает actual6.3 godliness occurrence; словарный пример3.16 НЕ используется как occurrence proof6.3. NET same6.3 содержит Greek occurrence и опубликованный BBE rendering true religion. Скан над6.3 имеет heading «Правдиве благочестя», используемую лишь как локальный editorial context. Семантический стандарт сохранён одной украинской phrase; old NULL/addition decomposition не учитывает эту реализацию. Предлагается отдельная reciprocal correction εὐσέβειαν→правдивою+вірою, без смены источника/Strong.

**Scan:** DjVu leaf 1465 / печатная стр. 1461.

**Exact target spans:** правдивою `uk7:MZK:022:110:119` scalars[110,119), bytes[197,215); вірою `uk7:MZK:023:120:125` scalars[120,125), bytes[216,226).

**Original IDs:** εὐσέβειαν `tagnt:fdc8bb01d8344e60a170aea62ba043fc6a8be1a8a84ba600779717da7483c4a7:c01` lemma εὐσέβεια source raw ['G2150'] classic ['G2150'].

**Вывод:** `deferred_strong_unassigned_pending_distinct_correction`.

**Missing proof:** Для принятия исправленного accounting нужны отдельный corrector и независимый post-correction QC. Current original_omitted/translation_addition labels не освобождаются этой исследовательской ролью.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:98361d5a6a9bde627988654ced595cff`, `target:gold7:target:0f55c9c9b589cfb6a875a63ff0fb6a20`, `target:gold7:target:c381d95b80883673e527b4db3fa2ec42`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/eusebeia), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=6&verse=3).

**Отдельный correction proposal:** `group005-research-1Tim6.3-eusebeia`; researcher не authorizes accepted change и не переписывает historical QC.

- `original:gold7:original:98361d5a6a9bde627988654ced595cff`: {"group_original_token_ids": ["tagnt:fdc8bb01d8344e60a170aea62ba043fc6a8be1a8a84ba600779717da7483c4a7:c01"], "null_reason": null, "relation": "one_to_many", "target_token_ids": ["uk7:MZK:022:110:119", "uk7:MZK:023:120:125"]}.

- `target:gold7:target:0f55c9c9b589cfb6a875a63ff0fb6a20`: {"linked_original_token_ids": ["tagnt:fdc8bb01d8344e60a170aea62ba043fc6a8be1a8a84ba600779717da7483c4a7:c01"], "target_status": "aligned"}.

- `target:gold7:target:c381d95b80883673e527b4db3fa2ec42`: {"linked_original_token_ids": ["tagnt:fdc8bb01d8344e60a170aea62ba043fc6a8be1a8a84ba600779717da7483c4a7:c01"], "target_status": "aligned"}.

## 1Tim.6.10

**Exact OH1988:** Бо корень усього лихого — то грошолюбство, якому віддавшись, дехто відбились від віри й поклали на себе великі стражда́ння.

Exact raw source — πολλαῖς.¶ (лемма πολύς/G4183, dative plural adjective) в ὀδύναις πολλαῖς; exact target — «великі» modifying «стражда́ння». Ни πολλάς, ни «великими» не являются locked spans этого случая. TAGNT/UGNT/SBL/NET подтверждают ту же пару pains+quantitative modifier. Mounce lexical range включает many, great, large, magnitude/quantity; actual6.10 occurrence приведён как many pains, что отделено от общего диапазона. Украинское великі передаёт величину страданий того же predication, а не вводит другой adjective occurrence. Единственный selected modifier, тот же modified head, отсутствие competing source adjective и допустимый magnitude sense делают reciprocal link поддержанным. Предлагается separate correction old sourceNULL/targetaddition→one_to_one, retainingG4183.

**Scan:** DjVu leaf 1466 / печатная стр. 1462.

**Exact target spans:** великі `uk7:MZR:017:104:110` scalars[104,110), bytes[190,202).

**Original IDs:** πολλαῖς.¶ `tagnt:0760a386b29a718125ec45c421875a13c9bbdfd2f4b3cc82d24bad37b446aa24:c01` lemma πολύς source raw ['G4183'] classic ['G4183'].

**Вывод:** `deferred_strong_unassigned_pending_distinct_correction`.

**Missing proof:** Нужны отдельный corrector и independent post-correction QC; researcher не меняет old NULL/addition payloads и не освобождает их до исправления.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:a419d6d377bf185f7c6e8491ceba60a5`, `target:gold7:target:176fc3c75ed56e14e659a55d335a9f41`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/polys), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=6&verse=10).

**Отдельный correction proposal:** `group005-research-1Tim6.10-polys`; researcher не authorizes accepted change и не переписывает historical QC.

- `original:gold7:original:a419d6d377bf185f7c6e8491ceba60a5`: {"group_original_token_ids": ["tagnt:0760a386b29a718125ec45c421875a13c9bbdfd2f4b3cc82d24bad37b446aa24:c01"], "null_reason": null, "relation": "one_to_one", "target_token_ids": ["uk7:MZR:017:104:110"]}.

- `target:gold7:target:176fc3c75ed56e14e659a55d335a9f41`: {"linked_original_token_ids": ["tagnt:0760a386b29a718125ec45c421875a13c9bbdfd2f4b3cc82d24bad37b446aa24:c01"], "target_status": "aligned"}.

## 1Tim.6.21

**Exact OH1988:** Дехто віддався йому, та й від віри відпав. Благода́ть з тобою. Амі́нь.

Exact OH «з тобою. Амі́нь» имеет singular second-person и завершающую particle. Selected ὑμῶν — plural; TAGNT unified lemma σύ/G4771 не отменяет number contrast. SBL apparatus явно противопоставляет μεθ᾽ ὑμῶν и RP μετὰ σοῦ Ἀμήν. Locked UGNT has plural same occurrence and no amen node; NET textual note и printed scan подтверждают обе фактические стороны. Current selected source содержит no amen original ID, и singular σου/G4675 alternative не selected. Ни shared lemma, ни наличие traditional alternative не доказывают current sourceNULL/targetaddition механизм и не разрешают новые номера.

**Scan:** DjVu leaf 1466 / печатная стр. 1462.

**Exact target spans:** тобою `uk7:N02:011:56:61` scalars[56,61), bytes[100,110); Амі́нь `uk7:N02:012:63:69` scalars[63,69), bytes[112,124).

**Original IDs:** ὑμῶν `tagnt:13c7b1fed6e70343cc37551466dd389d855e2fcedb22d7be56171e42cf309f18:c01` lemma σύ source raw ['G4771'] classic ['G4771'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Нет selected singular original ID для тобою и selected amen ID. Не доказаны intentional number adaptation или translation-addition mechanism, поэтому три current keys остаются без недоказанного Strong/classifier.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:a7e713066ae304a3d08f5322a9bb0d82`, `target:gold7:target:1124c6d1730b755e2f42ec33209dd108`, `target:gold7:target:379ea9029f4d7db268483ded834a962b`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=6&verse=21).

## 2Tim.1.5

**Exact OH1988:** Я приво́джу на пам'ять собі твою нелицемірну віру, що перше була́ осели́лася в бабі твоїй Лоі́ді та в твоїй матері Евні́кії; певен же я, що й у тобі вона осели́лась.

Exact OH «Я приво́джу на пам'ять собі» реализует remembrance predication ὑπόμνησιν λαβών; selected λαβών/λαμβάνω/G2983 — тот же receiving/calling-to-mind lexical occurrence. Mounce не только общий gloss: прямо определяет λαμβάνειν ὑπόμνησιν как recollect/call to mind с ref2Tim1.5 и отдельно отображает actual λαβών. NET same-verse note объясняет превращение Greek continuation participle в новую finite-I sentence. Controlled subject same Paul; Я+приводжу — finite reconstruction selected participle, а на пам'ять собі относится к отдельно учтённому ὑπόμνησιν. SBL apparatus λαβών/λαμβάνων меняет aspect, не lexical identity, governing memory object или число source occurrences. Existing three reciprocal labels доказаны относительно выбранного source; exact historical tense/exemplar не заявлен.

**Scan:** DjVu leaf 1466 / печатная стр. 1462.

**Exact target spans:** Я `uk7:N07:001:0:1` scalars[0,1), bytes[0,2); приво́джу `uk7:N07:002:2:11` scalars[2,11), bytes[3,21).

**Original IDs:** λαβὼν `tagnt:3e1e6f833393accebc6da0a351029b809dc49929243773a0116e7cc686ca45f2:c01` lemma λαμβάνω source raw ['G2983'] classic ['G2983'].

**Вывод:** `proven_existing_selected_assignment_author_proposal`.

**Released keys:** `original:gold7:original:d333cb757196388fa98a75883989cd37`, `target:gold7:target:32fa8d65405c4798023fe5f351690756`, `target:gold7:target:e5b1d0173ec1e586c9004fcab7d1ca60`.

**Deferred current keys:** 0.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/lambano), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=1&verse=5).

## 2Tim.2.16

**Exact OH1988:** Стережися ж базі́кань марни́х, бо вони ще більше провадять до безбожности,

Selected βεβήλους/βέβηλος/G952 modifies κενοφωνίας, а OH «марни́х» modifies «базі́кань». Mounce actual2Tim2.16 показывает unholy chatter; source adjective has profane/godless semantic range. Vain/empty force уже содержится в distinct κενοφωνίας. Phrase-level paraphrase базікань марних вероятна, но one-to-one βεβήλους→марних не доказана достаточным lexical contribution distinction. Нельзя перенести G2757 с noun или исключить source adjective как доказанную omission.

**Scan:** DjVu leaf 1468 / печатная стр. 1464.

**Exact target spans:** марни́х `uk7:N10:004:22:29` scalars[22,29), bytes[41,55).

**Original IDs:** βεβήλους `tagnt:0f537932b06114ed722e8c7281428d4500882a275f5a9e2a43fd54a9231f5284:c01` lemma βέβηλος source raw ['G0952'] classic ['G952'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Не установлен достаточный occurrence-specific proof, что отдельно марних реализует profane qualifier rather than empty-talk contribution of κενοφωνίας; альтернативная phrase grouping не доказана в текущем accounting.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:73c958d7bacaf82fcf8d2b081166c7b6`, `target:gold7:target:101e17432b93a2eb7f80541da658b253`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/bebelos).

## 2Tim.3.8

**Exact OH1988:** Як Янній та Ямврій протиставилися були Мойсеєві, так і ці протиста́вляться правді, люди зіпсутого розуму, не́уки щодо віри.

Selected ἀδόκιμοι/ἀδόκιμος/G96 — failing test/disqualified concerning the faith. OH точно печатает «не́уки щодо віри». Locked Greek occurrences и Mounce/NET same3.8 подтверждают failing/disapproved sense, а direct evidence для перехода к ignorant/uneducated не получено. Same phrase position и same faith topic дают plausible referential correspondence, но сами по себе не достаточны для точной lexical binding. Никакой другой ignorance Strong не назначается; current QC uncertainty не превращается в definite error.

**Scan:** DjVu leaf 1468 / печатная стр. 1464.

**Exact target spans:** не́уки `uk7:N1I:016:106:112` scalars[106,112), bytes[194,206).

**Original IDs:** ἀδόκιμοι `tagnt:a23b0e1ce2db86831de5bc878e5f19d83540d2eb49eb23684c5bb306f6b7f008:c01` lemma ἀδόκιμος source raw ['G0096'] classic ['G96'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Нет occurrence-specific филологического или авторского proof, связывающего неуки с failed-approval/unfitness predicate сильнее простой topical paraphrase.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:1bee42c0e8c7a189450dd264f0bccac7`, `target:gold7:target:574362de0109f147552eab6dbd78d2cf`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/adokimos), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=3&verse=8).

## 2Tim.4.14

**Exact OH1988:** Котля́р Олександер нако́їв був лиха чимало мені... Нехай Госпо́дь йому віддасть за його вчинками!

Repayment lexical identity ἀποδώσει/ἀποδίδωμι/G591 и exact «віддасть» в Lord→Alexander according deeds clause подтверждена locked sources и Mounce/NET actual4.14. Но current original group включает также «Нехай», который эксплицитно выражает wish/jussive, тогда как selected verb — future indicative. Official SBL apparatus содержит optativeἀποδῴη; обе формы имеют одну lemma, но sharedG591 не доказывает selected indicative mood contribution к Нехай. Лексическое ядро доказано отдельно; current complete one-to-many group остаётся fail-closed. Exact historical edition не требуется, но без дополнительного proof нельзя приписать selected indicative именно jussive particle. Номер optative не импортируется, NULL/addition для Нехай не изобретается.

**Scan:** DjVu leaf 1469 / печатная стр. 1465.

**Exact target spans:** Нехай `uk7:N25:008:51:56` scalars[51,56), bytes[92,102); віддасть `uk7:N25:011:71:79` scalars[71,79), bytes[129,145).

**Original IDs:** ἀποδώσει `tagnt:3c9ed6b67fd40f02d036bebd87218005e2dcebe952cbe9c7f98456784a077e07:c01` lemma ἀποδίδωμι source raw ['G0591'] classic ['G591'].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Недостаточен proof полной current group ἀποδώσει→Нехай+віддасть, specifically modal particle contribution. Для narrower lexical-only correction нужна separate controlled accounting adjudication; текущие три reciprocal group labels следует defer together.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:4f03413faeca871285e339af11f62957`, `target:gold7:target:d229b9253d3ace75c7c5842f1eb212bc`, `target:gold7:target:f52b968158761e8faca15a79bd4653d0`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/apodidomi), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=4&verse=14).

## 2Tim.4.22

**Exact OH1988:** Господь з твоїм духом! Благода́ть з вами! Амі́нь.

OH точно имеет closing «Амі́нь». Selected TAGNT/UGNT/SBL заканчиваются grace-with-you clause без amen node. Official SBL apparatus attests RP+Ἀμήν, а NET same-verse control lists traditional amen; это доказательство textual alternative, не author-added Ukrainian word и не controlled selected original identity. Совпадение с G281 из unselected reading не разрешает production/classic assignment. Source scope plural grace «вами» здесь не questioned и не переопределяется.

**Scan:** DjVu leaf 1469 / печатная стр. 1465.

**Exact target spans:** Амі́нь `uk7:N2D:008:42:48` scalars[42,48), bytes[75,87).

**Original IDs:** В selected grid нет corresponding original node..

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Нет selected amen original ID и proof translation-addition mechanism. Для Strong нужна controlled source-policy resolution; current single target remains deferred.

**Released keys:** 0.

**Deferred current keys:** `target:gold7:target:23d504bf265048a9fdfea3e0f7ff0c66`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=4&verse=22).

## 1Tim.1.13

**Exact OH1988:** мене, що давніше був богознева́жник, і гноби́тель, і напасни́к, але був помилуваний, бо я те чинив нетяму́чий у невірстві.

Current effective adjudication имеет one-to-one selected neuterτὸ/G3588→що; participleὄντα/G1510 separately→був. Selected τὸπρότερον — adverbial formerly, а neuterτὸ не masculine attributive article toὄντα. Locked UGNT/SBL attest τὸ; apparatus RPτὸν допускает другое traditional construction, но не подменяет selected token. Same-verse NET Greek distinguishes neuter article/adverbial and masculine participle; printed OH1462 has «мене, що давніше був». Ukrainian relative finite clause що…був reconstructs masculine participle with antecedentPaul; formerly is already rendered давніше. Therefore existingτὸ→що attaches different grammatical roles. Well-supported exact4row correction proposal keeps article as grammatical_function_not_overt and assignsщо+був jointly toὄντα. No morphology or source selection edits, no generic source-text omission.

**Scan:** DjVu leaf 1462 / печатная стр. 1458.

**Exact target spans:** що `uk7:MXA:002:6:8` scalars[6,8), bytes[10,14); був `uk7:MXA:004:17:20` scalars[17,20), bytes[30,36).

**Original IDs:** τὸ `tagnt:aaadfe922d225261541e290618248b5634fd81b7e002784c660d3bfc8be22000:c01` lemma ὁ source raw ['G3588'] classic ['G3588']; ὄντα `tagnt:7469660963fce0e8dd6de6fc460d5c8071fc47170d8afd45be6784c2c7cf9299:c01` lemma εἰμί source raw ['G1510'] classic ['G1510'].

**Вывод:** `deferred_strong_unassigned_pending_distinct_correction`.

**Missing proof:** Требуются отдельный corrector и independent post-correction QC for exact4rows. До этого два newly questioned keys оставляются deferred; already accepted participle/був neighbors included in candidate scope, not silently rewritten.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:18c1e6b0f3f681df32d4a3e7992e9aa3`, `target:gold7:target:1c6bda4247fbaa2e5fcaf7722a17cbee`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=1Ti&chapter=1&verse=13).

**Отдельный correction proposal:** `group005-research-1Tim1.13-neuter-adverbial-article`; researcher не authorizes accepted change и не переписывает historical QC.

- `original:gold7:original:18c1e6b0f3f681df32d4a3e7992e9aa3`: {"group_original_token_ids": ["tagnt:aaadfe922d225261541e290618248b5634fd81b7e002784c660d3bfc8be22000:c01"], "null_reason": "grammatical_function_not_overt", "relation": "original_omitted", "target_token_ids": []}.

- `original:gold7:original:2378f2abe4cd58eed68151e0995902df`: {"group_original_token_ids": ["tagnt:7469660963fce0e8dd6de6fc460d5c8071fc47170d8afd45be6784c2c7cf9299:c01"], "null_reason": null, "relation": "one_to_many", "target_token_ids": ["uk7:MXA:002:6:8", "uk7:MXA:004:17:20"]}.

- `target:gold7:target:1c6bda4247fbaa2e5fcaf7722a17cbee`: {"linked_original_token_ids": ["tagnt:7469660963fce0e8dd6de6fc460d5c8071fc47170d8afd45be6784c2c7cf9299:c01"], "target_status": "aligned"}.

- `target:gold7:target:9fe4b75d7d3df5d68409ef784d7af4d8`: {"linked_original_token_ids": ["tagnt:7469660963fce0e8dd6de6fc460d5c8071fc47170d8afd45be6784c2c7cf9299:c01"], "target_status": "aligned"}.

## 1Tim.1.16

**Exact OH1988:** Але я тому́ був помилуваний, щоб Ісус Христос на першім мені показав усе довготерпіння, для при́кладу тим, що мають увірувати в Нього на вічне життя.

Selected ἅπασαν/ἅπας/G537 modifies μακροθυμίαν; exact OH усе modifies довготерпіння and preserves whole/complete extent. Locked UGNT same1.16 hasἅπασαν/G05370; Mounce actual1.16 displays complete patience andG537; SBL apparatus attests alternativeπᾶσαν/G3956 without changing this syntactic role. Proof uses selected whole-totality lexical contribution and exact target, not an inference of historical edition. G3956 is not promoted; existing two labels retained.

**Scan:** DjVu leaf 1462 / печатная стр. 1458.

**Exact target spans:** усе `uk7:MXD:013:69:72` scalars[69,72), bytes[125,131).

**Original IDs:** ἅπασαν `tagnt:aa24a6e455cdb008f157fca27484624849014695e57e37c9fec74a6e79f86a71:c01` lemma ἅπας source raw ['G0537'] classic ['G537'].

**Вывод:** `proven_existing_selected_assignment_author_proposal`.

**Released keys:** `original:gold7:original:4eaec762166059e87b6b808ab97c0f78`, `target:gold7:target:ecad8c04ed4a95b1f22df5bab39d7b0e`.

**Deferred current keys:** 0.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/hapas).

## 1Tim.2.3

**Exact OH1988:** Бо це добре й приємне Спасителеві нашому Богові,

Exact initialБо introduces explanation. Selected Greek startsτοῦτο and contains noγάρ node; lockedUGNT agrees, while SBL apparatus explicitly addsγὰρ inRP. Current function_token/translation_addition accounting is inherited label, not proof that the translator independently added this connector. Traditionalsource provides plausible source occurrence outside selectedgrid, so missing sourceID cannot be compensated by adoptingG1063 or definite addition.

**Scan:** DjVu leaf 1463 / печатная стр. 1459.

**Exact target spans:** Бо `uk7:MXK:001:0:2` scalars[0,2), bytes[0,4).

**Original IDs:** В selected grid нет corresponding original node..

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Нет selectedγάρ originalID and proof Ukrainianfunction/addition origin; currentsingle target needs registered exclusion without Strong/classifier.

**Released keys:** 0.

**Deferred current keys:** `target:gold7:target:0b1c9b84a801e1c4161b4eafb0ce9ab0`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt).

## 1Tim.6.11

**Exact OH1988:** Але ти, о Божа люди́но, утікай від такого, а женися за праведністю, благоче́стям, вірою, любов'ю, терпеливістю, ла́гідністю!

Exact selectedπραϋπαθίαν/G6073 and OHла́гідністю sharegentleness lexical contribution in samevirtuelist, proved by lockedTAGNT/UGNT/SBL and Mounceactual6.11. Classicalidentity differs from G6063 case: verifiedTBESGline5860 eStrongG6073,dStrongG6073=,uStrongG6073 (selfidentity), withG4236 described only as manuscript substitutionπραότης. UGNT exactπραϋπαθία lemma tagsG42385, a nonclassic identifier; stripping final5 would falsely produce differentlemma G4238. Mounce publishes4236 forπραϋπάθεια, but supplier-specific classic correspondence remains unproved in the presence of explicitdifferentlemma alternative. Lexicalmatch alone does not license conversion toG4236. Bothlabelsdefer forclassicalidentity, frozenclassic[]preserved.

**Scan:** DjVu leaf 1466 / печатная стр. 1462.

**Exact target spans:** ла́гідністю `uk7:MZS:017:112:123` scalars[112,123), bytes[199,221).

**Original IDs:** πραϋπαθίαν· `tagnt:711a61ff52a12d4b2e3a29b2f3bee4d5aedaf582aeaeb2d5dab8cd4c0aab5c50:c01` lemma πραϋπαθία source raw ['G6073'] classic [].

**Вывод:** `deferred_strong_unassigned`.

**Missing proof:** Не установлена non-competing conventionalclassicStrong identity for exactselectedπραϋπαθία/G6073; TAGNT selfidentity, UGNT customG42385, Mounce4236 convention do not supply explicitform-equivalence bridge. No G4236/G4238/G4240 is assigned.

**Released keys:** 0.

**Deferred current keys:** `original:gold7:original:b0f6f0dd38802d9a15cefb81675f960e`, `target:gold7:target:73dc453e90785869fc3b2d474c5aed86`.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/1Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/1Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/praupatheia), [primary occurrence / apparatus](https://github.com/STEPBible/STEPBible-Data/blob/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt), [primary occurrence / apparatus](https://moments.nbseminary.com/archives/148-pursuing-praupatheia-an-essential-virtue-for-christian-leaders-1-timothy-611/).

## 2Tim.2.14

**Exact OH1988:** Нагадуй про це й заклинай перед Богом, щоб не спереча́лись словами, бо ніна́що воно, хіба слухача́м на руїну.

Exact selectedἐπ᾽οὐδὲνχρήσιμον realizes purpose/result to no benefit; OH«бо ніна́що воно» compresses this phrase into exactadverbніна́що. LockedUGNT tagsfirstἐπ᾽G19090 beforeοὐδὲνχρήσιμον; Mounceactual2.14 explicitly glosses selectedprep as resultsin nothingbeneficial; NETsameverseGreek and translationnote confirm beneficialfornothing. Distinctlaterἐπὶκαταστροφῇ corresponds to ruinclause and is not reused. SBL/TAGNTalternativeεἰς/G1519 is acknowledged but not imported. Existing three-original/one-targetgroup preserves selectedprep relationalcontribution + negation + usefulness idiom. Four scopedlabels accepted as existinggroup; exacthistorical edition unprovedunneeded.

**Scan:** DjVu leaf 1467 / печатная стр. 1463.

**Exact target spans:** ніна́що `uk7:N0Y:013:71:78` scalars[71,78), bytes[128,142).

**Original IDs:** ἐπ᾽ `tagnt:96a7e8912aa4e0248e1437bc4131a2d624d6a9b8e3cb9dcceae73b9485b8bb0b:c01` lemma ἐπί source raw ['G1909'] classic ['G1909']; οὐδὲν `tagnt:e67e5317aef5bff350a136083065b8f7dc9b38f5ccbbf6ff3c23516be44e7c7b:c01` lemma οὐδείς source raw ['G3762'] classic ['G3762']; χρήσιμον `tagnt:c0413dcb079531b2f56c9e18631df9289b863add9e6c9b7b1d6bef50a8becd1d:c01` lemma χρήσιμος source raw ['G5539'] classic ['G5539'].

**Вывод:** `proven_existing_selected_assignment_author_proposal`.

**Released keys:** `original:gold7:original:fd47ca8653db7ac205a477b4ea9cb73e`, `original:gold7:original:61e00fc436411d167664ec0474dfcc61`, `original:gold7:original:0cf7dee9cd3f0ab108a0fd836fcb136e`, `target:gold7:target:5822a2b16e008e8e1e18e5b705297f47`.

**Deferred current keys:** 0.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/epi), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=2&verse=14).

## 2Tim.3.15

**Exact OH1988:** І ти знаєш з дити́нства Писа́ння святе, що може зробититебе мудрим на спасі́ння вірою в Христа Ісуса.

Exact selectedοἶδας/G6063, perfactind2sg, realizes«ти знаєш». VerifiedofficialTBESGline5850 explicitly marksG6063=aFormof uStrongG1492H andlemmaοἶδα; lines1630–1632 carryconventionalG1492. This approvedgroup4 correspondence is reused as dictionary proofonly, not as occurrenceproof fromEph. LockedUGNTactual2Tim3.15 hasοἶδας,lemmaοἶδα,G14920, withexact nativewordordinal7 despite selectedTAGNTordinal8 (separatearticlevariation), so crosswalk uses form/role, notposition. NETactual3.15 confirms knowledgeofholyScriptures; scannedOH hasти знаєш. Threeexistinglabelslexicallyandclassic-proven; frozenG6063andclassic[]unchanged, no newproductionnumber.

**Scan:** DjVu leaf 1468 / печатная стр. 1464, DjVu leaf 1469 / печатная стр. 1465.

**Exact target spans:** ти `uk7:N1P:002:2:4` scalars[2,4), bytes[3,7); знаєш `uk7:N1P:003:5:10` scalars[5,10), bytes[8,18).

**Original IDs:** οἶδας, `tagnt:20a76490112499feeb706c8d286a424f3dc3060844fdb239b36ee89627b136b5:c01` lemma εἴδω source raw ['G6063'] classic [].

**Вывод:** `proven_existing_selected_assignment_author_proposal`.

**Released keys:** `original:gold7:original:ef96f82de603eea70cc309bcccdb8f16`, `target:gold7:target:be6d09158a259d253a2ce2e8c0d5be55`, `target:gold7:target:eb988b9602e7d941c8e5fc0360a97e2f`.

**Deferred current keys:** 0.

**Источники:** [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/2Tim.txt), [primary occurrence / apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2Tim.txt), [primary occurrence / apparatus](https://www.billmounce.com/greek-dictionary/oida), [primary occurrence / apparatus](https://github.com/STEPBible/STEPBible-Data/blob/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/Lexicons/TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20Greek%20-%20STEPBible.org%20CC%20BY.txt), [primary occurrence / apparatus](https://classic.net.bible.org/verse.php?book=2Ti&chapter=3&verse=15).

## Integrity / scope receipts

34 preflight locks PASS; exact selected text scalar/byte span checks 22 PASS; UGNT member native locators/raw-fragment SHA сохранены; SBL text/apparatus pinned commit `c4d241a9c1c479a55b989ba35a4976c1d0b8052c`; TAGNT/TBESG commit `b9dcc831a98e0fd6f3c7e122be9ff68377c310c0`; UGNT commit `fc95b2b8aad08bb65ab54628ab685413a1139e97`.

Недоступные попытки учтены: initial SBL abbreviated filenames `1Ti/2Ti` returned404, corrected to official `1Tim/2Tim`; NET2Tim2.16 fetch timed out and not claimed inspected; five СУМ URLs unavailable through browsing and not used as proof. Subsequent source archiving is receipt preparation, not a second philological cycle. No paid experts assumed.

License scope: SBL CC BY4.0; existing STEPBible CC BY4.0; existing UGNT CC BY-SA4.0 retained only as research/control evidence. Mounce/NET scholarly sources citation-only; no third-party runtime dependency/component adopted or redistributed with the application. No license/policy text changes.

Change checklist: only private first-party research scripts/artifacts; Flutter/runtime/tests/docs approved pairs/dependencies/localization/release/schema unchanged (N/A to runtime gates). Research validation uses exact input locks, source native occurrences, scalar+byte spans, JSON roster and output manifest. Root handles publication/navigation/global checks.

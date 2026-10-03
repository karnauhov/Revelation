# Группа №2: bounded source resolution Luke / John v1

Дата: 2026-10-03. Автор: `codex-group002-luke-john-research-20261003-01`.
Роль: только исследователь/автор; автор не является независимым QC.

**Авторский итог: из 24 прежних uncertain stable keys предложено сохранить 6 доказанных ключей (3 reciprocal пары), 18 ключей завершить как `deferred_strong_unassigned`. Definite content errors и correction scopes: 0.** Это не приёмка книг: отдельный content QC и mechanical completion остаются за root/reviewer.

## Зафиксированные входы и фактическая цепочка

До полного чтения work JSONL физически проверены 121 релевантный input lock по SHA и bytes, включая inventory `99b3cfd9328308e19e823eefdea5659d4ddcbf9fcd1f2a20fb53335cc9f7f29f` (1422496 bytes), selected original layer (1190235451 bytes) и original universe (1102373802 bytes). Полный entry roster и роли находятся в [`role_and_input_locks.v1.json`](../../work/ukrainian_stage_7_20260801/session_group2_20261003_luke_john_research_01/role_and_input_locks.v1.json).

Luke: frozen batch042 хранит исторический QC9c34b5a2…; текущий downstream rebase использует adjudication6060591b…/sidecar1d34d91e… и QCaa6ce85b…/sidecarb4906325…. Изменённых semantic QC rows в provenance rebase0. John: repaired pass2/comparison → adjudication139ffd0f…/sidecar5410146d… → QC67233ff0…/sidecar08c0a235…. Никакой blind pass/adjudication здесь не повторяется. Shared issue inventory a2d7b575… inspected only; новые строки туда автор не пишет.

OT39 completed/38 strict не открывались. Runtime, БД, gold selection, stage5/6 текст/комментарии, старые passes и QC сохранены. Историческое имя издания не требуется, если сам occurrence lemma/Strong/span доказан. Но synonymous Ukrainian wording при разных Strong не считается proof.

## Авторские выводы по exact occurrences

### Luke.1.76

**0 resolved / 2 deferred keys.** OH1988 leaf 1267; printed page 1263.

OH1988 печатает «будеш ходи́ти перед Господом». В exact occurrence TAGNT selected ἐνώπιον/G1799; аппарат SBLGNT противопоставляет ему πρὸ προσώπου, TAGNT πρὸ/G4253 и πρόσωπον/G4383. Обе конструкции выражают предшествование/нахождение перед Господом. Украинское «перед» не различает эти источники; отсутствие отдельного «лица» может быть обычным идиоматическим сокращением. Synonym fit не доказывает один Strong.

Exact target: Ти ж, дитино, станеш пророком Всеви́шнього, бо будеш ходи́ти перед Господом, щоб дорогу Йому приготува́ти,

Точные ключи:

- `original:gold7:original:4a15ce4e87e0d34545591c5c8c35bacf` — deferred_strong_unassigned
- `target:gold7:target:854800f2bbdf898e2bc13d6b5d6d938e` — deferred_strong_unassigned

Попытки: ἐνώπιον/G1799 → перед; πρὸ/G4253 + προσώπου/G4383 → перед (idiomatic reduction).

Недостающий довод: Occurrence-specific evidence distinguishing ἐνώπιον from πρὸ προσώπου, or independently justified selected-reference accounting that does not merely assume synonymous equivalence.

Будущий шаг: Optional: obtain an occurrence-specific author/edition note or documented source collation; do not repeat broad edition research.

### Luke.10.15

**2 resolved / 4 deferred keys.** OH1988 leaf 1284; printed page 1280.

Скан подтверждает утвердительное «що … піднісся» и «зійдеш!», без отрицательного вопроса. Аппарат различает μὴ … ὑψωθήσῃ и ἡ … ὑψωθεῖσα; обе формы ὑψόω имеют тот же G5312 и в том же clause соответствуют «піднісся». Эта отдельная reciprocal пара доказана на уровне леммы/Strong; morphology/Vorlage не объявлены установленными. Для μὴ/G3361 ↔ NULL и «що» ↔ source NULL нельзя доказать source omission или target addition лишь по формулировке. Καταβήσῃ/G2597 и καταβιβασθήσῃ/G2601 оба способны получить украинское «зійдеш»; разные номера остаются недоказанными.

Exact target: А ти, Капернау́ме, що „до неба піднісся, — аж до аду ти зійдеш!“

Точные ключи:

- `original:gold7:original:37e013a050e63313864e95759d39340b` — deferred_strong_unassigned
- `original:gold7:original:4883ea5680c6e81e3ecb854eea946bd2` — resolved_retained_reference_alignment_pending_independent_qc
- `original:gold7:original:6ceecb3822aaef8a22acc3f9481dc0cd` — deferred_strong_unassigned
- `target:gold7:target:91102576ac24d85192322e10404437ee` — deferred_strong_unassigned
- `target:gold7:target:a16d0beccd9f673fb17f0c1aec942756` — resolved_retained_reference_alignment_pending_independent_qc
- `target:gold7:target:ae8d8183078b01580361b0de017e70e9` — deferred_strong_unassigned

Попытки: μὴ/G3361 versus ἡ/G3588; ὑψωθήσῃ versus ὑψωθεῖσα: same ὑψόω/G5312; καταβήσῃ/G2597 versus καταβιβασθήσῃ/G2601.

Недостающий довод: For four deferred keys: occurrence-specific proof of the negative/article accounting and the down-verb lemma; affirmative Ukrainian morphology alone is insufficient.

Будущий шаг: Optional later source/author evidence for the two genuinely different lemma/accounting choices. Preserve the invariant G5312 pair now.

### Luke.10.42

**0 resolved / 1 deferred keys.** OH1988 leaf 1285; printed page 1281.

На скане «а потрібне одне»; SBLGNT/WH имеют ὀλίγων … ἢ ἑνός, а Treg/RP/NA28 ἑνὸς … . Selected gold occurrence ὀλίγων/G3641 не имеет явно выраженного украинского количества. Сокращённая передача длинного чтения и короткое source reading остаются альтернативами. Нельзя объявить translation omission доказанным, а от отсутствия «небагато» нельзя произвести source ID или новый NULL verdict.

Exact target: а потрібне одне. Марія ж обрала найкращу ча́стку, яка не відбереться від неї“.

Точные ключи:

- `original:gold7:original:f3e182098db2fce895701bdd4d32358e` — deferred_strong_unassigned

Попытки: few-or-one source rendered by one-only summarization; one-only source; selected few component does not establish OH source.

Недостающий довод: Positive evidence establishing whether selected ὀλίγων actually contributed to this target sentence rather than assuming a source/translation omission.

Будущий шаг: Optional documented occurrence-level source or author explanation for the short rendering.

### Luke.13.7

**0 resolved / 1 deferred keys.** OH1988 leaf 1291; printed page 1287.

Скан даёт «зрубай його, — нащо й землю марну́є воно?» без отдельного «отже/тому». TAGNT и SBLGNT apparatus подтверждают οὖν/G3767 в NA28/NA27/Tyn, но отсутствие в SBL/WH/Treg/TR/Byz. Inferential relation in the imperative can remain implicit when οὖν is present. Поэтому невидимый overt marker не различает implicit discourse rendering и reading without οὖν. Исходный uncertain не превращается в content error или definite source omission.

Exact target: І сказав винаре́ві: „Оце́ третій рік, відко́ли прихо́джу шукати плоду на цім фіґовім дереві, але не знахо́джу; зрубай його, — нащо й землю марну́є воно?“

Точные ключи:

- `original:gold7:original:2846e9eaf03eaa2995e24a7124c48dae` — deferred_strong_unassigned

Попытки: οὖν present, inferential discourse contribution implicit; οὖν absent in source reading.

Недостающий довод: Occurrence-specific proof of the discourse contribution/presence; punctuation and the lack of a separate word do not settle the source-versus-rendering issue.

Будущий шаг: Optional local discourse/source evidence only; no repeated broad research required for completion.

### Luke.16.21

**0 resolved / 1 deferred keys.** OH1988 leaf 1296; printed page 1292.

Exact «кри́шками, що зо сто́лу багатого падали» подтверждено визуально. Critical source имеет τῶν πιπτόντων, traditional/Treg/RP добавляет τῶν ψιχίων. TAGNT даёт exact alternative ψιχίων/G5589, но selected layer не выбирает этот source atom. Само contextual food noun «кри́шками» можно получить при конкретизации nominalized participle; NET occurrence control допускает food-context wording без ψιχίων. Поэтому G5589 не переносится и inherited target_addition остаётся лишь historical selected-layer snapshot, не новым доказанным отсутствием source contribution.

Exact target: і бажав годува́тися кри́шками, що зо сто́лу багатого падали; пси ж прихо́дили й рани лизали йому́.

Точные ключи:

- `target:gold7:target:2e915cd0795e80bdb5dc8937c9229b6a` — deferred_strong_unassigned

Попытки: explicit ψιχίων/G5589; contextual concretization of τῶν πιπτόντων/G4098 group.

Недостающий довод: Proof that the crumb noun is sourced from the existing ψιχίων occurrence rather than contextual nominalization of falling food; no dictionary/other-verse substitution suffices.

Будущий шаг: Optional exact source or author note establishing this lexical choice; do not add G5589 without that proof.

### Luke.20.34

**0 resolved / 3 deferred keys.** OH1988 leaf 1303; printed page 1299.

Exact «промовив у відповідь» стоит после вопроса саддукеев. Selected εἶπεν/G2036 и target «промовив» имеют доказанную локальную speech связь. Но frozen source decision объединяет «промовив», «у», «відповідь»: последнее может отражать existing traditional ἀποκριθείς/G0611 либо contextual answering expansion of εἶπεν. SBLGNT apparatus прямо фиксирует +ἀποκριθείς RP. Ни вопросительный контекст, ни общая dictionary возможность «said in answer» не различают эти причины. Whole hyperedge source key остаётся deferred; частичная новая alignment не создаётся. Proven «промовив» поддержка сохранена отдельно в evidence/history.

Exact target: Ісус же промовив у відповідь їм: „Женяться й заміж виходять сини цього віку.

Точные ключи:

- `original:gold7:original:cb3d5d6e320b1a19c215501a4eb56315` — deferred_strong_unassigned
- `target:gold7:target:a38ca82c264a544d8d775ed859646a17` — deferred_strong_unassigned
- `target:gold7:target:cd60c02c25f3849fb369f8e5fd08edd7` — deferred_strong_unassigned

Попытки: εἶπεν/G2036 contextually expanded as промовив у відповідь; ἀποκριθείς/G0611 + εἶπεν/G2036.

Недостающий довод: Proof assigning the answering span to the selected εἶπεν alone or to an existing alternative ἀποκριθείς occurrence; enough to change the whole hyperedge without speculation.

Будущий шаг: Optional occurrence-specific author/source evidence. Until then effective projection must close the reciprocal component, including the accepted collateral «промовив» target node, while preserving its accepted semantic verdict.

### John.1.18

**0 resolved / 3 deferred keys.** OH1988 leaf 1312; printed page 1308.

Скан однозначно печатает «Одноро́джений Син». Current selected layer уже содержит qualified υἱός/G5207 apparatus ID и preceding ὁ; это inspected provenance, не новое доказательство. SBLGNT apparatus сохраняет θεός versus ὁ … υἱός. NET primary editorial note объясняет, что substantival μονογενής может подразумевать сына без отдельного υἱός. Поэтому буквальное совпадение «Син» поддерживает traditional candidate, но не устраняет конкурентный contextual/substantival parse и отдельную судьбу θεός. Три uncertain keys сохраняются; G2316 или G5207 заново не назначаются.

Exact target: Ніхто Бога ніко́ли не бачив, — Одноро́джений Син, що в лоні Отця, Той Сам виявив був.

Точные ключи:

- `original:gold7:original:b1bd4cda7b0de0c316a3e1de1082a745` — deferred_strong_unassigned
- `original:gold7:original:d4aed7a2e9803b3435bc429428d56fc6` — deferred_strong_unassigned
- `target:gold7:target:29407746f5ea70c280f1b75f43c6095c` — deferred_strong_unassigned

Попытки: ὁ μονογενὴς υἱός/G5207; μονογενὴς θεός with substantival μονογενής understood as son/unique one.

Недостающий довод: Occurrence-specific proof that exact target Син represents the qualified υἱός atom, with defensible accounting of the article and the competing θεός/μονογενής analysis.

Будущий шаг: Optional author/edition or occurrence-level syntactic evidence. Keep already qualified selection as historical evidence without pretending its inspected label resolves the source choice.

### John.1.28

**2 resolved / 0 deferred keys.** OH1988 leaf 1313; printed page 1309.

Exact proper-name token «Віфа́нії» scalar[5:13), UTF8[8:24) is visually confirmed. The selected original Βηθανίᾳ is the case form of Βηθανία/G0963 (normalized classic G963), with the same local position in the clause and matching name stem. The recorded alternative Βηθαβαρᾶ/G0962 (G962) is a different proper-name stem, not merely another inflection or synonymous preposition. Its predicted Ukrainian transliteration has -вар-, absent here; no apparatus/author note indicates replacing that name by Віфанія. Thus the exact selected-name reciprocal atom is retained; historical edition title and geographic identification of Bethany are not prerequisites and are not claimed.

Exact target: Це в Віфа́нії ді́ялося, на тім боці Йорда́ну, де христив був Іван.

Точные ключи:

- `original:gold7:original:4d936b2f55de892a7836e8a9ed7a3586` — resolved_retained_reference_alignment_pending_independent_qc
- `target:gold7:target:202ca6d084c844654c4f934552a2f42a` — resolved_retained_reference_alignment_pending_independent_qc

Попытки: Βηθανίᾳ/G0963 matches exact Віфа́нії; Βηθαβαρᾶ/G0962 does not match the printed proper-name stem.

Недостающий довод: Нет дополнительного Strong gate; отдельный QC должен проверить локальную неизменённую связь.

Будущий шаг: Independent QC must confirm this exact name-stem and reciprocal atom; historical exemplar/geography may remain optional.

### John.8.11

**0 resolved / 3 deferred keys.** OH1988 leaf 1324, 1325; printed page 1320, 1321.

OH1988 печатает всю pericope; «Іди собі, але більш не гріши!» содержит no separate «відтепер». TAGNT selected ἀπὸ τοῦ νῦν has G0575/G3588/G3568, whereas TR/Byz omit those three words; selected «більш не» already belongs to μηκέτι/G3371. The reading with a redundant temporal phrase and the shorter reading both yield this Ukrainian clause. Presence of the whole pericope proves its inclusion, not the exact internal variant. The three source NULL decisions remain uncertain; no invented deletion or new multiword alignment to вже/більш.

Exact target: А вона відказала: „Ніхто, Господи“. І сказав їй Ісус: „Не засуджую й Я тебе. Іди собі, але більш не гріши!“

Точные ключи:

- `original:gold7:original:04a14fa394542afbad8fbb68a39d5c29` — deferred_strong_unassigned
- `original:gold7:original:a30c43f00b717900d06277eaf3ea26b7` — deferred_strong_unassigned
- `original:gold7:original:bfa3125202aa83daf77dabb0384a875b` — deferred_strong_unassigned

Попытки: ἀπὸ τοῦ νῦν present but temporally absorbed; traditional internal pericope reading without ἀπὸ τοῦ νῦν.

Недостающий довод: Positive evidence distinguishing absorption of the temporal phrase from its source absence, with no double assignment of the already justified μηκέτι span.

Будущий шаг: Optional exact pericope internal source/author note; current inclusion controls do not require another research cycle.

### John.14.15

**2 resolved / 0 deferred keys.** OH1988 leaf 1336; printed page 1332.

Exact «зберігайте» scalar[36:46), UTF8[65:85) is visually confirmed in the commandment clause. Critical τηρήσετε and traditional τηρήσατε are inflections of the same τηρέω/G5083. The local object remains «Мої заповіді», and the target keeps/observes them; the raw selected G5083G qualifier denotes the same observe sense. SBLGNT apparatus confirms future/imperative alternatives, and the primary commentary discusses the future used with imperative force. Thus the reciprocal lexical alignment is invariant; this resolves Strong/link uncertainty without changing morphology or declaring an exact exemplar.

Exact target: Якщо Ви Мене любите, — Мої заповіді зберігайте!

Точные ключи:

- `original:gold7:original:f5d0d4b2358edfc89f051946baeb60a6` — resolved_retained_reference_alignment_pending_independent_qc
- `target:gold7:target:d2cc691c969f2c0dcc527f18e986e732` — resolved_retained_reference_alignment_pending_independent_qc

Попытки: τηρήσετε future: τηρέω/G5083; τηρήσατε imperative: τηρέω/G5083.

Недостающий довод: Нет дополнительного Strong gate; отдельный QC должен проверить локальную неизменённую связь.

Будущий шаг: Independent QC of the unchanged reciprocal pair. Optional grammatical/historical research is not a Strong gate.

## Source-qualified controls и закрытое reciprocal accounting

Все12 exact OH1988 страниц визуально прочитаны; renders имеют SHA/bytes. John.5.4 присутствует и печатает «ангол Господній». Текущий fingerprint-qualified TAGNT layer имеет27 source occurrences, но отдельного κύριος/G2962 не содержит. NET editors сообщают expansion witnesses с Lord phrase: это предостерегает от утверждения, будто переводчик добавил её сам. Existing selected-layer target accounting оставлен как история; новый G2962 не присвоен, другой verse/dictionary не используется.

John.7.53–8.11 на exact scans включены. Это подтверждает включение pericope, а не все её внутренние readings. Ранее доказанные links вне трёх temporal source keys не пересматриваются этим исследованием; final full-grid QC проверяет их отдельно.

Luke.20.34 original deferred key имеет frozen one-to-many hyperedge ко всем трём target tokens. Поэтому completion projection должна закрыть reciprocal component и collateral исключить прежний accepted target key `target:gold7:target:a716d9890919b51ecb6114b98740536a` («промовив»), сохранив его accepted semantic verdict и доказанное G2036 evidence в history. Это1 collateral dependency key сверх18 uncertain keys, не новая ошибка и не потеря исторического proof. Новая partial alignment или correction не создана.

## Доступные первичные источники и scholarly control

- [OH1988 exact scan](https://commons.wikimedia.org/wiki/File:Ivan_Ohienko_Bible.djvu), pinned full SHA0f10b278…; local12 PNG renders проверены визуально. CC BY-SA4.0, существующий source registry; никаких новых runtime dependencies.
- [STEPBible TAGNT exact committed file](https://github.com/STEPBible/STEPBible-Data/blob/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0/Translators%20Amalgamated%20OT%2BNT/TAGNT%20Mat-Jhn%20-%20Translators%20Amalgamated%20Greek%20NT%20-%20STEPBible.org%20CC-BY.txt), SHAab8eaaeb…; CC BY4.0. Exact local occurrence data, не общий dictionary vote.
- [SBLGNT Luke text](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/Luke.txt) / [apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/Luke.txt), [John text](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgnt/text/John.txt) / [apparatus](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/John.txt), commitc4d241a9…, CC BY4.0 по exact LICENSE. Речь о differences between editions, не самостоятельном manuscripts census.
- [NET John1.18 editorial note](https://classic.net.bible.org/verse.php?book=Joh&chapter=1&tab=commentaries&theme=wiki&verse=18): конкурентный substantival μονογενής анализ. [NET Luke16.21](https://classic.net.bible.org/verse.php?book=Luk&chapter=16&verse=21) и [Luke20.34](https://classic.net.bible.org/verse.php?book=Luk&chapter=20&verse=34) — local Greek/context controls only, никакого translation-transfer vote.
- [John14 commentary, Bob Utley](https://bible.org/seriespage/john-14) поддерживает future with imperative force; лемма/Strong доказываются непосредственно TAGNT. [NET John5.4 note](https://classic.net.bible.org/verse.php?book=Joh&chapter=5&verse=4) фиксирует расширение и internal diversity. Citation-only notes; полные copyrighted статьи не сохраняются/не распространяются.

## Ограничения и проверки

В каждом трудном месте выполнен один bounded cycle: scan → exact original occurrence/alternative IDs → accessible edition apparatus → доступный scholarly/context control → reasoned disposition. Paid access не предполагался. Реестр содержит точную missing proof/future follow-up; deferred записано без Strong и без переименования uncertain в error/omission/addition. Дальнейшее исследование необязательно для completion после inventory/coverage/QC checks.

Проверены exact24key roster, 6 resolved/18 deferred, unique stable IDs, пустые assigned_strongs и null strong_assignment для всех18 deferrals, 0 definite errors,0 correction proposals, source/target scalar/byte spans и physical output SHA/bytes. Author inspection не называется QC. Flutter/runtime tests N/A: изменены только новые research artifacts; независимая philological/mechanical проверка обязательна отдельно.

Machine deliverables: [`source_resolution.key_dispositions.v1.jsonl`](../../work/ukrainian_stage_7_20260801/session_group2_20261003_luke_john_research_01/source_resolution.key_dispositions.v1.jsonl), [`source_resolution.cases.v1.jsonl`](../../work/ukrainian_stage_7_20260801/session_group2_20261003_luke_john_research_01/source_resolution.cases.v1.jsonl), [`source_qualified_controls.v1.jsonl`](../../work/ukrainian_stage_7_20260801/session_group2_20261003_luke_john_research_01/source_qualified_controls.v1.jsonl), [`proven_correction_scopes.v1.json`](../../work/ukrainian_stage_7_20260801/session_group2_20261003_luke_john_research_01/proven_correction_scopes.v1.json).

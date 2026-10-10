# Группа008: source-resolution 2John, 3John, Jude — v2

Дата: 2026-10-10. Автор `codex-group008-letters-research-20261010-01`, фактическая роль `/root/letters_research`: исследователь и автор source-resolution, не corrector и не независимый QC.

Лично прочитаны все 52 выбранные полные сетки и 1871 метка: 2John — 491, 3John — 446, Jude — 934. Выполнен один bounded research cycle для каждого из 19 исторических loci / 44 stable keys; 15 дополнительных records отвечают на впервые предъявленные вопросы reviewer и собственные semantic probes. Старые passes, adjudication и initial QC не повторялись.

До полного чтения work проверены физические SHA256 и bytes 42 locks цепочек и 10 locks исходников. Original alternative inventory и TBESG закреплены отдельно. Точные сканы OH1988 1503–1505 лично визуально прочитаны; каждый case содержит input digests, exact source/target IDs, physical-line SHA и scalar/byte spans. Все вопросы из immutable списка reviewer имеют покрытие exact cases.

Новых Strong: 0. Исполненных researcher corrections: 0. Для семи существующих lexical keys предложено узкое разрешение: G2038 в 2John1.8 (три keys) и G1125 в двух writing occurrences 3John1.13 (четыре keys). Первый σοι в 3John1.13 остаётся недоказанным. Независимый reviewer должен отдельно оценить эти выводы.

Два исторических error loci 2John1.7 и 2John1.9 сохраняют error verdicts. Точные альтернативы εἰσῆλθόν/G1525 и παραβαίνων/G3845 доказаны, но их применение требует отдельно запечатанного source overlay и reciprocal grid. Изменить только номер Strong на неизменном греческом слове было бы неверно.

На скане 2John1.1 напечатано «поправді», тогда как frozen target содержит «поправці»; в 3John1.7 frozen target сливает «Ймення» и «Його» в scalar20:31 / bytes36:58. Печатные сведения не подменяют замороженные слова или их границы. В 2John1.9 второй native slot содержит nonselected τοῦ Χριστοῦ, а не αὐτοῦ: местоимение «Його» не получает G846 из отсутствующего occurrence.

Источники: [закреплённый TAGNT](https://github.com/STEPBible/STEPBible-Data/tree/b9dcc831a98e0fd6f3c7e122be9ff68377c310c0), [SBLGNT2John](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/2John.txt), [SBLGNT3John](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/3John.txt), [SBLGNTJude](https://github.com/Faithlife/SBLGNT/blob/c4d241a9c1c479a55b989ba35a4976c1d0b8052c/data/sblgntapp/text/Jude.txt), [OH1988 scan](https://commons.wikimedia.org/wiki/File:Ivan_Ohienko_Bible.djvu). Научные same-verse notes: [NET2John](https://bible.org/sites/bible.org/resources/download/netbible/ondemand/bybook/2jo.pdf), [NET3John](https://bible.org/sites/bible.org/resources/download/netbible/ondemand/bybook/3jo.pdf), [NETJude](https://bible.org/sites/bible.org/resources/download/netbible/ondemand/bybook/jud.pdf). TAGNT, TBESG и SBLGNT: CC BY4.0; NET использован для короткого paraphrase и ссылок, полные PDF не сохранялись.

Исследование завершено. Недоказанные атомы и spans рекомендуются как `deferred_strong_unassigned`; registered deferrals удовлетворяют completion и не требуют второго цикла. Отсутствие названия исторической греческой редакции само по себе не является missing proof. Идентичные lemma/Strong при том же occurrence/span могут давать узкое lexical доказательство; конкурирующие разные Strong требуют различающего доказательства.

## Exact cases


### group008:2John.1.1:historical-1:source-resolution-v1

- Scan1503 prints «поправді», while the frozen target t009 is «поправці», scalar46:54/bytes83:99. The exact native ἐν+ἀληθείᾳ expresses in-truth. This proves a transcription discrepancy, but not that both source atoms belong to the opaque frozen word.
- The frozen text is preserved. The clearly printed adverb and neighboring3John1.1 cannot silently replace this target occurrence.

Вывод: `printed_reading_proven_frozen_target_atom_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A target-text or subspan contract accounting for the exact frozen «поправці» is missing. A printed correction cannot be substituted for frozen bytes.

Exact keys: `original:gold7:original:a0da37678b07dd3e2ec8f37ece06257f`, `original:gold7:original:eb75ff6bc9d5f3afcf15f11fd79bdc78`, `target:gold7:target:d6938afa047da8dd6adc9dcbd30b2c3b`.

### group008:2John.1.3:historical-1:source-resolution-v1

- Exact o003ἡμῶν/P-1GP/G3165 is first-person. Printed and frozen «вами» are second-person. The locked line lists every witness withἡμῶν and only lexical G2257, without a textualὑμῶν occurrence.
- A recipient-oriented Ukrainian greeting can explain the translation, but does not prove an exact G3165→вами allocation or authorize G4771 from another occurrence.

Вывод: `unproved_person_pronoun_correspondence`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A same-slot second-person source occurrence or specifically justified person allocation is missing. Current NULL/addition labels do not establish a textual omission.

Exact keys: `original:gold7:original:cb038960bf5fb9267c8302f97f84966f`, `target:gold7:target:2fd50b959bdfab26e4b4e36c2a6ae77d`.

### group008:2John.1.7:historical-1:source-resolution-v1

- Exact selectedἐξῆλθον/ἐξέρχομαι/G1831 means went out. Printed and frozen «увійшло» means entered. Same-parent c06εἰσῆλθόν/G1525 is independently SBL RP; locked TBESG suppliesεἰσέρχομαι, enter.
- The narrow alternate correspondence is proven. The current reciprocal G1831 edge preserves its historical error verdict.

Вывод: `historical_error_preserved_exact_alternate_proven`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A sealed overlay admitting the exactεἰσῆλθόν ID and reciprocal edge is absent. Changing only the Strong on unchangedἐξῆλθον would not repair this occurrence.

Exact keys: `original:gold7:original:7bfc34f032a8ef9b27f1b06c9d6b3a17`, `target:gold7:target:fdef4183d4af3113ea47b415760765f6`.

### group008:2John.1.8:historical-1:source-resolution-v1

- Same-parent εἰργασάμεθα and εἰργάσασθε both have lemmaἐργάζομαι and G2038. The exact «працювали» means worked; «над» is its Ukrainian government in «над чим працювали».
- The frozen work component contains no separately linked first-person pronoun. Contextual implied person does not change the work lemma or G2038. Historical form uncertainty is retained as history; these three lexical labels have narrow proof for distinct QC.

Вывод: `invariant_local_lemma_Strong_component_narrow_proven`. Рекомендация: `narrow_lexical_resolution_recommended_distinct_QC`.

Недостающее доказательство: Distinct QC confirmation remains for these existing lexical labels. An exact Greek person/edition is not claimed and is not itself missing lexical Strong proof.

Exact keys: `original:gold7:original:347e1fb7bc18213e183c79027f57c650`, `target:gold7:target:2bbf05c7d02989f42fe8e42bd8fbf0c2`, `target:gold7:target:441366c57f60a00af3baa3ebf9ffca41`.

### group008:2John.1.9:historical-1:source-resolution-v1

- Nativeπροάγων/προάγω/G4254 means going ahead. «Робить переступ» narrowly supports same-parentπαραβαίνων/G3845, independently SBL RP. Locked TBESG supplies the lemmaπαραβαίνω, transgress.
- The three current G4254 component errors remain errors. A different number is not assigned to the unchanged source form.

Вывод: `historical_error_preserved_exact_alternate_proven`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: An admitted source overlay for exactπαραβαίνων plus all three reciprocal component rows is absent.

Exact keys: `original:gold7:original:78766b8422fe5c5616b49b104c5e6afc`, `target:gold7:target:70fa251c3ad96ec29e40f96c635baa4c`, `target:gold7:target:fc817e66b4e2d8f1bfbae8aa84f323ba`.

### group008:2John.1.9:historical-2:source-resolution-v1

- Printed italic «Його» is an anaphoric supplement after the second «науці». Exact nonselected nodes at orders20–21 areτοῦ+Χριστοῦ/G5547. There is noαὐτοῦ/G846 occurrence in this locked slot.
- SBL RP apparatus also recordsτοῦΧριστοῦ. Referential paraphrase of Christ by a pronoun does not prove a native G846 atom.

Вывод: `anaphoric_target_nonselected_christ_candidate_no_pronoun_atom_proof`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: An admitted secondΧριστοῦ occurrence plus justified allocation to soleЙого, or a genuine same-slot pronoun occurrence, is missing. The firstΧριστοῦ is a different occurrence.

Exact keys: `target:gold7:target:4f8c06e04c2ee45da38d6eeeae8a8451`.

### group008:2John.1.12:historical-1:source-resolution-v1

- γενέσθαι/G1096 and the exact same-parentἐλθεῖν/G2064 can both support «прибути». Arrival meaning does not uniquely identify the source lexeme.
- Exactἡμῶν/G3165 is first-person, while «ваша» is second-person. Same-parentὑμῶν/P-2GP/G5216 is explicitly SBL+WH+Treg and independently in SBL apparatus. That narrow alternate correspondence is proven.

Вывод: `arrival_lexeme_collision_and_proven_second_person_alternative`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A discriminator for the G1096/G2064 arrival atom is missing. The provenὑμῶν occurrence also lacks an admitted sealed source overlay and reciprocal target selection.

Exact keys: `original:gold7:original:0a246037437bd0e1d51ef21088c1c0b4`, `original:gold7:original:154420e3a71e1e3bc7224a8419cb87d3`, `target:gold7:target:1e3202cdfc5c6f98a8cb1360c3adccde`, `target:gold7:target:bdca89856e2cf006d85cee9a1edba935`.

### group008:2John.1.13:historical-1:source-resolution-v1

- Scan1503 prints closing Amen. Same-slot nonselected rawo010ἀμήν/lemmaἀμήν/G281 is TR+Byz and independently SBL RP apparatus. This is an exact native closing occurrence, not a neighboring liturgical transfer.

Вывод: `nonselected_closing_occurrence_narrow_proven`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: The exact native Amen is outside the selected full grid. A source-node overlay and reciprocal target admission are absent.

Exact keys: `target:gold7:target:6689961acd97a33846cf0f0a813a4535`.

### group008:3John.1.4:historical-1:source-resolution-v1

- Selectedτῇ/G3588 beforeἀληθείᾳ is WH+Treg+NA27; SBL apparatus records its absence in NA28+RP. Ukrainian «у правді» has no overt Greek article counterpart.
- Grammatical nonrendering is legitimate if the article is present. Ukrainian zero article cannot distinguish source presence from absence.

Вывод: `article_presence_unproved_no_target_Strong`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: An actual source-node disposition is missing; articleless Ukrainian syntax cannot prove source presence. No target lexical Strong edge is invented.

Exact keys: `original:gold7:original:07f9e56e021669da1d46a44026edbd87`.

### group008:3John.1.5:historical-1:source-resolution-v1

- SBL apparatus contrasts selectedτούτο/G3778 with RPεἰςτοὺς. The locked universe has a nonselected secondεἰς and same-parentτοὺς/G3588.
- The second printed «для» can repeat the first preposition in Ukrainian or realize the alternative secondεἰς. Both explanations remain legitimate.

Вывод: `repeat_preposition_atom_allocation_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: Unique allocation of the secondдля to a specific nativeεἰς is missing, as is proof that selectedτούτο was actually omitted. No article/demonstrative Strong is assigned toдля.

Exact keys: `original:gold7:original:9261078f61d207aba6ff990f13560bd4`, `target:gold7:target:f387d68fc880ab22018c2a6868b30ee8`.

### group008:3John.1.7:historical-1:source-resolution-v1

- Same-parentἐθνικῶν/G1482 andἐθνῶν/G1484 both denote Gentiles here. SBL RP apparatus records the alternate, and NET explicitly discusses their same-verse synonymy.
- «Поган» proves Gentile meaning, but not which of the two different source lemma/Strong atoms supplied it.

Вывод: `different_Strong_same_target_lexeme_collision`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A discriminator for the exact G1482/G1484 occurrence is missing. Dictionary synonymy does not select the atom.

Exact keys: `original:gold7:original:681ed2ff24b09b6417ce83feed496bd5`, `target:gold7:target:7a06700415f616f53bf21c9ee7423e6a`.

### group008:3John.1.8:historical-1:source-resolution-v1

- Selectedὑπολαμβάνειν/G5274 and same-parentἀπολαμβάνειν/G618 can both mean receiving or supporting visitors. SBL RP confirms the alternate; «приймати» has that broad receive sense.

Вывод: `receive_lexeme_collision`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: The exact G5274/G618 source atom is not uniquely identified by the broad receive meaning.

Exact keys: `original:gold7:original:46c0474fbc412725185b0c8dcdef574f`, `target:gold7:target:95164d0eaf279dac3bade875797ca4d0`.

### group008:3John.1.9:historical-1:source-resolution-v1

- Exactτι/G5100 is an indefinite object, something. SBL RP omits it, while «Я до Церкви писав був» has no overt indefinite object.
- This supports source-presence ambiguity, not a definite assertion that the source or translation accidentally omitted a word.

Вывод: `indefinite_object_presence_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A supported selected-source disposition or exact semantic allocation ofτι is missing. No other occurrence may fill the atom.

Exact keys: `original:gold7:original:cfe56e5a266e7635ce6faac73228296f`.

### group008:3John.1.11:historical-1:source-resolution-v1

- The second «а» is contrastive. A nonselected TR-onlyδὲ/G1161 occurs at this clause, but Ukrainian can independently supply the same antithesis.
- Article plus substantive-adjective/participle groups were inspected and preserved. No rule detaches every article from a nominal group.

Вывод: `contrast_target_source_presence_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: An exact realization of nonselectedδὲ cannot be distinguished from target-side contrast support. The native occurrence is not admitted to the selected grid.

Exact keys: `target:gold7:target:75f08d15070c532ccd228a01b59adb61`.

### group008:3John.1.12:historical-1:source-resolution-v1

- Selectedοἶδας is second-person singular; scan1504 explicitly has plural «ви знаєте». Exact same-parentοἴδατε/G6063 is plural and independently SBL RP apparatus.
- G6063 is out_of_classic_range with strong_classic=[] in the frozen occurrence. Locked TBESG identifies it as a form of G1492H/οἶδα. Knowledge meaning is proven, but no normalization or new classic assignment was performed.

Вывод: `person_alternate_proven_nonclassic_mapping_not_applied`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: The selected person mismatch needs an admittedοἴδατε overlay. A specific native-form/classic-identity normalization contract and distinct QC are absent.

Exact keys: `original:gold7:original:9852564a8dca30ea3f9b7215a9446fed`, `target:gold7:target:b64286420804810364c07e56da12f058`, `target:gold7:target:c23d1cce8cca7fb47881c082a63e1d9c`.

### group008:3John.1.13:historical-1:source-resolution-v1

- Both exact writing positionsγράψαι/γράφειν and their reversed form alternatives haveγράφω/G1125. Each «писати» expresses writing at its own scalar position. Aspect does not identify an edition, but does not remove this local lexical identity.
- The firstσοι has no overt first-clause target; only second-clause «до тебе» is printed. SBL RP firstγράφειν lacksσοι. Transferring the second pronoun or asserting certain translation omission is unsupported.

Вывод: `four_writing_lexical_keys_proven_first_pronoun_unresolved`. Рекомендация: `narrow_lexical_resolution_recommended_distinct_QC`.

Недостающее доказательство: Four G1125 lexical keys need distinct QC only. The firstσοι still lacks proof of source presence/nonrendering or unique span allocation.

Exact keys: `original:gold7:original:86d5241807ac39691e041e1cebeaee5d`, `original:gold7:original:cb7c87c4f8205851adf3625584317a56`, `original:gold7:original:e6b0b3ebbce7f150ef288a57ddc8984c`, `target:gold7:target:8a7227eca6795bc3013f01b7cc806cb2`, `target:gold7:target:b98b86a82a1f3619762d0ee188979b4c`.

### group008:Jude.1.12:historical-1:source-resolution-v1

- SBL RP omits selectedοἱ/G3588; articleless Ukrainian cannot establish source presence.
- Selectedπαραφερόμεναι/G3911 and same-parentπεριφερόμεναι/G4064 both describe wind-borne clouds as «носяться». This does not uniquely choose a carry compound.

Вывод: `article_presence_and_carry_lexeme_unresolved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A discriminator for the G3911/G4064 carry atom and an actual article-presence disposition are missing. Neighbor2Peter is not a transfer source.

Exact keys: `original:gold7:original:7d843852be9d982b0a8d9ec774dd82fa`, `original:gold7:original:d0f7ae5100536f15f2748fbe3cf9da89`, `target:gold7:target:3fafed33286a66716d2f03348ed77274`.

### group008:Jude.1.15:historical-1:source-resolution-v1

- Exactπᾶσανψυχὴν means every soul/person. Printed «всіх безбожних» instead has plural all plus ungodly. Same-parentπάντας/G3956+ἀσεβεῖς/G765 with rawτοὺς form the independently SBL-attested alternative.
- G3956 all is invariant, but selectedψυχὴν NULL and targetбезбожних addition do not implement that alternative construction. The later ungodly-sinners occurrence supplies no transfer vote.

Вывод: `nonselected_ungodly_clause_narrow_proven`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A closed admitted source-block scope for exactπάντας+τοὺς+ἀσεβεῖς and reciprocal target spans is missing. Current every-soul cannot be accepted as all-ungodly.

Exact keys: `original:gold7:original:44ef20a00fa0505447946d75638ea813`, `original:gold7:original:704e7aaa4d42085b15947e9005f27027`, `target:gold7:target:232662e4d9eef8482cfe38e789faf045`, `target:gold7:target:27817ec4cb228f660e9d57088560acfd`.

### group008:Jude.1.25:historical-1:source-resolution-v1

- Exact printed «премудрому» narrowly matches same-slot nonselectedσοφῷ/σοφός/G4680. SBL RP apparatus confirms the wise addition.
- Other printed doxology parts retain the longer critical reading; a historical edition label cannot automatically admit this node.

Вывод: `nonselected_wise_occurrence_narrow_proven`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: The exactσοφῷ node remains outside the selected grid. A source overlay and reciprocal target admission are missing.

Exact keys: `target:gold7:target:4dd5223dd7ad7372bd4d67709f086099`.

### group008:2John.1.2:printed-tense:source-resolution-v1

- Scan1503 has «пробуває», while frozen Stage6 has «пробував». Exactμένω/G3306 supplies abiding at this occurrence. A transcription tense difference does not itself change the lemma or prove a false Strong.

Вывод: `same_lemma_print_transcription_difference_preserved`. Рекомендация: `inspection_only_no_new_exclusion_claim`.

Недостающее доказательство: No text repair was made. Distinct QC can assess the lexical edge separately from printed tense; no new exclusion is claimed solely because of tense.

Exact keys: `original:gold7:original:808907c9b83462fcb3f775c8df3bc81e`, `target:gold7:target:2de7114cade2745e80737e370e2622dd`.

### group008:2John.1.7:copula-particle:source-resolution-v1

- Nativeἐστιν/G1510 is a copula. «То» in «Такий — то обманець» is also interpretable as a demonstrative/focus particle with zero overt verbal be. Clause predication survives, but isolated G1510→то is not uniquely proven.

Вывод: `copula_to_particle_atom_unproved`. Рекомендация: `deferred_strong_unassigned_if_independent_QC_confirms`.

Недостающее доказательство: Proof assigning being toто rather than zero copula plus focus particle is missing. No G3778 or NULL rewrite was invented.

Exact keys: `original:gold7:original:cedb281dc1b18dcddbcb747d2ebca220`, `target:gold7:target:31cc90e9e565e87d10085678ff25ccdf`.

### group008:3John.1.6:audience-dative:source-resolution-v1

- ἐνώπιον/G1799+ἐκκλησίας/G1577 means before the church; sole «Церкві» is dative audience ofсвідчили. Whole communication meaning is plausible. NET discusses this audience, but does not establish exact allocation of the before/presence atom to the inflected noun.

Вывод: `whole_audience_equivalence_atom_allocation_unproved`. Рекомендация: `deferred_strong_unassigned_if_independent_QC_confirms`.

Недостающее доказательство: Specific construction evidence forἐνώπιον through dativeЦеркві is missing. Whole-clause equivalence alone does not prove this atom.

Exact keys: `original:gold7:original:275930e2d696f886195c141e05dd7284`, `original:gold7:original:734566efab34c6c6c8f6191b78f55789`, `target:gold7:target:07fa2964df2210ce5d7e746e80257428`.

### group008:3John.1.7:fused-name:source-resolution-v1

- Exact frozen target Йме́нняЙого, scalar20:31 and bytes36:58, fuses name plus possessive across the page boundary. Scans1503/1504 read Ймення and Його as name plus pronoun. Native selectedὀνόματος/G3686 has noαὐτοῦ at this slot. NET discusses the unqualified Name with Greek article and several possible identity referents.

Вывод: `fused_name_possessive_atom_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A target atom/subspan contract separating the name lexeme and the unlinked possessive is missing. Whole-token G3686 allocation is not proven; no G846 from elsewhere.

Exact keys: `original:gold7:original:4cb253f4b95d99c21ae39858e43ddcbf`, `target:gold7:target:5dc3e656a521b63cb9572daa9ce3b3e4`.

### group008:3John.1.14:closing-amen:source-resolution-v1

- Scan1504 prints Amen after verse15, mapped to target1.14. The locked TAGNT universe has no closing Amen occurrence; SBL ends atὄνομα. NET2John notes some3John Amen witnesses but supplies no stable local native candidate.

Вывод: `printed_amen_no_native_candidate_identity`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: An actual closing native Amen occurrence with stable ID and source control is missing. Liturgical meaning alone does not assign G281.

Exact keys: `target:gold7:target:fe0346e01e6e1888b244940c5f525cd3`.

### group008:Jude.1.5:knowledge-form:source-resolution-v1

- Exactεἰδότας/εἴδω with rawG6063 is a knowledge participle; pairedὑμᾶς supplies plural person in this construction. «Знаєте» expresses know. TBESG form-ofG1492H is explicit mapping evidence, but strong_classic=[] remains frozen.

Вывод: `knowledge_lemma_proven_nonclassic_mapping_scope_unapplied`. Рекомендация: `deferred_strong_unassigned_if_classic_identity_required`.

Недостающее доказательство: Knowledge meaning is proven. Classic identity admission from rawG6063 requires a specific normalization contract and distinct QC; no new G1492 link was assigned.

Exact keys: `original:gold7:original:49a3da543132867aa72b12471525f0a4`, `original:gold7:original:ad5969a2085f592882f68c3a354b04fb`, `target:gold7:target:0dd2526bf11142bd636962d3bf9789e9`.

### group008:Jude.1.5:all-demonstrative:source-resolution-v1

- Printed «усе» is universal. Selectedπάντα/πᾶς/G3956 supplies all at this exact slot, while alternativeτοῦτο/G5124 is a demonstrative. The target directly supports the selected universal atom without an edition-name gate.

Вывод: `selected_universal_atom_narrow_proven`. Рекомендация: `inspection_only_existing_lexical_edge_supported`.

Недостающее доказательство: No lexical proof remains missing for this pair; retain the current edge subject to distinct reviewer acceptance.

Exact keys: `original:gold7:original:427265013b1fb9eb1853103d9ec046da`, `target:gold7:target:428baf86ef62e77dbd8a92ce23c64b10`.

### group008:Jude.1.8:particle-and-future:source-resolution-v1

- Nativeμέντοι is a contrastive/emphatic particle without an overt however in Ukrainian. «Буде» explicitly adds future predication; there is no future be occurrence in the selected Greek construction. Current unlinked addition does not pretend G3305→буде.

Вывод: `unlinked_particle_future_addition_inspected`. Рекомендация: `inspection_only_no_new_Strong_edge`.

Недостающее доказательство: Existing empty-link classifiers can record the nonrendered particle and target future addition. No source omission or G1510 assignment is asserted; independent QC decides classifier adequacy.

Exact keys: `original:gold7:original:5d437bb0a39278cc4530abc9b7f9d411`, `target:gold7:target:58cd2a4ce9960d0bc050eb69bc51d662`.

### group008:Jude.1.9:emphatic-sam:source-resolution-v1

- Printed «сам» emphasizes Michael. Locked GreekὁδὲΜιχαὴλὁἀρχάγγελος has noαὐτός in this slot. Current unlinked translation_addition represents the explicit Ukrainian emphasis without a fabricated source word.

Вывод: `unlinked_target_emphasis_supported`. Рекомендация: `inspection_only_current_NULL_addition_supported`.

Недостающее доказательство: No Strong assignment is needed to preserve this unlinked addition. Anotherαὐτός occurrence is not a candidate.

Exact keys: `target:gold7:target:d650148d26039c07c6c72e1d7bea1bc0`.

### group008:Jude.1.10:knowledge-form:source-resolution-v1

- Exactοἴδασιν/rawG6063 is plural knowledge matching the first «знають». Laterἐπίστανται/G1987 matches the distinct second «знають». The repeated Ukrainian words have separately identified occurrences.
- TBESG form-ofG1492H is cited as native mapping evidence; frozen strong_classic=[] is not rewritten.

Вывод: `knowledge_lemma_proven_nonclassic_mapping_scope_unapplied`. Рекомендация: `deferred_strong_unassigned_if_classic_identity_required`.

Недостающее доказательство: Classic Strong admission forG6063 requires a specific native-form normalization contract and QC. Know meaning is proven but is not a researcher assignment.

Exact keys: `original:gold7:original:aaf04a52119d2b2628c6d559cde1aa6c`, `target:gold7:target:64321aec87134fc920b9c911030798e6`.

### group008:Jude.1.15:convict-prefix:source-resolution-v1

- ἐλέγξαι/ἐλέγχω/G1651 and same-parent TRἐξἐλέγξαι/G1827 can both render «винуватити». The locked spelling is preserved. The compound is a different lemma/Strong; NET convict meaning does not uniquely choose the OH source atom.

Вывод: `convict_prefix_lexeme_collision`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A discriminator for same-slot G1651 versusG1827 is missing. No other occurrence supplies the selection.

Exact keys: `original:gold7:original:cfb53106d9e7dd38061649b1802bb45e`, `target:gold7:target:51a13cb88c05ac3230660f75d94ff55e`.

### group008:Jude.1.16:reflexive-possessive:source-resolution-v1

- Selectedἑαυτῶν/G1438 means own; same-parentαὐτῶν/G846 means their. Ukrainian «своїх» is reflexive but can also idiomatically render ordinary Greek possession when it refers to the clause subject. NET own-lusts discussion does not distinguish the variant.

Вывод: `reflexive_possessive_source_atom_collision`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: A unique G1438/G846 source-atom proof is missing; Ukrainian reflexive usage leaves the legitimate Greek nonreflexive alternative.

Exact keys: `original:gold7:original:0b619e5b7fd591446dbe6314f22b57be`, `target:gold7:target:4a642e0b1817c8d01ce00f91b8fcbf3c`.

### group008:Jude.1.18:temporal-preposition:source-resolution-v1

- ἐπ᾽/G1909 plus genitive and TRἐν/G1722 plus dative both denote the last time. «За останнього часу» favors temporalἐπί and genitive, but Ukrainian idiom does not invariantly identify a Greek preposition. SBL independently confirms both constructions.

Вывод: `temporal_preposition_atom_collision`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: Exclusive G1909/G1722 allocation toЗа is missing. The case parallel favors one construction without proving a unique Strong atom.

Exact keys: `original:gold7:original:d2fb439b25bc59bdf59851ac17ba50be`, `target:gold7:target:0c117b4c1cc2476303efdf9a5bf7968f`.

### group008:Jude.1.23:first-relative:source-resolution-v1

- Selected firstοὓς introduces a separate group beforeσῴζετε. Printedспасайте/виривайте continues the preceding wavering group without a new object pronoun. SBL WH and RP22–23 apparatus show competing group structures; current NULL does not establish accidental omission.

Вывод: `relative_presence_and_two_three_group_scope_unproved`. Рекомендация: `deferred_strong_unassigned`.

Недостающее доказательство: The exact firstοὓς block needs a source disposition using the preceding verse and stable occurrences. A new NULL is not fabricated to close the case.

Exact keys: `original:gold7:original:21262f3cf7c6cf4a22058f1fae8a4ff8`.

### group008:Jude.1.14:conjunction-function:source-resolution-v1

- Nativeκαὶτούτοις is additive in the prophesy clause; Ukrainianі beforeказав coordinates prophesy and speech. And remains lexical conjunction, while its function is redistributed through finite rendering of the participle. Position difference alone is not a definite content error.

Вывод: `conjunction_redistribution_inspected`. Рекомендация: `inspection_only_no_new_exclusion_claim`.

Недостающее доказательство: Distinct QC may assess clause-function redistribution. No new exclusion is claimed merely because of reorder.

Exact keys: `original:gold7:original:43c9963cdc68ea5026fd58c5d5fdb50c`, `target:gold7:target:9836ae50b94ef808d7ecdb94b06b0b79`.

## Роль, сохранность и проверки

Все source-resolution cases авторские; чтение старых QC является inspection, а не авторством. Вопросы reviewer прочитаны отдельно от его QC; они не выдаются за мои независимые вердикты. Packet содержит перечень всех 52 personally inspected verses. Source registry, единый Markdown issue registry, исходные QC, immutable selected layer, frozen text и grid не менялись.

Checklist: runtime, DB, dependencies, localization и approved RU/EN pairs не изменены. Flutter format/analyze/test/smoke N/A для evidence-only scope. UTF8, JSONL, exact stable keys и physical source locks проверены author validation. Parent navigation links и общий registry/inventory обновляет root. Commit и push не выполнялись.

## Metadata errata v2

Вступление v1 ошибочно указало 16 дополнительных records. Фактически их 15: всего 34 cases, из них 19 исторических и 15 дополнительных. Case JSONL, авторские выводы, исходники и все v1 файлы сохранены побайтно. V2 исправляет только это число; новый исследовательский цикл не проводился.

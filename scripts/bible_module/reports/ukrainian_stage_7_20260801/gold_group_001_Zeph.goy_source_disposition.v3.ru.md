# Zeph.2.14: גוי и «польова́» — ограниченное авторское исследование v3

Дата: 2026-10-03. Автор: `subagent:/root/nah_zeph_research`, исследователь, **не independent QC**. ID: `gold7:philology:group001:Zeph2.14:goy:authored:v3:20261003`.

## Конкретное заключение

**Текущая одиночная reciprocal пара o011 → t008 не получила достаточного филологического доказательства для acceptance. Однако рассмотренные данные не доказывают definite gold error и не дают основания автоматически заменить пару на NULL/addition.** Рекомендация автора — сохранить frozen answers неизменными и оставить эту пару отдельным `philological_uncertainty`. Это новый узкий остаток по уже согласованной паре, а не пересмотр других исследованных locus gaps в v2.

Реально проверены: выбранная Hebrew occurrence, точная украинская фраза и её ударение, первичные scholarly interpretations collective/species, альтернативные readings «earth/valley», историческое предложение Eitan о неизменённом גוי и прямое фонологическое возражение Albright. Ни «нет доказанной другой edition», ни одно словарное значение сами по себе не используются как доказательство ошибки. Full-clause idiomatic equivalence возможна, но ниже не выдается за доказанную atom-level связь.

## Неизменный source и точные spans

Выбранный источник — pinned TAHOT primary MT. Фраза: `כָּל־חַיְתוֹ־ג֔וֹי`, локаторы `Zep.2.14#04=L`–`#06=L`. o009 — construct `חַיְתוֹ`, H2416C/classic H2416, HNcfsc; o011 — `ג֔וֹי`, H1471A/classic H1471, HNcmsa. TAHOT не предъявляет alternate token на o011. No new Strong, no replacement Hebrew occurrence.

Frozen OH1988 здесь **«усяка польова́ звіри́на»**, не «уся». Скан leaf1165, печатная1161, левая колонка2.14 визуально просмотрен. Exact text slice scalar[34:57), UTF8[61:105). Accent в `звіри́на` стоит на **и**. Нельзя незаметно заменить слово на `звірина́`.

| Индекс | Exact ID | Значение / span |
|---|---|---|
| o007 | `tahot:8646f6a65b83af67f5c21418364c61318a8413c167f022f76ae717f72c68c7a0:g01:a01` | כָּל / H3605 |
| o009 | `tahot:700b82dc2aa10939ac609e2984b05e22367106177304e87fccd630b4ee8a6f0b:g01:a01` | חַיְתוֹ / H2416C |
| o011 | `tahot:c8d785c891caffd13f289bfec768b181c847e0b1f2c0b6ad7da995c849371618:g01:a01` | ג֔וֹי / H1471A |
| t007 | `uk7:HLW:007:34:39` | усяка; scalar[34:39), UTF8[61:71) |
| t008 | `uk7:HLW:008:40:48` | польова́; scalar[40:48), UTF8[72:88) |
| t009 | `uk7:HLW:009:49:57` | звіри́на; scalar[49:57), UTF8[89:105) |

Main source decision: `gold7:original:10fc92cfed6f96220c8e399e5cae90df`. Main target accounting: `gold7:target:0f7a3987f7a982ea98a91541df10fa80`. Frozen relation: source `one_to_one`, target_status `aligned`, one reciprocal pair. Rationale asserts functional rendering of nation as adjective «польова́». Exact records, neighbours, offsets and unchanged digests are sealed separately in `zeph_2_14_goy_source_evidence.v3.json` and manifest.

## Что первичные источники действительно устанавливают

1. **BDB exact entry גוי §2** places Zeph2.14 under a figurative animal-species use, alongside swarm usage elsewhere. This supports a nonhuman collective interpretation of the **actual** גוי, rather than forcing its usual political sense. It does not identify a field/habitat adjective as the contribution of this noun. Read BDB section of the hosted primary dictionary text; unrelated modern topical material on that page is not used. [BDB](https://biblehub.com/hebrew/1471.htm).

2. **Keil–Delitzsch, exact2.14 commentary** interprets the phrase as animal crowds/mass and takes the genitive as apposition. The account supports an animal collective, with wildness supplied by the surrounding scene. It is evidence against treating political nation as the only possible sense; it is not evidence for the lexical equation גוי = поле. [KD](https://biblehub.com/commentaries/kad/zephaniah/2.htm).

3. **S.R.Driver1906, printed128–129 / PDF146–147**, visually inspected: the RV margin's singular nation and species interpretation are problematic in his judgement. He offers plural nations, following Greek earth, or Halevy's different Hebrew valley reading. His native contextual interpretation includes wild creatures in devastated Nineveh. These alternatives explicitly show why habitat rendering can be reasonable at the phrase level while a singular pinned noun-to-adjective edge still needs proof. [Primary scan](https://biblicalstudies.org.uk/pdf/e-books/driver_s-r/minor-prophets-2_century-bible_driver.pdf).

4. **Clark/Hatton1989, UBS Handbook, exact2.14**, official TIPs reproduction: a field rendering follows the Aramaic Targum, whereas unchanged MT can be interpreted as animal flocks or species. The authors recommend the species interpretation as contextual translation. This is primary translation scholarship, not evidence that every field adjective directly represents H1471. [Official handbook reproduction](https://tips.translation.bible/story/translation-commentary-on-zephaniah-214/).

5. **Eitan1924 p32 proposal, known here through Albright's contemporary direct review**: Albright1925 JPOSV printed158–159 / PDF197–198, visually inspected, reports proposed Hebrew גוי meaning wide valley, associated with Arabic *gaww*. He objects that the expected Hebrew phonological result is *gayy*, already represented by the normal valley word. This is a substantive scholarly challenge, not merely edition uncertainty. The book itself was sought in HathiTrust full-view catalogue; the viewer returned403 and the linked IA metadata was empty. Therefore this report does **not** claim direct inspection of Eitan p32, nor complete refutation of every possible field/homonym account. [Albright's primary review](https://museum.birzeit.edu/sites/default/files/publications/JPOSV.pdf), [actual book catalogue](https://catalog.hathitrust.org/Record/001641717).

6. **СУМ11, volumeIII p484, licensed dictionary reproduction**, differentiates `звіри́на` (an individual wild animal; also animal generally) and final-stressed `звірина́` (collective wild animals). The site explicitly credits the Institute of Linguistics for permission. Thus the intuitive rescue “OH already uses a collective noun and that directly absorbs גוי” cannot simply be asserted for this exact stressed surface. Distributive `усяка` still supplies a universal animal range; stress does not prove that no phrase-level interpretation is possible. [Primary dictionary entry as licensed reproduction](https://slovnyk.ua/index.php?swrd=%D0%B7%D0%B2%D1%96%D1%80%D0%B8%D0%BD%D0%B0).

The local cached primary MT controls and Greek2.14 were already inspected in authored v2. Greek `τῆς γῆς` supplies earth rather than nation; the Targum field tradition and scholarly valley readings are evidence of competing interpretations/readings of this locus, not a newly attested Hebrew H1471 field occurrence. No borrowed occurrence from another verse is introduced.

## Accounting alternatives and why neither is authorized as a correction here

**A. Current atom:** o007↔t007 and o009↔t009 are straightforward lexical correspondences. The residual o011↔t008 fits positional allocation but presently lacks a positively demonstrated field sense or an independent rule locating the collective/species contribution specifically in «польова́». Polysemy is real; this particular allocation remains unproved.

**B. Phrase hyperedge:** the contract's multi-token/m:n policy can in principle allow o007,o009,o011 ↔ t007,t008,t009 (all animal species / every wild animal). Another possible distribution is o007,o011 ↔ t007 and o009 ↔ t008,t009. The first is semantically plausible under species reading; the second tries to separate universal range from wild animal description. Neither establishes that these exact OH words conventionally and completely express every source component, rather than losing or adding habitat/collectivity information. Merely grouping all tokens would conceal the unresolved question. These are **research hypotheses, not accepted replacements**; no group IDs or new Strong assignments are manufactured.

**C. NULL/addition:** if future independent philological decision establishes that the selected MT nation/animal-collective contribution is actually unrendered and field adjective has no aligned source contribution, the exact narrow accounting would be o011=`original_omitted`, target_token_ids=[], null reason `source_text_not_rendered`; t008 would be a target addition with linked_original_token_ids=[] and the target-added-expression status/reason permitted by the existing contract. Existing o007↔t007, o009↔t009, o008/o010 maqaf omissions remain. This is **not a recommendation to apply those values now**: contested lexical field account and viable phrase distribution mean nonexpression is not positively established. A NULL merely because the isolated equation is unproved would overstate the evidence.

## Precise remaining evidence gap

Required for acceptance of the current atom is a source-qualified argument for this exact singular גוי's habitat/field contribution, addressing the reported phonological objection and locating it in exact t008. Required for a group replacement is an independently checked explanation of which parts of the exact phrase render the collective/species contribution and which, if any, are actually absent or added. Required for corrective NULL/addition is positive exclusion of those live phrase/lexical accounts, rather than absence of a historical edition name.

The author has examined accessible primary evidence and makes the bounded conclusion now. No paid expert, edition label, invented occurrence or lowered QC gate is requested. Historical dependence of Огієнко on Eitan, Targum, LXX or another translation remains unknown and is not an acceptance gate. Independent QC retains responsibility for the verdict and correction eligibility.

## Preservation and provenance

Only the author's new ignored work directory was written. Frozen review answers, original universe, target inventory, selected source, stages3–7, mapping/folds, runtime, DB, NT and commits were not changed. Authored v2 and root combined v2 were preserved by digest. This note is not a QC manifest and does not set accepted-book status. All downloaded scholarly/dictionary material is a read-only research control, not an adopted redistributable corpus or dependency; rights information is recorded with source evidence.

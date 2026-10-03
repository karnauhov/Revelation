# OH1988 7.4 — собственное филологическое заключение по пяти loci, v1

Дата: 2026-10-03. ID: `gold7:philology:group001:opinion:v1:20261003`.
Автор: текущая сессия Codex; роль — source research, **не independent content QC**.
[Задание](gold_group_001_philological_assignment.v1.ru.md),
[SHA-locked manifest](gold_group_001_philological_opinion.v1.manifest.json),
[HANDOFF](HANDOFF.ru.md). Это первое заключение; supersedes отсутствует.
Исследовательские checkpoint v1 и blocking QC сохранены без перезаписи.

## Вывод и рекомендуемое решение

Ни в одном из пяти clauses не доказана связь спорного украинского слова с
нынешней selected MT леммой. Текущая source tokenization соответствует pinned
TAHOT; повреждения frozen OH1988 в просмотренных пяти сканах не обнаружены.
Совпадение с вариантной традицией объясняет расхождения, но не превращает
ретроверсию в засвидетельствованный Hebrew token данного стиха.

Рекомендую **сохранить существующие MT NULL/function/addition решения как
кандидаты на отдельную QC-проверку**. Здесь addition означает отсутствие
selected-source counterpart; это не утверждение, что Огиенко придумал слово,
и не отрицание вариантного оригинала. Не назначать ему Strong другой леммы
без принятого original layer. Для такой оценки не нужно точное историческое
название издания. При выборе alternate source проверять весь затронутый clause.

| Locus | Что установлено | Рекомендация относительно frozen selected MT | Что остаётся для alternate layer |
| --- | --- | --- | --- |
| Nah.1.8 | place/her не равно «між Його заколотниками»; Greek имеет восстающих | o007–o008 NULL; t008 function; t009–t010 без selected-source link | конкретный adversaries token и possessive/referent accounting |
| Zeph.2.14 | desolation не равно raven; Greek raven засвидетельствован | o026 NULL, t027 selected-MT addition | Hebrew raven occurrence; H6158 — lexical candidate |
| Zeph.3.17 | silence не равно renew; Greek и OH имеют разные объекты | o014 NULL, t014 selected-MT addition; love/his links сохраняются | renew occurrence и полный verb/preposition/object/suffix разбор |
| Zech.11.7 | therefore/afflicted не равно merchant clause; Greek не буквально «торговцы отары» | o008–o010 NULL; t008/t010 addition, t009 function; flock link сохраняется | alternative segmentation и merchant occurrence; H3669 lexical candidate |
| Zech.14.6 | precious не равно cold; qere/ketiv имеют classic H7087 | o011 NULL, t011 selected-MT addition; frost link сохраняется | cold occurrence; H7135 доказан для конкретной conjecture; проверить отрицание |

Всего 16 исходных blockers. Новых accepted книг **0**, gold **36/66**.
Таблица — исследовательская рекомендация, не изменение QC verdict или gold rows.

## Nah.1.8 — пять critical stable decisions

Scope и полные IDs: [Nah manifest v1](gold_group_001_Nah.source_resolution.v1.manifest.json).
OH1988: «між Його заколо́тниками». Selected `מְקוֹמָהּ` содержит place/H4725
и 3fs suffix; это место с принадлежностью женскому референту, а не plural
participle «восстающие». Нормализация или другая огласовка того же place noun
не даёт adversaries lemma. Разница лексическая, не только грамматическая.

[Greek Rahlfs–Hanhart 2006, 1:8](https://www.die-bibel.de/en/bible/LXX/NAM.1)
имеет `τοὺς ἐπεγειρομένους`; это свидетельство значения восстающих в Greek.
В этой короткой phrase нет отдельного possessive `αὐτοῦ`; оно стоит при
следующих enemies. [Аппарат NET](https://classic.net.bible.org/passage.php?passage=nah+1%3A8-10)
обсуждает несколько Hebrew retroversions. Поэтому ни точную форму, ни suffix
для OH «Його» нельзя выбрать голосованием переводов. Возможный H6965
относится к гипотезе о קום, а не к selected H4725.

[Qumran-Digital 4Q169, версия 2023-05-17](https://lexicon.qumran-digital.org/transcriptions/4Q169/2023-05-17/index.html)
не содержит locus 1:8 в опубликованной transcription. Указание аппарата на
4QpNah не принято как проверенное occurrence. Это ограничение доступного
свидетельства, не заявление о просмотре всех изображений рукописи.

Рекомендации: o007/place и o008/her оставить original_omitted; t008/між —
function_token; t010/заколотниками — translation_addition относительно MT.
Для t009/Його сохранить отсутствие link как консервативный кандидат: source
o008/3fs не является его референтом. Уже agreed o011/3ms при enemies не
переносить автоматически через границу noun phrase. Если проверяется перенос
possessive или alternate participle, расширить scope до o007–o011/t008–t012;
это условная проверка, а не доказанная ошибка agreed o011.

Exact scan leaf1156/printed1152 и отсутствие locus-specific сноски согласуются
с frozen input. Коррекция текста не требуется. Остаток: original occurrence
для adversaries и положительное доказательство antecedent/link «Його».

**Nah проверена, но не принята; счётчик остаётся 36/66.**

## Zeph.2.14 — два high stable decisions

Scope/IDs: [Zeph manifest v1](gold_group_001_Zeph.source_resolution.v1.manifest.json).
Selected `חֹרֶב` H2721B — desolation; OH «воро́на» на пороге — название птицы,
а не контекстуальная форма этого abstract noun. Parser defect не найден.

[Greek 2:14](https://www.die-bibel.de/en/bible/LXX/ZEP.2) содержит `κόρακες`
при воротах. [NET textual note](https://classic.net.bible.org/verse.php?book=Zep&chapter=2&verse=14)
указывает Hebrew emendation `עֹרֵב` по versional tradition. Разница plural
Greek/singular Ukrainian сама по себе не меняет raven lemma; замена
desolation/raven меняет лемму и Strong. Нельзя назначить H2721 птице или G-number
в Hebrew OT только потому, что Greek значение установлено.

Рекомендую сохранить o026 NULL, t027 translation_addition относительно selected
MT; это точное accounting текстового расхождения. Candidate `עֹרֵב`/H6158
филологически объясняет OH, но occurrence данного Hebrew token в принятом
alternate original source ещё не установлен. Если он принят, нужны новый
stable token ID и reciprocal raven link; ближайшие threshold/gate links
проверять по исходным границам, не заменять номера по позиции.

Exact scan leaf1165/printed1161 подтверждает «ворона». Frozen corruption нет.
Остаток для overlay: source-qualified occurrence raven; для существующего
MT accounting — отдельный QC вердикт по двум stable IDs.

## Zeph.3.17 — два high решения и управление clause

Selected `יַחֲרִישׁ`/H2790B — silence, Hiphil; OH «обно́вить любов Свою»
обозначает renew с прямым объектом love. Из gloss «silent» нельзя получить
renew через стилистическую или грамматическую нормализацию.

[Greek Rahlfs–Hanhart 2006](https://www.die-bibel.de/en/bible/LXX/ZEP.3)
содержит `καινιεῖ σε ἐν τῇ ἀγαπήσει αὐτοῦ`: объект renew — `σε`, адресат,
а love находится в prepositional phrase. Эта точная edition form записана
явно; формы «любви» в других Greek displays не подменяют её автоматически.
[NET note](https://classic.net.bible.org/passage.php?passage=Zep+3%3A17)
предлагает יְחַדֵּשׁ с подразумеваемым объектом «ты»; обсуждает также causative
понимание MT. Ни одно из них само по себе не доказывает OH объект love.

Мой вывод: H2318/חדש — допустимый lexical candidate для renew, но положительный
link требует либо самостоятельного original reading, либо доказательства
переоформления управления. Заменить только o014 и объявить остальной clause
буквальным нельзя. При неизменном MT нынешние love/H0160 → t015/любов и
3ms suffix → t016/Свою выражают ту же лексему и того же обладателя; украинская
рефлексивная форма определяется субъектом Господь. Preposition o015/ב не
имеет самостоятельного украинского preposition; его existing function NULL
согласуется с переоформлением clause.

Рекомендую сохранить существующие o014 NULL/t014 addition и уже принятые
love/suffix accounting. Условная revalidation при alternate source:
o014–o017/t014–t016, с явным учётом отсутствующего Greek «ты», если Greek
используется как диагностический witness. Exact scan leaf1166/printed1162
подтверждает renew **любов**, не «тебе»; input не исправлять под версии.

**Zeph проверена, но не принята; счётчик остаётся 36/66.**

## Zech.11.7 — пять high/critical решений, word division

Scope/IDs: [Zech manifest v1](gold_group_001_Zech.source_resolution.v1.manifest.json).
Selected `לָכֵן עֲנִיֵּי הַצֹּאן`: therefore/afflicted/flock. OH имеет
«тим, хто торгує отарою». TAHOT делит לכן на морфемы ל + כן; это не
доказательство самостоятельного dative recipient у fossilized therefore.
Поэтому o008/ל нельзя привязать к «тим» лишь из-за похожей грамматической роли.

[Greek 11:7, издатель Rahlfs–Hanhart](https://www.die-bibel.de/en/bible/LXX/ZEC.11)
читает `εἰς τὴν Χαναανῖτιν`, без отдельного flock token в этой phrase.
Это не готовое пословное свидетельство «торговцам отары». [NET apparatus](https://classic.net.bible.org/passage.php?passage=Zec+11%3A7)
описывает alternative Hebrew word division. [Micheli 2014, printed113](https://asset.library.wisc.edu/1711.dl/SLJSCCINPKDRH9B/R/file-2bf6c.pdf)
объясняет Greek через Canaanite/merchant, а Peshitta — через multitude of flock
при MT-like Vorlage. Эти чтения нельзя считать двумя голосами за merchant.

[Dunham 2018, pp14–15, notes53–54](https://dbts.edu/wp-content/uploads/2025/10/Zechariah-11-and-the-Eschatological-Shepherds-Dunham.pdf)
защищает asseverative MT и отдельно отмечает Greek omission flock. Прочитан
релевантный извлечённый текст, а не весь PDF; скачивание дало HTTP403, screenshot
не получен. Его вторичные ссылки на Qumran не выдаются здесь за просмотренные
рукописи. Конкурирующий scholarly разбор показывает, почему merchant нельзя
объявить единственно засвидетельствованным Hebrew reading.

Лексическая возможность merchant подтверждена дополнительно **в утверждённом
pinned TAHOT dictionary mapping**: `Zec.14.21#18=L` содержит
`H3669B=כְּנַעֲנִי=merchant`, classic H3669. Это доказательство леммы/номера,
не перенос occurrence из 14:21 в 11:7. Украинский finite «торгує» здесь
входит в аналитическое relative выражение «те, кто торгует»: он не обязывает
выбрать другой Hebrew verb Strong вроде H5503. При alternate merchant reading
проверять весь recipient/relative group, а не одно слово «торгує».

Рекомендую сохранить o008 function NULL, o009/therefore и o010/afflicted NULL;
t008/тим и t010/торгує — selected-MT additions, t009/хто — function,
o012/flock → t011/отарою — сохраняемый lexical link. Условная область нового
source reading: o008–o012/t008–t011. Exact scan leaf1177/printed1173 подтверждает
merchant clause; stage-6 repair не требуется. Остаток: original occurrence и
word division alternate merchant, либо отдельное принятие текущего MT accounting.

## Zech.14.6 — два high решения, cold и frost отдельно

Selected `יְקָרוֹת`/H3368 — precious/splendid, feminine plural; OH «холод».
Qere `קִפָּאוֹן` noun и ketiv `יִקְפְּאוּן` verb/conjugational ending
в pinned TAHOT явно разведены; обе lexical analyses normalize to classic H7087.
Это **Strong-equivalent grammar variation**, а не право заменить precious
на cold или объявить noun/verb одной точной формой.

[Greek 14:6](https://www.die-bibel.de/en/bible/LXX/ZEC.14) имеет `ψῦχος`
и `πάγος`. [NET apparatus](https://classic.net.bible.org/passage.php?passage=Zec+14%3A6)
обсуждает conjectural cold/ice reading. Новое уточнение:
[BDB, entry H7135 на BLB](https://www.blueletterbible.org/lexicon/h7135/kjv/wlc/0-1/)
прямо относит conjecture `וְקָרוֹת` в Zech.14.6 к noun קָרָה/cold.
Approved TAHOT `Nam.3.17#09=L` независимо фиксирует dictionary mapping
`H7135=קָרָה=cold`. Значит **H7135 обоснован как lexical candidate именно
для plural קָרוֹת conjecture**. Это новый результат; он не является назначением
H7135 frozen o011. Другую reconstruction `וְקָרוּת` нельзя молча объявить
тем же exact token. H7119/adjective и H7120/noun не выбраны по общему gloss.

Дополнительная span проблема: Greek имеет одну construction `οὐκ ἔσται`
перед перечислением; OH явно ограничивает отрицание light и добавляет
положительное «і буде холод». Само присутствие Greek cold не доказывает
совпадения scope отрицания. Это основание **условно расширить** revalidation
при выборе alternate layer до o007–o014/t006–t013 (negative/copula/light,
conjunction/cold/frost), а не только o011–o014/t011–t013. Уже accepted rows
не объявляются ошибками: selected qere frost → «замерзання» сохраняется.

Рекомендую сохранить H3368 source NULL и t011/холод selected-MT addition.
Qere H7087 → t013/замерзання и conjunction → t012/та остаются. Exact scan
leaf1180/printed1176 подтверждает positive cold clause; сноска страницы
не объясняет 14:6. Остаток для overlay: licensed original occurrence cold,
word/morpheme boundaries и operator/span scope. Точное историческое название
edition не требуется как самостоятельное условие.

**Zech проверена, но не принята; счётчик остаётся 36/66.**

## Классификация и дальнейшая операция

- Parsing: доказанного дефекта текущего TAHOT parser нет. Zech.11.7 alternate
  word division относится к source selection, а не к исправлению по позиции.
- Lexical readings: все пять loci; новые candidate Strong не назначены.
- Grammar-only: Zeph.2.14 number при raven; Zeph.3.17 reflexive possessive;
  Zech.14.6 qere/ketiv H7087. Они не закрывают lexical/token вопросы.
- Link/null/group: все 16 blockers; особо Nah possessive, Zeph renew object,
  Zech merchant relative group и cold negative scope.
- Frozen input damage: не найдено в пяти exact scans; stage-6 text/comment
  и mapping этапа 5 неизменны.

Собственное исследование выполнено, а не оставлено владельцу как просьба найти
эксперта. Для дальнейшей работы сохранены конкретные NULL-рекомендации и
проверяемые alternate hypotheses. Перед продолжением QC надо установить
происхождение его исполнителя относительно pass1/pass2/adjudicator/corrector
и reviewed decisions. Внешняя платная экспертиза не обязательна: фактически
отдельный проверяющий контекст может быть другой сессией Codex, если она
самостоятельно проверяет источники и не переименовывает текущего автора.
Текущая сессия, уже изучившая и сформулировавшая рекомендации, не объявляет
своё заключение независимым подтверждением этих же рекомендаций.

Коррекция требует sealed definite-error scope; нынешние QC имеют uncertain,
error=0 и не дают correction proposals. Поэтому source overlays/corrections
не применены. Оригинальные reviewer answers и book semantics не регенерировались.
Следующая группа не запускалась. Нужен следующий фактический QC/source-choice
шаг по этому пакету, а не неизвестное владельцу стороннее заключение.

## Источники, права и воспроизводимость

Licensed original anchors: pinned TAHOT CC BY4.0; OSHB WLC text Public Domain,
annotations CC BY4.0; UXLC Hebrew control с разрешением просмотра/копирования.
Exact OH1988 scan — ранее принятый CC BY-SA4.0 control. Авторские pp232–234
(1963) объясняют общий метод перевода, не доказывают отдельные readings.

Greek Rahlfs–Hanhart ©2006 DBG, NET notes, Biblesoft electronic BDB и scholarly
PDFs используются read-only для bounded исследования; новые corpus/Strong
annotations из них в original universe не импортированы. Micheli PDF и PNG
остаются в ignored work с SHA-locks исходного checkpoint. Dunham binary не
получен, digest скачанного файла не выдуман. Парафразы источников ограничены;
цитаты короткие, выводы текущего автора отмечены как рекомендации.

SHA всех используемых frozen packets, scans, источников и v1 manifests,
точный список 16 stable IDs, расширенные conditional scopes и digest этого
заключения фиксирует [manifest](gold_group_001_philological_opinion.v1.manifest.json).
Executed checks и N/A — в [validation log](validation_log.md).

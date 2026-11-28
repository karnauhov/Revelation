# Библиография исходной методики исследования Откровения

В апреле 2026 года проект закрепил семь приоритетов и подборку конкретных трудов для каждого этапа исследования. Сохранены все указатели из разделов «Каталог источников» и «Методология по этапам» исходной русской редакции. Это снимок библиографии на 7 апреля. Действующие издания, доступность, альтернативные адреса, ограничения на использование и решения о применимости учитываются в [рабочем каталоге](revelation-study-sources.md).

Исходный файл на компьютере владельца находится в `%USERPROFILE%/Downloads/Revelation/revelation-study-methodology.ru.md`. Его текст сверен построчно с [редакцией bb73366b](https://github.com/karnauhov/Revelation/blob/bb73366b6fbb4aa222578ca7ae215b0001e723c8/docs/ru/studies/revelation-study-methodology.ru.md). [Английская редакция](https://github.com/karnauhov/Revelation/blob/bb73366b6fbb4aa222578ca7ae215b0001e723c8/docs/en/studies/revelation-study-methodology.en.md)

## Поиск по сохранённым текстам

[Опись локальной библиотеки](revelation-study-library.tsv) содержит ссылки на конкретные PDF, контрольные суммы и количество страниц. В первой описи 40 полных файлов и 5735 страниц. В неё входят 22 главы построчного комментария Полиена, его перевод, план и методологические работы, английская, русская и испанская Библии, «Деяния апостолов», пособие Субботней школы и перевод двух греческих версий Даниила. Отдельно доступны тексты библейских модулей Revelation и аппарат рукописей. Доступ по ссылке, наличие полного экземпляра и сверка конкретной страницы отмечаются раздельно в досье стиха.

Из корня репозитория можно найти нужную страницу в оригинале. Индекс сохраняется в исключённой из Git папке `.build/revelation-study`. Для сборки используется установленный Poppler (`pdftotext`) и Python 3.11 или новее с SQLite FTS5.

```powershell
python .agents/skills/revelation-study/scripts/search_pages.py build
python .agents/skills/revelation-study/scripts/search_pages.py search "testimony of Jesus"
```

Команда читает имеющиеся экземпляры из `~/Downloads/Revelation/revelation-commentary-facebook/`, соседние `Revelation-Outline.pdf` и `Revelation-Translation.pdf` и PDF из `.build/revelation-study/research-pdfs/`. Для другой библиотеки Полиена передай `build --library ПУТЬ`, для дополнительных легально полученных файлов - `build --extra ФАЙЛ ...`. При восстановлении сверь имя, SHA-256 и число страниц с описью. Для каждой ссылки используй условия конкретного издания. Поиск выводит имя PDF, номер страницы и контекст фразы. Повтори его с вариантами переводов и тематическими синонимами, затем прочитай страницу и соседние рассуждения. Скан без распознанного текста исследуй по изображению страниц.

## 1. Классические переводы

| Язык | База | Ссылки |
| --- | --- | --- |
| Английский | `KJV` | [DBS PDF](https://bibles.dbs.org/ENGKJV/pdf/ENGKJV.pdf), [Bible.com Rev 1](https://www.bible.com/bible/1/REV.1.KJV) |
| Русский | `Синодальный перевод` | [DBS PDF](https://bibles.dbs.org/RUSS76/pdf/RUSS76.pdf), [Bible.com Rev 1](https://www.bible.com/bible/400/REV.1.SYNOD) |
| Испанский | `Reina-Valera 1909` | [DBS PDF](https://bibles.dbs.org/SPARV09/pdf/SPARV09.pdf), [Bible.com Rev 1](https://www.bible.com/es/bible/1718/REV.1.RVR09) |
| Испанский, доп. сверка | `Reina-Valera 1960` | [Bible.com Rev 1](https://www.bible.com/bible/149/REV.1.RVR1960) |
| Украинский | `Іван Огієнко 1962 (UBIO)` | [Bible.com Rev 1](https://www.bible.com/bible/186/REV.1.UBIO), [страница версии](https://www.bible.com/sq/audio-bible-app-versions/186-ubio-ukrainian-ohienko-1962) |

Правило: перевод не заменяет греческий текст, а служит слоем проверки и сопоставления.

## 2. Jon Paulien

Полные индексы:

- [The Battle of Armageddon sitemap](https://www.thebattleofarmageddon.com/wp-sitemap.xml)
- [Revelation-Armageddon sitemap](https://revelation-armageddon.com/wp-sitemap.xml)

Главные хабы:

- [Facebook Commentary on Revelation](https://www.thebattleofarmageddon.com/revelation-commentary-facebook/)
- [Twitter Commentary on Revelation](https://www.thebattleofarmageddon.com/revelation-tweets/)
- [Armageddon Articles](https://www.thebattleofarmageddon.com/articles-on-armageddon/)
- [Blog](https://revelation-armageddon.com/)
- [YouTube channel](https://www.youtube.com/@DrJonPaulien)
- [Lecture playlist](https://www.youtube.com/playlist?list=PL1MTivDDDnyuStBHIT7KWA3FUrxYSUmL5)
- [Library](https://www.thebattleofarmageddon.com/library/)

Ключевые тексты:

- [Revelation Translation](https://www.thebattleofarmageddon.com/wp-content/uploads/2022/09/Revelation-Translation.pdf)
- [Revelation Outline](https://www.thebattleofarmageddon.com/wp-content/uploads/2022/09/Revelation-Outline.pdf)
- [A Short Review of Method for the Study of Revelation](https://www.thebattleofarmageddon.com/wp-content/uploads/2024/09/A-Short-Review-of-Method-for-the-Study-of-Revelation.pdf)
- [Patterns of Prophecy](https://www.thebattleofarmageddon.com/wp-content/uploads/2022/09/Patterns-of-Prophecy.pdf)
- [History of Interpretation of Revelation (1999)](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/05/History-of-Interpretation-of-Revelation-1999.pdf)
- [Hermeneutics of Apocalyptic](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/10/Hermeneutics-of-Apocalyptic.pdf)
- [Finding Christ in the Book of Revelation](https://revelation-armageddon.com/2025/03/finding-christ-in-the-book-of-revelation/)
- [The Deep Things of God](https://www.thebattleofarmageddon.com/the-deep-things-of-god-2/)
- [Armageddon at the Door](https://www.thebattleofarmageddon.com/armageddon-at-the-door/)
- [Present Truth in the Real World](https://www.thebattleofarmageddon.com/present-truth-in-the-real-world/)
- [Meet God Again for the First Time](https://www.thebattleofarmageddon.com/meet-god-again-for-the-first-time/)
- [Knowing God in the Real World](https://www.thebattleofarmageddon.com/knowing-god-in-the-real-world/)
- [Interpreting the Seven Trumpets](https://www.thebattleofarmageddon.com/wp-content/uploads/2024/08/Interpreting-the-Seven-Trumpets.pdf)
- [The 1260 Days in Revelation](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/11/The-1260-Days-in-Revelation.pdf)
- [Ellen White and the Book of Revelation](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/08/Ellen-White-and-the-Book-of-Revelation.pdf)

Правило: если у Paulien есть прямой материал по тексту, он используется раньше любых других интерпретационных авторов.

## 3. Комментарии АСД

- [EGW SDA Bible Commentary, vol. 7](https://m.egwwritings.org/en/book/96.35)

## 4. Официальные доктрины АСД

- [Adventist.org beliefs](https://www.adventist.org/beliefs/)
- [GC Documents](https://gc.adventist.org/beliefs/documents/)
- [Seventh-day Adventists Believe / CREENCIAS... sample PDF](https://adventistbookcenter.com/amfile/file/download/file/1439/product/9374/)

## 5. Ellen G. White

- [EGW Writings](https://egwwritings.org/)
- [White Estate](https://whiteestate.org/)

## 6. Другие авторы АСД и официальные уроки

- [Adult Bible Study Guide: current quarter](https://absg.adventist.org/current-quarter)
- [Adult Bible Study Guide: archive](https://absg.adventist.org/archive)
- [Official lesson PDF example](https://absg.adventist.org/assets/public/files/lessons/2023/2Q/TE/PDFs/ETQ223_03.pdf)
- [Hope Sabbath School](https://hopetv.org/shows/hopess)
- [Biblical Research Institute](https://www.adventistbiblicalresearch.org/)
- [Andrews Digital Commons: Revelation + Paulien](https://digitalcommons.andrews.edu/do/search/?q=Revelation%20Paulien&start=0&context=3288059)
- [Andrews Digital Commons: Revelation + Stefanovic](https://digitalcommons.andrews.edu/do/search/?q=Revelation%20Stefanovic&start=0&context=3288059)
- [Andrews Digital Commons: Revelation + Mueller](https://digitalcommons.andrews.edu/do/search/?q=Revelation%20Mueller&start=0&context=3288059)

## 7. Ранние реформаторы и историки

Ранние толкователи:

- [John Bale, The Image of Both Churches](https://archive.org/details/bim_early-english-books-1475-1640_the-image-of-both-church_bale-john_1570)
- [Heinrich Bullinger, A Hundred Sermons Upon the Apocalypse](https://archive.org/details/BullingerHenry)
- [Thomas Brightman, Revelation of the Revelation](https://archive.org/details/BrightmanThomas.RevelationOfTheRevelationThatIsTheRevelationOfSt)

Исторические контрольные источники:

- [Eusebius, Church History](https://www.ccel.org/ccel/schaff/npnf201.html)
- [Socrates and Sozomen, Ecclesiastical Histories](https://www.ccel.org/ccel/schaff/npnf202.html)
- [Philip Schaff, History of the Christian Church](https://www.ccel.org/ccel/schaff/hcc1.html)
- [Edward Gibbon, Decline and Fall](https://www.gutenberg.org/ebooks/25717)

## Методология по этапам

| Этап | Цель | Главные источники | Итог |
| --- | --- | --- | --- |
| `1` | Честно зафиксировать текст | [CNTR](https://www.greekcntr.org/), [NTVMR](https://ntvmr.uni-muenster.de/), [INTF](https://www.uni-muenster.de/INTF/en/institut/index.html), [Codex Sinaiticus](https://codexsinaiticus.org/en/), [CSNTM](https://collections.csntm.org/), [Vatican Library](https://digi.vatlib.it/), [ECM VI/1](https://gssbibles.com/media/bc/2c/b7/1733099623/ECM%20VI1.%20Offenbarung.%20Text.pdf.pdf?ts=1770873022) | Консолидированный вариантный текст и таблица разночтений |
| `2` | Понять слова и синтаксис | [Logeion](https://logeion.uchicago.edu/), [STEP Bible](https://www.stepbible.org/), [Robertson](https://archive.org/details/grammarofgreekne0000atro), [Abbott-Smith](https://archive.org/details/manualgreeklexic00abbo), [Moulton/Milligan](https://archive.org/details/vocabularyofgree0000jame_z6d9) | Словарь, синтаксическая схема, микровыводы |
| `3` | Найти реальные OT-аллюзии | [Paulien ch. 7](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/05/The-Deep-Things-of-God-7-Allusions.pdf), [History of Interpretation](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/05/History-of-Interpretation-of-Revelation-1999.pdf), `SDA BC`, классические переводы | Матрица аллюзий и ранжирование по силе |
| `4` | Увидеть Христа в центре | [Finding Christ in Revelation](https://revelation-armageddon.com/2025/03/finding-christ-in-the-book-of-revelation/), [Paulien ch. 8](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/05/The-Deep-Things-of-God-8-Christ-in-the-OT.pdf), [The Lion Lamb King](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/09/The-Lion-Lamb-King.pdf), beliefs, EGW | Христологическая ось текста |
| `5` | Понять место текста в книге | [Revelation Outline](https://www.thebattleofarmageddon.com/wp-content/uploads/2022/09/Revelation-Outline.pdf), [Revelation Translation](https://www.thebattleofarmageddon.com/wp-content/uploads/2022/09/Revelation-Translation.pdf), [Facebook Commentary](https://www.thebattleofarmageddon.com/revelation-commentary-facebook/) | Структурная карта и связи |
| `6` | Проверить историю и возможные исполнения | [Paulien history texts](https://www.thebattleofarmageddon.com/wp-content/uploads/2025/05/History-of-Interpretation-of-Revelation-1999.pdf), реформаторы, [Eusebius](https://www.ccel.org/ccel/schaff/npnf201.html), [Schaff](https://www.ccel.org/ccel/schaff/hcc1.html), [Gibbon](https://www.gutenberg.org/ebooks/25717) | Таблица истории толкования и возможных исполнений |
| `7` | Перейти от знания к ответу веры | [EGW Writings](https://egwwritings.org/), [White Estate](https://whiteestate.org/), [Hope Sabbath School](https://hopetv.org/shows/hopess) | Духовный вывод, вопросы, призыв к действию |

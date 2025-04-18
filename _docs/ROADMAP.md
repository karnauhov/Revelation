## Схема изменения версий программы
  - Major: 1.x.x (Пролог 1:1-8); 2.x.x (7 церквей 1:9-3:22); 3.x.x (7 печатей 4:1-8:1); 4.x.x (7 труб 8:2-11:18);  5.x.x (Заключительный кризис 11:19-15:4); 6.x.x (7 чаш 15:5-18:24); 7.x.x (1000-летнее царство 19:1-20:15); 8.x.x (Новый Иерусалим 21:1-22:5); 9.x.x (Эпилог 22:6-21);
  - Minor: x.N.x - разбиение на отрывки, изменение когда закончены все 7 этапов изучения отрывка;
  - Patch: x.x.M - изменение когда пройден один этап изучения отрывка или реализована одна фича;
  - Build: x.x.x (B) - постоянный инкремент с каждым новым автобилдом;
  - Для каждой версии: добавление в changelog, удаление отсюда, release и tag в GitHub

## План разработки для версий 1.x.x (Пролог)

### 1.0.x (Вступление)

#### 1.0.0
  + Написать небольшое предисловие про Откровение и про выбор перечня первоисточников.
  + Сделать экран перечня первоисточников (7 папирусов и 12 маюскулов).
  + Публикация в PlayMarket.

#### 1.0.1
  + Загружать первоисточники с сервера.
  + Сделать экран одного первоисточника на котором можно будет выбрать фрагмент и увидеть его изображение.
  * Обновление изображений первоисточников.
  - Дополнить предисловие размышлением на тему принципов изучения Библии по Библии (прочтение, понимание, исполнение).
  - Публикация в Microsoft Store.

#### 1.0.2
  - Улучшить экран одного первоисточника. Добавить больше инструментов для работы с изображением: негатив, контрастность, яркость, заменить цвет, сделать черно-белым, удалить шум, сохранить изменения.
  - Расширить предисловие информацией про 7 этапов изучения каждого отрывка (согласно правилу: прочтение, понимание, исполнение).
  - Публикация в Web (GitHub Pages, свой домен).

#### 1.0.3
  - Добавить больше инструментов для работы с изображением: поиск и обводка цветов, выделение границ, распознавание, детекторы текста на основе ИИ.
  - Сделать область просмотра транскрипции фрагмента для экрана одного первоисточника.
  - Добавить транскрипции для текстов данного отрывка на всех источниках где он есть.
  - Выполнить и выписать Этап 1 (Формулирование общего текста всех первоисточников). Первоисточники этого отрывка.
  - Публикация в Flathub (Linux).

#### 1.0.4
  - Добавить в область просмотра при наведении - выделение слова прямоугольником (и в транскрипции).
  - Добавить в область транскрипции при наведении - выделение слова (и в области просмотра).
  - В общем тексте во вступлении каждое слово это ссылка которая открывает небольшой виджет с таблицей, в которой для каждого первоисточника показано название, изображене того как выглядит это слово в том месте, его транскрипция там и ссылка по нажатию на которую открывается окно данного первоисточника с выбранным местом и выделяет его.
  - Публикация в Mac App Store (macOS).
  - Публикация в App Store (iOS).

#### 1.0.x
  - Расписать план по версиям для Этапа 2 (Словарь и структура предложений). Этап включает: составление словаря слов отрывка, работа с номерами Стронга и словарными статьями по каждому слову, проведение разбора каждого предложения и слова согласно грамматическим правилам древнегреческого языка (Коинэ).
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

#### 1.0.x
  - Расписать план по версиям для Этапа 3 (Выявление и анализ аллюзий и ссылок). Этап включает: разбор каждого слова и словосочетания, изучение семантики и этимологии, исследование взаимосвязи текста с другими библейскими книгами. см. главу 7 "Глубины Божьи".
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

#### 1.0.x
  - Расписать план по версиям для Этапа 4 (Христос в книге Откровение). Этап включает: определение того как каждая часть текста указывает на личность и служение Христа. см. главу 8 "Глубины Божьи".
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

#### 1.0.x
  - Расписать план по версиям для Этапа 5 (Структуры и связи). Этап включает: исследование хиастической структуры книги Откровение, соотнесение отрывка с другими выявленными структурами, анализ того как текст связан с другими книгами Нового Завета, книгой Даниила, Ветхого Завета и всей Библией. см. главу 6 "Глубины Божьи".
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

#### 1.0.x
  - Расписать план по версиям для Этапа 6 (Исполнение в истории и в будущем). Этап включает: определение того как и когда текст мог исполниться в истории и может исполнится в будущем.
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

#### 1.0.x
  - Расписать план по версиям план для Этапа 7 (Исполнение личное). Этап включает: выявление духовных уроков для личной жизни, определение того что стоит изменить в своей жизни в свете изученного.
  - Определить экраны и виджеты для удобной работы с этим этапом и их подробный функционал.
  - Определить когда и что написать во вступлении как содержание этого этапа.

### 1.1.x (Приветствие)
  - Написать план.
  - Добавить перевод на испанский язык.

## План разработки для версий 2.x.x (7 церквей)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 3.x.x (7 печатей)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 4.x.x (7 труб)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 5.x.x (Заключительный кризис)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 6.x.x (7 чаш)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 7.x.x (1000-летнее царство)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 8.x.x (Новый Иерусалим)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

## План разработки для версий 9.x.x (Эпилог)
  - Разбить на отрывки, написать план.
  - Добавить задания на перевод на еще больше языков.

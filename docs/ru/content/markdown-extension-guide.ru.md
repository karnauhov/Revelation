# Руководство по расширению Markdown (RU)

Doc-Version: `1.3.0`  
Last-Updated: `2026-04-11`  
Source-Commit: `working-tree`

## Назначение

Зафиксировать подход Revelation к расширению Markdown на базе `flutter_markdown_plus` и `markdown`, включая кастомный синтаксис изображений и поддерживаемые форматы ссылок на изображения.

## Базовый стек

- В проекте используются `flutter_markdown_plus` и transitive `markdown`.
- `Markdown` и `MarkdownBody` подключаются через общий Revelation markdown config.
- Общий config расширяет `gitHubFlavored` и добавляет `md.EmojiSyntax()`.

## Что уже доступно в Markdown

- таблицы;
- task lists;
- footnotes;
- strikethrough;
- autolinks;
- emoji shortcodes при включённом `EmojiSyntax`.

## Кастомный блок изображения

Для статей Revelation поддерживается специальный блок:

```md
{{image}}
src: images/map.jpg
alt: Карта печатей
align: center
width: 640
height: 360
caption: Необязательная подпись
{{/image}}
```

Поддерживаемые поля:

- `src`
- `alt`
- `align`: `left`, `center`, `right`
- `width`
- `height`
- `caption`

## Fallback для неизвестных кастомных блоков

Общий markdown config теперь распознаёт и любой кастомный блок, который использует ту же внешнюю обёртку, что и `{{image}}`:

```md
{{timeline}}
title: Seven seals
layout: compact
{{/timeline}}
```

Поведение:

- Известные блоки вроде `{{image}}` продолжают рендериться через свой отдельный builder.
- Неизвестные блоки отображаются как центрированный compatibility placeholder, а не исчезают молча.
- В нативных сборках приложение показывает рекомендацию открыть страницу `download`, чтобы пользователь сам выбрал удобный маркетплейс.
- В web-сборке остаётся только fallback placeholder без дополнительной подсказки/действия по обновлению.

## Поддерживаемые варианты источника изображения

Парсер изображений понимает эти формы и в кастомном блоке `{{image}}`, и в обычном markdown-синтаксисе `![Alt](...)`.

### Asset

```md
![Иконка](resource:assets/images/UI/app_icon.png)
```

### DB Resource

```md
![Схема](dbres:topic/diagram.svg)
```

### Короткая запись для Supabase bucket

Рекомендуемый вариант для изображений статей из публичного bucket `images`:

```md
{{image}}
src: images/map.jpg
alt: Карта
align: right
width: 320
height: 200
{{/image}}
```

Такая запись автоматически трактуется как путь в публичном Supabase bucket `images`.

### Явный путь Supabase

```md
![Диаграмма](supabase:images/charts/seals.svg)
```

### Полный public URL Supabase

```md
![Карта](https://adfdfxnzxmzyoioedwuy.supabase.co/storage/v1/object/public/images/map.jpg)
```

Полный public URL автоматически распознаётся обратно как `bucket/path`.

### Внешний URL

```md
![Внешнее изображение](https://example.com/reference/chart.png)
```

Внешние URL по-прежнему поддерживаются, но для стабильного контента статей лучше переносить изображения в Supabase проекта и ссылаться на них через bucket `images`.

## Локальный кеш изображений

Для topic-статей:

- удалённые изображения из Supabase и внешних URL скачиваются один раз при первом открытии;
- локальные файлы сохраняются в `Documents/revelation/images/`;
- файлы имеют читаемые имена и расширения, а не hash-only имена кеша;
- если источник находится в bucket `images`, локальный путь повторяет этот путь напрямую.

Примеры:

- `images/map.jpg` -> `Documents/revelation/images/map.jpg`
- `images/maps/seal-1.svg` -> `Documents/revelation/images/maps/seal-1.svg`
- внешние URL сохраняются в `Documents/revelation/images/external/...`

## Размер placeholder до загрузки

- Если заданы `width` и `height`, временный фрейм сразу занимает нужный размер.
- Для обычного markdown-изображения размер можно задать и через fragment:

```md
![Встроенная карта](images/map.jpg#640x360)
```

## YouTube-блок

Revelation также поддерживает встроенный YouTube-блок для проигрывания видео прямо внутри markdown-статьи:

```md
{{youtube}}
url: https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=42s
title: Big Buck Bunny
width: 960
height: 540
{{/youtube}}
```

Поддерживаемые поля:

- `url`: полный YouTube URL, например `watch`, `youtu.be`, `embed`, `shorts`
- `id`: прямой YouTube video id, если не нужен полный URL
- `title`
- `start`
- `width`
- `height`
- `aspect_ratio`: например `16:9`

Поведение:

- В web-сборке рендерится обычный YouTube iframe.
- В Android, iOS, macOS, Windows и Linux используется локальный HTML shell через `flutter_inappwebview` на базе официального YouTube IFrame Player API.
- Встроенный плеер сохраняет родные YouTube controls и fullscreen-поведение.
- В Android, iOS, macOS, Windows и Linux любая попытка открыть страницу вне локального player shell перенаправляется в системный браузер и не заменяет плеер внутри markdown-блока.
- Markdown-блок рендерит только поверхность плеера, без дополнительного заголовка/подписи/ссылки под ним.

## Где подключается общий markdown config

- `lib/shared/ui/widgets/description_markdown_view.dart`
- `lib/features/topics/presentation/screens/topic_screen.dart`
- `lib/shared/ui/dialogs/dialogs_utils.dart`

Рекомендуемое место helper-а:

- `lib/shared/ui/markdown/revelation_markdown_config.dart`

## Быстрый checklist

1. Держать markdown-рендеринг на общем Revelation markdown config.
2. Использовать `{{image}}` для изображений статьи и `{{youtube}}` для встроенного YouTube-воспроизведения.
3. Для изображений статей предпочитать ссылки вида `images/...` из публичного Supabase bucket `images`.
4. Указывать `width` и `height`, когда важна стабильная раскладка.
5. Обновлять тесты при изменении markdown-парсинга или рендера.

# Руководство по расширению Markdown (RU)

Doc-Version: `1.0.0`  
Last-Updated: `2026-03-30`  
Source-Commit: `working-tree`

## Назначение

Зафиксировать практический подход для Revelation: как расширять Markdown без перехода на полный HTML runtime, и как включить нужные возможности на текущем стеке `flutter_markdown_plus` + `markdown`.

## База стека

- В проекте используется `flutter_markdown_plus` и transitive `markdown`.
- По умолчанию `Markdown`/`MarkdownBody` работают с `md.ExtensionSet.gitHubFlavored`.
- Это уже покрывает: таблицы, task lists (чекбоксы), footnotes, strikethrough, autolinks.
- Для `:emoji_shortcodes:` нужно явно добавить `md.EmojiSyntax()`.

## Что можно получить в документе Markdown

### Task Lists

```md
- [x] Уже выполнено
- [ ] Еще в работе
```

### Footnotes

```md
Текст со сноской[^a].

[^a]: Содержимое сноски.
```

### Таблицы

```md
| Символ | Значение |
|:------|---------:|
| Агнец | Христос  |
| Рог   | Власть   |
```

### Автоссылки

```md
https://www.revelation.website
support@example.com
```

### Superscript для footnotes

- Индексы сносок в `flutter_markdown_plus` поднимаются автоматически.
- При необходимости можно сменить font feature через `superscriptFontFeatureTag` в `MarkdownStyleSheet`.

## Включение emoji shortcodes

```dart
import 'package:markdown/markdown.dart' as md;

md.ExtensionSet buildRevelationExtensionSet() {
  return md.ExtensionSet(
    md.ExtensionSet.gitHubFlavored.blockSyntaxes,
    <md.InlineSyntax>[
      md.EmojiSyntax(),
      ...md.ExtensionSet.gitHubFlavored.inlineSyntaxes,
    ],
  );
}
```

Использование:

```dart
MarkdownBody(
  data: markdown,
  extensionSet: buildRevelationExtensionSet(),
)
```

Пример в тексте:

```md
Важно :warning: и радость :smiley:
```

## Кастомные bullets и checkboxes

`bulletBuilder` и `checkboxBuilder` позволяют менять только рендер, не меняя Markdown-синтаксис.

```dart
MarkdownBody(
  data: markdown,
  extensionSet: buildRevelationExtensionSet(),
  bulletBuilder: (params) {
    if (params.style == BulletStyle.orderedList) {
      return CircleAvatar(
        radius: 10,
        child: Text('${params.index + 1}'),
      );
    }
    return Icon(
      params.nestLevel == 0 ? Icons.star : Icons.chevron_right,
      size: 16,
    );
  },
  checkboxBuilder: (checked) {
    return Icon(
      checked ? Icons.check_circle : Icons.radio_button_unchecked,
      size: 18,
    );
  },
)
```

## Кастомные элементы в Markdown

Если нужен виджет в теле статьи (например, видео-блок, callout, compare-card), используется пара:

1. `md.BlockSyntax` или `md.InlineSyntax` для парсинга.
2. `MarkdownElementBuilder` для рендера Flutter-виджета.

Пример Markdown:

```md
{{video}}
src: https://cdn.example.com/intro.mp4
caption: Введение
{{/video}}
```

Пример рендера (идея):

- `VideoBlockSyntax` распознает блок `{{video}}...{{/video}}` и создает узел `md.Element('video')` с атрибутами.
- `VideoBuilder` (наследник `MarkdownElementBuilder`) получает этот узел и возвращает ваш `Widget` (карточка, плеер, placeholder, и т.д.).

## Где подключать в Revelation

Единообразно прокидывать один и тот же конфиг markdown в:

- `lib/shared/ui/widgets/description_markdown_view.dart`
- `lib/features/topics/presentation/screens/topic_screen.dart`
- `lib/shared/ui/dialogs/dialogs_utils.dart`

Рекомендуется вынести это в один helper, например:

- `lib/shared/ui/markdown/revelation_markdown_config.dart`

## Практические ограничения

- Markdown-путь хорош для статей с контролируемым набором блоков.
- Для произвольного HTML/CSS/JS и сложного браузерного поведения нужен WebView runtime.
- Не стоит делать “бесконечный DSL”: лучше утвердить whitelist блоков и поддерживать его стабильно.

## Экспорт и дополнительные возможности

- Для экспорта уже отрендеренного Flutter markdown-экрана в PDF: `flutter_to_pdf` (MIT).
- Для отдельного документного PDF-pipeline: `htmltopdfwidgets` + `pdf` + `printing` (Apache-2.0).
- Для математики в markdown: `flutter_markdown_plus_latex` (Apache-2.0).

## Быстрый checklist внедрения

1. Вынести общий `extensionSet`.
2. Добавить `EmojiSyntax` поверх `gitHubFlavored`.
3. Централизовать `bulletBuilder` и `checkboxBuilder`.
4. При необходимости настроить `superscriptFontFeatureTag`.
5. Для сложных блоков добавить custom syntax + builder.
6. Добавить тесты на новые markdown-возможности и кастомные блоки.


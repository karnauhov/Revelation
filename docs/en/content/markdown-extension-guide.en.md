# Markdown Extension Guide (EN)

Doc-Version: `1.0.0`  
Last-Updated: `2026-03-30`  
Source-Commit: `working-tree`

## Purpose

Document a practical Revelation strategy for extending Markdown without moving to a full HTML runtime, using the current `flutter_markdown_plus` + `markdown` stack.

## Stack Baseline

- The project uses `flutter_markdown_plus` and transitive `markdown`.
- `Markdown`/`MarkdownBody` default to `md.ExtensionSet.gitHubFlavored`.
- This already provides: tables, task lists (checkboxes), footnotes, strikethrough, and autolinks.
- `:emoji_shortcodes:` need an explicit `md.EmojiSyntax()` addition.

## What You Can Get in Markdown

### Task Lists

```md
- [x] Done
- [ ] In progress
```

### Footnotes

```md
Text with a footnote[^a].

[^a]: Footnote content.
```

### Tables

```md
| Symbol | Meaning |
|:-------|--------:|
| Lamb   | Christ  |
| Horn   | Power   |
```

### Autolinks

```md
https://www.revelation.website
support@example.com
```

### Superscript for footnotes

- Footnote indices are superscripted automatically by `flutter_markdown_plus`.
- If needed, tune font feature behavior with `superscriptFontFeatureTag` in `MarkdownStyleSheet`.

## Enabling Emoji Shortcodes

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

Usage:

```dart
MarkdownBody(
  data: markdown,
  extensionSet: buildRevelationExtensionSet(),
)
```

Markdown sample:

```md
Important :warning: and joy :smiley:
```

## Custom Bullets and Checkboxes

`bulletBuilder` and `checkboxBuilder` customize rendering only; Markdown syntax stays standard.

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

## Custom Widgets Inside Markdown

For article widgets (video block, callout, compare-card), use:

1. `md.BlockSyntax` or `md.InlineSyntax` to parse.
2. `MarkdownElementBuilder` to render a Flutter widget.

Markdown sample:

```md
{{video}}
src: https://cdn.example.com/intro.mp4
caption: Intro
{{/video}}
```

Rendering idea:

- `VideoBlockSyntax` parses `{{video}}...{{/video}}` and creates `md.Element('video')` with attributes.
- `VideoBuilder` (extends `MarkdownElementBuilder`) reads those attributes and returns your widget (card, player, placeholder, etc.).

## Where to Wire This in Revelation

Keep one consistent markdown config for:

- `lib/shared/ui/widgets/description_markdown_view.dart`
- `lib/features/topics/presentation/screens/topic_screen.dart`
- `lib/shared/ui/dialogs/dialogs_utils.dart`

Recommended helper location:

- `lib/shared/ui/markdown/revelation_markdown_config.dart`

## Practical Limits

- Markdown is a strong fit for controlled article layouts with a known block set.
- Arbitrary HTML/CSS/JS and browser-like behavior still requires a WebView runtime.
- Avoid an unbounded DSL; define and maintain a stable whitelist of custom blocks.

## Export and Useful Add-ons

- Export rendered Flutter markdown screens to PDF: `flutter_to_pdf` (MIT).
- Dedicated document PDF pipeline: `htmltopdfwidgets` + `pdf` + `printing` (Apache-2.0).
- Math in markdown: `flutter_markdown_plus_latex` (Apache-2.0).

## Quick Adoption Checklist

1. Extract a shared markdown `extensionSet`.
2. Add `EmojiSyntax` on top of `gitHubFlavored`.
3. Centralize `bulletBuilder` and `checkboxBuilder`.
4. Tune `superscriptFontFeatureTag` if needed for fonts.
5. Add custom syntax + builder for richer article blocks.
6. Add tests for new markdown features and custom blocks.


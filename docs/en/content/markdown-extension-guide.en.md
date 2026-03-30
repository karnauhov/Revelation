# Markdown Extension Guide (EN)

Doc-Version: `1.1.0`  
Last-Updated: `2026-03-30`  
Source-Commit: `working-tree`

## Purpose

Document the Revelation markdown extension approach built on top of `flutter_markdown_plus` and `markdown`, including the custom image block syntax and the supported image source forms.

## Stack Baseline

- The project uses `flutter_markdown_plus` and transitive `markdown`.
- `Markdown` and `MarkdownBody` are wired through a shared Revelation markdown config.
- The shared config extends `gitHubFlavored` and adds `md.EmojiSyntax()`.

## Built-in Markdown Features

- Tables
- Task lists
- Footnotes
- Strikethrough
- Autolinks
- Emoji shortcodes when `EmojiSyntax` is enabled

## Custom Image Blocks

Revelation supports a custom block image syntax for article content:

```md
{{image}}
src: images/map.jpg
alt: Map of the seals
align: center
width: 640
height: 360
caption: Optional caption
{{/image}}
```

Supported fields:

- `src`
- `alt`
- `align`: `left`, `center`, `right`
- `width`
- `height`
- `caption`

## Supported Image Source Forms

The image parser recognizes these forms in both the custom `{{image}}` block and regular markdown image syntax such as `![Alt](...)`.

### Asset

```md
![Icon](resource:assets/images/UI/app_icon.png)
```

### DB Resource

```md
![Diagram](dbres:topic/diagram.svg)
```

### Supabase Bucket Shorthand

Recommended for article images stored in the public `images` bucket:

```md
{{image}}
src: images/map.jpg
alt: Map
align: right
width: 320
height: 200
{{/image}}
```

This resolves to the Supabase public storage path for the `images` bucket.

### Explicit Supabase Bucket Path

```md
![Chart](supabase:images/charts/seals.svg)
```

### Full Public Supabase URL

```md
![Map](https://adfdfxnzxmzyoioedwuy.supabase.co/storage/v1/object/public/images/map.jpg)
```

Full public storage URLs are parsed back into `bucket/path` form automatically.

### External URL

```md
![Reference image](https://example.com/reference/chart.png)
```

External URLs are still supported, but the preferred content workflow is to move stable article images into the project Supabase storage and reference them from the `images` bucket.

## Local Image Caching

For topic articles:

- remote Supabase and external images are downloaded once on first load;
- cached files are stored locally under `Documents/revelation/images/`;
- files keep readable image names and extensions instead of opaque cache-only names;
- if the source comes from the `images` bucket, the local file path mirrors that bucket path directly.

Examples:

- `images/map.jpg` -> `Documents/revelation/images/map.jpg`
- `images/maps/seal-1.svg` -> `Documents/revelation/images/maps/seal-1.svg`
- external URLs are stored under `Documents/revelation/images/external/...`

## Placeholder Sizing

- If `width` and `height` are provided, the placeholder frame uses those dimensions immediately.
- For regular markdown images, dimensions can also be embedded as a source fragment:

```md
![Inline map](images/map.jpg#640x360)
```

## Where the Shared Markdown Config Is Used

- `lib/shared/ui/widgets/description_markdown_view.dart`
- `lib/features/topics/presentation/screens/topic_screen.dart`
- `lib/shared/ui/dialogs/dialogs_utils.dart`

Helper location:

- `lib/shared/ui/markdown/revelation_markdown_config.dart`

## Quick Adoption Checklist

1. Keep markdown rendering wired through the shared Revelation markdown config.
2. Use `{{image}}` when you need alignment, caption, or explicit placeholder size.
3. Prefer `images/...` references for article images stored in the public Supabase `images` bucket.
4. Add width and height when layout stability matters.
5. Keep tests updated when markdown parsing or rendering behavior changes.

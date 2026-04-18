# Markdown Extension Guide (EN)

Doc-Version: `1.3.0`  
Last-Updated: `2026-04-11`  
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

## Unknown Custom Block Fallback

The shared markdown config also recognizes any custom block that follows the same wrapper format as `{{image}}`:

```md
{{timeline}}
title: Seven seals
layout: compact
{{/timeline}}
```

Behavior:

- Known blocks such as `{{image}}` continue to render through their dedicated builder.
- Unknown blocks render as a centered compatibility placeholder instead of disappearing silently.
- Native app builds show a recommendation to open the `download` page so users can choose their marketplace manually.
- Web builds keep only the fallback placeholder without the extra update hint/action.

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

## YouTube Blocks

Revelation also supports an embedded YouTube block for inline playback inside markdown articles:

```md
{{youtube}}
url: https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=42s
title: Big Buck Bunny
width: 960
height: 540
{{/youtube}}
```

Supported fields:

- `url`: full YouTube URL such as `watch`, `youtu.be`, `embed`, `shorts`
- `id`: direct YouTube video id when you do not want to store the full URL
- `title`
- `start`
- `width`
- `height`
- `aspect_ratio`: for example `16:9`

Behavior:

- Web builds render a regular YouTube iframe.
- Android, iOS, macOS, Windows, and Linux builds render a local HTML shell through `flutter_inappwebview`, powered by the official YouTube IFrame Player API.
- The embedded player keeps native YouTube controls and fullscreen behavior.
- On Android, iOS, macOS, Windows, and Linux, any attempt to open a page outside the local player shell is redirected to the system browser instead of replacing the player inside the markdown block.
- The markdown block renders only the player surface, without extra title/caption/link UI under it.

## Where the Shared Markdown Config Is Used

- `lib/shared/ui/widgets/description_markdown_view.dart`
- `lib/features/topics/presentation/screens/topic_screen.dart`
- `lib/shared/ui/dialogs/dialogs_utils.dart`

Helper location:

- `lib/shared/ui/markdown/revelation_markdown_config.dart`

## Quick Adoption Checklist

1. Keep markdown rendering wired through the shared Revelation markdown config.
2. Use `{{image}}` for article images and `{{youtube}}` for embedded YouTube playback.
3. Prefer `images/...` references for article images stored in the public Supabase `images` bucket.
4. Add width and height when layout stability matters.
5. Keep tests updated when markdown parsing or rendering behavior changes.

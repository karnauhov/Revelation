import 'dart:ui_web' as ui_web;

import 'package:flutter/widgets.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';
import 'package:web/web.dart' as web;

final Set<String> _registeredViewTypes = <String>{};

Widget buildRevelationMarkdownYoutubePlayer({
  Key? key,
  required RevelationMarkdownYoutubeData video,
}) {
  final embedUri = video.embedUri;
  if (embedUri == null) {
    return const SizedBox.shrink();
  }

  final viewType = 'revelation-markdown-youtube-${video.viewTypeKey}';
  if (_registeredViewTypes.add(viewType)) {
    ui_web.platformViewRegistry.registerViewFactory(viewType, (viewId) {
      final iframe = web.HTMLIFrameElement()
        ..src = embedUri.toString()
        ..title = video.title ?? 'YouTube video'
        ..allow =
            'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen'
        ..allowFullscreen = true
        ..loading = 'lazy'
        ..referrerPolicy = 'strict-origin-when-cross-origin'
        ..style.border = '0'
        ..style.width = '100%'
        ..style.height = '100%'
        ..style.overflow = 'hidden';
      iframe.setAttribute('scrolling', 'no');
      return iframe;
    });
  }

  return HtmlElementView(key: key, viewType: viewType);
}

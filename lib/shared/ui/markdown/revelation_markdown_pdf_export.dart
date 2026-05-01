import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:get_it/get_it.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/core/platform/file_downloader.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';

const String _revelationMarkdownPdfBaseFontAsset =
    'assets/fonts/Arimo/Arimo.ttf';
const String _revelationMarkdownPdfCopticFontAsset =
    'assets/fonts/NotoSansCoptic/NotoSansCoptic-Regular.ttf';
const String revelationMarkdownPdfAuthor = 'Karnauhov Oleh';
const int _combiningOverlineCodePoint = 0x0305;
const double revelationMarkdownPdfPageMargin = 18 * PdfPageFormat.mm;

const Map<String, String> revelationMarkdownPdfFonts = {
  'Arimo': _revelationMarkdownPdfBaseFontAsset,
  'Segoe UI': _revelationMarkdownPdfBaseFontAsset,
  'Segoe UI Symbol': _revelationMarkdownPdfBaseFontAsset,
  'Segoe UI Variable': _revelationMarkdownPdfBaseFontAsset,
  'Roboto': _revelationMarkdownPdfBaseFontAsset,
  'Arial': _revelationMarkdownPdfBaseFontAsset,
  'Helvetica Neue': _revelationMarkdownPdfBaseFontAsset,
  'Liberation Sans': _revelationMarkdownPdfBaseFontAsset,
  'Ubuntu': _revelationMarkdownPdfBaseFontAsset,
  'sans-serif': _revelationMarkdownPdfBaseFontAsset,
  'monospace': _revelationMarkdownPdfBaseFontAsset,
  'Noto Sans Coptic': _revelationMarkdownPdfCopticFontAsset,
};

typedef RevelationMarkdownPdfSaver =
    Future<String?> Function({
      required Uint8List bytes,
      required String fileName,
      required String mimeType,
    });

Future<_RevelationMarkdownPdfFonts>? _pdfFontsFuture;

Future<String?> exportRevelationMarkdownPdf({
  required String markdown,
  required String documentTitle,
  required String appName,
  MarkdownImageLoader? markdownImageLoader,
  RevelationMarkdownPdfSaver? saveFile,
}) async {
  final title = _normalizeDocumentTitle(documentTitle);
  final bytes = await buildRevelationMarkdownPdfData(
    markdown: markdown,
    documentTitle: title,
    appName: appName,
    pageFormat: PdfPageFormat.a4,
    markdownImageLoader: markdownImageLoader,
  );
  final saver = saveFile ?? saveDownloadableFile;

  return saver(
    bytes: bytes,
    fileName: _pdfFileName(title),
    mimeType: 'application/pdf',
  );
}

Future<Uint8List> buildRevelationMarkdownPdfData({
  required String markdown,
  required String documentTitle,
  required String appName,
  required PdfPageFormat pageFormat,
  MarkdownImageLoader? markdownImageLoader,
}) async {
  final fonts = await _loadPdfFonts();
  final theme = fonts.toTheme();
  final title = _normalizeDocumentTitle(documentTitle);
  final buildContext = _RevelationMarkdownPdfBuildContext(
    markdownImageLoader: _resolveMarkdownImageLoader(markdownImageLoader),
  );
  final widgets = await buildContext.build(markdown);
  final subject = _normalizeDocumentSubject(appName);

  final document = pw.Document(
    pageMode: buildContext.hasOutlineEntries
        ? PdfPageMode.outlines
        : PdfPageMode.none,
    title: title,
    author: revelationMarkdownPdfAuthor,
    creator: 'Revelation',
    subject: subject,
    producer: 'Revelation',
    theme: theme,
  );

  document.addPage(
    pw.MultiPage(
      pageFormat: pageFormat,
      margin: const pw.EdgeInsets.all(revelationMarkdownPdfPageMargin),
      theme: theme,
      build: (_) => widgets.isEmpty ? <pw.Widget>[pw.SizedBox()] : widgets,
    ),
  );

  return document.save(enableEventLoopBalancing: true);
}

Future<_RevelationMarkdownPdfFonts> _loadPdfFonts() {
  _pdfFontsFuture ??= _loadPdfFontsFromAssets();
  return _pdfFontsFuture!;
}

Future<_RevelationMarkdownPdfFonts> _loadPdfFontsFromAssets() async {
  final baseFont = pw.Font.ttf(
    await rootBundle.load(_revelationMarkdownPdfBaseFontAsset),
  );
  final copticFont = pw.Font.ttf(
    await rootBundle.load(_revelationMarkdownPdfCopticFontAsset),
  );
  return _RevelationMarkdownPdfFonts(base: baseFont, fallback: [copticFont]);
}

MarkdownImageLoader? _resolveMarkdownImageLoader(
  MarkdownImageLoader? markdownImageLoader,
) {
  if (markdownImageLoader != null) {
    return markdownImageLoader;
  }
  if (GetIt.I.isRegistered<MarkdownImageLoader>()) {
    return GetIt.I<MarkdownImageLoader>();
  }
  return null;
}

String _normalizeDocumentTitle(String documentTitle) {
  final normalized = documentTitle.trim().replaceAll(RegExp(r'\s+'), ' ');
  return normalized.isEmpty ? 'Revelation' : normalized;
}

String _normalizeDocumentSubject(String appName) {
  final normalized = appName.trim().replaceAll(RegExp(r'\s+'), ' ');
  return normalized.isEmpty ? 'Revelation' : normalized;
}

String _pdfFileName(String documentTitle) {
  return documentTitle.toLowerCase().endsWith('.pdf')
      ? documentTitle
      : '$documentTitle.pdf';
}

@visibleForTesting
bool isRevelationMarkdownPdfExternalHttpLink(String? href) {
  return _externalHttpLinkDestination(href) != null;
}

@visibleForTesting
final class RevelationMarkdownPdfTextSegment {
  const RevelationMarkdownPdfTextSegment(this.text, {required this.overlined});

  final String text;
  final bool overlined;

  @override
  bool operator ==(Object other) {
    return other is RevelationMarkdownPdfTextSegment &&
        text == other.text &&
        overlined == other.overlined;
  }

  @override
  int get hashCode => Object.hash(text, overlined);

  @override
  String toString() {
    return 'RevelationMarkdownPdfTextSegment('
        'text: $text, '
        'overlined: $overlined'
        ')';
  }
}

@visibleForTesting
List<RevelationMarkdownPdfTextSegment>
segmentRevelationMarkdownPdfTextForExport(String text) {
  return _splitTextSegments(text);
}

String? _externalHttpLinkDestination(String? href) {
  final normalized = href?.trim() ?? '';
  return RegExp(r'^https?://', caseSensitive: false).hasMatch(normalized)
      ? normalized
      : null;
}

List<RevelationMarkdownPdfTextSegment> _splitTextSegments(String text) {
  if (!text.runes.contains(_combiningOverlineCodePoint)) {
    return <RevelationMarkdownPdfTextSegment>[
      RevelationMarkdownPdfTextSegment(text, overlined: false),
    ];
  }

  final segments = <RevelationMarkdownPdfTextSegment>[];
  final normal = StringBuffer();
  final overlined = StringBuffer();
  final runes = text.runes.toList(growable: false);

  void flushNormal() {
    if (normal.isEmpty) {
      return;
    }
    segments.add(
      RevelationMarkdownPdfTextSegment(normal.toString(), overlined: false),
    );
    normal.clear();
  }

  void flushOverlined() {
    if (overlined.isEmpty) {
      return;
    }
    segments.add(
      RevelationMarkdownPdfTextSegment(overlined.toString(), overlined: true),
    );
    overlined.clear();
  }

  for (var index = 0; index < runes.length; index++) {
    final rune = runes[index];
    if (rune == _combiningOverlineCodePoint) {
      flushOverlined();
      normal.writeCharCode(rune);
      continue;
    }

    final hasOverline =
        index + 1 < runes.length &&
        runes[index + 1] == _combiningOverlineCodePoint;
    if (hasOverline) {
      flushNormal();
      overlined.writeCharCode(rune);
      index++;
    } else {
      flushOverlined();
      normal.writeCharCode(rune);
    }
  }

  flushNormal();
  flushOverlined();
  return segments;
}

class _RevelationMarkdownPdfFonts {
  const _RevelationMarkdownPdfFonts({
    required this.base,
    required this.fallback,
  });

  final pw.Font base;
  final List<pw.Font> fallback;

  pw.ThemeData toTheme() {
    return pw.ThemeData.withFont(
      base: base,
      bold: base,
      italic: base,
      boldItalic: base,
      fontFallback: fallback,
    );
  }
}

class _RevelationMarkdownPdfBuildContext {
  _RevelationMarkdownPdfBuildContext({required this.markdownImageLoader});

  static const double _blockSpacing = 8;
  static const double _listIndent = 18;

  final MarkdownImageLoader? markdownImageLoader;
  var _outlineCounter = 0;
  var _hasOutlineEntries = false;

  final pw.TextStyle baseStyle = const pw.TextStyle(
    fontSize: 11,
    height: 1.35,
    color: PdfColors.black,
  );

  bool get hasOutlineEntries => _hasOutlineEntries;
  final pw.TextStyle codeStyle = const pw.TextStyle(
    fontSize: 9.5,
    height: 1.25,
    color: PdfColors.black,
  );

  Future<List<pw.Widget>> build(String markdown) async {
    final document = md.Document(
      extensionSet: buildRevelationMarkdownExtensionSet(),
      encodeHtml: false,
    );
    return _buildBlocks(document.parse(markdown));
  }

  Future<List<pw.Widget>> _buildBlocks(List<md.Node> nodes) async {
    final widgets = <pw.Widget>[];
    for (final node in nodes) {
      final widget = await _buildBlock(node);
      if (widget != null) {
        widgets.add(widget);
      }
    }
    return widgets;
  }

  Future<pw.Widget?> _buildBlock(md.Node node) async {
    if (node is md.Text) {
      return _spaced(_richText(<md.Node>[node], baseStyle));
    }
    if (node is! md.Element) {
      return null;
    }

    switch (node.tag) {
      case 'h1':
      case 'h2':
      case 'h3':
      case 'h4':
      case 'h5':
      case 'h6':
        return _spaced(_heading(node));
      case 'p':
        return _spaced(_richText(node.children, baseStyle));
      case 'ul':
        return _spaced(await _list(node, ordered: false));
      case 'ol':
        return _spaced(await _list(node, ordered: true));
      case 'blockquote':
        return _spaced(await _blockquote(node));
      case 'pre':
        return _spaced(_codeBlock(node.textContent));
      case 'hr':
        return _spaced(pw.Divider(color: PdfColors.grey500));
      case 'table':
        return _spaced(_table(node));
      case RevelationMarkdownImageBlockSyntax.tag:
      case 'img':
        return _spaced(await _imageBlock(node));
      case RevelationMarkdownYoutubeData.tag:
        return _spaced(_placeholder(node.attributes['title'] ?? 'YouTube'));
      case RevelationMarkdownUnknownBlockData.tag:
        return _spaced(_placeholder(node.attributes['name'] ?? ''));
      default:
        if (node.children == null || node.children!.isEmpty) {
          return null;
        }
        return _spaced(
          pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.stretch,
            children: await _buildBlocks(node.children!),
          ),
        );
    }
  }

  pw.TextStyle _headingStyle(String tag) {
    final size = switch (tag) {
      'h1' => 24.0,
      'h2' => 20.0,
      'h3' => 17.0,
      'h4' => 14.0,
      'h5' => 12.5,
      _ => 11.5,
    };
    return baseStyle.copyWith(
      fontSize: size,
      fontWeight: pw.FontWeight.bold,
      height: 1.18,
    );
  }

  pw.Widget _heading(md.Element element) {
    final content = _richText(element.children, _headingStyle(element.tag));
    final title = element.textContent.trim().replaceAll(RegExp(r'\s+'), ' ');
    if (title.isEmpty) {
      return content;
    }

    _hasOutlineEntries = true;
    return pw.Outline(
      name: 'heading-${_outlineCounter++}',
      title: title,
      level: _headingOutlineLevel(element.tag),
      child: content,
    );
  }

  int _headingOutlineLevel(String tag) {
    final level = int.tryParse(tag.substring(1)) ?? 1;
    return level < 1 ? 0 : level - 1;
  }

  pw.Widget _richText(List<md.Node>? nodes, pw.TextStyle style) {
    return pw.RichText(
      overflow: pw.TextOverflow.span,
      text: pw.TextSpan(style: style, children: _inlineSpans(nodes, style)),
    );
  }

  List<pw.InlineSpan> _inlineSpans(List<md.Node>? nodes, pw.TextStyle style) {
    if (nodes == null || nodes.isEmpty) {
      return const <pw.InlineSpan>[];
    }

    final spans = <pw.InlineSpan>[];
    for (final node in nodes) {
      if (node is md.Text) {
        spans.addAll(_textSpans(node.text, style));
        continue;
      }
      if (node is! md.Element) {
        continue;
      }

      if (node.tag == 'br') {
        spans.add(pw.TextSpan(text: '\n', style: style));
      } else if (node.tag == 'code') {
        final nextStyle = _styleForInlineTag(node.tag, style);
        spans.add(pw.TextSpan(text: node.textContent, style: nextStyle));
      } else if (node.tag == 'img') {
        final nextStyle = _styleForInlineTag(node.tag, style);
        final image = RevelationMarkdownImageData.fromMarkdownElement(node);
        final label = image?.alt ?? node.attributes['alt'] ?? '';
        if (label.trim().isNotEmpty) {
          spans.add(pw.TextSpan(text: label.trim(), style: nextStyle));
        }
      } else if (node.tag == 'a') {
        final href = node.attributes['href'];
        final nextStyle = _styleForLink(href, style);
        final annotation = _annotationForLink(href);
        final children = _inlineSpans(node.children, nextStyle);
        if (annotation == null) {
          spans.addAll(children);
        } else {
          spans.add(
            pw.TextSpan(
              style: nextStyle,
              annotation: annotation,
              children: children,
            ),
          );
        }
      } else {
        final nextStyle = _styleForInlineTag(node.tag, style);
        spans.addAll(_inlineSpans(node.children, nextStyle));
      }
    }
    return spans;
  }

  List<pw.InlineSpan> _textSpans(String text, pw.TextStyle style) {
    return _splitTextSegments(text)
        .map(
          (segment) => pw.TextSpan(
            text: segment.text,
            style: segment.overlined ? _overlineStyle(style) : style,
          ),
        )
        .toList(growable: false);
  }

  pw.TextStyle _styleForInlineTag(String tag, pw.TextStyle style) {
    switch (tag) {
      case 'strong':
        return style.copyWith(fontWeight: pw.FontWeight.bold);
      case 'em':
        return style.copyWith(fontStyle: pw.FontStyle.italic);
      case 'code':
        return codeStyle.copyWith(
          color: PdfColors.grey900,
          background: pw.BoxDecoration(color: PdfColors.grey200),
        );
      case 'del':
        return style.copyWith(decoration: pw.TextDecoration.lineThrough);
      default:
        return style;
    }
  }

  pw.TextStyle _styleForLink(String? href, pw.TextStyle style) {
    if (!isRevelationMarkdownPdfExternalHttpLink(href)) {
      return style;
    }
    return style.copyWith(
      color: PdfColors.blue700,
      decoration: pw.TextDecoration.underline,
    );
  }

  pw.TextStyle _overlineStyle(pw.TextStyle style) {
    return style.copyWith(
      decoration:
          style.decoration?.merge(pw.TextDecoration.overline) ??
          pw.TextDecoration.overline,
    );
  }

  pw.AnnotationUrl? _annotationForLink(String? href) {
    final destination = _externalHttpLinkDestination(href);
    return destination == null ? null : pw.AnnotationUrl(destination);
  }

  Future<pw.Widget> _list(md.Element element, {required bool ordered}) async {
    final children = element.children ?? const <md.Node>[];
    final items = <pw.Widget>[];
    var index = _parseStartIndex(element);

    for (final child in children) {
      if (child is! md.Element || child.tag != 'li') {
        continue;
      }
      final marker = ordered ? '${index++}.' : '\u2022';
      items.add(
        pw.Padding(
          padding: const pw.EdgeInsets.only(bottom: 4),
          child: pw.Row(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.SizedBox(
                width: _listIndent,
                child: pw.Text(marker, style: baseStyle),
              ),
              pw.Expanded(child: _richText(_flattenListItem(child), baseStyle)),
            ],
          ),
        ),
      );
    }

    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.stretch,
      children: items,
    );
  }

  int _parseStartIndex(md.Element element) {
    final start = int.tryParse(element.attributes['start'] ?? '');
    return start == null || start < 1 ? 1 : start;
  }

  List<md.Node> _flattenListItem(md.Element element) {
    final nodes = <md.Node>[];
    for (final child in element.children ?? const <md.Node>[]) {
      if (child is md.Element && child.tag == 'p') {
        nodes.addAll(child.children ?? const <md.Node>[]);
      } else {
        nodes.add(child);
      }
    }
    return nodes;
  }

  Future<pw.Widget> _blockquote(md.Element element) async {
    final blocks = await _buildBlocks(element.children ?? const <md.Node>[]);
    return pw.Container(
      decoration: const pw.BoxDecoration(
        border: pw.Border(
          left: pw.BorderSide(color: PdfColors.grey600, width: 2),
        ),
      ),
      padding: const pw.EdgeInsets.only(left: 10),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.stretch,
        children: blocks,
      ),
    );
  }

  pw.Widget _codeBlock(String text) {
    return pw.Container(
      color: PdfColors.grey100,
      padding: const pw.EdgeInsets.all(8),
      child: pw.Text(
        text.trimRight(),
        style: codeStyle,
        overflow: pw.TextOverflow.span,
      ),
    );
  }

  pw.Widget _table(md.Element element) {
    final rows = <pw.TableRow>[];
    for (final row in _tableRows(element)) {
      rows.add(
        pw.TableRow(children: row.map(_tableCell).toList(growable: false)),
      );
    }

    if (rows.isEmpty) {
      return pw.SizedBox();
    }

    return pw.Table(
      border: pw.TableBorder.all(color: PdfColors.grey400, width: 0.5),
      defaultColumnWidth: const pw.FlexColumnWidth(),
      children: rows,
    );
  }

  Iterable<List<md.Element>> _tableRows(md.Element element) sync* {
    for (final child in element.children ?? const <md.Node>[]) {
      if (child is md.Element && child.tag == 'tr') {
        yield child.children?.whereType<md.Element>().toList() ??
            const <md.Element>[];
      } else if (child is md.Element) {
        yield* _tableRows(child);
      }
    }
  }

  pw.Widget _tableCell(md.Element element) {
    final isHeader = element.tag == 'th';
    final style = isHeader
        ? baseStyle.copyWith(fontWeight: pw.FontWeight.bold)
        : baseStyle;
    return pw.Padding(
      padding: const pw.EdgeInsets.all(5),
      child: _richText(element.children, style),
    );
  }

  Future<pw.Widget> _imageBlock(md.Element element) async {
    final image = RevelationMarkdownImageData.fromMarkdownElement(element);
    if (image == null) {
      return _placeholder('');
    }

    final bytes = await _loadImageBytes(image);
    if (bytes == null) {
      return _placeholder(image.alt);
    }

    final width = image.width ?? (image.isBlockImage ? 320.0 : null);
    final height = image.height ?? (image.isBlockImage ? 180.0 : null);
    final imageWidget = _isSvgImage(image, bytes)
        ? pw.SvgImage(
            svg: utf8.decode(bytes),
            width: width,
            height: height,
            fit: pw.BoxFit.contain,
          )
        : pw.Image(
            pw.MemoryImage(bytes),
            width: width,
            height: height,
            fit: pw.BoxFit.contain,
          );

    final content = <pw.Widget>[imageWidget];
    final caption = image.caption;
    if (caption != null && caption.trim().isNotEmpty) {
      content.add(
        pw.Padding(
          padding: const pw.EdgeInsets.only(top: 5),
          child: pw.Text(
            caption.trim(),
            style: baseStyle.copyWith(fontSize: 9, color: PdfColors.grey700),
            textAlign: _textAlignFor(image.alignment),
          ),
        ),
      );
    }

    return pw.Align(
      alignment: _alignmentFor(image.alignment),
      child: pw.Column(
        crossAxisAlignment: _crossAxisAlignmentFor(image.alignment),
        children: content,
      ),
    );
  }

  Future<Uint8List?> _loadImageBytes(RevelationMarkdownImageData image) async {
    final assetPath = image.source.assetPath;
    if (assetPath != null && assetPath.isNotEmpty) {
      try {
        final data = await rootBundle.load(assetPath);
        return data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
      } catch (_) {
        return null;
      }
    }

    final request = image.toLoadRequest();
    final loader = markdownImageLoader;
    if (request == null || loader == null) {
      return null;
    }

    final result = await loader.loadImage(request);
    if (!result.isSuccess || result.bytes == null) {
      return null;
    }
    return result.bytes;
  }

  bool _isSvgImage(RevelationMarkdownImageData image, Uint8List bytes) {
    if (image.source.isSvg) {
      return true;
    }
    final prefix = utf8.decode(bytes.take(120).toList(), allowMalformed: true);
    return prefix.trimLeft().startsWith('<svg');
  }

  pw.Widget _placeholder(String label) {
    final normalized = label.trim();
    return pw.Container(
      padding: const pw.EdgeInsets.all(8),
      decoration: pw.BoxDecoration(
        color: PdfColors.grey100,
        border: pw.Border.all(color: PdfColors.grey400, width: 0.5),
      ),
      child: pw.Text(
        normalized.isEmpty ? 'Content unavailable for PDF export' : normalized,
        style: baseStyle.copyWith(fontSize: 9, color: PdfColors.grey700),
      ),
    );
  }

  pw.Widget _spaced(pw.Widget child) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: _blockSpacing),
      child: child,
    );
  }

  pw.Alignment _alignmentFor(RevelationMarkdownImageAlignment alignment) {
    switch (alignment) {
      case RevelationMarkdownImageAlignment.left:
        return pw.Alignment.centerLeft;
      case RevelationMarkdownImageAlignment.right:
        return pw.Alignment.centerRight;
      case RevelationMarkdownImageAlignment.center:
        return pw.Alignment.center;
    }
  }

  pw.CrossAxisAlignment _crossAxisAlignmentFor(
    RevelationMarkdownImageAlignment alignment,
  ) {
    switch (alignment) {
      case RevelationMarkdownImageAlignment.left:
        return pw.CrossAxisAlignment.start;
      case RevelationMarkdownImageAlignment.right:
        return pw.CrossAxisAlignment.end;
      case RevelationMarkdownImageAlignment.center:
        return pw.CrossAxisAlignment.center;
    }
  }

  pw.TextAlign _textAlignFor(RevelationMarkdownImageAlignment alignment) {
    switch (alignment) {
      case RevelationMarkdownImageAlignment.left:
        return pw.TextAlign.left;
      case RevelationMarkdownImageAlignment.right:
        return pw.TextAlign.right;
      case RevelationMarkdownImageAlignment.center:
        return pw.TextAlign.center;
    }
  }
}

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:get_it/get_it.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/core/platform/file_downloader.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';

const String _revelationMarkdownPdfBaseFontAsset =
    'assets/fonts/Arimo/Arimo.ttf';
const String _revelationMarkdownPdfCopticFontAsset =
    'assets/fonts/NotoSansCoptic/NotoSansCoptic-Regular.ttf';
const String _revelationMarkdownPdfSymbolsFontAsset =
    'assets/fonts/NotoSansSymbols2/NotoSansSymbols2-Regular.ttf';
const String revelationMarkdownPdfAuthor = 'Karnauhov Oleh';
const String revelationMarkdownPdfUnknownBlockLink =
    'https://www.revelation.website';
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
  'Noto Sans Symbols2': _revelationMarkdownPdfSymbolsFontAsset,
};

typedef RevelationMarkdownPdfSaver =
    Future<String?> Function({
      required Uint8List bytes,
      required String fileName,
      required String mimeType,
    });
typedef RevelationMarkdownPdfUnknownBlockDescriptionBuilder =
    String Function(String blockName);

class RevelationMarkdownPdfStrings {
  RevelationMarkdownPdfStrings({
    required this.imageNotLoaded,
    required this.contentUnavailable,
    required this.youtubeUnavailableTitle,
    required this.youtubeUnavailableDescription,
    required this.unknownBlockTitle,
    required this.unknownBlockDescription,
    required this.unknownBlockUpdateHint,
    required this.unknownBlockUpdateAction,
  });

  factory RevelationMarkdownPdfStrings.fromLocalizations(
    AppLocalizations l10n,
  ) {
    return RevelationMarkdownPdfStrings(
      imageNotLoaded: l10n.image_not_loaded,
      contentUnavailable: l10n.image_not_loaded,
      youtubeUnavailableTitle: l10n.markdown_youtube_unavailable_title,
      youtubeUnavailableDescription:
          l10n.markdown_youtube_unavailable_description,
      unknownBlockTitle: l10n.markdown_unknown_block_title,
      unknownBlockDescription: l10n.markdown_unknown_block_description,
      unknownBlockUpdateHint: l10n.markdown_unknown_block_update_hint,
      unknownBlockUpdateAction: l10n.markdown_unknown_block_update_action,
    );
  }

  static final RevelationMarkdownPdfStrings
  fallback = RevelationMarkdownPdfStrings(
    imageNotLoaded: 'Image not loaded',
    contentUnavailable: 'Content unavailable for PDF export',
    youtubeUnavailableTitle: 'YouTube video unavailable',
    youtubeUnavailableDescription:
        'This YouTube block could not be rendered in the embedded player.',
    unknownBlockTitle: 'Unsupported content block',
    unknownBlockDescription: (blockName) =>
        'This version of the app cannot display the `$blockName` block.',
    unknownBlockUpdateHint:
        'Open the downloads page to install a newer app version for your platform.',
    unknownBlockUpdateAction: 'Update app',
  );

  final String imageNotLoaded;
  final String contentUnavailable;
  final String youtubeUnavailableTitle;
  final String youtubeUnavailableDescription;
  final String unknownBlockTitle;
  final RevelationMarkdownPdfUnknownBlockDescriptionBuilder
  unknownBlockDescription;
  final String unknownBlockUpdateHint;
  final String unknownBlockUpdateAction;
}

Future<_RevelationMarkdownPdfFonts>? _pdfFontsFuture;

Future<String?> exportRevelationMarkdownPdf({
  required String markdown,
  required String documentTitle,
  required String appName,
  MarkdownImageLoader? markdownImageLoader,
  RevelationMarkdownPdfStrings? strings,
  RevelationMarkdownPdfSaver? saveFile,
}) async {
  final title = _normalizeDocumentTitle(documentTitle);
  final bytes = await buildRevelationMarkdownPdfData(
    markdown: markdown,
    documentTitle: title,
    appName: appName,
    pageFormat: PdfPageFormat.a4,
    markdownImageLoader: markdownImageLoader,
    strings: strings,
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
  RevelationMarkdownPdfStrings? strings,
}) async {
  final fonts = await _loadPdfFonts();
  final theme = fonts.toTheme();
  final title = _normalizeDocumentTitle(documentTitle);
  final buildContext = _RevelationMarkdownPdfBuildContext(
    markdownImageLoader: _resolveMarkdownImageLoader(markdownImageLoader),
    contentWidth: _contentWidthFor(pageFormat),
    contentHeight: _contentHeightFor(pageFormat),
    strings: strings ?? RevelationMarkdownPdfStrings.fallback,
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

double _contentWidthFor(PdfPageFormat pageFormat) {
  final width =
      pageFormat.availableWidth - (revelationMarkdownPdfPageMargin * 2);
  if (width > 0) {
    return width;
  }
  return pageFormat.width;
}

double _contentHeightFor(PdfPageFormat pageFormat) {
  final height =
      pageFormat.availableHeight - (revelationMarkdownPdfPageMargin * 2);
  if (height > 0) {
    return height;
  }
  return pageFormat.height;
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
  final symbolsFont = pw.Font.ttf(
    await rootBundle.load(_revelationMarkdownPdfSymbolsFontAsset),
  );
  return _RevelationMarkdownPdfFonts(
    base: baseFont,
    fallback: [copticFont, symbolsFont],
  );
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

class _PdfSize {
  const _PdfSize({required this.width, required this.height});

  final double width;
  final double height;
}

class _RevelationMarkdownPdfBuildContext {
  _RevelationMarkdownPdfBuildContext({
    required this.markdownImageLoader,
    required this.contentWidth,
    required this.contentHeight,
    required this.strings,
  });

  static const double _blockSpacing = 8;
  static const double _listIndent = 18;
  static const double _defaultBlockImageWidth = 320;
  static const double _defaultBlockImageHeight = 180;
  static const double _defaultInlineImageWidth = 320;
  static const double _defaultInlineImageHeight = 180;
  static const double _defaultYoutubeWidth = 960;
  static const double _unknownBlockMaxWidth = 420;

  final MarkdownImageLoader? markdownImageLoader;
  final double contentWidth;
  final double contentHeight;
  final RevelationMarkdownPdfStrings strings;
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
        final imageElement = _singleImageChild(node);
        if (imageElement != null) {
          return _spaced(await _imageBlock(imageElement));
        }
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
        return _spaced(await _youtubeBlock(node));
      case RevelationMarkdownUnknownBlockData.tag:
        return _spaced(_unknownBlock(node));
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

  md.Element? _singleImageChild(md.Element element) {
    final children = element.children;
    if (children == null || children.isEmpty) {
      return null;
    }

    md.Element? imageElement;
    for (final child in children) {
      if (child is md.Text && child.text.trim().isEmpty) {
        continue;
      }
      if (child is md.Element && child.tag == 'img' && imageElement == null) {
        imageElement = child;
        continue;
      }
      return null;
    }
    return imageElement;
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

    final imageWidget = _buildPdfImageWidget(image: image, bytes: bytes);
    if (imageWidget == null) {
      return _placeholder(image.alt);
    }

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

  pw.Widget? _buildPdfImageWidget({
    required RevelationMarkdownImageData image,
    required Uint8List bytes,
  }) {
    if (_isSvgImage(image, bytes)) {
      return _buildSvgImageWidget(image: image, bytes: bytes);
    }
    return _buildRasterImageWidget(image: image, bytes: bytes);
  }

  pw.Widget? _buildSvgImageWidget({
    required RevelationMarkdownImageData image,
    required Uint8List bytes,
  }) {
    final svg = utf8.decode(bytes, allowMalformed: true);
    final intrinsicSize = _parseSvgSize(svg);
    final size = _resolveMediaSize(
      explicitWidth: image.width,
      explicitHeight: image.height,
      intrinsicWidth: intrinsicSize?.width,
      intrinsicHeight: intrinsicSize?.height,
      defaultWidth: image.isBlockImage
          ? _defaultBlockImageWidth
          : _defaultInlineImageWidth,
      defaultHeight: image.isBlockImage
          ? _defaultBlockImageHeight
          : _defaultInlineImageHeight,
      useDefaultSizeWhenUnspecified: image.isBlockImage,
    );

    try {
      return pw.SvgImage(
        svg: svg,
        width: size.width,
        height: size.height,
        fit: pw.BoxFit.contain,
      );
    } catch (_) {
      return null;
    }
  }

  pw.Widget? _buildRasterImageWidget({
    required RevelationMarkdownImageData image,
    required Uint8List bytes,
  }) {
    final imageProvider = _memoryImageOrNull(bytes);
    if (imageProvider == null) {
      return null;
    }

    final size = _resolveMediaSize(
      explicitWidth: image.width,
      explicitHeight: image.height,
      intrinsicWidth: imageProvider.width?.toDouble(),
      intrinsicHeight: imageProvider.height?.toDouble(),
      defaultWidth: image.isBlockImage
          ? _defaultBlockImageWidth
          : _defaultInlineImageWidth,
      defaultHeight: image.isBlockImage
          ? _defaultBlockImageHeight
          : _defaultInlineImageHeight,
      useDefaultSizeWhenUnspecified: image.isBlockImage,
    );

    return pw.Image(
      imageProvider,
      width: size.width,
      height: size.height,
      fit: pw.BoxFit.contain,
    );
  }

  Future<pw.Widget> _youtubeBlock(md.Element element) async {
    final video = RevelationMarkdownYoutubeData.fromMarkdownElement(element);
    if (video == null || !video.isValid) {
      return _youtubeUnavailableCard();
    }

    final targetWidth = video.maxWidth ?? _defaultYoutubeWidth;
    final size = _resolveMediaSize(
      explicitWidth: targetWidth,
      explicitHeight: targetWidth / video.resolvedAspectRatio,
      intrinsicWidth: targetWidth,
      intrinsicHeight: targetWidth / video.resolvedAspectRatio,
      defaultWidth: _defaultYoutubeWidth,
      defaultHeight: _defaultYoutubeWidth / video.resolvedAspectRatio,
    );
    final thumbnail = await _loadYoutubeThumbnailBytes(video);
    final poster = thumbnail == null
        ? _youtubePosterFallback()
        : _youtubeThumbnailImage(thumbnail, size: size);
    final player = pw.ClipRRect(
      horizontalRadius: 12,
      verticalRadius: 12,
      child: pw.SizedBox(
        width: size.width,
        height: size.height,
        child: pw.Stack(
          fit: pw.StackFit.expand,
          children: [
            poster,
            pw.Positioned.fill(
              child: pw.Opacity(
                opacity: 0.18,
                child: pw.Container(color: PdfColors.black),
              ),
            ),
            pw.Center(child: _playButton()),
          ],
        ),
      ),
    );
    final destination = video.originalVideoUri?.toString();
    final linkedPlayer = destination == null
        ? player
        : pw.UrlLink(destination: destination, child: player);

    return pw.Center(child: linkedPlayer);
  }

  pw.Widget _youtubeUnavailableCard() {
    return pw.Center(
      child: pw.SizedBox(
        width: _fitWidth(_unknownBlockMaxWidth),
        child: pw.Container(
          padding: const pw.EdgeInsets.all(16),
          decoration: pw.BoxDecoration(
            color: const PdfColor.fromInt(0xffe7e0ec),
            borderRadius: pw.BorderRadius.circular(12),
            border: pw.Border.all(
              color: const PdfColor.fromInt(0xffcac4d0),
              width: 0.5,
            ),
          ),
          child: pw.Column(
            mainAxisSize: pw.MainAxisSize.min,
            children: [
              _videoIcon(),
              pw.SizedBox(height: 12),
              pw.Text(
                strings.youtubeUnavailableTitle,
                textAlign: pw.TextAlign.center,
                style: baseStyle.copyWith(
                  fontSize: 12,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
              pw.SizedBox(height: 8),
              pw.Text(
                strings.youtubeUnavailableDescription,
                textAlign: pw.TextAlign.center,
                style: baseStyle.copyWith(
                  fontSize: 9.5,
                  color: const PdfColor.fromInt(0xff49454f),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  pw.Widget _youtubeThumbnailImage(Uint8List bytes, {required _PdfSize size}) {
    final imageProvider = _memoryImageOrNull(bytes);
    if (imageProvider == null) {
      return _youtubePosterFallback();
    }
    return pw.Image(
      imageProvider,
      width: size.width,
      height: size.height,
      fit: pw.BoxFit.cover,
    );
  }

  pw.Widget _youtubePosterFallback() {
    return pw.Container(color: PdfColors.black);
  }

  pw.Widget _playButton() {
    return pw.Container(
      width: 54,
      height: 54,
      decoration: const pw.BoxDecoration(
        shape: pw.BoxShape.circle,
        color: PdfColor(0, 0, 0, 0.66),
      ),
      child: pw.Center(
        child: pw.CustomPaint(
          size: const PdfPoint(18, 22),
          painter: (canvas, size) {
            canvas
              ..setFillColor(PdfColors.white)
              ..moveTo(size.x * 0.25, size.y * 0.1)
              ..lineTo(size.x * 0.25, size.y * 0.9)
              ..lineTo(size.x * 0.9, size.y * 0.5)
              ..closePath()
              ..fillPath();
          },
        ),
      ),
    );
  }

  pw.Widget _videoIcon() {
    return pw.CustomPaint(
      size: const PdfPoint(36, 36),
      painter: (canvas, size) {
        final centerX = size.x / 2;
        final centerY = size.y / 2;
        canvas
          ..setStrokeColor(const PdfColor.fromInt(0xff49454f))
          ..setLineWidth(2)
          ..drawEllipse(centerX, centerY, 16, 16)
          ..strokePath()
          ..setFillColor(const PdfColor.fromInt(0xff49454f))
          ..moveTo(centerX - 4, centerY - 8)
          ..lineTo(centerX - 4, centerY + 8)
          ..lineTo(centerX + 8, centerY)
          ..closePath()
          ..fillPath();
      },
    );
  }

  Future<Uint8List?> _loadYoutubeThumbnailBytes(
    RevelationMarkdownYoutubeData video,
  ) async {
    final loader = markdownImageLoader;
    if (loader == null) {
      return null;
    }

    for (final uri in _youtubeThumbnailUris(video.videoId)) {
      final source = RevelationMarkdownImageSource.parse(uri.toString());
      final result = await loader.loadImage(
        MarkdownImageRequest(
          kind: MarkdownImageRequestKind.network,
          cacheKey: 'youtube-thumbnail:${video.videoId}:${uri.path}',
          networkUri: uri,
          guessedMimeType: 'image/jpeg',
          localRelativePath: source.buildLocalRelativePath(
            mimeType: 'image/jpeg',
          ),
        ),
      );
      if (result.isSuccess && result.bytes != null) {
        return result.bytes;
      }
    }
    return null;
  }

  Iterable<Uri> _youtubeThumbnailUris(String videoId) sync* {
    yield Uri.https('i.ytimg.com', '/vi/$videoId/hqdefault.jpg');
  }

  pw.Widget _unknownBlock(md.Element element) {
    final block = RevelationMarkdownUnknownBlockData.fromMarkdownElement(
      element,
    );
    if (block == null) {
      return _placeholder('');
    }

    final card = pw.Center(
      child: pw.SizedBox(
        width: _fitWidth(_unknownBlockMaxWidth),
        child: pw.Container(
          padding: const pw.EdgeInsets.all(16),
          decoration: pw.BoxDecoration(
            color: const PdfColor.fromInt(0xffe7e0ec),
            borderRadius: pw.BorderRadius.circular(12),
            border: pw.Border.all(
              color: const PdfColor.fromInt(0xffcac4d0),
              width: 0.5,
            ),
          ),
          child: pw.Column(
            mainAxisSize: pw.MainAxisSize.min,
            children: [
              _unknownBlockIcon(),
              pw.SizedBox(height: 12),
              pw.Text(
                strings.unknownBlockTitle,
                textAlign: pw.TextAlign.center,
                style: baseStyle.copyWith(
                  fontSize: 12,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
              pw.SizedBox(height: 8),
              pw.Text(
                strings.unknownBlockDescription(block.name),
                textAlign: pw.TextAlign.center,
                style: baseStyle.copyWith(
                  color: const PdfColor.fromInt(0xff49454f),
                ),
              ),
              pw.SizedBox(height: 8),
              pw.Text(
                strings.unknownBlockUpdateHint,
                textAlign: pw.TextAlign.center,
                style: baseStyle.copyWith(
                  fontSize: 9.5,
                  color: const PdfColor.fromInt(0xff49454f),
                ),
              ),
              pw.SizedBox(height: 16),
              _unknownBlockButton(),
            ],
          ),
        ),
      ),
    );

    return pw.UrlLink(
      destination: revelationMarkdownPdfUnknownBlockLink,
      child: card,
    );
  }

  pw.Widget _unknownBlockButton() {
    return pw.Container(
      padding: const pw.EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: pw.BoxDecoration(
        color: const PdfColor.fromInt(0xffeaddff),
        borderRadius: pw.BorderRadius.circular(20),
      ),
      child: pw.Text(
        strings.unknownBlockUpdateAction,
        style: baseStyle.copyWith(
          fontSize: 10,
          fontWeight: pw.FontWeight.bold,
          color: const PdfColor.fromInt(0xff4f378b),
        ),
      ),
    );
  }

  pw.Widget _unknownBlockIcon() {
    return pw.CustomPaint(
      size: const PdfPoint(32, 32),
      painter: (canvas, size) {
        canvas
          ..setStrokeColor(const PdfColor.fromInt(0xff49454f))
          ..setLineWidth(2)
          ..drawRRect(5, 5, size.x - 10, size.y - 10, 5, 5)
          ..strokePath()
          ..moveTo(10, 10)
          ..lineTo(size.x - 10, size.y - 10)
          ..moveTo(size.x - 10, 10)
          ..lineTo(10, size.y - 10)
          ..strokePath();
      },
    );
  }

  pw.MemoryImage? _memoryImageOrNull(Uint8List bytes) {
    try {
      return pw.MemoryImage(bytes);
    } catch (_) {
      return null;
    }
  }

  _PdfSize _resolveMediaSize({
    required double? explicitWidth,
    required double? explicitHeight,
    required double? intrinsicWidth,
    required double? intrinsicHeight,
    required double defaultWidth,
    required double defaultHeight,
    bool useDefaultSizeWhenUnspecified = false,
  }) {
    final safeExplicitWidth = _positiveOrNull(explicitWidth);
    final safeExplicitHeight = _positiveOrNull(explicitHeight);
    final safeIntrinsicWidth = _positiveOrNull(intrinsicWidth);
    final safeIntrinsicHeight = _positiveOrNull(intrinsicHeight);
    final safeDefaultWidth = _positiveOrNull(defaultWidth) ?? 1;
    final safeDefaultHeight = _positiveOrNull(defaultHeight) ?? 1;
    final aspectRatio = _resolveAspectRatio(
      width: safeExplicitWidth,
      height: safeExplicitHeight,
      fallbackWidth: safeIntrinsicWidth,
      fallbackHeight: safeIntrinsicHeight,
      defaultWidth: safeDefaultWidth,
      defaultHeight: safeDefaultHeight,
    );

    late double width;
    late double height;
    if (safeExplicitWidth != null && safeExplicitHeight != null) {
      width = safeExplicitWidth;
      height = safeExplicitHeight;
    } else if (safeExplicitWidth != null) {
      width = safeExplicitWidth;
      height = safeExplicitWidth / aspectRatio;
    } else if (safeExplicitHeight != null) {
      height = safeExplicitHeight;
      width = safeExplicitHeight * aspectRatio;
    } else if (useDefaultSizeWhenUnspecified) {
      width = safeDefaultWidth;
      height = safeDefaultHeight;
    } else if (safeIntrinsicWidth != null && safeIntrinsicHeight != null) {
      width = safeIntrinsicWidth;
      height = safeIntrinsicHeight;
    } else {
      width = safeDefaultWidth;
      height = safeDefaultHeight;
    }

    return _scaleMediaToPage(width: width, height: height);
  }

  double _resolveAspectRatio({
    required double? width,
    required double? height,
    required double? fallbackWidth,
    required double? fallbackHeight,
    required double defaultWidth,
    required double defaultHeight,
  }) {
    if (width != null && height != null) {
      return width / height;
    }
    if (fallbackWidth != null && fallbackHeight != null) {
      return fallbackWidth / fallbackHeight;
    }
    return defaultWidth / defaultHeight;
  }

  _PdfSize _scaleMediaToPage({required double width, required double height}) {
    final maxWidth = _positiveOrNull(contentWidth);
    final maxHeight = _positiveOrNull(contentHeight);
    var scale = 1.0;

    if (maxWidth != null && width > maxWidth) {
      scale = maxWidth / width;
    }
    if (maxHeight != null && height * scale > maxHeight) {
      final heightScale = maxHeight / height;
      if (heightScale < scale) {
        scale = heightScale;
      }
    }

    if (scale <= 0) {
      return const _PdfSize(width: 1, height: 1);
    }
    return _PdfSize(width: width * scale, height: height * scale);
  }

  double _fitWidth(double width) {
    final maxWidth = _positiveOrNull(contentWidth);
    if (maxWidth != null && width > maxWidth) {
      return maxWidth;
    }
    return _positiveOrNull(width) ?? 1;
  }

  double? _positiveOrNull(double? value) {
    if (value == null || value <= 0 || value.isNaN || value.isInfinite) {
      return null;
    }
    return value;
  }

  _PdfSize? _parseSvgSize(String svg) {
    final width = _parseSvgDimension(
      RegExp(r'''\bwidth\s*=\s*["']([^"']+)["']''').firstMatch(svg)?.group(1),
    );
    final height = _parseSvgDimension(
      RegExp(r'''\bheight\s*=\s*["']([^"']+)["']''').firstMatch(svg)?.group(1),
    );
    if (width != null && height != null) {
      return _PdfSize(width: width, height: height);
    }

    final viewBox = RegExp(
      r'''\bviewBox\s*=\s*["']\s*'''
      r'[-+]?(?:\d+(?:\.\d+)?|\.\d+)[,\s]+'
      r'[-+]?(?:\d+(?:\.\d+)?|\.\d+)[,\s]+'
      r'([-+]?(?:\d+(?:\.\d+)?|\.\d+))[,\s]+'
      r'([-+]?(?:\d+(?:\.\d+)?|\.\d+))',
      caseSensitive: false,
    ).firstMatch(svg);
    if (viewBox == null) {
      return null;
    }

    final viewBoxWidth = double.tryParse(viewBox.group(1) ?? '');
    final viewBoxHeight = double.tryParse(viewBox.group(2) ?? '');
    if (_positiveOrNull(viewBoxWidth) == null ||
        _positiveOrNull(viewBoxHeight) == null) {
      return null;
    }
    return _PdfSize(width: viewBoxWidth!, height: viewBoxHeight!);
  }

  double? _parseSvgDimension(String? rawValue) {
    final match = RegExp(
      r'^\s*([0-9]+(?:\.[0-9]+)?|\.[0-9]+)',
    ).firstMatch(rawValue ?? '');
    if (match == null) {
      return null;
    }
    return _positiveOrNull(double.tryParse(match.group(1)!));
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
        normalized.isEmpty ? strings.contentUnavailable : normalized,
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

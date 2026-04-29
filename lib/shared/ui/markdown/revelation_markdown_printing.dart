import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:get_it/get_it.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_config.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_block_syntax.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_unknown_block_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_youtube_data.dart';

const String _revelationMarkdownPrintFontAsset = 'assets/fonts/Arimo/Arimo.ttf';

const Map<String, String> revelationMarkdownPrintFonts = {
  'Arimo': _revelationMarkdownPrintFontAsset,
  'Segoe UI': _revelationMarkdownPrintFontAsset,
  'Segoe UI Symbol': _revelationMarkdownPrintFontAsset,
  'Segoe UI Variable': _revelationMarkdownPrintFontAsset,
  'Roboto': _revelationMarkdownPrintFontAsset,
  'Arial': _revelationMarkdownPrintFontAsset,
  'Helvetica Neue': _revelationMarkdownPrintFontAsset,
  'Liberation Sans': _revelationMarkdownPrintFontAsset,
  'Ubuntu': _revelationMarkdownPrintFontAsset,
  'sans-serif': _revelationMarkdownPrintFontAsset,
  'monospace': _revelationMarkdownPrintFontAsset,
};

Future<pw.Font>? _printFontFuture;

Future<void> printRevelationMarkdown({
  required String markdown,
  required String documentTitle,
  MarkdownImageLoader? markdownImageLoader,
}) async {
  final title = _normalizeDocumentTitle(documentTitle);

  await Printing.layoutPdf(
    name: title,
    format: PdfPageFormat.a4,
    dynamicLayout: true,
    onLayout: (format) => buildRevelationMarkdownPdfData(
      markdown: markdown,
      documentTitle: title,
      pageFormat: format,
      markdownImageLoader: markdownImageLoader,
    ),
  );
}

Future<Uint8List> buildRevelationMarkdownPdfData({
  required String markdown,
  required String documentTitle,
  required PdfPageFormat pageFormat,
  MarkdownImageLoader? markdownImageLoader,
}) async {
  final font = await _loadPrintFont();
  final title = _normalizeDocumentTitle(documentTitle);
  final buildContext = _RevelationMarkdownPdfBuildContext(
    markdownImageLoader: _resolveMarkdownImageLoader(markdownImageLoader),
  );
  final widgets = await buildContext.build(markdown);

  final document = pw.Document(
    title: title,
    creator: 'Revelation',
    producer: 'Revelation',
    theme: pw.ThemeData.withFont(
      base: font,
      bold: font,
      italic: font,
      boldItalic: font,
    ),
  );

  document.addPage(
    pw.MultiPage(
      pageFormat: pageFormat,
      theme: pw.ThemeData.withFont(
        base: font,
        bold: font,
        italic: font,
        boldItalic: font,
      ),
      build: (_) => widgets.isEmpty ? <pw.Widget>[pw.SizedBox()] : widgets,
    ),
  );

  return document.save(enableEventLoopBalancing: true);
}

Future<pw.Font> _loadPrintFont() {
  _printFontFuture ??= rootBundle
      .load(_revelationMarkdownPrintFontAsset)
      .then(pw.Font.ttf);
  return _printFontFuture!;
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

class _RevelationMarkdownPdfBuildContext {
  _RevelationMarkdownPdfBuildContext({required this.markdownImageLoader});

  static const double _blockSpacing = 8;
  static const double _listIndent = 18;

  final MarkdownImageLoader? markdownImageLoader;

  final pw.TextStyle baseStyle = const pw.TextStyle(
    fontSize: 11,
    height: 1.35,
    color: PdfColors.black,
  );
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
        return _spaced(_richText(node.children, _headingStyle(node.tag)));
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
        spans.add(pw.TextSpan(text: node.text, style: style));
        continue;
      }
      if (node is! md.Element) {
        continue;
      }

      final nextStyle = _styleForInlineTag(node.tag, style);
      if (node.tag == 'br') {
        spans.add(pw.TextSpan(text: '\n', style: nextStyle));
      } else if (node.tag == 'code') {
        spans.add(pw.TextSpan(text: node.textContent, style: nextStyle));
      } else if (node.tag == 'img') {
        final image = RevelationMarkdownImageData.fromMarkdownElement(node);
        final label = image?.alt ?? node.attributes['alt'] ?? '';
        if (label.trim().isNotEmpty) {
          spans.add(pw.TextSpan(text: label.trim(), style: nextStyle));
        }
      } else {
        spans.addAll(_inlineSpans(node.children, nextStyle));
      }
    }
    return spans;
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
      case 'a':
        return style.copyWith(
          color: PdfColors.blue700,
          decoration: pw.TextDecoration.underline,
        );
      case 'del':
        return style.copyWith(decoration: pw.TextDecoration.lineThrough);
      default:
        return style;
    }
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
        normalized.isEmpty ? 'Content unavailable for print' : normalized,
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

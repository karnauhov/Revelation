import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as image;
import 'package:pdf/pdf.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_pdf_export.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'markdown PDF export registers asset-backed aliases for common fonts',
    () {
      expect(
        revelationMarkdownPdfFonts['Arimo'],
        'assets/fonts/Arimo/Arimo.ttf',
      );
      expect(
        revelationMarkdownPdfFonts['Segoe UI'],
        'assets/fonts/Arimo/Arimo.ttf',
      );
      expect(
        revelationMarkdownPdfFonts['Roboto'],
        'assets/fonts/Arimo/Arimo.ttf',
      );
      expect(
        revelationMarkdownPdfFonts['monospace'],
        'assets/fonts/Arimo/Arimo.ttf',
      );
      expect(
        revelationMarkdownPdfFonts['Noto Sans Coptic'],
        'assets/fonts/NotoSansCoptic/NotoSansCoptic-Regular.ttf',
      );
      expect(
        revelationMarkdownPdfFonts['Noto Sans Symbols2'],
        'assets/fonts/NotoSansSymbols2/NotoSansSymbols2-Regular.ttf',
      );
    },
  );

  test('markdown PDF export uses explicit page margins', () {
    expect(revelationMarkdownPdfPageMargin, 18 * PdfPageFormat.mm);
  });

  test('markdown PDF export embeds document metadata', () async {
    const title = '\u041b\u0438\u0446\u0435\u043d\u0437\u0438\u044f Apache';
    const appName =
        '\u041e\u0442\u043a\u0440\u043e\u0432\u0435\u043d\u0438\u0435';

    final bytes = await buildRevelationMarkdownPdfData(
      markdown: '# $title\n\n\u0412\u0435\u0440\u0441\u0438\u044f 2.0',
      documentTitle: title,
      appName: appName,
      pageFormat: PdfPageFormat.a4,
    );

    expect(bytes, isNotEmpty);
    expect(
      _containsBytes(bytes, _utf16BeWithBom(title)),
      isTrue,
      reason: 'PDF metadata should preserve Cyrillic titles.',
    );
    expect(
      _containsPdfString(bytes, revelationMarkdownPdfAuthor),
      isTrue,
      reason: 'PDF metadata should include the configured author.',
    );
    expect(
      _containsPdfString(bytes, appName),
      isTrue,
      reason: 'PDF metadata subject should use the localized app name.',
    );
  });

  test(
    'markdown PDF export creates a hierarchical outline from headings',
    () async {
      final bytes = await buildRevelationMarkdownPdfData(
        markdown: '# Root\n\n## Child\n\n### Grandchild\n\n# Second',
        documentTitle: 'Heading outline',
        appName: 'Revelation',
        pageFormat: PdfPageFormat.a4,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(pdfText, contains('/Outlines'));
      expect(pdfText, contains('/PageMode/UseOutlines'));
      expect(pdfText, contains('/Count 2'));
      expect(pdfText, contains('/Count -2'));
      expect(pdfText, contains('/Count -1'));
      expect(_containsPdfString(bytes, 'Root'), isTrue);
      expect(_containsPdfString(bytes, 'Child'), isTrue);
      expect(_containsPdfString(bytes, 'Grandchild'), isTrue);
      expect(_containsPdfString(bytes, 'Second'), isTrue);
    },
  );

  test('markdown PDF export paginates long content', () async {
    final markdown = List<String>.generate(
      90,
      (index) =>
          'Paragraph $index. This printable text is long enough to require '
          'multiple pages when rendered on a small page format.',
    ).join('\n\n');

    final bytes = await buildRevelationMarkdownPdfData(
      markdown: markdown,
      documentTitle: 'Long article',
      appName: 'Revelation',
      pageFormat: PdfPageFormat.a6,
    );
    final pdfText = latin1.decode(bytes, allowInvalid: true);
    final pageCount = RegExp(r'/Type\s*/Page\b').allMatches(pdfText).length;

    expect(pageCount, greaterThan(1));
  });

  test(
    'markdown PDF export keeps text as PDF text with Coptic fallback',
    () async {
      final bytes = await buildRevelationMarkdownPdfData(
        markdown:
            'Text remains selectable.\n\n'
            '\u2c80\u2c81 \u2c82\u2c83 \u03e3\u03e9',
        documentTitle: 'Coptic text',
        appName: 'Revelation',
        pageFormat: PdfPageFormat.a4,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(pdfText, contains('/ToUnicode'));
      expect(pdfText, contains('NotoSansCoptic'));
      expect(pdfText, isNot(contains('/Subtype /Image')));
    },
  );

  test(
    'markdown PDF export keeps heavy exclamation symbol as PDF text',
    () async {
      final bytes = await buildRevelationMarkdownPdfData(
        markdown: 'Important ❗',
        documentTitle: 'Symbol text',
        appName: 'Revelation',
        pageFormat: PdfPageFormat.a4,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(pdfText, contains('/ToUnicode'));
      expect(pdfText, contains('NotoSansSymbols2'));
      expect(pdfText, isNot(contains('/Subtype /Image')));
    },
  );

  test('markdown PDF export downloads generated PDF bytes', () async {
    Uint8List? capturedBytes;
    String? capturedFileName;
    String? capturedMimeType;

    final location = await exportRevelationMarkdownPdf(
      markdown: '# Exported',
      documentTitle: ' Exported Article ',
      appName: 'Revelation',
      saveFile:
          ({
            required Uint8List bytes,
            required String fileName,
            required String mimeType,
          }) async {
            capturedBytes = bytes;
            capturedFileName = fileName;
            capturedMimeType = mimeType;
            return fileName;
          },
    );

    expect(location, 'Exported Article.pdf');
    expect(capturedBytes, isNotNull);
    expect(capturedBytes, isNotEmpty);
    expect(capturedFileName, 'Exported Article.pdf');
    expect(capturedMimeType, 'application/pdf');
  });

  test('markdown PDF export styles only http links as links', () {
    expect(
      isRevelationMarkdownPdfExternalHttpLink('https://example.com'),
      isTrue,
    );
    expect(
      isRevelationMarkdownPdfExternalHttpLink('HTTP://example.com'),
      isTrue,
    );

    for (final href in <String>[
      'dbfile:topic-media/sample.pdf',
      'screen:settings',
      'topic:intro',
      'bible:Rev.1.1',
      'word:logos',
      'strong:G25',
      'strong_picker:G25',
      'mailto:hello@example.com',
      '#local-anchor',
      'custom:future-link',
      '',
      ' httpx://not-http',
    ]) {
      expect(
        isRevelationMarkdownPdfExternalHttpLink(href),
        isFalse,
        reason: href,
      );
    }
  });

  test('markdown PDF export writes URL annotations for http links', () async {
    final bytes = await buildRevelationMarkdownPdfData(
      markdown:
          '[7 papyri and 12 uncials]'
          '(https://en.wikipedia.org/wiki/Biblical_manuscript)\n\n'
          '[Topic](topic:intro)',
      documentTitle: 'Links',
      appName: 'Revelation',
      pageFormat: PdfPageFormat.a4,
    );
    final pdfText = latin1.decode(bytes, allowInvalid: true);

    expect(pdfText, contains('/Subtype/Link'));
    expect(
      pdfText,
      contains('/URI(https://en.wikipedia.org/wiki/Biblical_manuscript)'),
    );
    expect(pdfText, isNot(contains('/URI(topic:intro)')));
  });

  test('markdown PDF export renders image-only paragraphs as images', () async {
    final loader = _FakeMarkdownImageLoader(
      resultsByUri: <String, MarkdownImageLoadResult>{
        'https://example.com/road.png': MarkdownImageLoadResult.success(
          bytes: _png1x1,
          mimeType: 'image/png',
        ),
      },
    );

    final bytes = await buildRevelationMarkdownPdfData(
      markdown: '![road](https://example.com/road.png#640x360)',
      documentTitle: 'Image paragraph',
      appName: 'Revelation',
      pageFormat: PdfPageFormat.a4,
      markdownImageLoader: loader,
    );

    expect(loader.requests, hasLength(1));
    expect(
      loader.requests.single.networkUri.toString(),
      'https://example.com/road.png',
    );
    expect(_containsPdfImage(bytes), isTrue);
    expect(
      _containsPdfString(bytes, 'road'),
      isFalse,
      reason: 'A standalone image should not collapse to its alt text.',
    );
  });

  test(
    'markdown PDF export renders youtube blocks as linked poster images',
    () async {
      final loader = _FakeMarkdownImageLoader(
        resultsByUri: <String, MarkdownImageLoadResult>{
          'https://i.ytimg.com/vi/Cp8LoFXv5j4/hqdefault.jpg':
              MarkdownImageLoadResult.success(
                bytes: _png1x1,
                mimeType: 'image/png',
              ),
        },
      );

      final bytes = await buildRevelationMarkdownPdfData(
        markdown: '''
{{youtube}}
id: Cp8LoFXv5j4
start: 30
width: 960
height: 540
{{/youtube}}
''',
        documentTitle: 'Video',
        appName: 'Revelation',
        pageFormat: PdfPageFormat.a4,
        markdownImageLoader: loader,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(
        loader.requests.single.networkUri.toString(),
        'https://i.ytimg.com/vi/Cp8LoFXv5j4/hqdefault.jpg',
      );
      expect(_containsPdfImage(bytes), isTrue);
      expect(
        pdfText,
        contains('/URI(https://www.youtube.com/watch?v=Cp8LoFXv5j4&t=30s)'),
      );
    },
  );

  test(
    'markdown PDF export links unknown block cards to the website',
    () async {
      final bytes = await buildRevelationMarkdownPdfData(
        markdown: '''
{{timeline}}
title: Seven seals
{{/timeline}}
''',
        documentTitle: 'Unknown block',
        appName: 'Revelation',
        pageFormat: PdfPageFormat.a4,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(pdfText, contains('/URI($revelationMarkdownPdfUnknownBlockLink)'));
    },
  );

  test('markdown PDF export segments combining overlines for decoration', () {
    expect(
      segmentRevelationMarkdownPdfTextForExport(
        '\u0399\u0305\u03a5\u0305 \u03a7\u0305\u03a5\u0305',
      ),
      <RevelationMarkdownPdfTextSegment>[
        const RevelationMarkdownPdfTextSegment('\u0399\u03a5', overlined: true),
        const RevelationMarkdownPdfTextSegment(' ', overlined: false),
        const RevelationMarkdownPdfTextSegment('\u03a7\u03a5', overlined: true),
      ],
    );
    expect(
      segmentRevelationMarkdownPdfTextForExport('A\u0305B'),
      <RevelationMarkdownPdfTextSegment>[
        const RevelationMarkdownPdfTextSegment('A', overlined: true),
        const RevelationMarkdownPdfTextSegment('B', overlined: false),
      ],
    );
  });
}

bool _containsBytes(Uint8List bytes, List<int> pattern) {
  if (pattern.isEmpty || pattern.length > bytes.length) {
    return false;
  }

  for (var i = 0; i <= bytes.length - pattern.length; i++) {
    var matched = true;
    for (var j = 0; j < pattern.length; j++) {
      if (bytes[i + j] != pattern[j]) {
        matched = false;
        break;
      }
    }
    if (matched) {
      return true;
    }
  }
  return false;
}

List<int> _utf16BeWithBom(String value) {
  final bytes = <int>[0xfe, 0xff];
  for (final unit in value.codeUnits) {
    bytes
      ..add((unit & 0xff00) >> 8)
      ..add(unit & 0x00ff);
  }
  return bytes;
}

bool _containsPdfString(Uint8List bytes, String value) {
  final latin1Bytes = _tryLatin1(value);
  return (latin1Bytes != null && _containsBytes(bytes, latin1Bytes)) ||
      _containsBytes(bytes, _utf16BeWithBom(value));
}

bool _containsPdfImage(Uint8List bytes) {
  final pdfText = latin1.decode(bytes, allowInvalid: true);
  return pdfText.contains('/Subtype/Image') ||
      pdfText.contains('/Subtype /Image');
}

List<int>? _tryLatin1(String value) {
  try {
    return latin1.encode(value);
  } catch (_) {
    return null;
  }
}

class _FakeMarkdownImageLoader implements MarkdownImageLoader {
  _FakeMarkdownImageLoader({required this.resultsByUri});

  final Map<String, MarkdownImageLoadResult> resultsByUri;
  final List<MarkdownImageRequest> requests = <MarkdownImageRequest>[];

  @override
  Future<MarkdownImageLoadResult> loadImage(
    MarkdownImageRequest request,
  ) async {
    requests.add(request);
    return resultsByUri[request.networkUri?.toString()] ??
        const MarkdownImageLoadResult.failure();
  }
}

final Uint8List _png1x1 = _createPng1x1();

Uint8List _createPng1x1() {
  final data = image.Image(width: 1, height: 1);
  data.setPixelRgb(0, 0, 255, 255, 255);
  return Uint8List.fromList(image.encodePng(data));
}

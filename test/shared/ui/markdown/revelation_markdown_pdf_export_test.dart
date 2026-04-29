import 'dart:convert';
import 'dart:typed_data';

import 'package:pdf/pdf.dart';
import 'package:flutter_test/flutter_test.dart';
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
    },
  );

  test('markdown PDF export uses explicit page margins', () {
    expect(revelationMarkdownPdfPageMargin, 18 * PdfPageFormat.mm);
  });

  test('markdown PDF export embeds a Unicode document title', () async {
    const title = 'Лицензия Apache';

    final bytes = await buildRevelationMarkdownPdfData(
      markdown: '# $title\n\nВерсия 2.0',
      documentTitle: title,
      pageFormat: PdfPageFormat.a4,
    );

    expect(bytes, isNotEmpty);
    expect(
      _containsBytes(bytes, _utf16BeWithBom(title)),
      isTrue,
      reason: 'PDF metadata should preserve Cyrillic titles.',
    );
  });

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
        markdown: 'Text remains selectable.\n\nⲀⲁ Ⲃⲃ ϣϩ',
        documentTitle: 'Coptic text',
        pageFormat: PdfPageFormat.a4,
      );
      final pdfText = latin1.decode(bytes, allowInvalid: true);

      expect(pdfText, contains('/ToUnicode'));
      expect(pdfText, contains('NotoSansCoptic'));
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

import 'dart:convert';
import 'dart:typed_data';

import 'package:pdf/pdf.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_printing.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('markdown printing registers asset-backed aliases for common fonts', () {
    expect(
      revelationMarkdownPrintFonts['Arimo'],
      'assets/fonts/Arimo/Arimo.ttf',
    );
    expect(
      revelationMarkdownPrintFonts['Segoe UI'],
      'assets/fonts/Arimo/Arimo.ttf',
    );
    expect(
      revelationMarkdownPrintFonts['Roboto'],
      'assets/fonts/Arimo/Arimo.ttf',
    );
    expect(
      revelationMarkdownPrintFonts['monospace'],
      'assets/fonts/Arimo/Arimo.ttf',
    );
  });

  test('markdown printing embeds a Unicode document title', () async {
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

  test('markdown printing paginates long content', () async {
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

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';

void main() {
  group('Bible text search', () {
    test('strips Strong tokens from visible Bible text', () {
      expect(
        plainBibleText('En G1722 arche G746 kai G2532 logos G3056'),
        'En arche kai logos',
      );
    });

    test('normalizes search query whitespace', () {
      expect(normalizeBibleSearchQuery('  En   arche  '), 'En arche');
    });

    test('finds phrase matches in visible text case-insensitively', () {
      expect(findBibleTextMatches('En arche kai en arche', 'en arche'), const [
        BibleTextMatch(start: 0, end: 8),
        BibleTextMatch(start: 13, end: 21),
      ]);
    });

    test('finds Greek matches without case and breathing marks', () {
      const text = '\u{1F10}\u{03BD} \u{1F00}\u{03C1}\u{03C7}\u{1FC7}';
      const query = '\u{0395}\u{039D} \u{0391}\u{03A1}\u{03A7}\u{0397}';

      final matches = findBibleTextMatches(text, query);

      expect(
        normalizeBibleSearchText(text),
        '\u{03B5}\u{03BD} \u{03B1}\u{03C1}\u{03C7}\u{03B7}',
      );
      expect(matches, const [BibleTextMatch(start: 0, end: text.length)]);
    });

    test('keeps decomposed combining marks inside highlighted matches', () {
      const text = '\u{03B1}\u{0313}\u{03C1}\u{03C7}\u{03B7}';

      expect(findBibleTextMatches(text, '\u{03B1}'), const [
        BibleTextMatch(start: 0, end: 2),
      ]);
      expect(findBibleTextMatches(text, '\u{03B1}\u{03C1}\u{03C7}\u{03B7}'), [
        const BibleTextMatch(start: 0, end: text.length),
      ]);
    });
  });
}

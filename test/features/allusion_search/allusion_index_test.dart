import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap map;
  setUpAll(() async => map = await BibleVerseMap.loadFromAssets());

  BibleVerseText verse(int book, int chapter, int verse, String text) =>
      BibleVerseText(
        verseKey: map
            .referenceFor(bookId: book, chapter: chapter, verse: verse)
            .verseKey,
        text: text,
      );
  AllusionQuery query({
    int book = 66,
    int chapter = 1,
    int verse = 1,
    int length = 1,
    AllusionScope scope = AllusionScope.wholeBible,
  }) => (
    bookId: book,
    chapter: chapter,
    verse: verse,
    length: length,
    scope: scope,
  );
  const weights = {
    10: 1.0,
    20: 1.0,
    30: 1.0,
    40: 1.0,
    50: 1.0,
    60: 1.0,
    3588: 0.0,
    3756: 0.35,
  };

  test(
    'the source counts repeated forms across the range and weighs each search ID once',
    () {
      final a = verse(66, 1, 1, 'λόγος G10 G10 θεός G20 καί G3588');
      final b = verse(66, 1, 2, 'λόγου G10 λόγος G10 G30 H10');
      final target = verse(1, 1, 1, 'word G10 second G20 third G30');
      final index = AllusionIndex.build(
        verseMap: map,
        verses: [a, b, target],
        baseWeights: weights,
      );
      final refs = [
        map.referenceForKey(a.verseKey)!,
        map.referenceForKey(b.verseKey)!,
      ];
      final summary = index.sourceVocabulary(refs, {
        a.verseKey: a.text,
        b.verseKey: b.text,
      });
      expect(summary.words.keys, [10, 20, 30]);
      expect(summary.words[10]!.occurrences, 3);
      expect(summary.words[10]!.form, 'λόγος');
      expect(summary.words[30]!.occurrences, 1);
      final result = index.search(query(chapter: 1, verse: 1, length: 2));
      expect(summary.words.keys, result.sourceNumbers);
      expect(
        summary.totalWeight,
        result.forLevel(AllusionLevel.verse).single.sharedWeight,
      );
      expect(
        summary.words.values.fold<double>(
          0.0,
          (sum, word) => sum + word.searchWeight,
        ),
        closeTo(summary.totalWeight, 1e-9),
      );
      final partial = index.sourceVocabulary(refs, {a.verseKey: a.text});
      expect(partial.totalWeight, summary.totalWeight);
      expect(partial.words[10]!.occurrences, isNull);
      expect(partial.words[20]!.occurrences, 1);
    },
  );

  test(
    'unique G numbers, source exclusion, weak words and testament scopes',
    () {
      final index = AllusionIndex.build(
        verseMap: map,
        baseWeights: weights,
        verses: [
          verse(66, 1, 1, 'a G10 G10 b G20 c G30 G3588 H10 H20 H30'),
          verse(1, 1, 1, 'G10 G20 G30'),
          verse(40, 1, 1, 'g10 g20 g30'),
          verse(1, 1, 2, 'H10 H20 H30 G3588'),
        ],
      );
      final results = index.search(query());
      expect(results.sourceNumbers, [10, 20, 30]);
      expect(results.forLevel(AllusionLevel.verse).length, 2);
      expect(
        results
            .forLevel(AllusionLevel.verse)
            .every((match) => match.score == 1),
        isTrue,
      );
      expect(
        index
            .search(query(scope: AllusionScope.oldTestament))
            .forLevel(AllusionLevel.verse)
            .single
            .reference
            .bookId,
        1,
      );
      expect(
        index
            .search(query(scope: AllusionScope.newTestament))
            .forLevel(AllusionLevel.verse)
            .single
            .reference
            .bookId,
        40,
      );
    },
  );

  test(
    'grammar alone cannot admit a candidate and long unrelated verses rank lower',
    () {
      final index = AllusionIndex.build(
        verseMap: map,
        baseWeights: weights,
        verses: [
          verse(66, 1, 1, 'G10 G20 G30 G3756'),
          verse(1, 1, 1, 'G10 G20 G30 G3756'),
          verse(1, 1, 2, 'G10 G20 G30 G40 G50 G60 G3756'),
          verse(1, 1, 3, 'G3756 G3588'),
        ],
      );
      final matches = index.search(query()).forLevel(AllusionLevel.verse);
      expect(matches.map((match) => match.reference.verse), [1, 2]);
      expect(matches.first.score, greaterThan(matches.last.score));
      expect(matches.first.numbers, contains(3756));
    },
  );

  test(
    'group coverage deduplicates matches across verses and uses a matching reference',
    () {
      final index = AllusionIndex.build(
        verseMap: map,
        baseWeights: weights,
        verses: [
          verse(66, 1, 1, 'G10 G20 G30'),
          verse(1, 1, 3, 'G10 G20'),
          verse(1, 1, 4, 'G20 G30'),
        ],
      );
      final results = index.search(query());
      expect(results.forLevel(AllusionLevel.verse), isEmpty);
      for (final level in [AllusionLevel.chapter, AllusionLevel.book]) {
        final match = results.forLevel(level).single;
        expect(match.numbers, [10, 20, 30]);
        expect(match.score, closeTo(1, 0.000001));
        expect(match.reference.verse, 3);
        expect(match.references.map((ref) => ref.verse), [3, 4]);
      }
    },
  );

  test(
    'group previews open the strongest concrete verse, retaining all contributors',
    () {
      final index = AllusionIndex.build(
        verseMap: map,
        baseWeights: weights,
        verses: [
          verse(66, 1, 1, 'G10 G20 G30'),
          verse(1, 1, 1, 'G10'),
          verse(1, 1, 2, 'G10 G20 G30'),
          verse(1, 1, 3, 'G3756'),
        ],
      );
      final results = index.search(query());
      for (final level in [AllusionLevel.chapter, AllusionLevel.book]) {
        final group = results.forLevel(level).single;
        expect(group.reference.verse, 2);
        expect(group.references.map((ref) => ref.verse), [2, 1]);
      }
    },
  );

  test('range crosses chapters and clips at the final verse', () {
    final index = AllusionIndex.build(
      verseMap: map,
      baseWeights: weights,
      verses: [
        verse(66, 1, 20, 'G10'),
        verse(66, 2, 1, 'G20 G30'),
        verse(1, 1, 1, 'G10 G20 G30'),
      ],
    );
    final results = index.search(query(verse: 20, length: 2));
    expect(results.end.chapter, 2);
    expect(results.sourceNumbers, [10, 20, 30]);
    expect(
      index.search(query(chapter: 22, verse: 21, length: 77)).end.verseKey,
      map.lastVerseKey,
    );
    expect(() => index.search(query(length: 0)), throwsRangeError);
  });

  test(
    'unknown number requires policy maintenance, invalid keys are rejected',
    () {
      expect(
        () => AllusionIndex.build(
          verseMap: map,
          baseWeights: weights,
          verses: [verse(1, 1, 1, 'G99999')],
        ),
        throwsFormatException,
      );
      expect(
        () => AllusionIndex.build(
          verseMap: map,
          baseWeights: weights,
          verses: [const BibleVerseText(verseKey: 'ZZZ', text: 'G10')],
        ),
        throwsFormatException,
      );
    },
  );
}

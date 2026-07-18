import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_search_result.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

void main() {
  const reference = BibleVerseReference(
    verseKey: '001',
    bookId: 1,
    chapter: 1,
    verse: 1,
  );

  test('BibleModuleInfo exposes display title and value equality', () {
    const module = BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: 'TEST',
      moduleId: 'test',
      title: 'Test Bible',
      description: 'Description',
      language: 'en',
      canon: '66',
      versification: 'kjv',
      license: 'CC BY 4.0',
      sourceSummary: 'Source',
    );
    const same = BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: 'TEST',
      moduleId: 'test',
      title: 'Test Bible',
      description: 'Description',
      language: 'en',
      canon: '66',
      versification: 'kjv',
      license: 'CC BY 4.0',
      sourceSummary: 'Source',
    );
    const titleOnly = BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: '  ',
      moduleId: 'test',
      title: 'Test Bible',
      description: 'Description',
      language: 'en',
      canon: '66',
      versification: 'kjv',
      license: 'CC BY 4.0',
      sourceSummary: 'Source',
    );

    expect(module.displayTitle, 'TEST');
    expect(titleOnly.displayTitle, 'Test Bible');
    expect(module, same);
    expect(module.hashCode, same.hashCode);
    expect(module, isNot(titleOnly));
    expect(module == Object(), isFalse);
  });

  test('BibleSearchResult and BibleTextMatch compare nested values', () {
    const match = BibleTextMatch(start: 0, end: 5);
    const sameMatch = BibleTextMatch(start: 0, end: 5);
    const result = BibleSearchResult(
      reference: reference,
      text: 'logos',
      matches: [match],
    );
    const sameResult = BibleSearchResult(
      reference: reference,
      text: 'logos',
      matches: [sameMatch],
    );
    const differentMatch = BibleSearchResult(
      reference: reference,
      text: 'logos',
      matches: [BibleTextMatch(start: 1, end: 6)],
    );

    expect(match, sameMatch);
    expect(match.hashCode, sameMatch.hashCode);
    expect(match == Object(), isFalse);
    expect(result.matchCount, 1);
    expect(result, sameResult);
    expect(result.hashCode, sameResult.hashCode);
    expect(result, isNot(differentMatch));
    expect(result == Object(), isFalse);
  });
}

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
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

  test('verse equality includes its separate comment', () {
    const text = BibleVerseText(verseKey: '001', text: 'Text', comment: 'Note');
    const same = BibleVerseText(verseKey: '001', text: 'Text', comment: 'Note');
    const other = BibleVerseText(verseKey: '001', text: 'Text');
    expect(text, same);
    expect(text.hashCode, same.hashCode);
    expect(text, isNot(other));
    const verse = BibleChapterVerse(
      reference: reference,
      text: 'Text',
      comment: 'Note',
    );
    const sameVerse = BibleChapterVerse(
      reference: reference,
      text: 'Text',
      comment: 'Note',
    );
    expect(verse, sameVerse);
    expect(verse.hashCode, sameVerse.hashCode);
    expect(
      verse,
      isNot(const BibleChapterVerse(reference: reference, text: 'Text')),
    );
  });

  test('module equality includes each version metadata value', () {
    BibleModuleInfo module({
      int schema = 3,
      int data = 17,
      DateTime? date,
      bool strong = false,
    }) => BibleModuleInfo(
      fileName: 'bible_test.sqlite',
      code: 'TEST',
      moduleId: 'test',
      title: 'Test',
      description: '',
      language: 'en',
      canon: '',
      versification: '',
      license: '',
      sourceSummary: '',
      hasStrongNumbers: strong,
      schemaVersion: schema,
      dataVersion: data,
      date: date ?? DateTime.utc(2026, 10, 24),
    );
    expect(module(), module());
    expect(module().hashCode, module().hashCode);
    expect(module(), isNot(module(schema: 4)));
    expect(module(), isNot(module(data: 18)));
    expect(module().hasStrongNumbers, isFalse);
    expect(module(), isNot(module(strong: true)));
    expect(module(), isNot(module(date: DateTime.utc(2026, 10, 25))));
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

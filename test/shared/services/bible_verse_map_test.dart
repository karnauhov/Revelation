import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late BibleVerseMap verseMap;

  setUpAll(() async {
    verseMap = await BibleVerseMap.loadFromAssets();
  });

  test('loads the complete KJV/protestant canonical verse map', () {
    expect(verseMap.totalBooks, 66);
    expect(verseMap.totalVerses, 31102);
    expect(verseMap.firstVerseKey, '001');
    expect(verseMap.lastVerseKey, 'NZY');
  });

  test('maps verse_key to book, chapter and verse in constant time', () {
    expect(
      verseMap.referenceForKey('001'),
      const BibleVerseReference(
        verseKey: '001',
        bookId: 1,
        chapter: 1,
        verse: 1,
      ),
    );
    expect(
      verseMap.referenceForKey('NZY'),
      const BibleVerseReference(
        verseKey: 'NZY',
        bookId: 66,
        chapter: 22,
        verse: 21,
      ),
    );
    expect(
      verseMap.referenceForKey('kcu'),
      const BibleVerseReference(
        verseKey: 'KCU',
        bookId: 43,
        chapter: 7,
        verse: 53,
      ),
    );
  });

  test('maps book, chapter and verse back to stable verse_key', () {
    expect(verseMap.verseKeyFor(bookId: 1, chapter: 1, verse: 1), '001');
    expect(verseMap.verseKeyFor(bookId: 43, chapter: 7, verse: 53), 'KCU');
    expect(verseMap.verseKeyFor(bookId: 66, chapter: 22, verse: 21), 'NZY');
  });

  test('exposes canonical chapter and verse counts', () {
    expect(verseMap.bookCode(1), 'Gen');
    expect(verseMap.bookCode(66), 'Rev');
    expect(verseMap.chapterCount(1), 50);
    expect(verseMap.chapterCount(66), 22);
    expect(verseMap.verseCount(bookId: 19, chapter: 119), 176);
    expect(verseMap.verseCount(bookId: 43, chapter: 7), 53);
  });

  test('returns null for unknown verse keys and out-of-range references', () {
    expect(verseMap.referenceForKey('000'), isNull);
    expect(verseMap.referenceForKey('NZ!'), isNull);
    expect(verseMap.referenceForKey('NZZ'), isNull);
    expect(verseMap.verseKeyFor(bookId: 43, chapter: 7, verse: 54), isNull);
    expect(verseMap.verseKeyFor(bookId: 67, chapter: 1, verse: 1), isNull);
  });

  test('builds chapter verse keys and navigates between chapters', () {
    expect(verseMap.bookIds.first, 1);
    expect(verseMap.bookIds.last, 66);
    expect(verseMap.verseKeysForChapter(bookId: 66, chapter: 22).last, 'NZY');
    expect(
      verseMap.adjacentChapterReference(bookId: 1, chapter: 1, forward: false),
      isNull,
    );
    final exodusStartKey = verseMap.verseKeyFor(
      bookId: 2,
      chapter: 1,
      verse: 1,
    );
    expect(
      verseMap.adjacentChapterReference(bookId: 1, chapter: 50, forward: true),
      BibleVerseReference(
        verseKey: exodusStartKey!,
        bookId: 2,
        chapter: 1,
        verse: 1,
      ),
    );
    expect(
      verseMap.adjacentChapterReference(bookId: 66, chapter: 22, forward: true),
      isNull,
    );
  });
}

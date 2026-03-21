import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';

void main() {
  test('strong request stores strong number and reports strong kind', () {
    const request = StrongDescriptionRequest(strongNumber: 3056);

    expect(request.strongNumber, 3056);
    expect(request.kind, DescriptionKind.strongNumber);
  });

  test('word request stores source, page and word index', () {
    const request = WordDescriptionRequest(
      sourceId: 'source-a',
      pageName: 'page-7',
      wordIndex: 12,
    );

    expect(request.sourceId, 'source-a');
    expect(request.pageName, 'page-7');
    expect(request.wordIndex, 12);
    expect(request.kind, DescriptionKind.word);
  });

  test('word request allows missing source/page for broad lookup', () {
    const request = WordDescriptionRequest(wordIndex: 0);

    expect(request.sourceId, isNull);
    expect(request.pageName, isNull);
    expect(request.wordIndex, 0);
    expect(request.kind, DescriptionKind.word);
  });

  test('verse request defaults combineAcrossPages to true', () {
    const request = VerseDescriptionRequest(chapterNumber: 3, verseNumber: 16);

    expect(request.chapterNumber, 3);
    expect(request.verseNumber, 16);
    expect(request.sourceId, isNull);
    expect(request.pageName, isNull);
    expect(request.combineAcrossPages, isTrue);
    expect(request.kind, DescriptionKind.verse);
  });

  test('verse request supports explicit source/page and combine flag', () {
    const request = VerseDescriptionRequest(
      chapterNumber: 8,
      verseNumber: 4,
      sourceId: 'source-b',
      pageName: 'p-2',
      combineAcrossPages: false,
    );

    expect(request.chapterNumber, 8);
    expect(request.verseNumber, 4);
    expect(request.sourceId, 'source-b');
    expect(request.pageName, 'p-2');
    expect(request.combineAcrossPages, isFalse);
    expect(request.kind, DescriptionKind.verse);
  });
}

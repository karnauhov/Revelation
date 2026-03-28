import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/verse.dart';

void main() {
  test('findSourceById trims input and returns match', () {
    final source = _buildSource(id: 'source-1', pages: []);
    final service = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );

    expect(service.findSourceById(' source-1 '), same(source));
    expect(service.findSourceById(''), isNull);
  });

  test('findPageByName returns page by name and ignores empty', () {
    final page = _buildPage('page-1', words: [PageWord('Word', const [])]);
    final source = _buildSource(id: 'source-1', pages: [page]);
    final service = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );

    expect(service.findPageByName(source, ' page-1 '), same(page));
    expect(service.findPageByName(source, '  '), isNull);
  });

  test('resolveWord uses fallback page and respects pageName', () {
    final pageA = _buildPage('page-a', words: [PageWord('A', const [])]);
    final pageB = _buildPage('page-b', words: [PageWord('B', const [])]);
    final source = _buildSource(id: 'source-1', pages: [pageA, pageB]);
    final service = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );

    final fallbackResult = service.resolveWord(
      wordIndex: 0,
      sourceId: 'source-1',
      fallbackSource: source,
      fallbackPage: pageB,
    );
    expect(fallbackResult, isNotNull);
    expect(fallbackResult!.page, same(pageB));

    final missingPageResult = service.resolveWord(
      wordIndex: 0,
      sourceId: 'source-1',
      pageName: 'missing',
    );
    expect(missingPageResult, isNull);

    final negativeResult = service.resolveWord(
      wordIndex: -1,
      sourceId: 'source-1',
    );
    expect(negativeResult, isNull);

    final missingSourceResult = service.resolveWord(
      wordIndex: 0,
      sourceId: 'missing',
    );
    expect(missingSourceResult, isNull);
  });

  test('resolveVerse honors combineAcrossPages and pageName', () {
    final pageA = _buildPage(
      'page-a',
      words: [PageWord('A', const [])],
      verses: [
        const Verse(
          chapterNumber: 1,
          verseNumber: 1,
          labelPosition: Offset.zero,
          wordIndexes: [0],
        ),
      ],
    );
    final pageB = _buildPage(
      'page-b',
      words: [PageWord('B', const [])],
      verses: [
        const Verse(
          chapterNumber: 1,
          verseNumber: 1,
          labelPosition: Offset.zero,
          wordIndexes: [0],
        ),
      ],
    );
    final source = _buildSource(id: 'source-1', pages: [pageA, pageB]);
    final service = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );

    final combined = service.resolveVerse(
      chapterNumber: 1,
      verseNumber: 1,
      sourceId: 'source-1',
      combineAcrossPages: true,
    );
    expect(combined.length, 2);

    final fallbackOnly = service.resolveVerse(
      chapterNumber: 1,
      verseNumber: 1,
      sourceId: 'source-1',
      combineAcrossPages: false,
      fallbackSource: source,
      fallbackPage: pageB,
    );
    expect(fallbackOnly.length, 1);
    expect(fallbackOnly.first.page, same(pageB));

    final byPageName = service.resolveVerse(
      chapterNumber: 1,
      verseNumber: 1,
      sourceId: 'source-1',
      pageName: 'page-a',
    );
    expect(byPageName.length, 1);
    expect(byPageName.first.page, same(pageA));
  });
}

class _FakePrimarySourcesDbRepository extends PrimarySourcesDbRepository {
  _FakePrimarySourcesDbRepository(this._sources);

  final List<PrimarySource> _sources;

  @override
  List<PrimarySource> getAllSourcesSync() => _sources;
}

PrimarySource _buildSource({
  required String id,
  required List<model.Page> pages,
}) {
  return PrimarySource(
    id: id,
    title: 'Title',
    date: 'Date',
    content: 'Content',
    quantity: 1,
    material: 'Material',
    textStyle: 'Text style',
    found: 'Found',
    classification: 'Classification',
    currentLocation: 'Location',
    preview: 'preview.png',
    maxScale: 1,
    isMonochrome: false,
    pages: pages,
    attributes: const [],
    permissionsReceived: true,
  );
}

model.Page _buildPage(
  String name, {
  List<PageWord> words = const [],
  List<Verse> verses = const [],
}) {
  return model.Page(
    name: name,
    content: 'content-$name',
    image: '$name.png',
    words: words,
    verses: verses,
  );
}

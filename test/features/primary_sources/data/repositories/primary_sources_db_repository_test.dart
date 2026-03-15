import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;

void main() {
  test('loadGroupedSourcesResult returns failure when not initialized',
      () async {
    final repository = PrimarySourcesDbRepository(
      dataSource: _FakePrimarySourcesDataSource(isInitialized: false),
    );

    final result = await repository.loadGroupedSourcesResult();

    expect(result, isA<AppFailureResult<PrimarySourcesLoadResult>>());
    expect(
      (result as AppFailureResult<PrimarySourcesLoadResult>).error,
      const AppFailure.dataSource(
        'Primary sources data is not initialized in local database.',
      ),
    );
  });

  test('getAllSourcesSync returns empty when not initialized', () {
    final repository = PrimarySourcesDbRepository(
      dataSource: _FakePrimarySourcesDataSource(isInitialized: false),
    );

    expect(repository.getAllSourcesSync(), isEmpty);
  });

  test('getAllSourcesSync maps rows, pages, links and attributions', () {
    final repository = PrimarySourcesDbRepository(
      dataSource: _buildDataSource(),
    );

    final sources = repository.getAllSourcesSync();

    expect(sources.length, 2);
    final source = sources.firstWhere((item) => item.id == 's1');
    expect(source.pages.length, 1);
    expect(source.pages.single.words.single.text, 'Word');
    expect(source.pages.single.verses.single.chapterNumber, 1);
    expect(source.links.single.titleOverride, 'Link Title');
    expect(source.attributes, isNotNull);
    expect(source.attributes!.single['text'], 'Attr');
  });

  test('getAllSources includes preview bytes when available', () async {
    final repository = PrimarySourcesDbRepository(
      dataSource: _buildDataSource(),
    );

    final sources = await repository.getAllSources(includePreviewBytes: true);
    final sourceWithPreview = sources.firstWhere((item) => item.id == 's1');
    final sourceWithAsset = sources.firstWhere((item) => item.id == 's2');

    expect(sourceWithPreview.previewBytes, isNotNull);
    expect(sourceWithPreview.previewBytes, Uint8List.fromList([1, 2, 3]));
    expect(sourceWithAsset.previewBytes, isNull);
  });

  test('loadGroupedSourcesResult groups sources by kind', () async {
    final repository = PrimarySourcesDbRepository(
      dataSource: _buildDataSource(),
    );

    final result = await repository.loadGroupedSourcesResult();

    expect(result, isA<AppSuccess<PrimarySourcesLoadResult>>());
    final data = (result as AppSuccess<PrimarySourcesLoadResult>).data;
    expect(data.fullPrimarySources.map((item) => item.id), contains('s1'));
    expect(data.fragmentsPrimarySources.map((item) => item.id), contains('s2'));
    expect(data.significantPrimarySources, isEmpty);
  });

  test('loadGroupedSourcesResult returns failure for invalid json', () async {
    final repository = PrimarySourcesDbRepository(
      dataSource: _buildDataSource(invalidJson: true),
    );

    final result = await repository.loadGroupedSourcesResult();

    expect(result, isA<AppFailureResult<PrimarySourcesLoadResult>>());
    expect(
      (result as AppFailureResult<PrimarySourcesLoadResult>).error,
      const AppFailure.dataSource(
        'Unable to load primary sources from local database.',
      ),
    );
  });
}

_FakePrimarySourcesDataSource _buildDataSource({bool invalidJson = false}) {
  final wordRectangles = invalidJson ? 'invalid-json' : '[]';
  return _FakePrimarySourcesDataSource(
    isInitialized: true,
    primarySourceRows: [
      const common_db.PrimarySource(
        id: 's1',
        family: 'fam',
        number: 1,
        groupKind: 'full',
        sortOrder: 0,
        versesCount: 1,
        previewResourceKey: 'remote-preview',
        defaultMaxScale: 2.5,
        canShowImages: true,
        imagesAreMonochrome: false,
        notes: '',
      ),
      const common_db.PrimarySource(
        id: 's2',
        family: 'fam',
        number: 2,
        groupKind: 'fragment',
        sortOrder: 1,
        versesCount: 0,
        previewResourceKey: 'assets/preview.png',
        defaultMaxScale: 2.0,
        canShowImages: false,
        imagesAreMonochrome: true,
        notes: '',
      ),
    ],
    primarySourceTextRows: const [
      localized_db.PrimarySourceText(
        sourceId: 's1',
        titleMarkup: 'Title 1',
        dateLabel: 'Date 1',
        contentLabel: 'Content 1',
        materialText: 'Material 1',
        textStyleText: 'Style 1',
        foundText: 'Found 1',
        classificationText: 'Class 1',
        currentLocationText: 'Loc 1',
      ),
      localized_db.PrimarySourceText(
        sourceId: 's2',
        titleMarkup: 'Title 2',
        dateLabel: 'Date 2',
        contentLabel: 'Content 2',
        materialText: 'Material 2',
        textStyleText: 'Style 2',
        foundText: 'Found 2',
        classificationText: 'Class 2',
        currentLocationText: 'Loc 2',
      ),
    ],
    primarySourceLinkRows: const [
      common_db.PrimarySourceLink(
        sourceId: 's1',
        linkId: 'link-1',
        sortOrder: 0,
        linkRole: 'ref',
        url: 'http://example.test',
      ),
    ],
    primarySourceLinkTextRows: const [
      localized_db.PrimarySourceLinkText(
        sourceId: 's1',
        linkId: 'link-1',
        title: 'Link Title',
      ),
    ],
    primarySourceAttributionRows: const [
      common_db.PrimarySourceAttribution(
        sourceId: 's1',
        attributionId: 'attr-1',
        sortOrder: 0,
        displayText: 'Attr',
        url: 'http://attr.test',
      ),
    ],
    primarySourcePageRows: const [
      common_db.PrimarySourcePage(
        sourceId: 's1',
        pageName: 'p1',
        sortOrder: 0,
        contentRef: 'C1',
        imagePath: 'p1.png',
      ),
    ],
    primarySourceWordRows: [
      common_db.PrimarySourceWord(
        sourceId: 's1',
        pageName: 'p1',
        wordIndex: 0,
        wordText: 'Word',
        strongNumber: 1,
        strongPronounce: true,
        strongXShift: 0.5,
        missingCharIndexesJson: '[1]',
        rectanglesJson: wordRectangles,
      ),
    ],
    primarySourceVerseRows: const [
      common_db.PrimarySourceVerse(
        sourceId: 's1',
        pageName: 'p1',
        verseIndex: 0,
        chapterNumber: 1,
        verseNumber: 1,
        labelX: 1,
        labelY: 2,
        wordIndexesJson: '[0]',
        contoursJson: '[]',
      ),
    ],
    previewBytes: Uint8List.fromList([1, 2, 3]),
  );
}

class _FakePrimarySourcesDataSource implements PrimarySourcesDataSource {
  _FakePrimarySourcesDataSource({
    required this.isInitialized,
    this.primarySourceRows = const [],
    this.primarySourceLinkRows = const [],
    this.primarySourceAttributionRows = const [],
    this.primarySourcePageRows = const [],
    this.primarySourceWordRows = const [],
    this.primarySourceVerseRows = const [],
    this.primarySourceTextRows = const [],
    this.primarySourceLinkTextRows = const [],
    this.previewBytes,
  });

  @override
  final bool isInitialized;

  @override
  final List<common_db.PrimarySource> primarySourceRows;

  @override
  final List<common_db.PrimarySourceLink> primarySourceLinkRows;

  @override
  final List<common_db.PrimarySourceAttribution> primarySourceAttributionRows;

  @override
  final List<common_db.PrimarySourcePage> primarySourcePageRows;

  @override
  final List<common_db.PrimarySourceWord> primarySourceWordRows;

  @override
  final List<common_db.PrimarySourceVerse> primarySourceVerseRows;

  @override
  final List<localized_db.PrimarySourceText> primarySourceTextRows;

  @override
  final List<localized_db.PrimarySourceLinkText> primarySourceLinkTextRows;

  final Uint8List? previewBytes;

  @override
  Future<Uint8List?> getCommonResourceData(String key) async {
    if (key == 'remote-preview') {
      return previewBytes;
    }
    return null;
  }
}

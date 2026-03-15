import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/primary_sources_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/primary_sources_database_gateway.dart';

void main() {
  test('DbManagerPrimarySourcesDataSource exposes gateway data', () async {
    final gateway = _FakePrimarySourcesGateway(
      isInitialized: true,
      primarySourceRows: const [
        common_db.PrimarySource(
          id: 's1',
          family: 'fam',
          number: 1,
          groupKind: 'full',
          sortOrder: 0,
          versesCount: 0,
          previewResourceKey: 'preview',
          defaultMaxScale: 1,
          canShowImages: true,
          imagesAreMonochrome: false,
          notes: '',
        ),
      ],
      primarySourceTextRows: const [
        localized_db.PrimarySourceText(
          sourceId: 's1',
          titleMarkup: 'Title',
          dateLabel: 'Date',
          contentLabel: 'Content',
          materialText: 'Material',
          textStyleText: 'Style',
          foundText: 'Found',
          classificationText: 'Class',
          currentLocationText: 'Location',
        ),
      ],
      previewBytes: Uint8List.fromList([1, 2, 3]),
    );

    final dataSource = DbManagerPrimarySourcesDataSource(
      databaseGateway: gateway,
    );

    expect(dataSource.isInitialized, isTrue);
    expect(dataSource.primarySourceRows.single.id, 's1');
    expect(dataSource.primarySourceTextRows.single.sourceId, 's1');
    final bytes = await dataSource.getCommonResourceData('preview');
    expect(bytes, Uint8List.fromList([1, 2, 3]));
  });
}

class _FakePrimarySourcesGateway implements PrimarySourcesDatabaseGateway {
  _FakePrimarySourcesGateway({
    required this.isInitialized,
    this.primarySourceRows = const [],
    this.primarySourceTextRows = const [],
    this.previewBytes,
  });

  @override
  final bool isInitialized;

  @override
  final List<common_db.PrimarySource> primarySourceRows;

  @override
  final List<common_db.PrimarySourceLink> primarySourceLinkRows = const [];

  @override
  final List<common_db.PrimarySourceAttribution> primarySourceAttributionRows =
      const [];

  @override
  final List<common_db.PrimarySourcePage> primarySourcePageRows = const [];

  @override
  final List<common_db.PrimarySourceWord> primarySourceWordRows = const [];

  @override
  final List<common_db.PrimarySourceVerse> primarySourceVerseRows = const [];

  @override
  final List<localized_db.PrimarySourceText> primarySourceTextRows;

  @override
  final List<localized_db.PrimarySourceLinkText> primarySourceLinkTextRows =
      const [];

  final Uint8List? previewBytes;

  @override
  Future<void> initialize(String language) async {}

  @override
  Future<void> updateLanguage(String language) async {}

  @override
  Future<Uint8List?> getCommonResourceData(String key) async => previewBytes;
}

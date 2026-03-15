@Tags(['widget'])

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/description_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/verse.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('buildContent returns null when data source not initialized', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = DescriptionContentService(
      dataSource: _FakeDescriptionDataSource(isInitialized: false),
    );

    final content = service.buildContent(
      localizations,
      const StrongDescriptionRequest(strongNumber: 1),
    );

    expect(content, isNull);
  });

  test('getGreekStrongPickerEntries filters invalid entries and caches', () {
    final words = <common_db.GreekWord>[
      const common_db.GreekWord(
        id: 1,
        word: 'Alpha',
        category: '',
        synonyms: '',
        origin: '',
        usage: '',
      ),
      const common_db.GreekWord(
        id: 2717, // forbidden
        word: 'Forbidden',
        category: '',
        synonyms: '',
        origin: '',
        usage: '',
      ),
      const common_db.GreekWord(
        id: 2,
        word: '',
        category: '',
        synonyms: '',
        origin: '',
        usage: '',
      ),
    ];
    final dataSource = _FakeDescriptionDataSource(
      isInitialized: true,
      greekWords: words,
    );
    final service = DescriptionContentService(dataSource: dataSource);

    final entries = service.getGreekStrongPickerEntries();
    expect(entries.length, 1);
    expect(entries.first.number, 1);
    expect(entries.first.word, 'Alpha');

    words.add(
      const common_db.GreekWord(
        id: 3,
        word: 'Beta',
        category: '',
        synonyms: '',
        origin: '',
        usage: '',
      ),
    );
    final cached = service.getGreekStrongPickerEntries();
    expect(cached.length, 1);
  });

  testWidgets('buildStrongContent returns markdown and kind', (tester) async {
    final localizations = await _loadLocalizations(tester);
    final dataSource = _FakeDescriptionDataSource(
      isInitialized: true,
      greekWords: const [
        common_db.GreekWord(
          id: 1,
          word: 'Logos',
          category: '',
          synonyms: '',
          origin: '',
          usage: '',
        ),
      ],
      greekDescs: const [
        localized_db.GreekDesc(id: 1, desc: 'Strong description'),
      ],
    );
    final service = DescriptionContentService(dataSource: dataSource);

    final content = service.buildStrongContent(localizations, 1);

    expect(content, isNotNull);
    expect(content!.kind, DescriptionKind.strongNumber);
    expect(content.markdown, contains('Logos'));
    expect(content.markdown, contains('strong_picker:G1'));
  });

  testWidgets('buildWordContent includes strong link and description', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final source = _buildSource();
    final referenceResolver = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );
    final dataSource = _FakeDescriptionDataSource(
      isInitialized: true,
      greekWords: const [
        common_db.GreekWord(
          id: 1,
          word: 'Alpha',
          category: '',
          synonyms: '',
          origin: '',
          usage: '',
        ),
      ],
      greekDescs: const [
        localized_db.GreekDesc(id: 1, desc: 'Word description'),
      ],
    );
    final service = DescriptionContentService(
      dataSource: dataSource,
      referenceResolver: referenceResolver,
    );

    final content = service.buildContent(
      localizations,
      const WordDescriptionRequest(
        sourceId: 'source-1',
        pageName: 'page-1',
        wordIndex: 0,
      ),
    );

    expect(content, isNotNull);
    expect(content!.kind, DescriptionKind.word);
    expect(content.markdown, contains('strong:G1'));
    expect(content.markdown, contains('Word description'));
  });

  testWidgets('buildVerseContent creates word links', (tester) async {
    final localizations = await _loadLocalizations(tester);
    final source = _buildSource();
    final referenceResolver = PrimarySourceReferenceService(
      repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
    );
    final dataSource = _FakeDescriptionDataSource(isInitialized: true);
    final service = DescriptionContentService(
      dataSource: dataSource,
      referenceResolver: referenceResolver,
    );

    final content = service.buildContent(
      localizations,
      const VerseDescriptionRequest(
        sourceId: 'source-1',
        pageName: 'page-1',
        chapterNumber: 1,
        verseNumber: 1,
      ),
    );

    expect(content, isNotNull);
    expect(content!.kind, DescriptionKind.verse);
    expect(content.markdown, contains('word:source-1:page-1:0'));
  });
}

Future<AppLocalizations> _loadLocalizations(WidgetTester tester) async {
  final context = await pumpLocalizedContext(tester);
  return AppLocalizations.of(context)!;
}

class _FakeDescriptionDataSource implements DescriptionDataSource {
  _FakeDescriptionDataSource({
    required this.isInitialized,
    List<common_db.GreekWord>? greekWords,
    List<localized_db.GreekDesc>? greekDescs,
  })  : languageCode = 'en',
        greekWords = greekWords ?? const [],
        greekDescs = greekDescs ?? const [];

  @override
  final bool isInitialized;

  @override
  final String languageCode;

  @override
  final List<common_db.GreekWord> greekWords;

  @override
  final List<localized_db.GreekDesc> greekDescs;
}

class _FakePrimarySourcesDbRepository extends PrimarySourcesDbRepository {
  _FakePrimarySourcesDbRepository(this._sources);

  final List<PrimarySource> _sources;

  @override
  List<PrimarySource> getAllSourcesSync() => _sources;
}

PrimarySource _buildSource() {
  return PrimarySource(
    id: 'source-1',
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
    pages: [
      model.Page(
        name: 'page-1',
        content: 'content',
        image: 'page-1.png',
        words: [PageWord('Word', const [], sn: 1, snPronounce: false)],
        verses: const [
          Verse(
            chapterNumber: 1,
            verseNumber: 1,
            labelPosition: Offset.zero,
            wordIndexes: [0],
          ),
        ],
      ),
    ],
    attributes: const [],
    permissionsReceived: true,
  );
}

@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/services/description_content_service.dart';
import 'package:revelation/features/primary_sources/application/services/manuscript_greek_text_converter.dart';
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

  testWidgets(
    'buildContent converts primary-source manuscript words but not Strong words',
    (tester) async {
      final localizations = await _loadLocalizations(tester);
      final source = PrimarySource(
        id: 'source-greek',
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
            words: [PageWord('ΑΒΓΜΨΩ', const [], sn: 1, snPronounce: false)],
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
      final referenceResolver = PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
      );
      final dataSource = _FakeDescriptionDataSource(
        isInitialized: true,
        greekWords: const [
          common_db.GreekWord(
            id: 1,
            word: 'ΑΒΓΜΨΩ',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ],
        greekDescs: const [
          localized_db.GreekDesc(id: 1, desc: 'See [G1](strong:G1)'),
        ],
      );
      final service = DescriptionContentService(
        dataSource: dataSource,
        referenceResolver: referenceResolver,
        manuscriptGreekTextConverter: ManuscriptGreekTextConverter(
          letterReplacements: const <String, String>{
            'Α': 'Α',
            'Β': 'Ⲃ',
            'Γ': 'Ⲅ',
            'Μ': 'Μ',
            'Ψ': 'ⲯ',
            'Ω': 'Ⲱ',
          },
        ),
      );

      final wordContent = service.buildContent(
        localizations,
        const WordDescriptionRequest(
          sourceId: 'source-greek',
          pageName: 'page-1',
          wordIndex: 0,
        ),
      );
      final verseContent = service.buildContent(
        localizations,
        const VerseDescriptionRequest(
          sourceId: 'source-greek',
          pageName: 'page-1',
          chapterNumber: 1,
          verseNumber: 1,
        ),
      );
      final strongContent = service.buildStrongContent(localizations, 1);

      expect(wordContent, isNotNull);
      expect(wordContent!.markdown, contains('## ΑⲂⲄΜⲯⲰ'));
      expect(verseContent, isNotNull);
      expect(
        verseContent!.markdown,
        contains('[ΑⲂⲄΜⲯⲰ](word:source-greek:page-1:0)'),
      );
      expect(strongContent, isNotNull);
      expect(strongContent!.markdown, contains('## ΑΒΓΜΨΩ'));
      expect(strongContent.markdown, contains('**ΑΒΓΜΨΩ** ([G1](strong:G1))'));
    },
  );

  test('doesStrongNumberExist validates boundaries and forbidden ranges', () {
    final service = DescriptionContentService(
      dataSource: _FakeDescriptionDataSource(isInitialized: true),
    );

    expect(service.doesStrongNumberExist(0), isFalse);
    expect(service.doesStrongNumberExist(1), isTrue);
    expect(service.doesStrongNumberExist(2717), isFalse);
    expect(service.doesStrongNumberExist(3203), isFalse);
    expect(service.doesStrongNumberExist(3302), isFalse);
    expect(service.doesStrongNumberExist(3303), isTrue);
    expect(service.doesStrongNumberExist(5624), isTrue);
    expect(service.doesStrongNumberExist(5625), isFalse);
  });

  test('getNeighborStrongNumber skips blocked values and wraps around', () {
    final service = DescriptionContentService(
      dataSource: _FakeDescriptionDataSource(isInitialized: true),
    );

    expect(service.getNeighborStrongNumber(2716, forward: true), 2718);
    expect(service.getNeighborStrongNumber(3202, forward: true), 3303);
    expect(service.getNeighborStrongNumber(3303, forward: false), 3202);
    expect(service.getNeighborStrongNumber(5624, forward: true), 1);
    expect(service.getNeighborStrongNumber(1, forward: false), 5624);
  });

  testWidgets('buildStrongContent formats origins, synonyms, usage and links', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final dataSource = _FakeDescriptionDataSource(
      isInitialized: true,
      greekWords: const [
        common_db.GreekWord(
          id: 1,
          word: 'Logos',
          category: '@noun',
          synonyms: '2,2717,3',
          origin: 'G2,H123,G2717',
          usage: 'sample [], 2\nother [], 3',
        ),
        common_db.GreekWord(
          id: 2,
          word: 'Alpha',
          category: '',
          synonyms: '',
          origin: '',
          usage: '',
        ),
        common_db.GreekWord(
          id: 3,
          word: 'Beta',
          category: '',
          synonyms: '',
          origin: '',
          usage: '',
        ),
      ],
      greekDescs: const [
        localized_db.GreekDesc(id: 1, desc: 'See [G2](strong:G2) and text'),
      ],
    );
    final service = DescriptionContentService(dataSource: dataSource);

    final content = service.buildStrongContent(localizations, 1);

    expect(content, isNotNull);
    expect(content!.markdown, contains('**Alpha** ([G2](strong:G2))'));
    expect(content.markdown, contains('[H123](strong:H123)'));
    expect(content.markdown, contains('**Beta** ([G3](strong:G3))'));
    expect(content.markdown, contains('sample 2; **other 3'));
    expect(content.markdown, isNot(contains('@noun')));
  });

  testWidgets('buildStrongContent returns null when word is absent or blank', (
    tester,
  ) async {
    final localizations = await _loadLocalizations(tester);
    final service = DescriptionContentService(
      dataSource: _FakeDescriptionDataSource(
        isInitialized: true,
        greekWords: const [
          common_db.GreekWord(
            id: 1,
            word: '  ',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ],
      ),
    );

    expect(service.buildStrongContent(localizations, 999), isNull);
    expect(service.buildStrongContent(localizations, 1), isNull);
  });

  testWidgets(
    'buildWordContent applies strike and skips pronunciation for non letters',
    (tester) async {
      final localizations = await _loadLocalizations(tester);
      final source = PrimarySource(
        id: 'source-2',
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
            words: [
              PageWord(
                'ab',
                const [],
                notExist: const [1],
                sn: 2,
                snPronounce: false,
              ),
              PageWord('123', const []),
            ],
            verses: const [],
          ),
        ],
        attributes: const [],
        permissionsReceived: true,
      );
      final referenceResolver = PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
      );
      final service = DescriptionContentService(
        dataSource: _FakeDescriptionDataSource(
          isInitialized: true,
          greekWords: const [
            common_db.GreekWord(
              id: 2,
              word: 'Alpha',
              category: '',
              synonyms: '',
              origin: '',
              usage: '',
            ),
          ],
        ),
        referenceResolver: referenceResolver,
      );

      final first = service.buildContent(
        localizations,
        const WordDescriptionRequest(
          sourceId: 'source-2',
          pageName: 'page-1',
          wordIndex: 0,
        ),
      );
      final second = service.buildContent(
        localizations,
        const WordDescriptionRequest(
          sourceId: 'source-2',
          pageName: 'page-1',
          wordIndex: 1,
        ),
      );

      expect(first, isNotNull);
      expect(first!.markdown, contains('\u200E~~b~~'));
      expect(first.markdown, contains('[2](strong:G2)'));
      expect(second, isNotNull);
      expect(
        second!.markdown,
        isNot(contains(localizations.strong_pronunciation)),
      );
    },
  );

  testWidgets(
    'buildVerseContent shows fallback text when verse has no valid word indexes',
    (tester) async {
      final localizations = await _loadLocalizations(tester);
      final source = PrimarySource(
        id: 'source-3',
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
            words: [PageWord('Word', const [])],
            verses: const [
              Verse(
                chapterNumber: 1,
                verseNumber: 1,
                labelPosition: Offset.zero,
                wordIndexes: [99],
              ),
            ],
          ),
        ],
        attributes: const [],
        permissionsReceived: true,
      );
      final referenceResolver = PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
      );
      final service = DescriptionContentService(
        dataSource: _FakeDescriptionDataSource(isInitialized: true),
        referenceResolver: referenceResolver,
      );

      final content = service.buildContent(
        localizations,
        const VerseDescriptionRequest(
          sourceId: 'source-3',
          pageName: 'page-1',
          chapterNumber: 1,
          verseNumber: 1,
        ),
      );

      expect(content, isNotNull);
      expect(content!.markdown, contains(localizations.click_for_info));
    },
  );

  testWidgets(
    'buildVerseContent combines same verse across pages when requested',
    (tester) async {
      final localizations = await _loadLocalizations(tester);
      final source = PrimarySource(
        id: 'source-4',
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
            words: [PageWord('One', const [])],
            verses: const [
              Verse(
                chapterNumber: 1,
                verseNumber: 1,
                labelPosition: Offset.zero,
                wordIndexes: [0],
              ),
            ],
          ),
          model.Page(
            name: 'page-2',
            content: 'content',
            image: 'page-2.png',
            words: [PageWord('Two', const [])],
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
      final referenceResolver = PrimarySourceReferenceService(
        repository: _FakePrimarySourcesDbRepository(<PrimarySource>[source]),
      );
      final service = DescriptionContentService(
        dataSource: _FakeDescriptionDataSource(isInitialized: true),
        referenceResolver: referenceResolver,
      );

      final content = service.buildContent(
        localizations,
        const VerseDescriptionRequest(
          sourceId: 'source-4',
          chapterNumber: 1,
          verseNumber: 1,
          combineAcrossPages: true,
        ),
        fallbackSource: source,
        fallbackPage: source.pages.first,
      );

      expect(content, isNotNull);
      expect(content!.markdown, contains('word:source-4:page-1:0'));
      expect(content.markdown, contains('word:source-4:page-2:0'));
    },
  );
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
  }) : languageCode = 'en',
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

@Tags(['widget'])
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('buildStrongContent returns null when lexicon is unavailable', (
    tester,
  ) async {
    final l10n = await _loadLocalizations(tester);
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: const _FakeLexiconDatabaseGateway(
          isInitialized: false,
          languageCode: 'ru',
        ),
      ),
    );

    expect(service.buildStrongContent(l10n, 1), isNull);
    expect(service.getPickerEntries(), isEmpty);
  });

  test('getPickerEntries filters invalid entries and caches', () {
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
        id: 2717,
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
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: _FakeLexiconDatabaseGateway(greekWords: words),
      ),
    );

    final entries = service.getPickerEntries();
    expect(entries, const <StrongPickerEntry>[
      StrongPickerEntry(number: 1, word: 'Alpha', searchText: '1 g1 alpha'),
    ]);

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
    expect(identical(service.getPickerEntries(), entries), isTrue);
  });

  testWidgets('buildStrongContent returns markdown and kind', (tester) async {
    final l10n = await _loadLocalizations(tester);
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: const _FakeLexiconDatabaseGateway(
          greekWords: <common_db.GreekWord>[
            common_db.GreekWord(
              id: 1,
              word: 'Logos',
              category: '',
              synonyms: '',
              origin: '',
              usage: '',
            ),
          ],
          greekDescs: <localized_db.GreekDesc>[
            localized_db.GreekDesc(id: 1, desc: 'Strong description'),
          ],
        ),
      ),
    );

    final content = service.buildStrongContent(l10n, 1);

    expect(content, isNotNull);
    expect(content!.kind, DescriptionKind.strongNumber);
    expect(content.markdown, contains('Logos'));
    expect(content.markdown, contains('strong_picker:G1'));
    expect(content.markdown, contains('Strong description'));
  });

  testWidgets('buildStrongContent formats origins, synonyms, usage and links', (
    tester,
  ) async {
    final l10n = await _loadLocalizations(tester);
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: const _FakeLexiconDatabaseGateway(
          greekWords: <common_db.GreekWord>[
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
          greekDescs: <localized_db.GreekDesc>[
            localized_db.GreekDesc(id: 1, desc: 'See [G2](strong:G2)'),
          ],
        ),
      ),
    );

    final content = service.buildStrongContent(l10n, 1);

    expect(content, isNotNull);
    expect(content!.markdown, contains('${l10n.strong_origin}: '));
    expect(content.markdown, contains('**Alpha** ([G2](strong:G2))'));
    expect(content.markdown, contains('[H123](strong:H123)'));
    expect(content.markdown, contains('**Beta** ([G3](strong:G3))'));
    expect(content.markdown, contains('sample 2; **other 3'));
    expect(content.markdown, isNot(contains('@noun')));
  });

  testWidgets('buildStrongContent returns null when word is absent or blank', (
    tester,
  ) async {
    final l10n = await _loadLocalizations(tester);
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: const _FakeLexiconDatabaseGateway(
          greekWords: <common_db.GreekWord>[
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
      ),
    );

    expect(service.buildStrongContent(l10n, 999), isNull);
    expect(service.buildStrongContent(l10n, 1), isNull);
  });

  test('delegates Strong number policy behavior', () {
    final service = StrongsDictionaryContentService(
      repository: StrongsDictionaryRepository(
        databaseGateway: const _FakeLexiconDatabaseGateway(),
      ),
    );

    expect(service.isAllowedStrongNumber(1), isTrue);
    expect(service.isAllowedStrongNumber(2717), isFalse);
    expect(service.getNeighborStrongNumber(5624, forward: true), 1);
  });
}

Future<AppLocalizations> _loadLocalizations(WidgetTester tester) async {
  final context = await pumpLocalizedContext(tester);
  return AppLocalizations.of(context)!;
}

class _FakeLexiconDatabaseGateway implements LexiconDatabaseGateway {
  const _FakeLexiconDatabaseGateway({
    this.isInitialized = true,
    this.languageCode = 'en',
    this.greekWords = const <common_db.GreekWord>[],
    this.greekDescs = const <localized_db.GreekDesc>[],
  });

  @override
  final bool isInitialized;

  @override
  final String languageCode;

  @override
  final List<common_db.GreekWord> greekWords;

  @override
  final List<localized_db.GreekDesc> greekDescs;

  @override
  Future<void> initialize(String language) async {}

  @override
  Future<void> updateLanguage(String language) async {}
}

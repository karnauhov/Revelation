import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';

void main() {
  test('returns empty collections when lexicon is not initialized', () {
    final repository = StrongsDictionaryRepository(
      databaseGateway: const _FakeLexiconDatabaseGateway(
        isInitialized: false,
        languageCode: 'ru',
      ),
    );

    expect(repository.languageCode, 'ru');
    expect(repository.getEntries(), isEmpty);
    expect(repository.getPickerEntries(), isEmpty);
    expect(repository.findEntry(1), isNull);
  });

  test('maps lexicon rows to immutable dictionary entries', () {
    final repository = StrongsDictionaryRepository(
      databaseGateway: const _FakeLexiconDatabaseGateway(
        greekWords: <common_db.GreekWord>[
          common_db.GreekWord(
            id: 2,
            word: ' Beta ',
            category: ' @noun ',
            synonyms: ' 1 ',
            origin: ' G1 ',
            usage: ' Rev 1:1 ',
          ),
          common_db.GreekWord(
            id: 1,
            word: ' Alpha ',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ],
        greekDescs: <localized_db.GreekDesc>[
          localized_db.GreekDesc(id: 2, desc: ' Description '),
        ],
      ),
    );

    final entries = repository.getEntries();

    expect(entries.map((entry) => entry.number), <int>[1, 2]);
    expect(entries.last, isA<StrongDictionaryEntry>());
    expect(entries.last.word, 'Beta');
    expect(entries.last.category, '@noun');
    expect(entries.last.description, 'Description');
    expect(() => entries.add(entries.first), throwsUnsupportedError);
    expect(repository.findEntry(2), entries.last);
    expect(repository.findDescription(2), 'Description');
    expect(repository.findGreekWord(2), 'Beta');
    expect(repository.findEntry(999), isNull);
    expect(repository.findDescription(999), isNull);
    expect(repository.findGreekWord(999), isNull);
  });

  test('builds sorted picker entries from allowed non-empty words', () {
    final repository = StrongsDictionaryRepository(
      databaseGateway: const _FakeLexiconDatabaseGateway(
        greekWords: <common_db.GreekWord>[
          common_db.GreekWord(
            id: 2717,
            word: 'Forbidden',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
          common_db.GreekWord(
            id: 3,
            word: ' Gamma ',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
          common_db.GreekWord(
            id: 2,
            word: '',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
          common_db.GreekWord(
            id: 1,
            word: 'Alpha',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ],
      ),
    );

    final entries = repository.getPickerEntries();

    expect(entries, const <StrongPickerEntry>[
      StrongPickerEntry(number: 1, word: 'Alpha', searchText: '1 g1 alpha'),
      StrongPickerEntry(number: 3, word: 'Gamma', searchText: '3 g3 gamma'),
    ]);
    expect(entries.last.searchText, contains('g3'));
    expect(repository.closestPickerNumber(2), 3);
    expect(() => entries.add(entries.first), throwsUnsupportedError);
  });

  test('exposes number policy decisions through repository facade', () {
    final repository = StrongsDictionaryRepository(
      databaseGateway: const _FakeLexiconDatabaseGateway(
        greekWords: <common_db.GreekWord>[
          common_db.GreekWord(
            id: 1,
            word: 'Alpha',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
          common_db.GreekWord(
            id: 5624,
            word: 'Omega',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
          common_db.GreekWord(
            id: 6000,
            word: 'Extra',
            category: '',
            synonyms: '',
            origin: '',
            usage: '',
          ),
        ],
      ),
    );

    expect(repository.isAllowedStrongNumber(1), isTrue);
    expect(repository.isAllowedStrongNumber(2717), isFalse);
    expect(repository.isAllowedStrongNumber(6000), isTrue);
    expect(repository.isAllowedStrongNumber(6096), isFalse);
    expect(repository.isAllowedStrongNumber(21502), isFalse);
    expect(repository.getNeighborStrongNumber(5624, forward: true), 6000);
    expect(repository.getPickerEntries().map((entry) => entry.number), [
      1,
      5624,
      6000,
    ]);
  });
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

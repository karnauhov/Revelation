import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/data_sources/description_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';

void main() {
  test('DbManagerDescriptionDataSource exposes gateway data', () {
    final gateway = _FakeLexiconGateway(
      isInitialized: true,
      languageCode: 'uk',
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
      greekDescs: const [localized_db.GreekDesc(id: 1, desc: 'Desc')],
    );

    final dataSource = DbManagerDescriptionDataSource(databaseGateway: gateway);

    expect(dataSource.isInitialized, isTrue);
    expect(dataSource.languageCode, 'uk');
    expect(dataSource.greekWords.single.word, 'Logos');
    expect(dataSource.greekDescs.single.desc, 'Desc');
  });
}

class _FakeLexiconGateway implements LexiconDatabaseGateway {
  _FakeLexiconGateway({
    required this.isInitialized,
    required this.languageCode,
    required this.greekWords,
    required this.greekDescs,
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

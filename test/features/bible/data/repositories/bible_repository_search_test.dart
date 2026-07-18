import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/data/repositories/bible_preferences_store.dart';
import 'package:revelation/features/bible/data/repositories/bible_repository.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('searches visible verse text without Strong tokens', () async {
    final db = BibleModuleDB(NativeDatabase.memory());
    await db.customStatement('''
      CREATE TABLE verses (
        verse_key TEXT NOT NULL PRIMARY KEY,
        text TEXT NOT NULL DEFAULT ''
      )
    ''');
    await db.customInsert('''
      INSERT INTO verses (verse_key, text)
      VALUES
        ('001', 'En G1722 arche G746'),
        ('002', 'No matching phrase G1'),
        ('003', 'En arche again G2')
    ''');

    final repository = BibleRepository(
      moduleDataSource: _SingleDbBibleModuleDataSource(db),
      preferencesStore: _FakeBiblePreferencesStore(),
      loadVerseMap: BibleVerseMap.loadFromAssets,
    );

    final results = await repository.searchModule(
      moduleFile: 'bible_lxx_tr.sqlite',
      query: 'en arche',
    );

    expect(results, hasLength(2));
    expect(results.first.reference.bookId, 1);
    expect(results.first.reference.chapter, 1);
    expect(results.first.reference.verse, 1);
    expect(results.first.text, 'En arche');
    expect(results.first.matchCount, 1);
  });
}

class _SingleDbBibleModuleDataSource implements BibleModuleDataSource {
  const _SingleDbBibleModuleDataSource(this.db);

  final BibleModuleDB db;

  @override
  Future<List<String>> listModuleFiles({required String defaultModuleFile}) {
    return Future.value([defaultModuleFile]);
  }

  @override
  BibleModuleDB openModule(String moduleFile) => db;
}

class _FakeBiblePreferencesStore implements BiblePreferencesStore {
  @override
  Future<String?> loadLastModuleFile() async => null;

  @override
  Future<List<String>> loadLastModuleFiles() async => const <String>[];

  @override
  Future<String?> loadLastSearchQuery(String moduleFile) async => null;

  @override
  Future<List<String>> loadSearchHistory() async => const <String>[];

  @override
  Future<void> saveLastModuleFile(String moduleFile) async {}

  @override
  Future<void> saveLastModuleFiles(List<String> moduleFiles) async {}

  @override
  Future<void> saveLastSearchQuery({
    required String moduleFile,
    required String query,
  }) async {}

  @override
  Future<void> saveSearchHistory(List<String> queries) async {}
}

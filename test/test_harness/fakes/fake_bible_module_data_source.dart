import 'package:drift/native.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';

class FakeBibleModuleDataSource implements BibleModuleDataSource {
  FakeBibleModuleDataSource(this.modules);
  final Map<String, ({BibleModuleInfo info, List<BibleVerseText> verses})>
  modules;
  final opened = <String>[];
  final closed = <String>[];
  final unavailable = <String>{};
  List<String>? discoverableFiles;

  @override
  Future<List<String>> listModuleFiles({
    required String defaultModuleFile,
  }) async => discoverableFiles ?? modules.keys.toList();
  @override
  BibleModuleDB openModule(String moduleFile) {
    opened.add(moduleFile);
    return _FixtureModule(this, moduleFile);
  }
}

class _FixtureModule extends BibleModuleDB {
  _FixtureModule(this.source, this.file) : super(NativeDatabase.memory());
  final FakeBibleModuleDataSource source;
  final String file;
  @override
  Future<BibleModuleInfo> readInfo(
    String fileName, {
    bool includeStrongCapability = true,
  }) async {
    if (source.unavailable.contains(file)) throw StateError('Offline fixture');
    return source.modules[file]!.info;
  }

  @override
  Future<List<BibleVerseText>> readAllVerses() async =>
      source.modules[file]!.verses;
  @override
  Future<List<BibleVerseText>> readVersesByKeys(List<String> keys) async {
    if (source.unavailable.contains(file)) throw StateError('Offline fixture');
    return source.modules[file]!.verses
        .where((verse) => keys.contains(verse.verseKey))
        .toList();
  }

  @override
  Future<void> close() async {
    source.closed.add(file);
    await super.close();
  }
}

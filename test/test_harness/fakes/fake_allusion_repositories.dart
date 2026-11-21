import 'package:revelation/features/allusion_search/data/repositories/allusion_search_repository.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/bible/data/repositories/bible_library_repository.dart';
import 'package:revelation/features/bible/domain/models/bible_module_info.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

/// First-party synthetic passages for UI and lifecycle scenarios.
class FakeAllusionRepository extends AllusionSearchRepository {
  FakeAllusionRepository(BibleVerseMap map, {int genesisVerses = 1})
    : index = AllusionIndex.build(
        verseMap: map,
        baseWeights: const {10: 1.0, 20: 1.0, 30: 1.0},
        verses: [
          for (final ref in [
            (66, 1, 1),
            (40, 1, 1),
            for (var n = 1; n <= genesisVerses; n++) (1, 1, n),
          ])
            BibleVerseText(
              verseKey: map
                  .referenceFor(bookId: ref.$1, chapter: ref.$2, verse: ref.$3)
                  .verseKey,
              text: 'first G10 second G20 third G30',
            ),
        ],
      );
  final AllusionIndex index;
  int searches = 0;
  @override
  Future<BibleVerseMap> loadVerseMap() async => index.verseMap;
  @override
  Future<AllusionIndex> loadIndex() async => index;
  @override
  Future<AllusionResults> search(
    AllusionIndex index,
    AllusionQuery query,
  ) async {
    searches++;
    return index.search(query);
  }
}

class FakeBibleLibrary extends BibleLibraryRepository {
  FakeBibleLibrary({String Function()? selectedModule})
    : _selectedModule = selectedModule;
  final String Function()? _selectedModule;
  static const english = BibleModuleInfo(
    fileName: 'bible_kjv.sqlite',
    code: 'KJV',
    moduleId: 'kjv',
    title: 'English fixture',
    language: 'en',
    description: '',
    canon: '',
    versification: '',
    license: '',
    sourceSummary: '',
  );
  static const ukrainian = BibleModuleInfo(
    fileName: 'bible_ohienko_1988.sqlite',
    code: 'OH1988',
    moduleId: 'oh1988',
    title: 'Ukrainian fixture',
    language: 'uk',
    description: '',
    canon: '',
    versification: '',
    license: '',
    sourceSummary: '',
  );
  int previewCalls = 0;
  static const greek = BibleModuleInfo(
    fileName: 'bible_lxx_tr.sqlite',
    code: 'LXX_TR',
    moduleId: 'lxx_tr',
    language: 'grc',
    role: 'original',
    title: 'Greek fixture',
    description: '',
    canon: '',
    versification: '',
    license: '',
    sourceSummary: '',
  );
  @override
  Future<List<BibleModuleInfo>> cachedCatalog() async => [english, ukrainian];
  @override
  Future<List<BibleModuleInfo>> loadCatalog({bool refresh = false}) async => [
    english,
    ukrainian,
  ];
  @override
  Future<String?> preferredModuleFile() async =>
      _selectedModule?.call() == ukrainian.fileName
      ? ukrainian.fileName
      : english.fileName;
  @override
  Future<BiblePreview> loadPreview(
    List<String> keys, {
    String? moduleFile,
  }) async {
    previewCalls++;
    final file = moduleFile ?? await preferredModuleFile();
    final info = file == greek.fileName
        ? greek
        : file == ukrainian.fileName
        ? ukrainian
        : english;
    return (
      module: info,
      verses: [
        for (final key in keys)
          BibleVerseText(
            verseKey: key,
            text: info == greek
                ? 'λόγος G10 θεός G20 ποιέω G30'
                : '${info.language == 'uk' ? 'Український текст' : 'English passage'} $key',
          ),
      ],
    );
  }
}

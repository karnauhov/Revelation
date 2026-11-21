import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/data/repositories/allusion_search_repository.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_postings.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/domain/models/bible_verse_text.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late BibleVerseMap map;
  late Uint8List bytes;
  setUpAll(() async {
    map = await BibleVerseMap.loadFromAssets();
    bytes = Uint8List.sublistView(
      await rootBundle.load('assets/data/allusion_index.bin'),
    );
  });
  const AllusionQuery query = (
    bookId: 66,
    chapter: 1,
    verse: 1,
    length: 1,
    scope: AllusionScope.wholeBible,
  );
  test(
    'prepared and cooperative searches preserve the published ranking',
    () async {
      final data = AllusionPostings.decode(bytes, verseCount: map.totalVerses);
      final index = AllusionIndex.fromPostings(map, data.postings);
      final result = index.search(query);
      expect(await index.searchInBatches(query), result);
      final verses = result.forLevel(AllusionLevel.verse);
      expect(verses, hasLength(238));
      expect(
        verses.first.reference,
        map.referenceFor(bookId: 66, chapter: 22, verse: 6),
      );
      final damaged = Uint8List.fromList(bytes);
      damaged.last ^= 1;
      expect(
        () => AllusionPostings.decode(damaged, verseCount: map.totalVerses),
        throwsFormatException,
      );
    },
  );

  test(
    'legacy index rebuilds once, survives an offline restart, and follows data revisions',
    () async {
      final db = _Corpus(map);
      Uint8List? cached;
      AllusionSearchRepository repository() => AllusionSearchRepository(
        dataSource: db,
        loadVerseMap: () async => map,
        readCache: () async => cached,
        writeCache: (bytes) async {
          cached = bytes;
        },
      );
      final first = repository();
      expect(await first.loadVerseMap(), same(map));
      expect(db.opens, 0);
      final loading = first.loadIndex();
      expect(first.loadIndex(), same(loading));
      final index = await loading;
      expect(db.scans, 1);
      expect(db.opens, db.closes);
      expect(await first.loadIndex(), same(index));
      final before = index.search(query);
      final restarted = repository();
      expect((await restarted.loadIndex()).search(query), before);
      expect(db.scans, 1);
      final diskSnapshot = cached!;
      final oldPolicy = AllusionPostings.decode(
        diskSnapshot,
        verseCount: map.totalVerses,
      );
      cached = oldPolicy.postings.encode({
        ...oldPolicy.metadata,
        'weights_sha256': 'previous-policy',
      });
      expect((await repository().loadIndex()).search(query), before);
      expect(db.scans, 2);
      cached = Uint8List.fromList(diskSnapshot)..last ^= 1;
      expect((await repository().loadIndex()).search(query), before);
      expect(db.scans, 3);
      // The same revision/policy can be transported inside an updated module.
      db.embedded = base64Encode(diskSnapshot);
      cached = null;
      expect((await repository().loadIndex()).search(query), before);
      expect(db.scans, 3);
      db.revision++;
      final refreshed = await restarted.loadIndex();
      expect(refreshed.search(query).forLevel(AllusionLevel.verse), isEmpty);
      expect(db.scans, 4);
      expect(db.opens, db.closes);
    },
  );

  test(
    'actual corpus digest invalidates a bundled record with the same version tuple',
    () async {
      final db = _Corpus(map)
        ..revision = 17
        ..date = DateTime.utc(2026, 7, 25, 7, 16, 8);
      final repo = AllusionSearchRepository(
        dataSource: db,
        loadVerseMap: () async => map,
        readCache: () async => null,
        writeCache: (_) async {},
      );
      expect(
        (await repo.loadIndex()).search(query).forLevel(AllusionLevel.verse),
        hasLength(238),
      );
      expect(db.scans, 0);
      db.corpusHash = 'modified';
      expect(
        (await repo.loadIndex()).search(query).forLevel(AllusionLevel.verse),
        isEmpty,
      );
      expect(db.scans, 1);
    },
  );
  test(
    'a changed chapter boundary with the same total invalidates previously prepared postings',
    () async {
      final json =
          jsonDecode(await rootBundle.loadString(BibleVerseMap.assetPath))
              as Map<String, Object?>;
      final chapters =
          ((json['books'] as List).first as Map)['chapters'] as List;
      chapters[0] = (chapters[0] as int) - 1;
      chapters[1] = (chapters[1] as int) + 1;
      final alternate = BibleVerseMap.fromJson(json);
      expect(alternate.totalVerses, map.totalVerses);
      final db = _Corpus(alternate)
        ..revision = 17
        ..date = DateTime.utc(2026, 7, 25, 7, 16, 8);
      Uint8List? saved = bytes;
      AllusionSearchRepository repo() => AllusionSearchRepository(
        dataSource: db,
        loadVerseMap: () async => alternate,
        readCache: () async => saved,
        writeCache: (value) async {
          saved = value;
        },
      );
      await repo().loadIndex();
      expect(db.scans, 1);
      await repo().loadIndex();
      expect(db.scans, 1);
    },
  );
}

class _Corpus implements BibleModuleDataSource {
  _Corpus(this.map);
  final BibleVerseMap map;
  int revision = 1, opens = 0, closes = 0, scans = 0;
  DateTime date = DateTime.utc(2020);
  String? corpusHash, embedded;

  @override
  BibleModuleDB openModule(String moduleFile) {
    opens++;
    return _Snapshot(this);
  }

  @override
  Future<List<String>> listModuleFiles({
    required String defaultModuleFile,
  }) async => [defaultModuleFile];
}

class _Snapshot extends Fake implements BibleModuleDB {
  _Snapshot(this.corpus);
  final _Corpus corpus;
  @override
  Future<T> transaction<T>(
    Future<T> Function() action, {
    bool requireNew = false,
  }) => action();
  @override
  Future<DatabaseVersionInfo?> readVersionInfo() async => DatabaseVersionInfo(
    schemaVersion: 3,
    dataVersion: corpus.revision,
    date: corpus.date,
  );
  @override
  Future<String?> readMetadataValue(String key) async =>
      key == 'allusion_corpus_sha256' ? corpus.corpusHash : corpus.embedded;
  @override
  Stream<List<BibleVerseText>> readGreekIndexPages() async* {
    corpus.scans++;
    yield [
      BibleVerseText(
        verseKey: corpus.map
            .referenceFor(bookId: 66, chapter: 1, verse: 1)
            .verseKey,
        text: 'G2316 G32 G3004',
      ),
      BibleVerseText(
        verseKey: '001',
        text: corpus.revision == 1 ? 'G2316 G32 G3004' : 'G32',
      ),
    ];
  }

  @override
  Future<void> close() async {
    corpus.closes++;
  }
}

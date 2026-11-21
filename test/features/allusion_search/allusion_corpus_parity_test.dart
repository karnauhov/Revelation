@TestOn('vm')
library;

import 'dart:io';

import 'package:drift/native.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_postings.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:sqlite3/sqlite3.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
    'prepared postings reproduce every weighted pair and every rank of the live Greek corpus',
    () async {
      final map = await BibleVerseMap.loadFromAssets();
      final prepared = AllusionPostings.decode(
        Uint8List.sublistView(
          await rootBundle.load('assets/data/allusion_index.bin'),
        ),
        verseCount: map.totalVerses,
      );
      expect(prepared.metadata['canon'], map.canonSignature);
      final weights = prepared.postings.baseWeights;
      final builder = AllusionIndexBuilder(map, {
        for (var number = 1; number < weights.length; number++)
          number: weights[number],
      });
      final db = BibleModuleDB(
        NativeDatabase.opened(
          sqlite3.open(
            File('web/db/bible_lxx_tr.sqlite').absolute.path,
            mode: OpenMode.readOnly,
          ),
          enableMigrations: false,
        ),
      );
      try {
        await for (final page in db.readGreekIndexPages()) {
          builder.add(page);
        }
      } finally {
        await db.close();
      }
      final source = builder.finish(), stored = prepared.postings;
      expect(source.documents, stored.documents);
      expect(source.baseWeights, orderedEquals(stored.baseWeights));
      expect(source.verseOffsets, orderedEquals(stored.verseOffsets));
      expect(source.termOffsets, orderedEquals(stored.termOffsets));
      expect(source.terms, orderedEquals(stored.terms));
      expect(source.verses, orderedEquals(stored.verses));
      final built = AllusionIndex.fromPostings(map, source);
      final bundled = AllusionIndex.fromPostings(map, stored);
      for (final AllusionQuery query in [
        (
          bookId: 66,
          chapter: 1,
          verse: 1,
          length: 1,
          scope: AllusionScope.wholeBible,
        ),
        (
          bookId: 66,
          chapter: 2,
          verse: 27,
          length: 3,
          scope: AllusionScope.oldTestament,
        ),
        (
          bookId: 1,
          chapter: 1,
          verse: 1,
          length: 77,
          scope: AllusionScope.newTestament,
        ),
      ]) {
        expect(bundled.search(query), built.search(query));
      }
    },
  );
}

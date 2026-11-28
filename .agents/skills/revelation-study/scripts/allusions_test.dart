import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart' show debugPrintSynchronously;
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_postings.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test('query the shipped REV113 index', () async {
    final query =
        jsonDecode(Platform.environment['REVELATION_STUDY_QUERY']!)
            as Map<String, dynamic>;
    final map = await BibleVerseMap.loadFromAssets();
    final source = map.referenceForKey(query['key'] as String)!;
    final prepared = AllusionPostings.decode(
      Uint8List.sublistView(
        await rootBundle.load('assets/data/allusion_index.bin'),
      ),
      verseCount: map.totalVerses,
    );
    final metadata = prepared.metadata;
    final db = query['metadata'] as Map<String, dynamic>;
    expect(metadata['canon'], map.canonSignature);
    expect(metadata['module'], 'lxx_tr');
    expect(metadata['schema'], int.parse(db['schema_version']));
    expect(metadata['revision'], int.parse(db['data_version']));
    expect(DateTime.parse(metadata['date']), DateTime.parse(db['date']));
    if (db.containsKey('allusion_corpus_sha256')) {
      expect(metadata['corpus_sha256'], db['allusion_corpus_sha256']);
    }

    final length = query['length'] as int;
    final scope = AllusionScope.values.byName(query['scope']);
    final level = AllusionLevel.values.byName(query['level']);
    final result = AllusionIndex.fromPostings(map, prepared.postings).search((
      bookId: source.bookId,
      chapter: source.chapter,
      verse: source.verse,
      length: length,
      scope: scope,
    ));
    String label(BibleVerseReference ref) =>
        '${map.bookCode(ref.bookId)} ${ref.chapter}:${ref.verse} [${ref.verseKey}]';
    final matches = result.forLevel(level);
    debugPrintSynchronously(
      '${label(result.start)} - ${label(result.end)} | scope=${scope.name} '
      'level=${level.name} | total=${matches.length} | corpus=${metadata['corpus_sha256']}',
    );
    var rank = 0;
    for (final match in matches.take(query['limit'] as int)) {
      final codes = match.numbers.map((number) => 'G$number').join(', ');
      debugPrintSynchronously(
        '${++rank}. ${label(match.reference)} | ${match.score.toStringAsFixed(6)} | $codes',
      );
    }
  });
}

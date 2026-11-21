import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:revelation/features/allusion_search/domain/models/allusion_results.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_index.dart';
import 'package:revelation/features/allusion_search/domain/services/allusion_postings.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/storage/allusion_index_cache.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

typedef _PreparedIndex = ({
  Map<String, dynamic> metadata,
  AllusionPostings postings,
});
typedef _Revision = ({DatabaseVersionInfo version, String? corpusHash});

class AllusionSearchRepository {
  AllusionSearchRepository({
    BibleModuleDataSource dataSource = const LocalBibleModuleDataSource(),
    Future<BibleVerseMap> Function()? loadVerseMap,
    Future<Uint8List?> Function() readCache = readCachedAllusionIndex,
    Future<void> Function(Uint8List) writeCache = writeCachedAllusionIndex,
  }) : _dataSource = dataSource,
       _loadMap = loadVerseMap ?? BibleVerseMap.loadFromAssets,
       _readCache = readCache,
       _writeCache = writeCache;

  final BibleModuleDataSource _dataSource;
  final Future<BibleVerseMap> Function() _loadMap;
  final Future<Uint8List?> Function() _readCache;
  final Future<void> Function(Uint8List) _writeCache;
  Future<BibleVerseMap>? _map;
  Future<_PreparedIndex>? _bundle;
  Future<AllusionIndex>? _inFlight;
  _Revision? _currentRevision;
  AllusionIndex? _currentIndex;

  Future<BibleVerseMap> loadVerseMap() =>
      _map ??= _loadMap().catchError((Object error, StackTrace stack) {
        _map = null;
        Error.throwWithStackTrace(error, stack);
      });

  Future<AllusionIndex> loadIndex() =>
      _inFlight ??= _loadIndex().whenComplete(() => _inFlight = null);

  Future<_PreparedIndex> _readBundle() async {
    final bytes = await rootBundle.load('assets/data/allusion_index.bin');
    return AllusionPostings.decode(Uint8List.sublistView(bytes));
  }

  Future<AllusionIndex> _loadIndex() async {
    final map = await loadVerseMap();
    final db = _dataSource.openModule('bible_lxx_tr.sqlite');
    try {
      return await db.transaction(() async {
        final version = await db.readVersionInfo();
        final revision = version == null
            ? null
            : (
                version: version,
                corpusHash: await db.readMetadataValue(
                  'allusion_corpus_sha256',
                ),
              );
        if (revision != null &&
            revision == _currentRevision &&
            _currentIndex != null) {
          return _currentIndex!;
        }

        final bundled = await (_bundle ??= _readBundle().catchError((
          Object error,
          StackTrace stack,
        ) {
          _bundle = null;
          Error.throwWithStackTrace(error, stack);
        }));
        final AllusionPostings postings;
        if (_matchesRevision(bundled.metadata, revision, bundled: true) &&
            bundled.metadata['canon'] == map.canonSignature) {
          postings = bundled.postings;
        } else {
          postings = await _forOtherRevision(db, map, bundled, revision);
        }
        final index = AllusionIndex.fromPostings(map, postings);
        _currentRevision = revision;
        _currentIndex = index;
        return index;
      });
    } finally {
      await db.close();
    }
  }

  Future<AllusionPostings> _forOtherRevision(
    BibleModuleDB db,
    BibleVerseMap map,
    _PreparedIndex bundled,
    _Revision? revision,
  ) async {
    AllusionPostings? compatible(Uint8List bytes) {
      try {
        final candidate = AllusionPostings.decode(
          bytes,
          verseCount: map.totalVerses,
        );
        final metadata = candidate.metadata;
        if (_matchesRevision(metadata, revision) &&
            metadata['policy'] == bundled.metadata['policy'] &&
            metadata['weights_sha256'] == bundled.metadata['weights_sha256'] &&
            metadata['canon'] == map.canonSignature) {
          return candidate.postings;
        }
      } on FormatException {
        // Partial or incompatible derived data can be regenerated from the module.
      }
      return null;
    }

    if (revision != null) {
      final embedded = await db.readMetadataValue('allusion_index_v1');
      if (embedded != null) {
        try {
          final postings = compatible(base64Decode(embedded));
          if (postings != null) return postings;
        } on FormatException {
          // An older producer may use a different encoding.
        }
      }
      try {
        final cached = await _readCache();
        final postings = cached == null ? null : compatible(cached);
        if (postings != null) return postings;
      } catch (_) {
        // Browser privacy mode and read-only environments can disable the cache.
      }
    }

    final base = bundled.postings.baseWeights;
    final builder = AllusionIndexBuilder(map, {
      for (var i = 1; i < base.length; i++) i: base[i],
    });
    await for (final page in db.readGreekIndexPages()) {
      builder.add(page);
      // On Web compute shares the UI isolate. Yield between bounded database pages.
      await Future<void>.delayed(Duration.zero);
    }
    final postings = builder.finish();
    if (revision != null) {
      final metadata = {
        ...bundled.metadata,
        'canon': map.canonSignature,
        if (bundled.metadata['canon'] != map.canonSignature)
          'canon_sha256': null,
        'schema': revision.version.schemaVersion,
        'revision': revision.version.dataVersion,
        'date': revision.version.date.toUtc().toIso8601String(),
        'corpus_sha256': revision.corpusHash,
      };
      try {
        await _writeCache(postings.encode(metadata));
      } catch (_) {
        // The in-memory index remains usable if persistence fails.
      }
    }
    return postings;
  }

  static bool _matchesRevision(
    Map<String, dynamic> metadata,
    _Revision? revision, {
    bool bundled = false,
  }) {
    if (revision == null || metadata['module'] != 'lxx_tr') return false;
    final date = metadata['date'];
    return metadata['schema'] == revision.version.schemaVersion &&
        metadata['revision'] == revision.version.dataVersion &&
        date is String &&
        DateTime.tryParse(date)?.isAtSameMomentAs(revision.version.date) ==
            true &&
        ((bundled && revision.corpusHash == null) ||
            metadata['corpus_sha256'] == revision.corpusHash);
  }

  Future<AllusionResults> search(AllusionIndex index, AllusionQuery query) =>
      kIsWeb
      ? index.searchInBatches(query)
      : compute(_search, (index: index, query: query));
}

AllusionResults _search(({AllusionIndex index, AllusionQuery query}) input) =>
    input.index.search(input.query);

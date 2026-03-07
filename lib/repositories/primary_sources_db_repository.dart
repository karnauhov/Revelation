import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:revelation/managers/db_manager.dart';
import 'package:revelation/models/page.dart' as model;
import 'package:revelation/models/page_rect.dart';
import 'package:revelation/models/page_word.dart';
import 'package:revelation/models/primary_source.dart';
import 'package:revelation/models/primary_source_link_info.dart';
import 'package:revelation/models/verse.dart';

class PrimarySourcesLoadResult {
  final List<PrimarySource> fullPrimarySources;
  final List<PrimarySource> significantPrimarySources;
  final List<PrimarySource> fragmentsPrimarySources;

  const PrimarySourcesLoadResult({
    required this.fullPrimarySources,
    required this.significantPrimarySources,
    required this.fragmentsPrimarySources,
  });
}

class PrimarySourcesDbRepository {
  final DBManager _dbManager;

  PrimarySourcesDbRepository({DBManager? dbManager})
    : _dbManager = dbManager ?? DBManager();

  Future<PrimarySourcesLoadResult> loadGroupedSources() async {
    final sources = await getAllSources(includePreviewBytes: true);
    final groupKindById = {
      for (final row in _dbManager.primarySourceRows) row.id: row.groupKind,
    };

    return PrimarySourcesLoadResult(
      fullPrimarySources: sources
          .where((source) => groupKindById[source.id] == 'full')
          .toList(growable: false),
      significantPrimarySources: sources
          .where((source) => groupKindById[source.id] == 'significant')
          .toList(growable: false),
      fragmentsPrimarySources: sources
          .where((source) => groupKindById[source.id] == 'fragment')
          .toList(growable: false),
    );
  }

  Future<List<PrimarySource>> getAllSources({
    bool includePreviewBytes = false,
  }) async {
    final sources = getAllSourcesSync();
    if (!includePreviewBytes) {
      return sources;
    }

    return Future.wait(
      sources.map((source) async {
        final previewBytes = await _loadPreviewBytes(source.preview);
        return _copyWithPreviewBytes(source, previewBytes);
      }),
    );
  }

  List<PrimarySource> getAllSourcesSync() {
    if (!_dbManager.isInitialized) {
      return const [];
    }

    final localizedRowsBySource = {
      for (final row in _dbManager.primarySourceTextRows) row.sourceId: row,
    };
    final linkTitleOverrides = {
      for (final row in _dbManager.primarySourceLinkTextRows)
        '${row.sourceId}|${row.linkId}': row.title,
    };

    final linksBySource = _groupBy(
      _dbManager.primarySourceLinkRows,
      (row) => row.sourceId,
    );
    final attributionsBySource = _groupBy(
      _dbManager.primarySourceAttributionRows,
      (row) => row.sourceId,
    );
    final pagesBySource = _groupBy(
      _dbManager.primarySourcePageRows,
      (row) => row.sourceId,
    );
    final wordsByPage = _groupBy(
      _dbManager.primarySourceWordRows,
      (row) => '${row.sourceId}|${row.pageName}',
    );
    final versesByPage = _groupBy(
      _dbManager.primarySourceVerseRows,
      (row) => '${row.sourceId}|${row.pageName}',
    );

    final sourceRows = [..._dbManager.primarySourceRows]
      ..sort(
        (a, b) => _compareSourceRows(
          a.groupKind,
          a.sortOrder,
          a.id,
          b.groupKind,
          b.sortOrder,
          b.id,
        ),
      );

    return sourceRows
        .map((sourceRow) {
          final localized = localizedRowsBySource[sourceRow.id];
          if (localized == null) {
            return null;
          }

          final sourceLinks = [...?linksBySource[sourceRow.id]]
            ..sort((a, b) => a.sortOrder.compareTo(b.sortOrder));
          final sourceAttributions = [...?attributionsBySource[sourceRow.id]]
            ..sort((a, b) => a.sortOrder.compareTo(b.sortOrder));
          final sourcePages = [...?pagesBySource[sourceRow.id]]
            ..sort((a, b) => a.sortOrder.compareTo(b.sortOrder));

          final pages = sourcePages
              .map((pageRow) {
                final pageKey = '${pageRow.sourceId}|${pageRow.pageName}';
                final words = [...?wordsByPage[pageKey]]
                  ..sort((a, b) => a.wordIndex.compareTo(b.wordIndex));
                final verses = [...?versesByPage[pageKey]]
                  ..sort((a, b) => a.verseIndex.compareTo(b.verseIndex));

                return model.Page(
                  name: pageRow.pageName,
                  content: pageRow.contentRef,
                  image: pageRow.imagePath,
                  words: words.map(_buildWord).toList(growable: false),
                  verses: verses.map(_buildVerse).toList(growable: false),
                );
              })
              .toList(growable: false);

          return PrimarySource(
            id: sourceRow.id,
            title: localized.titleMarkup,
            date: localized.dateLabel,
            content: localized.contentLabel,
            quantity: sourceRow.versesCount,
            material: localized.materialText,
            textStyle: localized.textStyleText,
            found: localized.foundText,
            classification: localized.classificationText,
            currentLocation: localized.currentLocationText,
            link1Title: '',
            link1Url: '',
            link2Title: '',
            link2Url: '',
            link3Title: '',
            link3Url: '',
            preview: sourceRow.previewResourceKey,
            maxScale: sourceRow.defaultMaxScale,
            isMonochrome: sourceRow.imagesAreMonochrome,
            pages: pages,
            links: sourceLinks
                .map(
                  (link) => PrimarySourceLinkInfo(
                    role: link.linkRole,
                    url: link.url,
                    titleOverride:
                        linkTitleOverrides['${link.sourceId}|${link.linkId}'] ??
                        '',
                  ),
                )
                .toList(growable: false),
            attributes: sourceAttributions
                .map(
                  (item) => <String, String>{
                    'text': item.displayText,
                    'url': item.url,
                  },
                )
                .toList(growable: false),
            permissionsReceived: sourceRow.canShowImages,
          );
        })
        .whereType<PrimarySource>()
        .toList(growable: false);
  }

  PrimarySource? findSourceById(String sourceId) {
    final normalizedId = sourceId.trim();
    if (normalizedId.isEmpty) {
      return null;
    }
    for (final source in getAllSourcesSync()) {
      if (source.id == normalizedId) {
        return source;
      }
    }
    return null;
  }

  Future<Uint8List?> _loadPreviewBytes(String previewKey) async {
    if (previewKey.isEmpty || previewKey.startsWith('assets/')) {
      return null;
    }
    return _dbManager.getCommonResourceData(previewKey);
  }

  PrimarySource _copyWithPreviewBytes(
    PrimarySource source,
    Uint8List? previewBytes,
  ) {
    return PrimarySource(
      id: source.id,
      title: source.title,
      date: source.date,
      content: source.content,
      quantity: source.quantity,
      material: source.material,
      textStyle: source.textStyle,
      found: source.found,
      classification: source.classification,
      currentLocation: source.currentLocation,
      link1Title: source.link1Title,
      link1Url: source.link1Url,
      link2Title: source.link2Title,
      link2Url: source.link2Url,
      link3Title: source.link3Title,
      link3Url: source.link3Url,
      preview: source.preview,
      previewBytes: previewBytes,
      maxScale: source.maxScale,
      isMonochrome: source.isMonochrome,
      pages: source.pages,
      links: source.links,
      attributes: source.attributes,
      permissionsReceived: source.permissionsReceived,
    )..showMore = source.showMore;
  }

  PageWord _buildWord(dynamic row) {
    return PageWord(
      row.wordText,
      _decodeRectangles(row.rectanglesJson),
      notExist: _decodeIntList(row.missingCharIndexesJson),
      sn: row.strongNumber,
      snPronounce: row.strongPronounce,
      snXshift: row.strongXShift,
    );
  }

  Verse _buildVerse(dynamic row) {
    return Verse(
      chapterNumber: row.chapterNumber,
      verseNumber: row.verseNumber,
      labelPosition: Offset(row.labelX, row.labelY),
      wordIndexes: _decodeIntList(row.wordIndexesJson),
      contours: _decodeContours(row.contoursJson),
    );
  }

  List<int> _decodeIntList(String rawJson) {
    final decoded = jsonDecode(rawJson) as List<dynamic>;
    return decoded.map((item) => (item as num).toInt()).toList(growable: false);
  }

  List<PageRect> _decodeRectangles(String rawJson) {
    final decoded = jsonDecode(rawJson) as List<dynamic>;
    return decoded
        .map((item) {
          final values = (item as List<dynamic>)
              .map((value) => (value as num).toDouble())
              .toList(growable: false);
          return PageRect(values[0], values[1], values[2], values[3]);
        })
        .toList(growable: false);
  }

  List<List<Offset>> _decodeContours(String rawJson) {
    final decoded = jsonDecode(rawJson) as List<dynamic>;
    return decoded
        .map((contour) {
          return (contour as List<dynamic>)
              .map((point) {
                final values = (point as List<dynamic>)
                    .map((value) => (value as num).toDouble())
                    .toList(growable: false);
                return Offset(values[0], values[1]);
              })
              .toList(growable: false);
        })
        .toList(growable: false);
  }

  Map<String, List<T>> _groupBy<T>(
    Iterable<T> rows,
    String Function(T row) keyBuilder,
  ) {
    final result = <String, List<T>>{};
    for (final row in rows) {
      final key = keyBuilder(row);
      result.putIfAbsent(key, () => <T>[]).add(row);
    }
    return result;
  }

  int _compareSourceRows(
    String groupA,
    int sortOrderA,
    String idA,
    String groupB,
    int sortOrderB,
    String idB,
  ) {
    final groupOrder = {'full': 0, 'significant': 1, 'fragment': 2};
    final groupCompare = (groupOrder[groupA] ?? 99).compareTo(
      groupOrder[groupB] ?? 99,
    );
    if (groupCompare != 0) {
      return groupCompare;
    }
    final sortCompare = sortOrderA.compareTo(sortOrderB);
    if (sortCompare != 0) {
      return sortCompare;
    }
    return idA.compareTo(idB);
  }
}

import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/verse.dart';
import 'package:revelation/features/primary_sources/data/repositories/primary_sources_db_repository.dart';

class ResolvedWordReference {
  final PrimarySource source;
  final model.Page page;
  final PageWord word;
  final int wordIndex;

  const ResolvedWordReference({
    required this.source,
    required this.page,
    required this.word,
    required this.wordIndex,
  });
}

class ResolvedVerseReference {
  final PrimarySource source;
  final model.Page page;
  final Verse verse;
  final int verseIndex;

  const ResolvedVerseReference({
    required this.source,
    required this.page,
    required this.verse,
    required this.verseIndex,
  });
}

class PrimarySourceReferenceService {
  final PrimarySourcesDbRepository _repository;

  PrimarySourceReferenceService({PrimarySourcesDbRepository? repository})
    : _repository = repository ?? PrimarySourcesDbRepository();

  PrimarySource? findSourceById(String sourceId) {
    final normalizedId = sourceId.trim();
    if (normalizedId.isEmpty) {
      return null;
    }

    for (final source in _getAllSources()) {
      if (source.id == normalizedId) {
        return source;
      }
    }
    return null;
  }

  model.Page? findPageByName(PrimarySource source, String pageName) {
    final normalizedName = pageName.trim();
    if (normalizedName.isEmpty) {
      return null;
    }

    for (final page in source.pages) {
      if (page.name == normalizedName) {
        return page;
      }
    }
    return null;
  }

  ResolvedWordReference? resolveWord({
    required int wordIndex,
    String? sourceId,
    String? pageName,
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    if (wordIndex < 0) {
      return null;
    }

    final source = _resolveSource(
      sourceId: sourceId,
      fallbackSource: fallbackSource,
    );
    if (source == null) {
      return null;
    }

    final page = _resolvePageForWord(
      source,
      wordIndex: wordIndex,
      pageName: pageName,
      fallbackSource: fallbackSource,
      fallbackPage: fallbackPage,
    );
    if (page == null || wordIndex >= page.words.length) {
      return null;
    }

    return ResolvedWordReference(
      source: source,
      page: page,
      word: page.words[wordIndex],
      wordIndex: wordIndex,
    );
  }

  List<ResolvedVerseReference> resolveVerse({
    required int chapterNumber,
    required int verseNumber,
    String? sourceId,
    String? pageName,
    bool combineAcrossPages = true,
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    if (chapterNumber <= 0 || verseNumber <= 0) {
      return const [];
    }

    final source = _resolveSource(
      sourceId: sourceId,
      fallbackSource: fallbackSource,
    );
    if (source == null) {
      return const [];
    }

    final pages = _resolvePagesForVerse(
      source,
      chapterNumber: chapterNumber,
      verseNumber: verseNumber,
      pageName: pageName,
      combineAcrossPages: combineAcrossPages,
      fallbackSource: fallbackSource,
      fallbackPage: fallbackPage,
    );

    if (pages.isEmpty) {
      return const [];
    }

    final result = <ResolvedVerseReference>[];
    for (final page in pages) {
      for (int i = 0; i < page.verses.length; i++) {
        final verse = page.verses[i];
        if (verse.chapterNumber == chapterNumber &&
            verse.verseNumber == verseNumber) {
          result.add(
            ResolvedVerseReference(
              source: source,
              page: page,
              verse: verse,
              verseIndex: i,
            ),
          );
        }
      }
    }

    return result;
  }

  PrimarySource? _resolveSource({
    String? sourceId,
    PrimarySource? fallbackSource,
  }) {
    final normalizedSourceId = sourceId?.trim();

    if (normalizedSourceId == null || normalizedSourceId.isEmpty) {
      return fallbackSource;
    }

    if (fallbackSource != null && fallbackSource.id == normalizedSourceId) {
      return fallbackSource;
    }

    return findSourceById(normalizedSourceId);
  }

  model.Page? _resolvePageForWord(
    PrimarySource source, {
    required int wordIndex,
    String? pageName,
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    final normalizedPageName = pageName?.trim();

    if (normalizedPageName != null && normalizedPageName.isNotEmpty) {
      return findPageByName(source, normalizedPageName);
    }

    final canUseFallbackPage =
        fallbackSource != null &&
        fallbackPage != null &&
        fallbackSource.id == source.id &&
        source.pages.contains(fallbackPage) &&
        wordIndex < fallbackPage.words.length;

    if (canUseFallbackPage) {
      return fallbackPage;
    }

    for (final page in source.pages) {
      if (wordIndex >= 0 && wordIndex < page.words.length) {
        return page;
      }
    }

    return null;
  }

  List<model.Page> _resolvePagesForVerse(
    PrimarySource source, {
    required int chapterNumber,
    required int verseNumber,
    String? pageName,
    required bool combineAcrossPages,
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    final normalizedPageName = pageName?.trim();

    if (normalizedPageName != null && normalizedPageName.isNotEmpty) {
      final page = findPageByName(source, normalizedPageName);
      return page == null ? const [] : [page];
    }

    final hasVerseInFallback =
        fallbackSource != null &&
        fallbackPage != null &&
        fallbackSource.id == source.id &&
        source.pages.contains(fallbackPage) &&
        _pageContainsVerse(fallbackPage, chapterNumber, verseNumber);

    if (hasVerseInFallback && !combineAcrossPages) {
      return [fallbackPage];
    }

    final matches = <model.Page>[];
    for (final page in source.pages) {
      if (_pageContainsVerse(page, chapterNumber, verseNumber)) {
        matches.add(page);
      }
    }

    if (matches.isEmpty) {
      return const [];
    }

    if (combineAcrossPages) {
      return matches;
    }

    if (hasVerseInFallback) {
      return [fallbackPage];
    }

    return [matches.first];
  }

  bool _pageContainsVerse(model.Page page, int chapterNumber, int verseNumber) {
    for (final verse in page.verses) {
      if (verse.chapterNumber == chapterNumber &&
          verse.verseNumber == verseNumber) {
        return true;
      }
    }
    return false;
  }

  List<PrimarySource> _getAllSources() {
    return _repository.getAllSourcesSync();
  }
}

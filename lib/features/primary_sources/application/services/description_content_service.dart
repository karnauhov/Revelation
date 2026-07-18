import 'package:revelation/infra/db/data_sources/description_data_source.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/page_word.dart';
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/features/primary_sources/application/services/manuscript_greek_text_converter.dart';
import 'package:revelation/features/primary_sources/application/services/nomina_sacra_pronunciation_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_service.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_word_text_formatter.dart';
import 'package:revelation/shared/services/pronunciation_service.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

class DescriptionContentService {
  DescriptionContentService({
    DescriptionDataSource? dataSource,
    PronunciationService? pronunciation,
    NominaSacraPronunciationService? nominaSacraPronunciation,
    PrimarySourceReferenceService? referenceResolver,
    ManuscriptGreekTextConverter? manuscriptGreekTextConverter,
    PrimarySourceWordTextFormatter? wordTextFormatter,
    StrongsDictionaryContentService? strongsDictionaryContentService,
    BibleVerseMap? verseMap,
  }) : this._(
         dataSource ?? DbManagerDescriptionDataSource(),
         pronunciation: pronunciation,
         nominaSacraPronunciation: nominaSacraPronunciation,
         referenceResolver: referenceResolver,
         manuscriptGreekTextConverter: manuscriptGreekTextConverter,
         wordTextFormatter: wordTextFormatter,
         strongsDictionaryContentService: strongsDictionaryContentService,
         verseMap: verseMap,
       );

  DescriptionContentService._(
    DescriptionDataSource dataSource, {
    PronunciationService? pronunciation,
    NominaSacraPronunciationService? nominaSacraPronunciation,
    PrimarySourceReferenceService? referenceResolver,
    ManuscriptGreekTextConverter? manuscriptGreekTextConverter,
    PrimarySourceWordTextFormatter? wordTextFormatter,
    StrongsDictionaryContentService? strongsDictionaryContentService,
    BibleVerseMap? verseMap,
  }) : _dataSource = dataSource,
       _pronunciation = pronunciation ?? PronunciationService(),
       _nominaSacraPronunciation =
           nominaSacraPronunciation ?? NominaSacraPronunciationService(),
       _referenceResolver =
           referenceResolver ?? PrimarySourceReferenceService(),
       _wordTextFormatter =
           wordTextFormatter ??
           PrimarySourceWordTextFormatter(
             manuscriptGreekTextConverter:
                 manuscriptGreekTextConverter ?? ManuscriptGreekTextConverter(),
             nominaSacraPronunciation:
                 nominaSacraPronunciation ?? NominaSacraPronunciationService(),
           ),
       _strongsDictionaryContentService =
           strongsDictionaryContentService ??
           StrongsDictionaryContentService(
             repository: StrongsDictionaryRepository(
               databaseGateway: _DescriptionDataSourceLexiconGateway(
                 dataSource,
               ),
             ),
             pronunciation: pronunciation,
             verseMap: verseMap,
           );

  final DescriptionDataSource _dataSource;
  final PronunciationService _pronunciation;
  final NominaSacraPronunciationService _nominaSacraPronunciation;
  final PrimarySourceReferenceService _referenceResolver;
  final PrimarySourceWordTextFormatter _wordTextFormatter;
  final StrongsDictionaryContentService _strongsDictionaryContentService;

  DescriptionContent? buildContent(
    AppLocalizations localizations,
    DescriptionRequest request, {
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    if (!_dataSource.isInitialized) {
      return null;
    }

    return switch (request) {
      StrongDescriptionRequest strongRequest =>
        _strongsDictionaryContentService.buildStrongContent(
          localizations,
          strongRequest.strongNumber,
        ),
      WordDescriptionRequest wordRequest => _buildWordContent(
        localizations,
        wordRequest,
        fallbackSource: fallbackSource,
        fallbackPage: fallbackPage,
      ),
      VerseDescriptionRequest verseRequest => _buildVerseContent(
        localizations,
        verseRequest,
        fallbackSource: fallbackSource,
        fallbackPage: fallbackPage,
      ),
    };
  }

  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    return _strongsDictionaryContentService.buildStrongContent(
      localizations,
      strongNumber,
    );
  }

  List<StrongPickerEntry> getGreekStrongPickerEntries() {
    return _strongsDictionaryContentService.getPickerEntries();
  }

  int getNeighborStrongNumber(int current, {bool forward = true}) {
    return _strongsDictionaryContentService.getNeighborStrongNumber(
      current,
      forward: forward,
    );
  }

  String formatWordText(PageWord word) {
    return _wordTextFormatter.format(word);
  }

  bool doesStrongNumberExist(int sn) {
    return _strongsDictionaryContentService.isAllowedStrongNumber(sn);
  }

  DescriptionContent? _buildWordContent(
    AppLocalizations localizations,
    WordDescriptionRequest request, {
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    final resolved = _referenceResolver.resolveWord(
      sourceId: request.sourceId,
      pageName: request.pageName,
      wordIndex: request.wordIndex,
      fallbackSource: fallbackSource,
      fallbackPage: fallbackPage,
    );
    if (resolved == null) {
      return null;
    }

    return _buildWordDescriptionContent(
      localizations,
      resolved.word,
      includeHeading: true,
    );
  }

  DescriptionContent? buildSharedWordSupplementContent(
    AppLocalizations localizations,
    Iterable<PageWord> words,
  ) {
    final resolvedWords = words.toList(growable: false);
    if (resolvedWords.isEmpty) {
      return null;
    }

    final strongWords = resolvedWords
        .where((word) => word.sn != null)
        .toList(growable: false);
    if (strongWords.isEmpty) {
      return null;
    }

    final strongNumber = strongWords.first.sn!;
    for (final word in strongWords.skip(1)) {
      if (word.sn != strongNumber) {
        return null;
      }
    }

    return _buildWordDescriptionContent(
      localizations,
      strongWords.first,
      includeHeading: false,
    );
  }

  DescriptionContent? _buildVerseContent(
    AppLocalizations localizations,
    VerseDescriptionRequest request, {
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    final resolvedVerses = _referenceResolver.resolveVerse(
      sourceId: request.sourceId,
      pageName: request.pageName,
      chapterNumber: request.chapterNumber,
      verseNumber: request.verseNumber,
      combineAcrossPages: request.combineAcrossPages,
      fallbackSource: fallbackSource,
      fallbackPage: fallbackPage,
    );

    if (resolvedVerses.isEmpty) {
      return null;
    }

    final source = resolvedVerses.first.source;
    final verseRef = '${request.chapterNumber}:${request.verseNumber}';
    final buffer = StringBuffer();

    buffer.write('## ');
    buffer.write(localizations.app_name);
    buffer.write(' ');
    buffer.write(verseRef);
    buffer.write('\n\r');

    final parts = <String>[];
    for (final ref in resolvedVerses) {
      final words = ref.page.words;
      for (final wordIndex in ref.verse.wordIndexes) {
        if (wordIndex < 0 || wordIndex >= words.length) {
          continue;
        }
        final word = words[wordIndex];
        final text = formatWordText(word);
        parts.add('[$text](word:${source.id}:${ref.page.name}:$wordIndex)');
      }
    }

    if (parts.isNotEmpty) {
      buffer.write(parts.join(' '));
    } else {
      buffer.write(localizations.click_for_info);
    }

    return DescriptionContent(
      markdown: buffer.toString(),
      kind: DescriptionKind.verse,
    );
  }

  bool _containsAnyLetter(String text) {
    final regExp = RegExp(r'\p{L}', unicode: true);
    return regExp.hasMatch(text);
  }

  String? _resolveWordPronunciationSource(PageWord word) {
    if (word.snPronounce) {
      final nominaSacraSource = _nominaSacraPronunciation
          .resolvePronunciationSource(word.text);
      if (nominaSacraSource != null) {
        return nominaSacraSource;
      }
    }

    return word.text;
  }

  DescriptionContent? _buildWordDescriptionContent(
    AppLocalizations localizations,
    PageWord word, {
    required bool includeHeading,
  }) {
    final buffer = StringBuffer();

    if (includeHeading) {
      buffer.write('## ');
      buffer.write(formatWordText(word));
      buffer.write('\n\r');
    }

    if (word.sn != null) {
      buffer.write(localizations.strong_number);
      buffer.write(': ');
      buffer.write('**[${word.sn!}](strong:G${word.sn!})**');
      buffer.write('\n\r');
    }

    if (_containsAnyLetter(word.text)) {
      buffer.write(localizations.strong_pronunciation);
      buffer.write(': **');
      final pronunciationSource = _resolveWordPronunciationSource(word);
      if (pronunciationSource != null) {
        buffer.write(
          _pronunciation
              .convert(
                pronunciationSource.toLowerCase().trim(),
                _dataSource.languageCode,
              )
              .toLowerCase(),
        );
      }
      buffer.write('**\n\r');
    }

    if (word.sn != null) {
      final translation = _strongsDictionaryContentService
          .buildTranslationMarkdown(word.sn!);
      if (translation != null && translation.isNotEmpty) {
        buffer.write('\n\r');
        buffer.write(translation);
      }
    }

    final markdown = buffer.toString().trim();
    if (markdown.isEmpty) {
      return null;
    }

    return DescriptionContent(markdown: markdown, kind: DescriptionKind.word);
  }
}

class _DescriptionDataSourceLexiconGateway implements LexiconDatabaseGateway {
  const _DescriptionDataSourceLexiconGateway(this._dataSource);

  final DescriptionDataSource _dataSource;

  @override
  bool get isInitialized => _dataSource.isInitialized;

  @override
  String get languageCode => _dataSource.languageCode;

  @override
  List<common_db.GreekWord> get greekWords => _dataSource.greekWords;

  @override
  List<localized_db.GreekDesc> get greekDescs => _dataSource.greekDescs;

  @override
  Future<void> initialize(String language) async {}

  @override
  Future<void> updateLanguage(String language) async {}
}

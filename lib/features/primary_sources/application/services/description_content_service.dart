import 'package:flutter/material.dart';
import 'package:revelation/infra/db/data_sources/description_data_source.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/description_request.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/features/primary_sources/application/services/primary_source_reference_resolver.dart';
import 'package:revelation/utils/common.dart';
import 'package:revelation/utils/pronunciation.dart';

class DescriptionContentService {
  final DescriptionDataSource _dataSource;
  final Pronunciation _pronunciation;
  final PrimarySourceReferenceResolver _referenceResolver;

  List<GreekStrongPickerEntry>? _strongPickerEntriesCache;

  DescriptionContentService({
    DescriptionDataSource? dataSource,
    Pronunciation? pronunciation,
    PrimarySourceReferenceResolver? referenceResolver,
  }) : _dataSource = dataSource ?? DbManagerDescriptionDataSource(),
       _pronunciation = pronunciation ?? Pronunciation(),
       _referenceResolver =
           referenceResolver ?? PrimarySourceReferenceResolver();

  DescriptionContent? buildContent(
    BuildContext context,
    DescriptionRequest request, {
    PrimarySource? fallbackSource,
    model.Page? fallbackPage,
  }) {
    if (!_dataSource.isInitialized) {
      return null;
    }

    return switch (request) {
      StrongDescriptionRequest strongRequest => _buildStrongContent(
        context,
        strongRequest,
      ),
      WordDescriptionRequest wordRequest => _buildWordContent(
        context,
        wordRequest,
        fallbackSource: fallbackSource,
        fallbackPage: fallbackPage,
      ),
      VerseDescriptionRequest verseRequest => _buildVerseContent(
        context,
        verseRequest,
        fallbackSource: fallbackSource,
        fallbackPage: fallbackPage,
      ),
    };
  }

  DescriptionContent? buildStrongContent(
    BuildContext context,
    int strongNumber,
  ) {
    return buildContent(
      context,
      StrongDescriptionRequest(strongNumber: strongNumber),
    );
  }

  List<GreekStrongPickerEntry> getGreekStrongPickerEntries() {
    if (!_dataSource.isInitialized) {
      return const [];
    }

    _strongPickerEntriesCache ??= List<GreekStrongPickerEntry>.unmodifiable(
      _dataSource.greekWords
          .where((word) => doesStrongNumberExist(word.id))
          .map(
            (word) =>
                GreekStrongPickerEntry(number: word.id, word: word.word.trim()),
          )
          .where((entry) => entry.word.isNotEmpty)
          .toList()
        ..sort((a, b) => a.number.compareTo(b.number)),
    );

    return _strongPickerEntriesCache!;
  }

  int getNeighborStrongNumber(int current, {bool forward = true}) {
    const int minVal = 1;
    const int maxVal = 5624;

    if (current < minVal) {
      current = minVal;
    }
    if (current > maxVal) {
      current = maxVal;
    }

    int candidate = current;
    do {
      candidate = forward ? candidate + 1 : candidate - 1;
      if (candidate > maxVal) {
        candidate = minVal;
      }
      if (candidate < minVal) {
        candidate = maxVal;
      }
    } while (_isForbiddenStrongNumber(candidate));

    return candidate;
  }

  bool doesStrongNumberExist(int sn) {
    const int minVal = 1;
    const int maxVal = 5624;
    return sn >= minVal && sn <= maxVal && !_isForbiddenStrongNumber(sn);
  }

  DescriptionContent? _buildStrongContent(
    BuildContext context,
    StrongDescriptionRequest request,
  ) {
    final strongNumber = request.strongNumber;
    final wordIndex = _dataSource.greekWords.indexWhere(
      (word) => word.id == strongNumber,
    );
    if (wordIndex == -1) {
      return null;
    }

    final word = _dataSource.greekWords[wordIndex].word.trim();
    if (word.isEmpty) {
      return null;
    }

    final buffer = StringBuffer();

    buffer.write('## ');
    buffer.write(word);
    buffer.write('\n\r');

    buffer.write(AppLocalizations.of(context)!.strong_number);
    final prevId = getNeighborStrongNumber(
      _dataSource.greekWords[wordIndex].id,
      forward: false,
    );
    buffer.write(': [<-](strong:G$prevId) **');
    buffer.write(
      '[${_dataSource.greekWords[wordIndex].id}]'
      '(strong_picker:G${_dataSource.greekWords[wordIndex].id})',
    );
    final nextId = getNeighborStrongNumber(
      _dataSource.greekWords[wordIndex].id,
      forward: true,
    );
    buffer.write('** [->](strong:G$nextId)\n\r');

    buffer.write(AppLocalizations.of(context)!.strong_pronunciation);
    buffer.write(': **');
    buffer.write(
      _pronunciation
          .convert(word.toLowerCase(), _dataSource.languageCode)
          .toLowerCase(),
    );
    buffer.write('**\n\r');

    final descIndex = _dataSource.greekDescs.indexWhere(
      (desc) => desc.id == strongNumber,
    );
    if (descIndex != -1) {
      final desc = _dataSource.greekDescs[descIndex].desc.trim();
      if (desc.isNotEmpty) {
        buffer.write(_getTranslation(desc));
        buffer.write('\n\r');
      }
    }

    final category = _dataSource.greekWords[wordIndex].category.trim();
    if (category.isNotEmpty) {
      buffer.write(AppLocalizations.of(context)!.strong_part_of_speech);
      buffer.write(': **');
      buffer.write(_replaceKeys(context, category));
      buffer.write('**\n\r');
    }

    final origin = _dataSource.greekWords[wordIndex].origin.trim();
    if (origin.isNotEmpty) {
      buffer.write('\n\r');
      buffer.write(AppLocalizations.of(context)!.strong_origin);
      buffer.write(': ');
      buffer.write(_getOrigins(origin));
      buffer.write('\n\r');
    }

    final synonyms = _dataSource.greekWords[wordIndex].synonyms.trim();
    if (synonyms.isNotEmpty) {
      buffer.write('\n\r');
      buffer.write(AppLocalizations.of(context)!.strong_synonyms);
      buffer.write(': ');
      buffer.write(_getSynonyms(synonyms));
      buffer.write('\n\r');
    }

    final usage = _dataSource.greekWords[wordIndex].usage.trim();
    if (usage.isNotEmpty) {
      buffer.write(AppLocalizations.of(context)!.strong_usage);
      buffer.write(': ');
      buffer.write(_getUsage(usage));
      buffer.write('\n\r');
    }

    return DescriptionContent(
      markdown: buffer.toString(),
      kind: DescriptionKind.strongNumber,
    );
  }

  DescriptionContent? _buildWordContent(
    BuildContext context,
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

    final word = resolved.word;
    final buffer = StringBuffer();

    buffer.write('## ');
    buffer.write(_strikeThroughByIndexes(word.text, word.notExist));
    buffer.write('\n\r');

    if (word.sn != null) {
      buffer.write(AppLocalizations.of(context)!.strong_number);
      buffer.write(': ');
      buffer.write('**[${word.sn!}](strong:G${word.sn!})**');
      buffer.write('\n\r');
    }

    if (_containsAnyLetter(word.text)) {
      buffer.write(AppLocalizations.of(context)!.strong_pronunciation);
      buffer.write(': **');
      if (word.snPronounce && word.sn != null) {
        final index = _dataSource.greekWords.indexWhere((w) => w.id == word.sn);
        if (index != -1) {
          buffer.write(
            _pronunciation
                .convert(
                  _dataSource.greekWords[index].word.toLowerCase().trim(),
                  _dataSource.languageCode,
                )
                .toLowerCase(),
          );
        }
      } else {
        buffer.write(
          _pronunciation
              .convert(word.text.toLowerCase().trim(), _dataSource.languageCode)
              .toLowerCase(),
        );
      }
      buffer.write('**\n\r');
    }

    if (word.sn != null) {
      final descIndex = _dataSource.greekDescs.indexWhere(
        (desc) => desc.id == word.sn,
      );
      if (descIndex != -1) {
        final desc = _dataSource.greekDescs[descIndex].desc.trim();
        if (desc.isNotEmpty) {
          buffer.write('\n\r');
          buffer.write(_getTranslation(desc));
        }
      }
    }

    return DescriptionContent(
      markdown: buffer.toString(),
      kind: DescriptionKind.word,
    );
  }

  DescriptionContent? _buildVerseContent(
    BuildContext context,
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
    buffer.write(AppLocalizations.of(context)!.app_name);
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
        final text = _strikeThroughByIndexes(word.text, word.notExist);
        parts.add('[$text](word:${source.id}:${ref.page.name}:$wordIndex)');
      }
    }

    if (parts.isNotEmpty) {
      buffer.write(parts.join(' '));
    } else {
      buffer.write(AppLocalizations.of(context)!.click_for_info);
    }

    return DescriptionContent(
      markdown: buffer.toString(),
      kind: DescriptionKind.verse,
    );
  }

  bool _isForbiddenStrongNumber(int value) {
    return value == 2717 || (value >= 3203 && value <= 3302);
  }

  String _replaceKeys(BuildContext context, String input) {
    final regex = RegExp(r'@\w+');
    return input.replaceAllMapped(regex, (match) {
      final key = match.group(0)!;
      return locLinks(context, key);
    });
  }

  String _strikeThroughByIndexes(String word, Iterable<int> indices) {
    if (word.isEmpty) {
      return word;
    }

    final codePoints = word.runes.toList();
    final length = codePoints.length;
    final normalized = <int>{};

    for (final idx in indices) {
      if (idx >= 0 && idx < length) {
        normalized.add(idx);
      }
    }

    if (normalized.isEmpty) {
      return word;
    }

    final buffer = StringBuffer();
    for (var i = 0; i < length; i++) {
      final ch = String.fromCharCode(codePoints[i]);
      if (normalized.contains(i)) {
        buffer.write('\u200E~~');
        buffer.write(ch);
        buffer.write('~~');
      } else {
        buffer.write(ch);
      }
    }

    return buffer.toString();
  }

  bool _containsAnyLetter(String text) {
    final regExp = RegExp(r'\p{L}', unicode: true);
    return regExp.hasMatch(text);
  }

  String _getOrigins(String content) {
    if (content.isEmpty) {
      return '';
    }

    final buffer = StringBuffer();
    final originList = content.split(',');

    for (final rawOrigin in originList) {
      final origin = rawOrigin.trim();
      if (origin.startsWith('G')) {
        final originId = int.tryParse(origin.substring(1));
        if (originId != null && doesStrongNumberExist(originId)) {
          buffer.write('${_formatGreekStrongLink(originId)}, ');
        }
      } else if (origin.startsWith('H')) {
        buffer.write('[$origin](strong:$origin), ');
      }
    }

    var result = buffer.toString();
    if (result.endsWith(', ')) {
      result = result.substring(0, result.length - 2);
    }

    return result;
  }

  String _getSynonyms(String content) {
    if (content.isEmpty) {
      return '';
    }

    final buffer = StringBuffer();
    final synonymsList = content.split(',');

    for (final rawSynonym in synonymsList) {
      final synonym = int.tryParse(rawSynonym.trim());
      if (synonym != null && doesStrongNumberExist(synonym)) {
        buffer.write('${_formatGreekStrongLink(synonym)}, ');
      }
    }

    var result = buffer.toString();
    if (result.endsWith(', ')) {
      result = result.substring(0, result.length - 2);
    }

    return result;
  }

  String _getTranslation(String content) {
    if (content.isEmpty) {
      return '';
    }

    return '*** \n${_expandGreekStrongLinks(content.trim().replaceAll("\n\r", "\n"))}\n ***';
  }

  String _formatGreekStrongLink(int strongNumber) {
    final strongCode = 'G$strongNumber';
    final greekWord = _getGreekWordByStrongNumber(strongNumber);
    if (greekWord == null) {
      return '[$strongCode](strong:$strongCode)';
    }
    return '**$greekWord** ([$strongCode](strong:$strongCode))';
  }

  String? _getGreekWordByStrongNumber(int strongNumber) {
    final wordIndex = _dataSource.greekWords.indexWhere(
      (word) => word.id == strongNumber,
    );
    if (wordIndex == -1) {
      return null;
    }

    final greekWord = _dataSource.greekWords[wordIndex].word.trim();
    return greekWord.isEmpty ? null : greekWord;
  }

  String _expandGreekStrongLinks(String content) {
    final regex = RegExp(r'\[([Gg])(\d+)\]\(strong:([Gg])(\d+)\)');
    return content.replaceAllMapped(regex, (match) {
      final visibleNumber = int.tryParse(match.group(2)!);
      final hrefNumber = int.tryParse(match.group(4)!);
      if (visibleNumber == null ||
          hrefNumber == null ||
          visibleNumber != hrefNumber ||
          !doesStrongNumberExist(visibleNumber)) {
        return match.group(0)!;
      }
      return _formatGreekStrongLink(visibleNumber);
    });
  }

  String _getUsage(String content) {
    if (content.isEmpty) {
      return '';
    }

    var sum = 0;
    for (final line in content.split('\n')) {
      final index = line.lastIndexOf('], ');
      if (index == -1) {
        continue;
      }
      final wordUsages = int.tryParse(line.substring(index + 3));
      if (wordUsages != null) {
        sum += wordUsages;
      }
    }

    var result =
        '$sum\n\r**${content.trim().replaceAll(" [], ", " ").replaceAll("\n", "; **").replaceAll(":", "**:")}';

    if (result.endsWith('**')) {
      result = result.substring(0, result.length - 2);
    }

    return result;
  }
}

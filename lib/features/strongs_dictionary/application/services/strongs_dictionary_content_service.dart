import 'package:revelation/features/strongs_dictionary/application/services/strongs_dictionary_markdown_tokens.dart';
import 'package:revelation/features/strongs_dictionary/data/repositories/strongs_dictionary_repository.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_dictionary_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/bible_book_localization.dart';
import 'package:revelation/shared/localization/localization_utils.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';
import 'package:revelation/shared/services/pronunciation_service.dart';

class StrongsDictionaryContentService {
  StrongsDictionaryContentService({
    StrongsDictionaryRepository? repository,
    PronunciationService? pronunciation,
    BibleVerseMap? verseMap,
  }) : _repository = repository ?? StrongsDictionaryRepository(),
       _pronunciation = pronunciation ?? PronunciationService(),
       _verseMap = verseMap;

  final StrongsDictionaryRepository _repository;
  final PronunciationService _pronunciation;
  final BibleVerseMap? _verseMap;

  List<StrongPickerEntry>? _pickerEntriesCache;

  bool get isInitialized => _repository.isInitialized;

  List<StrongPickerEntry> getPickerEntries() {
    if (!isInitialized) {
      return const <StrongPickerEntry>[];
    }

    _pickerEntriesCache ??= _repository.getPickerEntries();
    return _pickerEntriesCache!;
  }

  bool isAllowedStrongNumber(int strongNumber) {
    return _repository.isAllowedStrongNumber(strongNumber);
  }

  int getNeighborStrongNumber(int current, {bool forward = true}) {
    return _repository.getNeighborStrongNumber(current, forward: forward);
  }

  DescriptionContent? buildStrongContent(
    AppLocalizations localizations,
    int strongNumber,
  ) {
    if (!isInitialized) {
      return null;
    }

    final entry = _repository.findEntry(strongNumber);
    if (entry == null || !entry.hasDisplayWord) {
      return null;
    }

    return DescriptionContent(
      markdown: _buildEntryMarkdown(localizations, entry),
      kind: DescriptionKind.strongNumber,
    );
  }

  String? buildTranslationMarkdown(int strongNumber) {
    final description = _repository.findDescription(strongNumber);
    if (description == null || description.isEmpty) {
      return null;
    }

    return _getTranslation(description);
  }

  String _buildEntryMarkdown(
    AppLocalizations localizations,
    StrongDictionaryEntry entry,
  ) {
    final buffer = StringBuffer();

    buffer.write('## ');
    buffer.write(entry.word);
    buffer.write('\n\r');

    buffer.write(localizations.strong_number);
    buffer.write(': **');
    buffer.write(entry.code);
    buffer.write('**\n\r');

    buffer.write(localizations.strong_pronunciation);
    buffer.write(': **');
    buffer.write(
      _pronunciation
          .convert(entry.word.toLowerCase(), _repository.languageCode)
          .toLowerCase(),
    );
    buffer.write('**\n\r');

    if (entry.description.isNotEmpty) {
      buffer.write(_getTranslation(entry.description));
      buffer.write('\n\r');
    }

    if (entry.category.isNotEmpty) {
      buffer.write(localizations.strong_part_of_speech);
      buffer.write(': **');
      buffer.write(_replaceKeys(localizations, entry.category));
      buffer.write('**\n\r');
    }

    if (entry.origin.isNotEmpty) {
      buffer.write('\n\r');
      buffer.write(localizations.strong_origin);
      buffer.write(':');
      buffer.write(strongOriginInfoMarkdownMarker);
      buffer.write(_getOrigins(entry.origin));
      buffer.write('\n\r');
    }

    if (entry.synonyms.isNotEmpty) {
      buffer.write('\n\r');
      buffer.write(localizations.strong_synonyms);
      buffer.write(': ');
      buffer.write(_getSynonyms(entry.synonyms));
      buffer.write('\n\r');
    }

    if (entry.usage.isNotEmpty) {
      buffer.write(localizations.strong_usage);
      buffer.write(': ');
      buffer.write(_getUsage(localizations, entry.usage));
      buffer.write('\n\r');
    }

    return buffer.toString();
  }

  String _replaceKeys(AppLocalizations localizations, String input) {
    final regex = RegExp(r'@\w+');
    return input.replaceAllMapped(regex, (match) {
      final key = match.group(0)!;
      return locLinksByLocalizations(localizations, key);
    });
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
        if (originId != null && isAllowedStrongNumber(originId)) {
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
      if (synonym != null && isAllowedStrongNumber(synonym)) {
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
    final greekWord = _repository.findGreekWord(strongNumber);
    if (greekWord == null) {
      return '[$strongCode](strong:$strongCode)';
    }
    return '**$greekWord** ([$strongCode](strong:$strongCode))';
  }

  String _expandGreekStrongLinks(String content) {
    final regex = RegExp(r'\[([Gg])(\d+)\]\(strong:([Gg])(\d+)\)');
    return content.replaceAllMapped(regex, (match) {
      final visibleNumber = int.tryParse(match.group(2)!);
      final hrefNumber = int.tryParse(match.group(4)!);
      if (visibleNumber == null ||
          hrefNumber == null ||
          visibleNumber != hrefNumber ||
          !isAllowedStrongNumber(visibleNumber)) {
        return match.group(0)!;
      }
      return _formatGreekStrongLink(visibleNumber);
    });
  }

  String _getUsage(AppLocalizations localizations, String content) {
    if (content.isEmpty) {
      return '';
    }

    var total = 0;
    final lines = <String>[];
    for (final rawLine in content.split('\n')) {
      final formattedLine = _formatUsageLine(localizations, rawLine.trim());
      if (formattedLine == null) {
        continue;
      }
      total += formattedLine.count;
      lines.add(formattedLine.markdown);
    }

    if (lines.isEmpty) {
      return '';
    }

    return '$total\n\r${lines.join('; ')}';
  }

  _FormattedUsageLine? _formatUsageLine(
    AppLocalizations localizations,
    String line,
  ) {
    if (line.isEmpty) {
      return null;
    }

    final openBracket = line.indexOf('[');
    final labelSeparator = openBracket == -1
        ? -1
        : line.lastIndexOf(':', openBracket);
    final closeBracket = line.indexOf(']', openBracket + 1);
    if (labelSeparator <= 0 || openBracket == -1 || closeBracket == -1) {
      return null;
    }

    final surface = line.substring(0, labelSeparator).trim();
    final refsText = line.substring(openBracket + 1, closeBracket).trim();
    final refs = refsText.isEmpty
        ? const <_UsageVerseReference>[]
        : refsText
              .split(';')
              .map((value) => _parseUsageVerseReference(value.trim()))
              .whereType<_UsageVerseReference>()
              .toList(growable: false);
    if (surface.isEmpty || refs.isEmpty) {
      return null;
    }

    final count = refs.fold<int>(0, (sum, ref) => sum + ref.count);
    final references = refs
        .map((ref) => _formatUsageVerseReference(localizations, ref))
        .join('; ');

    return _FormattedUsageLine(
      count: count,
      markdown: '**$surface**: $references',
    );
  }

  _UsageVerseReference? _parseUsageVerseReference(String value) {
    final match = RegExp(r'^([0-9A-Z]{3})(?:x([1-9]\d*))?$').firstMatch(value);
    if (match == null) {
      return null;
    }
    return _UsageVerseReference(
      verseKey: match.group(1)!,
      count: int.tryParse(match.group(2) ?? '1') ?? 1,
    );
  }

  String _formatUsageVerseReference(
    AppLocalizations localizations,
    _UsageVerseReference usageReference,
  ) {
    final reference = _verseMap?.referenceForKey(usageReference.verseKey);
    final label = reference == null
        ? usageReference.verseKey
        : '${localizedBibleBookCode(localizations, reference.bookId)} '
              '${reference.chapter}:${reference.verse}';
    if (usageReference.count <= 1) {
      return label;
    }
    return '$label x${usageReference.count}';
  }
}

class _FormattedUsageLine {
  const _FormattedUsageLine({required this.count, required this.markdown});

  final int count;
  final String markdown;
}

class _UsageVerseReference {
  const _UsageVerseReference({required this.verseKey, required this.count});

  final String verseKey;
  final int count;
}

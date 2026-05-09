import 'package:revelation/features/strongs_dictionary/data/repositories/strongs_dictionary_repository.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_dictionary_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/localization/localization_utils.dart';
import 'package:revelation/shared/models/description_content.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/services/pronunciation_service.dart';

class StrongsDictionaryContentService {
  StrongsDictionaryContentService({
    StrongsDictionaryRepository? repository,
    PronunciationService? pronunciation,
  }) : _repository = repository ?? StrongsDictionaryRepository(),
       _pronunciation = pronunciation ?? PronunciationService();

  final StrongsDictionaryRepository _repository;
  final PronunciationService _pronunciation;

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
    buffer.write('[${entry.number}](strong_picker:${entry.code})');
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
      buffer.write(': ');
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
      buffer.write(_getUsage(entry.usage));
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

import 'package:revelation/features/strongs_dictionary/domain/models/strong_dictionary_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_dictionary_search_normalizer.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_number_policy.dart';
import 'package:revelation/infra/db/runtime/gateways/lexicon_database_gateway.dart';

class StrongsDictionaryRepository {
  StrongsDictionaryRepository({
    LexiconDatabaseGateway? databaseGateway,
    StrongNumberPolicy? numberPolicy,
  }) : _databaseGateway = databaseGateway ?? DbManagerLexiconDatabaseGateway(),
       _numberPolicy = numberPolicy ?? const StrongNumberPolicy();

  final LexiconDatabaseGateway _databaseGateway;
  final StrongNumberPolicy _numberPolicy;

  String? _cachedLanguageCode;
  Object? _cachedGreekWordsIdentity;
  Object? _cachedGreekDescsIdentity;
  List<StrongDictionaryEntry>? _entriesCache;
  Map<int, StrongDictionaryEntry>? _entriesByNumberCache;
  Map<int, String>? _descriptionsByNumberCache;
  List<StrongPickerEntry>? _pickerEntriesCache;

  bool get isInitialized => _databaseGateway.isInitialized;

  String get languageCode => _databaseGateway.languageCode;

  bool isAllowedStrongNumber(int number) => _numberPolicy.isAllowed(number);

  int getNeighborStrongNumber(int current, {required bool forward}) {
    return _numberPolicy.neighbor(current, forward: forward);
  }

  List<StrongDictionaryEntry> getEntries() {
    if (!isInitialized) {
      return const <StrongDictionaryEntry>[];
    }

    _refreshCachesIfSourceChanged();
    return _entriesCache ??= _buildEntries();
  }

  List<StrongDictionaryEntry> _buildEntries() {
    final descriptionsByNumber = _getDescriptionsByNumber();

    final entries =
        _databaseGateway.greekWords
            .map(
              (word) => StrongDictionaryEntry(
                number: word.id,
                word: word.word.trim(),
                category: word.category.trim(),
                synonyms: word.synonyms.trim(),
                origin: word.origin.trim(),
                usage: word.usage.trim(),
                description: descriptionsByNumber[word.id] ?? '',
              ),
            )
            .toList(growable: false)
          ..sort((a, b) => a.number.compareTo(b.number));

    return List<StrongDictionaryEntry>.unmodifiable(entries);
  }

  StrongDictionaryEntry? findEntry(int strongNumber) {
    if (!isInitialized) {
      return null;
    }

    _refreshCachesIfSourceChanged();
    return (_entriesByNumberCache ??= {
      for (final entry in getEntries()) entry.number: entry,
    })[strongNumber];
  }

  String? findDescription(int strongNumber) {
    if (!isInitialized) {
      return null;
    }

    _refreshCachesIfSourceChanged();
    return _getDescriptionsByNumber()[strongNumber];
  }

  String? findGreekWord(int strongNumber) {
    if (!isInitialized) {
      return null;
    }

    final entry = findEntry(strongNumber);
    if (entry == null || entry.word.isEmpty) {
      return null;
    }
    return entry.word;
  }

  List<StrongPickerEntry> getPickerEntries() {
    if (!isInitialized) {
      return const <StrongPickerEntry>[];
    }

    _refreshCachesIfSourceChanged();
    return _pickerEntriesCache ??= _buildPickerEntries();
  }

  List<StrongPickerEntry> _buildPickerEntries() {
    final entries = getEntries()
        .where(
          (entry) =>
              _numberPolicy.isAllowed(entry.number) && entry.word.isNotEmpty,
        )
        .map((entry) {
          final searchText = normalizeStrongDictionarySearchText(
            '${entry.number} ${entry.code} ${entry.word} ${entry.description}',
          );
          return StrongPickerEntry(
            number: entry.number,
            word: entry.word,
            description: entry.description,
            searchText: searchText,
          );
        })
        .toList(growable: false);

    return List<StrongPickerEntry>.unmodifiable(entries);
  }

  int closestPickerNumber(int value) {
    return _numberPolicy.closestAvailableNumber(
      value,
      getPickerEntries().map((entry) => entry.number),
    );
  }

  Map<int, String> _getDescriptionsByNumber() {
    return _descriptionsByNumberCache ??= {
      for (final description in _databaseGateway.greekDescs)
        if (description.desc.trim().isNotEmpty)
          description.id: description.desc.trim(),
    };
  }

  void _refreshCachesIfSourceChanged() {
    final languageCode = _databaseGateway.languageCode;
    final greekWords = _databaseGateway.greekWords;
    final greekDescs = _databaseGateway.greekDescs;
    if (_cachedLanguageCode == languageCode &&
        identical(_cachedGreekWordsIdentity, greekWords) &&
        identical(_cachedGreekDescsIdentity, greekDescs)) {
      return;
    }

    _cachedLanguageCode = languageCode;
    _cachedGreekWordsIdentity = greekWords;
    _cachedGreekDescsIdentity = greekDescs;
    _entriesCache = null;
    _entriesByNumberCache = null;
    _descriptionsByNumberCache = null;
    _pickerEntriesCache = null;
  }
}

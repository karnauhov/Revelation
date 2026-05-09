import 'package:revelation/features/strongs_dictionary/domain/models/strong_dictionary_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
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

    final descriptionsByNumber = <int, String>{
      for (final description in _databaseGateway.greekDescs)
        description.id: description.desc.trim(),
    };

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

    for (final entry in getEntries()) {
      if (entry.number == strongNumber) {
        return entry;
      }
    }
    return null;
  }

  String? findDescription(int strongNumber) {
    if (!isInitialized) {
      return null;
    }

    for (final description in _databaseGateway.greekDescs) {
      if (description.id == strongNumber) {
        final value = description.desc.trim();
        return value.isEmpty ? null : value;
      }
    }
    return null;
  }

  String? findGreekWord(int strongNumber) {
    if (!isInitialized) {
      return null;
    }

    for (final word in _databaseGateway.greekWords) {
      if (word.id == strongNumber) {
        final value = word.word.trim();
        return value.isEmpty ? null : value;
      }
    }
    return null;
  }

  List<StrongPickerEntry> getPickerEntries() {
    if (!isInitialized) {
      return const <StrongPickerEntry>[];
    }

    final entries =
        _databaseGateway.greekWords
            .where((word) => _numberPolicy.isAllowed(word.id))
            .map(
              (word) =>
                  StrongPickerEntry(number: word.id, word: word.word.trim()),
            )
            .where((entry) => entry.word.isNotEmpty)
            .toList(growable: false)
          ..sort((a, b) => a.number.compareTo(b.number));

    return List<StrongPickerEntry>.unmodifiable(entries);
  }

  int closestPickerNumber(int value) {
    return _numberPolicy.closestAvailableNumber(
      value,
      getPickerEntries().map((entry) => entry.number),
    );
  }
}

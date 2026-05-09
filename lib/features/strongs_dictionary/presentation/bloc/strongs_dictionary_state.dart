import 'package:flutter/foundation.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_dictionary_search_normalizer.dart';

class StrongsDictionaryState {
  const StrongsDictionaryState({
    required this.strongNumber,
    required this.markdown,
    required this.pickerEntries,
    required this.searchQuery,
  });

  factory StrongsDictionaryState.initial({
    required int strongNumber,
    required List<StrongPickerEntry> pickerEntries,
  }) {
    return StrongsDictionaryState(
      strongNumber: strongNumber,
      markdown: null,
      pickerEntries: List<StrongPickerEntry>.unmodifiable(pickerEntries),
      searchQuery: '',
    );
  }

  final int strongNumber;
  final String? markdown;
  final List<StrongPickerEntry> pickerEntries;
  final String searchQuery;

  bool get hasContent => markdown != null;

  String get displayMarkdown => markdown ?? '-';

  List<StrongPickerEntry> get visiblePickerEntries {
    final query = normalizeStrongDictionarySearchText(searchQuery);
    if (query.isEmpty) {
      return pickerEntries;
    }

    return pickerEntries
        .where((entry) {
          final searchText = entry.searchText.isEmpty
              ? normalizeStrongDictionarySearchText(
                  '${entry.number} ${entry.code} ${entry.word} ${entry.description}',
                )
              : entry.searchText;
          return searchText.contains(query);
        })
        .toList(growable: false);
  }

  StrongsDictionaryState copyWith({
    int? strongNumber,
    String? markdown,
    bool markdownSet = false,
    List<StrongPickerEntry>? pickerEntries,
    String? searchQuery,
  }) {
    return StrongsDictionaryState(
      strongNumber: strongNumber ?? this.strongNumber,
      markdown: markdownSet ? markdown : this.markdown,
      pickerEntries: pickerEntries ?? this.pickerEntries,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is StrongsDictionaryState &&
            runtimeType == other.runtimeType &&
            strongNumber == other.strongNumber &&
            markdown == other.markdown &&
            listEquals(pickerEntries, other.pickerEntries) &&
            searchQuery == other.searchQuery;
  }

  @override
  int get hashCode => Object.hash(
    strongNumber,
    markdown,
    Object.hashAll(pickerEntries),
    searchQuery,
  );
}

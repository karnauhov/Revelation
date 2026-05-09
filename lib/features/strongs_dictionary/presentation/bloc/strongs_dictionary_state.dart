import 'package:flutter/foundation.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';

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
    final query = searchQuery.trim().toLowerCase();
    if (query.isEmpty) {
      return pickerEntries;
    }

    final numberQuery = query.startsWith('g') ? query.substring(1) : query;
    return pickerEntries
        .where((entry) {
          return entry.code.toLowerCase().contains(query) ||
              entry.number.toString().contains(numberQuery) ||
              entry.word.toLowerCase().contains(query);
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

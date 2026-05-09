import 'package:flutter/foundation.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';

class StrongNumberPickerState {
  const StrongNumberPickerState({
    required this.entries,
    required this.inputText,
    required this.selectedStrongNumber,
  });

  final List<StrongPickerEntry> entries;
  final String inputText;
  final int? selectedStrongNumber;

  StrongPickerEntry? get selectedEntry {
    final strongNumber = selectedStrongNumber;
    if (strongNumber == null) {
      return null;
    }

    for (final entry in entries) {
      if (entry.number == strongNumber) {
        return entry;
      }
    }
    return null;
  }

  bool get hasEntries => entries.isNotEmpty;

  StrongNumberPickerState copyWith({
    List<StrongPickerEntry>? entries,
    String? inputText,
    int? selectedStrongNumber,
    bool selectedStrongNumberSet = false,
  }) {
    return StrongNumberPickerState(
      entries: entries ?? this.entries,
      inputText: inputText ?? this.inputText,
      selectedStrongNumber: selectedStrongNumberSet
          ? selectedStrongNumber
          : this.selectedStrongNumber,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is StrongNumberPickerState &&
            runtimeType == other.runtimeType &&
            listEquals(entries, other.entries) &&
            inputText == other.inputText &&
            selectedStrongNumber == other.selectedStrongNumber;
  }

  @override
  int get hashCode =>
      Object.hash(Object.hashAll(entries), inputText, selectedStrongNumber);
}

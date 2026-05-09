import 'package:flutter/foundation.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';
import 'package:revelation/shared/models/description_kind.dart';

class PrimarySourceDescriptionState {
  const PrimarySourceDescriptionState({
    required this.content,
    required this.currentType,
    required this.currentNumber,
    required this.pickerEntries,
  });

  factory PrimarySourceDescriptionState.initial({
    required List<StrongPickerEntry> pickerEntries,
  }) {
    return PrimarySourceDescriptionState(
      content: null,
      currentType: DescriptionKind.info,
      currentNumber: null,
      pickerEntries: List<StrongPickerEntry>.unmodifiable(pickerEntries),
    );
  }

  final String? content;
  final DescriptionKind currentType;
  final int? currentNumber;
  final List<StrongPickerEntry> pickerEntries;

  PrimarySourceDescriptionState copyWith({
    String? content,
    bool contentSet = false,
    DescriptionKind? currentType,
    int? currentNumber,
    bool currentNumberSet = false,
    List<StrongPickerEntry>? pickerEntries,
  }) {
    return PrimarySourceDescriptionState(
      content: contentSet ? content : this.content,
      currentType: currentType ?? this.currentType,
      currentNumber: currentNumberSet ? currentNumber : this.currentNumber,
      pickerEntries: pickerEntries ?? this.pickerEntries,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is PrimarySourceDescriptionState &&
            runtimeType == other.runtimeType &&
            content == other.content &&
            currentType == other.currentType &&
            currentNumber == other.currentNumber &&
            listEquals(pickerEntries, other.pickerEntries);
  }

  @override
  int get hashCode => Object.hash(
    content,
    currentType,
    currentNumber,
    Object.hashAll(pickerEntries),
  );
}

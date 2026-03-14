import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';

class PrimarySourceDescriptionState {
  const PrimarySourceDescriptionState({
    required this.showDescription,
    required this.content,
    required this.currentType,
    required this.currentNumber,
    required this.pickerEntries,
  });

  factory PrimarySourceDescriptionState.initial({
    required List<GreekStrongPickerEntry> pickerEntries,
  }) {
    return PrimarySourceDescriptionState(
      showDescription: true,
      content: null,
      currentType: DescriptionKind.info,
      currentNumber: null,
      pickerEntries: List<GreekStrongPickerEntry>.unmodifiable(pickerEntries),
    );
  }

  final bool showDescription;
  final String? content;
  final DescriptionKind currentType;
  final int? currentNumber;
  final List<GreekStrongPickerEntry> pickerEntries;

  PrimarySourceDescriptionState copyWith({
    bool? showDescription,
    String? content,
    bool contentSet = false,
    DescriptionKind? currentType,
    int? currentNumber,
    bool currentNumberSet = false,
    List<GreekStrongPickerEntry>? pickerEntries,
  }) {
    return PrimarySourceDescriptionState(
      showDescription: showDescription ?? this.showDescription,
      content: contentSet ? content : this.content,
      currentType: currentType ?? this.currentType,
      currentNumber: currentNumberSet ? currentNumber : this.currentNumber,
      pickerEntries: pickerEntries ?? this.pickerEntries,
    );
  }
}

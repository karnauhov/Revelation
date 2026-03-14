import 'package:revelation/shared/models/description_kind.dart';

class PrimarySourceSelectionState {
  const PrimarySourceSelectionState({
    required this.currentType,
    required this.currentNumber,
  });

  static const PrimarySourceSelectionState initial =
      PrimarySourceSelectionState(
        currentType: DescriptionKind.info,
        currentNumber: null,
      );

  final DescriptionKind currentType;
  final int? currentNumber;

  PrimarySourceSelectionState copyWith({
    DescriptionKind? currentType,
    int? currentNumber,
    bool currentNumberSet = false,
  }) {
    return PrimarySourceSelectionState(
      currentType: currentType ?? this.currentType,
      currentNumber: currentNumberSet ? currentNumber : this.currentNumber,
    );
  }
}

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/strongs_dictionary/domain/models/strong_picker_entry.dart';
import 'package:revelation/features/strongs_dictionary/domain/services/strong_number_policy.dart';
import 'package:revelation/features/strongs_dictionary/presentation/bloc/strong_number_picker_state.dart';

class StrongNumberPickerCubit extends Cubit<StrongNumberPickerState> {
  StrongNumberPickerCubit({
    required List<StrongPickerEntry> entries,
    required int initialStrongNumber,
    StrongNumberPolicy numberPolicy = const StrongNumberPolicy(),
  }) : _numberPolicy = numberPolicy,
       super(
         _buildInitialState(
           entries: entries,
           initialStrongNumber: initialStrongNumber,
           numberPolicy: numberPolicy,
         ),
       );

  final StrongNumberPolicy _numberPolicy;

  static StrongNumberPickerState _buildInitialState({
    required List<StrongPickerEntry> entries,
    required int initialStrongNumber,
    required StrongNumberPolicy numberPolicy,
  }) {
    final normalizedEntries = List<StrongPickerEntry>.unmodifiable(entries);
    if (normalizedEntries.isEmpty) {
      return const StrongNumberPickerState(
        entries: <StrongPickerEntry>[],
        inputText: '',
        selectedStrongNumber: null,
      );
    }

    final selectedStrongNumber = numberPolicy.closestAvailableNumber(
      initialStrongNumber,
      normalizedEntries.map((entry) => entry.number),
    );
    return StrongNumberPickerState(
      entries: normalizedEntries,
      inputText: selectedStrongNumber.toString(),
      selectedStrongNumber: selectedStrongNumber,
    );
  }

  void updateInputText(String rawText) {
    final inputText = rawText.trim();
    if (inputText.isEmpty) {
      emit(
        state.copyWith(
          inputText: '',
          selectedStrongNumber: null,
          selectedStrongNumberSet: true,
        ),
      );
      return;
    }

    final parsed = int.tryParse(inputText);
    if (parsed == null || state.entries.isEmpty) {
      return;
    }

    final selectedStrongNumber = _numberPolicy.closestAvailableNumber(
      parsed,
      state.entries.map((entry) => entry.number),
    );
    emit(
      state.copyWith(
        inputText: selectedStrongNumber.toString(),
        selectedStrongNumber: selectedStrongNumber,
        selectedStrongNumberSet: true,
      ),
    );
  }
}

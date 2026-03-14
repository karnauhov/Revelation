import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_state.dart';
import 'package:revelation/shared/models/description_kind.dart';

class PrimarySourceSelectionCubit extends Cubit<PrimarySourceSelectionState> {
  PrimarySourceSelectionCubit() : super(PrimarySourceSelectionState.initial);

  void setSelection({required DescriptionKind type, required int? number}) {
    if (state.currentType == type && state.currentNumber == number) {
      return;
    }
    emit(
      state.copyWith(
        currentType: type,
        currentNumber: number,
        currentNumberSet: true,
      ),
    );
  }

  void selectWord(int wordIndex) {
    setSelection(type: DescriptionKind.word, number: wordIndex);
  }

  void selectVerse(int verseIndex) {
    setSelection(type: DescriptionKind.verse, number: verseIndex);
  }

  void selectStrongNumber(int strongNumber) {
    setSelection(type: DescriptionKind.strongNumber, number: strongNumber);
  }

  void clearSelection() {
    setSelection(type: DescriptionKind.info, number: null);
  }
}

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_selection_cubit.dart';
import 'package:revelation/shared/models/description_kind.dart';

void main() {
  test('initial state is info with no selected number', () {
    final cubit = PrimarySourceSelectionCubit();
    addTearDown(cubit.close);

    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
  });

  test('word/verse/strong selection methods update state', () {
    final cubit = PrimarySourceSelectionCubit();
    addTearDown(cubit.close);

    cubit.selectWord(3);
    expect(cubit.state.currentType, DescriptionKind.word);
    expect(cubit.state.currentNumber, 3);

    cubit.selectVerse(5);
    expect(cubit.state.currentType, DescriptionKind.verse);
    expect(cubit.state.currentNumber, 5);

    cubit.selectStrongNumber(3056);
    expect(cubit.state.currentType, DescriptionKind.strongNumber);
    expect(cubit.state.currentNumber, 3056);
  });

  test('clearSelection resets to info state', () {
    final cubit = PrimarySourceSelectionCubit();
    addTearDown(cubit.close);

    cubit.selectWord(1);
    cubit.clearSelection();

    expect(cubit.state.currentType, DescriptionKind.info);
    expect(cubit.state.currentNumber, isNull);
  });
}

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';

void main() {
  test('initial state normalizes blocked single number to closest entry', () {
    final cubit = StrongNumberPickerCubit(
      entries: const [
        StrongPickerEntry(number: 2718, word: 'word-2718'),
        StrongPickerEntry(number: 3303, word: 'word-3303'),
      ],
      initialStrongNumber: 2717,
    );
    addTearDown(cubit.close);

    expect(cubit.state.inputText, '2718');
    expect(cubit.state.selectedEntry?.word, 'word-2718');
  });

  test('updateInputText normalizes blocked range to closest entry', () {
    final cubit = StrongNumberPickerCubit(
      entries: const [
        StrongPickerEntry(number: 2718, word: 'word-2718'),
        StrongPickerEntry(number: 3303, word: 'word-3303'),
      ],
      initialStrongNumber: 2718,
    );
    addTearDown(cubit.close);

    cubit.updateInputText('3203');

    expect(cubit.state.inputText, '3303');
    expect(cubit.state.selectedStrongNumber, 3303);
    expect(cubit.state.selectedEntry?.word, 'word-3303');
  });

  test(
    'updateInputText ignores extended numbers until navigation is enabled',
    () {
      final cubit = StrongNumberPickerCubit(
        entries: const [
          StrongPickerEntry(number: 1, word: 'word-1'),
          StrongPickerEntry(number: 5624, word: 'word-5624'),
          StrongPickerEntry(number: 6000, word: 'word-6000'),
          StrongPickerEntry(number: 21502, word: 'word-21502'),
        ],
        initialStrongNumber: 6000,
      );
      addTearDown(cubit.close);

      expect(cubit.state.inputText, '5624');
      expect(cubit.state.selectedStrongNumber, 5624);
      expect(cubit.state.selectedEntry?.word, 'word-5624');

      cubit.updateInputText('21502');

      expect(cubit.state.inputText, '5624');
      expect(cubit.state.selectedStrongNumber, 5624);
      expect(cubit.state.selectedEntry?.word, 'word-5624');
    },
  );

  test('empty input clears selection without dropping entries', () {
    final cubit = StrongNumberPickerCubit(
      entries: const [StrongPickerEntry(number: 1, word: 'alpha')],
      initialStrongNumber: 1,
    );
    addTearDown(cubit.close);

    cubit.updateInputText('');

    expect(cubit.state.inputText, isEmpty);
    expect(cubit.state.selectedStrongNumber, isNull);
    expect(cubit.state.selectedEntry, isNull);
    expect(cubit.state.entries, hasLength(1));
  });

  test('empty entries keep picker in unavailable state', () {
    final cubit = StrongNumberPickerCubit(
      entries: const <StrongPickerEntry>[],
      initialStrongNumber: 1,
    );
    addTearDown(cubit.close);

    cubit.updateInputText('2');

    expect(cubit.state.hasEntries, isFalse);
    expect(cubit.state.inputText, isEmpty);
    expect(cubit.state.selectedStrongNumber, isNull);
  });
}

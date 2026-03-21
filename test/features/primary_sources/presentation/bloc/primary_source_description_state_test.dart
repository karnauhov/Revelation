import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_state.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';

void main() {
  test('initial keeps baseline mode and immutable picker entries', () {
    final sourceEntries = <GreekStrongPickerEntry>[
      const GreekStrongPickerEntry(number: 1, word: 'alpha'),
    ];
    final state = PrimarySourceDescriptionState.initial(
      pickerEntries: sourceEntries,
    );

    sourceEntries.add(const GreekStrongPickerEntry(number: 2, word: 'beta'));

    expect(state.content, isNull);
    expect(state.currentType, DescriptionKind.info);
    expect(state.currentNumber, isNull);
    expect(state.pickerEntries, hasLength(1));
    expect(
      () => state.pickerEntries.add(
        const GreekStrongPickerEntry(number: 3, word: 'gamma'),
      ),
      throwsUnsupportedError,
    );
  });

  test('copyWith respects explicit set flags for nullable fields', () {
    const initial = PrimarySourceDescriptionState(
      content: 'base',
      currentType: DescriptionKind.word,
      currentNumber: 2,
      pickerEntries: <GreekStrongPickerEntry>[
        GreekStrongPickerEntry(number: 1, word: 'alpha'),
      ],
    );

    final ignoredNullable = initial.copyWith(
      content: 'ignored',
      currentNumber: 9,
    );
    final withExplicitSet = initial.copyWith(
      content: null,
      contentSet: true,
      currentNumber: null,
      currentNumberSet: true,
      currentType: DescriptionKind.info,
    );

    expect(ignoredNullable.content, 'base');
    expect(ignoredNullable.currentNumber, 2);
    expect(withExplicitSet.content, isNull);
    expect(withExplicitSet.currentNumber, isNull);
    expect(withExplicitSet.currentType, DescriptionKind.info);
  });

  test('value equality compares picker entries deeply', () {
    const a = PrimarySourceDescriptionState(
      content: 'value',
      currentType: DescriptionKind.strongNumber,
      currentNumber: 10,
      pickerEntries: <GreekStrongPickerEntry>[
        GreekStrongPickerEntry(number: 10, word: 'deka'),
      ],
    );
    const b = PrimarySourceDescriptionState(
      content: 'value',
      currentType: DescriptionKind.strongNumber,
      currentNumber: 10,
      pickerEntries: <GreekStrongPickerEntry>[
        GreekStrongPickerEntry(number: 10, word: 'deka'),
      ],
    );
    final c = b.copyWith(currentType: DescriptionKind.verse);

    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a, isNot(c));
  });
}

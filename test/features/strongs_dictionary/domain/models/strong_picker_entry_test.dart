import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/strongs_dictionary/strongs_dictionary.dart';

void main() {
  test('supports value equality', () {
    const left = StrongPickerEntry(number: 12, word: 'logos');
    const right = StrongPickerEntry(number: 12, word: 'logos');

    expect(left, right);
    expect(left.hashCode, right.hashCode);
  });

  test('distinguishes number, word and search fields', () {
    const base = StrongPickerEntry(number: 12, word: 'logos');
    const differentNumber = StrongPickerEntry(number: 13, word: 'logos');
    const differentWord = StrongPickerEntry(number: 12, word: 'rhema');
    const differentDescription = StrongPickerEntry(
      number: 12,
      word: 'logos',
      description: 'Word',
    );
    const differentSearchText = StrongPickerEntry(
      number: 12,
      word: 'logos',
      searchText: 'logos word',
    );

    expect(base, isNot(differentNumber));
    expect(base, isNot(differentWord));
    expect(base, isNot(differentDescription));
    expect(base, isNot(differentSearchText));
  });

  test('exposes canonical Greek Strong code', () {
    expect(const StrongPickerEntry(number: 3056, word: 'logos').code, 'G3056');
  });
}

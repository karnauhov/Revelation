import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/greek_strong_picker_entry.dart';

void main() {
  test('entries are equal when number and word match', () {
    const left = GreekStrongPickerEntry(number: 12, word: 'logos');
    const right = GreekStrongPickerEntry(number: 12, word: 'logos');

    expect(left, right);
    expect(left.hashCode, right.hashCode);
  });

  test('entries are not equal when any field differs', () {
    const base = GreekStrongPickerEntry(number: 12, word: 'logos');
    const differentNumber = GreekStrongPickerEntry(number: 13, word: 'logos');
    const differentWord = GreekStrongPickerEntry(number: 12, word: 'rhema');

    expect(base, isNot(differentNumber));
    expect(base, isNot(differentWord));
    expect(base, isNot('not-an-entry'));
  });
}

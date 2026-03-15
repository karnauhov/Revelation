import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/utils/links_utils.dart';

void main() {
  test('splitTrailingDigits separates trailing digits', () {
    expect(splitTrailingDigits('Rev22'), ['Rev', '22']);
    expect(splitTrailingDigits(' Revelation 12 '), ['Revelation', '12']);
    expect(splitTrailingDigits('Psalm'), ['Psalm', '']);
    expect(splitTrailingDigits('  123 '), ['', '123']);
  });

  test('roundTo rounds to fixed precision', () {
    expect(roundTo(1.2345, 2), 1.23);
    expect(roundTo(1.235, 2), 1.24);
    expect(roundTo(-2.555, 2), -2.56);
  });

  test('createNonZeroRect enforces minimum size', () {
    final rect = createNonZeroRect(const Offset(0, 0), const Offset(0, 0));

    expect(rect.width, 1);
    expect(rect.height, 1);
  });

  test('createNonZeroRect normalizes bounds', () {
    final rect = createNonZeroRect(const Offset(5, 1), const Offset(2, 3));

    expect(rect.left, 2);
    expect(rect.top, 1);
    expect(rect.right, 5);
    expect(rect.bottom, 3);
  });
}

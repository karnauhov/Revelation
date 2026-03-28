import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/page_rect.dart';

void main() {
  test('constructor keeps all passed coordinates as is', () {
    final rect = PageRect(-1.25, 2.5, 9.75, -3.5);

    expect(rect.startX, -1.25);
    expect(rect.startY, 2.5);
    expect(rect.endX, 9.75);
    expect(rect.endY, -3.5);
  });
}

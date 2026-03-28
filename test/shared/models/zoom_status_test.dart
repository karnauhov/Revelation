import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/models/zoom_status.dart';

void main() {
  test('status values are compared by all capability flags', () {
    const left = ZoomStatus(canZoomIn: true, canZoomOut: false, canReset: true);
    const same = ZoomStatus(canZoomIn: true, canZoomOut: false, canReset: true);
    const different = ZoomStatus(
      canZoomIn: true,
      canZoomOut: true,
      canReset: true,
    );
    const differentReset = ZoomStatus(
      canZoomIn: true,
      canZoomOut: false,
      canReset: false,
    );

    expect(left, same);
    expect(left.hashCode, same.hashCode);
    expect(left, isNot(different));
    expect(left, isNot(differentReset));
    expect(left, isNot('not-zoom-status'));
  });
}

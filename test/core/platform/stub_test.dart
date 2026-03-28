import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/platform/stub.dart';

void main() {
  group('platform stub', () {
    test('returns safe defaults', () async {
      expect(getPlatformLanguage(), 'en');
      expect(isMobileBrowser(), isFalse);
      expect(getUserAgent(), isEmpty);
      expect(await fetchMaxTextureSize(), 0);
    });
  });
}

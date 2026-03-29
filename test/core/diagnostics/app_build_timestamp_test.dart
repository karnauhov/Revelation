import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/diagnostics/app_build_timestamp.dart';

void main() {
  test(
    'loadAppBuildTimestamp reads transformed asset when define is absent',
    () async {
      final timestamp = await loadAppBuildTimestamp(
        bundle: _FakeAssetBundle(
          strings: const {appBuildTimestampAssetPath: '2026-04-01T10:20:30Z'},
        ),
      );

      expect(timestamp, DateTime.utc(2026, 4, 1, 10, 20, 30));
    },
  );

  test(
    'loadAppBuildTimestamp returns null for invalid asset content',
    () async {
      final timestamp = await loadAppBuildTimestamp(
        bundle: _FakeAssetBundle(
          strings: const {
            appBuildTimestampAssetPath: 'BUILD_TIMESTAMP_PLACEHOLDER',
          },
        ),
      );

      expect(timestamp, isNull);
    },
  );
}

class _FakeAssetBundle extends CachingAssetBundle {
  _FakeAssetBundle({required this.strings});

  final Map<String, String> strings;

  @override
  Future<ByteData> load(String key) async {
    throw UnimplementedError();
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final value = strings[key];
    if (value == null) {
      throw StateError('Missing asset: $key');
    }
    return value;
  }
}

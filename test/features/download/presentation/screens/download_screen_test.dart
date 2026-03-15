@Tags(['widget'])

import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/download/download.dart';
import 'package:revelation/shared/ui/widgets/icon_link_item.dart';

import '../../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('DownloadScreen renders three platform sections', (tester) async {
    final bundle = _FakeAssetBundle(
      {
        'assets/images/UI/android.svg': _svg,
        'assets/images/UI/windows.svg': _svg,
        'assets/images/UI/linux.svg': _svg,
        'assets/images/UI/google_play.svg': _svg,
        'assets/images/UI/microsoft_store.svg': _svg,
        'assets/images/UI/snapcraft.svg': _svg,
      },
    );

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: buildLocalizedTestApp(
          child: const DownloadScreen(),
          withScaffold: false,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(IconLinkItem), findsNWidgets(3));
  });
}

const String _svg = '<svg viewBox="0 0 24 24"></svg>';

class _FakeAssetBundle extends AssetBundle {
  _FakeAssetBundle(this._assets);

  final Map<String, String> _assets;

  @override
  Future<ByteData> load(String key) async {
    final value = _assets[key];
    if (value == null) {
      throw Exception('Unable to load asset: $key');
    }
    final bytes = Uint8List.fromList(utf8.encode(value));
    return ByteData.sublistView(bytes);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final value = _assets[key];
    if (value == null) {
      throw Exception('Unable to load asset: $key');
    }
    return value;
  }

  @override
  Future<T> loadStructuredData<T>(
    String key,
    Future<T> Function(String value) parser,
  ) async {
    return parser(await loadString(key));
  }

  @override
  void evict(String key) {}

  @override
  void clear() {}
}

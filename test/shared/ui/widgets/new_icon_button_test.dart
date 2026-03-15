@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/shared/ui/widgets/new_icon_button.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('NewIconButton shows tooltip and handles tap', (tester) async {
    var tapped = false;
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/icon.svg': _svg,
    });

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: buildLocalizedTestApp(
          child: NewIconButton(
            assetPath: 'assets/images/UI/icon.svg',
            tooltip: 'Action',
            size: 24,
            onPressed: () {
              tapped = true;
            },
          ),
        ),
      ),
    );

    expect(find.byTooltip('Action'), findsOneWidget);

    await tester.tap(find.byType(InkWell));
    await tester.pump();

    expect(tapped, isTrue);
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

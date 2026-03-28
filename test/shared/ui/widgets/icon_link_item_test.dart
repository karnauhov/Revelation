@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/shared/ui/widgets/icon_link_item.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  testWidgets('IconLinkItem renders label and triggers onTap', (tester) async {
    var tapped = false;
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/email.svg': _svg,
    });

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: buildLocalizedTestApp(
          child: IconLinkItem(
            iconPath: 'assets/images/UI/email.svg',
            text: 'Email',
            onTap: () {
              tapped = true;
            },
          ),
        ),
      ),
    );

    expect(find.text('Email'), findsOneWidget);

    await tester.tap(find.byType(ListTile));
    await tester.pump();

    expect(tapped, isTrue);
  });

  testWidgets('IconLinkItem uses raster image for non-svg icons', (
    tester,
  ) async {
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/photo.png': '',
    });

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: buildLocalizedTestApp(
          child: const IconLinkItem(
            iconPath: 'assets/images/UI/photo.png',
            text: 'Photo',
            onTap: _noOp,
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(Image), findsOneWidget);
    expect(find.byType(SvgPicture), findsNothing);
  });

  testWidgets('IconLinkItem applies left margin and theme color contract', (
    tester,
  ) async {
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/email.svg': _svg,
    });
    const leftMargin = 14.0;

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: MaterialApp(
          theme: ThemeData(
            colorScheme: const ColorScheme.light(primary: Colors.orange),
          ),
          home: const Scaffold(
            body: IconLinkItem(
              iconPath: 'assets/images/UI/email.svg',
              text: 'Email',
              onTap: _noOp,
              leftMargin: leftMargin,
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    final tile = tester.widget<ListTile>(find.byType(ListTile));
    final title = tester.widget<Text>(find.text('Email'));

    expect(tile.contentPadding, const EdgeInsets.fromLTRB(leftMargin, 0, 0, 0));
    expect(title.style?.color, Colors.orange);
  });
}

const String _svg = '<svg viewBox="0 0 24 24"></svg>';
const _transparentPng =
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Zr8sAAAAASUVORK5CYII=';

void _noOp() {}

class _FakeAssetBundle extends AssetBundle {
  _FakeAssetBundle(this._assets);

  final Map<String, String> _assets;

  @override
  Future<ByteData> load(String key) async {
    if (key == 'AssetManifest.bin') {
      return ByteData.sublistView(_manifestBytes(_assets.keys));
    }

    if (key.toLowerCase().endsWith('.png')) {
      final bytes = base64Decode(_transparentPng);
      return ByteData.sublistView(bytes);
    }

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

Uint8List _manifestBytes(Iterable<String> keys) {
  final manifest = <String, List<Map<String, Object?>>>{};
  for (final key in keys) {
    manifest[key] = <Map<String, Object?>>[
      <String, Object?>{'asset': key},
    ];
  }
  final encoded = const StandardMessageCodec().encodeMessage(manifest)!;
  return Uint8List.view(
    encoded.buffer,
    encoded.offsetInBytes,
    encoded.lengthInBytes,
  );
}

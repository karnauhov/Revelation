@Tags(['widget'])
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_svg/flutter_svg.dart';
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

  testWidgets('NewIconButton renders raster icon and preserves size', (
    tester,
  ) async {
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/icon.png': '',
    });

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: buildLocalizedTestApp(
          child: const NewIconButton(
            assetPath: 'assets/images/UI/icon.png',
            tooltip: 'Raster',
            size: 30,
            onPressed: _noOp,
          ),
        ),
      ),
    );
    await tester.pump();

    final image = tester.widget<Image>(find.byType(Image));
    expect(image.width, 30);
    expect(image.height, 30);
    expect(find.byType(SvgPicture), findsNothing);
  });

  testWidgets('NewIconButton applies interaction shape and theme colors', (
    tester,
  ) async {
    final bundle = _FakeAssetBundle(<String, String>{
      'assets/images/UI/icon.svg': _svg,
    });

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: bundle,
        child: MaterialApp(
          theme: ThemeData(
            colorScheme: const ColorScheme.light(primary: Colors.teal),
          ),
          home: const Scaffold(
            body: NewIconButton(
              assetPath: 'assets/images/UI/icon.svg',
              tooltip: 'Action',
              size: 24,
              onPressed: _noOp,
            ),
          ),
        ),
      ),
    );
    await tester.pump();

    final inkWell = tester.widget<InkWell>(find.byType(InkWell));

    expect(inkWell.customBorder, isA<CircleBorder>());
    expect(inkWell.hoverColor, Colors.teal.withValues(alpha: 0.08));
    expect(inkWell.splashColor, Colors.teal.withValues(alpha: 0.12));
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

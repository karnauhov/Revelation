import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/presentation/screens/main_screen.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'smoke_test_harness.dart';
import 'package:revelation/main.dart' as app;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    SharedPreferences.setMockInitialValues(<String, Object>{});

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (message) async {
          if (message == null) {
            return null;
          }
          final key = utf8.decode(message.buffer.asUint8List());
          return _assetFor(key);
        });

    _installAudioChannelMocks();
  });

  testWidgets('App startup smoke: main entry renders home shell', (
    tester,
  ) async {
    app.main();
    await pumpAndSettleSmoke(tester);

    expect(find.byType(MainScreen), findsOneWidget);

    final context = tester.element(find.byType(MainScreen));
    final l10n = AppLocalizations.of(context)!;
    expect(find.byTooltip(l10n.menu), findsOneWidget);
  });
}

ByteData _assetFor(String key) {
  if (key.toLowerCase().endsWith('.png')) {
    return ByteData.sublistView(_pngBytes);
  }
  return ByteData.sublistView(_svgBytes);
}

void _installAudioChannelMocks() {
  const MethodChannel channel = MethodChannel('xyz.luan/audioplayers');
  const MethodChannel globalChannel = MethodChannel(
    'xyz.luan/audioplayers.global',
  );

  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(channel, (_) async => null);
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(globalChannel, (_) async => null);
}

final Uint8List _svgBytes = Uint8List.fromList(
  utf8.encode('<svg viewBox="0 0 24 24"></svg>'),
);

final Uint8List _pngBytes = Uint8List.fromList(<int>[
  0x89,
  0x50,
  0x4E,
  0x47,
  0x0D,
  0x0A,
  0x1A,
  0x0A,
  0x00,
  0x00,
  0x00,
  0x0D,
  0x49,
  0x48,
  0x44,
  0x52,
  0x00,
  0x00,
  0x00,
  0x01,
  0x00,
  0x00,
  0x00,
  0x01,
  0x08,
  0x06,
  0x00,
  0x00,
  0x00,
  0x1F,
  0x15,
  0xC4,
  0x89,
  0x00,
  0x00,
  0x00,
  0x0A,
  0x49,
  0x44,
  0x41,
  0x54,
  0x78,
  0x9C,
  0x63,
  0x00,
  0x01,
  0x00,
  0x00,
  0x05,
  0x00,
  0x01,
  0x0D,
  0x0A,
  0x2D,
  0xB4,
  0x00,
  0x00,
  0x00,
  0x00,
  0x49,
  0x45,
  0x4E,
  0x44,
  0xAE,
  0x42,
  0x60,
  0x82,
]);

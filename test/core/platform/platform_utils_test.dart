import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/core/platform/platform_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  const channel = MethodChannel('revelation/window');

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async => null);
  });

  tearDown(() async {
    debugDefaultTargetPlatformOverride = null;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, null);
    await GetIt.I.reset();
  });

  test('isDesktop/isMobile reflect the target platform', () {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    expect(isDesktop(), isTrue);
    expect(isMobile(), isFalse);

    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    expect(isDesktop(), isFalse);
    expect(isMobile(), isTrue);
  });

  test('macOS is desktop, but desktop window channel is unsupported', () {
    debugDefaultTargetPlatformOverride = TargetPlatform.macOS;

    expect(isDesktop(), isTrue);
    expect(isDesktopWindowChannelSupported(), isFalse);
  });

  test('isWeb and isLocalWeb are false on non-web', () {
    expect(isWeb(), isFalse);
    expect(isLocalWeb(), isFalse);
  });

  test('isLocalWebWith detects localhost and loopback on web override', () {
    expect(
      isLocalWebWith(
        isWebOverride: true,
        uriOverride: Uri.parse('https://localhost:8080/path'),
      ),
      isTrue,
    );
    expect(
      isLocalWebWith(
        isWebOverride: true,
        uriOverride: Uri.parse('https://127.0.0.1:3000/'),
      ),
      isTrue,
    );
    expect(
      isLocalWebWith(
        isWebOverride: true,
        uriOverride: Uri.parse('https://example.com'),
      ),
      isFalse,
    );
  });

  test('isLocalWebWith ignores localhost when running outside web', () {
    expect(
      isLocalWebWith(
        isWebOverride: false,
        uriOverride: Uri.parse('https://localhost:8080/path'),
      ),
      isFalse,
    );
  });

  test('stubbed platform delegates return defaults', () async {
    expect(isMobileBrowser(), isFalse);
    expect(getUserAgent(), isEmpty);
    expect(await fetchMaxTextureSize(), 0);
  });

  test('getPlatform returns the current target platform', () {
    debugDefaultTargetPlatformOverride = TargetPlatform.linux;
    expect(getPlatform(), TargetPlatform.linux);
  });

  test('isDesktopWindowChannelSupported only on windows/linux non-web', () {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    expect(isDesktopWindowChannelSupported(), isTrue);

    debugDefaultTargetPlatformOverride = TargetPlatform.linux;
    expect(isDesktopWindowChannelSupported(), isTrue);

    debugDefaultTargetPlatformOverride = TargetPlatform.macOS;
    expect(isDesktopWindowChannelSupported(), isFalse);

    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    expect(isDesktopWindowChannelSupported(), isFalse);
  });

  test('getSystemLanguage parses the platform locale', () {
    final localeName = Platform.localeName;
    final parts = localeName.split('_');
    final expected = parts.length == 1
        ? Locale(parts[0]).languageCode
        : parts.length >= 2
        ? Locale(parts[0], parts[1]).languageCode
        : 'en';

    expect(getSystemLanguage(), expected);
  });

  test('getSystemLanguageWith uses platform language provider on web', () {
    final value = getSystemLanguageWith(
      isWebOverride: true,
      platformLanguageProvider: () => 'es',
    );

    expect(value, 'es');
  });

  test('getSystemLanguageWith handles one-part locale values', () {
    final value = getSystemLanguageWith(
      isWebOverride: false,
      localeNameOverride: 'uk',
    );

    expect(value, 'uk');
  });

  test('getSystemLanguageWith handles locale with language and region', () {
    final value = getSystemLanguageWith(
      isWebOverride: false,
      localeNameOverride: 'es_ES',
    );

    expect(value, 'es');
  });

  test('getSystemLanguageWith does not call provider outside web', () {
    var providerCalled = false;

    final value = getSystemLanguageWith(
      isWebOverride: false,
      localeNameOverride: 'ru_RU',
      platformLanguageProvider: () {
        providerCalled = true;
        return 'should-not-be-used';
      },
    );

    expect(value, 'ru');
    expect(providerCalled, isFalse);
  });

  test('getSystemLanguageWith falls back to en on provider failure', () {
    final value = getSystemLanguageWith(
      isWebOverride: true,
      platformLanguageProvider: () => throw StateError('forced'),
    );

    expect(value, 'en');
  });

  test('setDesktopWindowTitle calls channel and caches last title', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          return null;
        });

    final first = await setDesktopWindowTitle('Title');
    final second = await setDesktopWindowTitle('Title');

    expect(first, isTrue);
    expect(second, isTrue);
    expect(calls.length, 1);
    expect(calls.first.method, 'setWindowTitle');
    expect(calls.first.arguments, containsPair('title', 'Title'));
  });

  test('setDesktopWindowTitle sends call when title changes', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          return null;
        });

    final first = await setDesktopWindowTitle('First');
    final second = await setDesktopWindowTitle('Second');

    expect(first, isTrue);
    expect(second, isTrue);
    expect(calls.length, 2);
    expect(calls[0].arguments, containsPair('title', 'First'));
    expect(calls[1].arguments, containsPair('title', 'Second'));
  });

  test('setDesktopWindowTitle returns false when channel throws', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          throw PlatformException(code: 'fail');
        });

    final result = await setDesktopWindowTitle('NewTitle');

    expect(result, isFalse);
  });

  test(
    'setDesktopWindowTitle does not cache title when previous send failed',
    () async {
      debugDefaultTargetPlatformOverride = TargetPlatform.windows;
      var shouldThrow = true;
      final calls = <MethodCall>[];
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(channel, (call) async {
            calls.add(call);
            if (shouldThrow) {
              throw PlatformException(code: 'fail');
            }
            return null;
          });

      final failed = await setDesktopWindowTitle('RetryTitle');
      shouldThrow = false;
      final retried = await setDesktopWindowTitle('RetryTitle');

      expect(failed, isFalse);
      expect(retried, isTrue);
      expect(calls.length, 2);
    },
  );

  test('setDesktopWindowTitle returns false when unsupported', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.android;

    final result = await setDesktopWindowTitle('Ignored');

    expect(result, isFalse);
  });

  test('unsupported setDesktopWindowTitle does not cache title', () async {
    const title = 'UnsupportedThenSupportedTitle';
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          return null;
        });

    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    final unsupportedResult = await setDesktopWindowTitle(title);

    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    final supportedResult = await setDesktopWindowTitle(title);

    expect(unsupportedResult, isFalse);
    expect(supportedResult, isTrue);
    expect(calls.length, 1);
    expect(calls.first.arguments, containsPair('title', title));
  });

  test('closeDesktopWindow calls channel when supported', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          return null;
        });

    final result = await closeDesktopWindow();

    expect(result, isTrue);
    expect(calls.length, 1);
    expect(calls.first.method, 'closeWindow');
  });

  test('closeDesktopWindow returns false when unsupported', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.android;

    final result = await closeDesktopWindow();

    expect(result, isFalse);
  });

  test('closeDesktopWindow calls channel on linux', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.linux;
    final calls = <MethodCall>[];
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          calls.add(call);
          return null;
        });

    final result = await closeDesktopWindow();

    expect(result, isTrue);
    expect(calls.length, 1);
    expect(calls.first.method, 'closeWindow');
  });

  test('closeDesktopWindow returns false when channel throws', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          throw PlatformException(code: 'close-failed');
        });

    final result = await closeDesktopWindow();

    expect(result, isFalse);
  });
}

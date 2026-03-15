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
    GetIt.I.registerSingleton<Talker>(Talker());
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

  test('isWeb and isLocalWeb are false on non-web', () {
    expect(isWeb(), isFalse);
    expect(isLocalWeb(), isFalse);
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

  test('setDesktopWindowTitle returns false when channel throws', () async {
    debugDefaultTargetPlatformOverride = TargetPlatform.windows;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (call) async {
          throw PlatformException(code: 'fail');
        });

    final result = await setDesktopWindowTitle('NewTitle');

    expect(result, isFalse);
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
}

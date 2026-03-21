import 'dart:async';
import 'dart:typed_data';

import 'package:audioplayers_platform_interface/audioplayers_platform_interface.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/shared/utils/links_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:url_launcher_platform_interface/link.dart';
import 'package:url_launcher_platform_interface/url_launcher_platform_interface.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late UrlLauncherPlatform originalUrlLauncherPlatform;
  late _FakeUrlLauncherPlatform fakeUrlLauncherPlatform;
  late AudioplayersPlatformInterface originalAudioPlatform;
  late GlobalAudioplayersPlatformInterface originalGlobalAudioPlatform;
  late _FakeAudioplayersPlatform fakeAudioPlatform;
  late _FakeGlobalAudioplayersPlatform fakeGlobalAudioPlatform;

  setUpAll(() async {
    originalUrlLauncherPlatform = UrlLauncherPlatform.instance;
    fakeUrlLauncherPlatform = _FakeUrlLauncherPlatform();
    UrlLauncherPlatform.instance = fakeUrlLauncherPlatform;

    originalAudioPlatform = AudioplayersPlatformInterface.instance;
    originalGlobalAudioPlatform = GlobalAudioplayersPlatformInterface.instance;
    fakeAudioPlatform = _FakeAudioplayersPlatform();
    fakeGlobalAudioPlatform = _FakeGlobalAudioplayersPlatform();
    AudioplayersPlatformInterface.instance = fakeAudioPlatform;
    GlobalAudioplayersPlatformInterface.instance = fakeGlobalAudioPlatform;
  });

  tearDownAll(() async {
    UrlLauncherPlatform.instance = originalUrlLauncherPlatform;
    AudioplayersPlatformInterface.instance = originalAudioPlatform;
    GlobalAudioplayersPlatformInterface.instance = originalGlobalAudioPlatform;
    await fakeGlobalAudioPlatform.dispose();
    await GetIt.I.reset();
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    fakeUrlLauncherPlatform.clear();
  });

  test('splitTrailingDigits separates trailing digits', () {
    expect(splitTrailingDigits('Rev22'), ['Rev', '22']);
    expect(splitTrailingDigits(' Revelation 12 '), ['Revelation', '12']);
    expect(splitTrailingDigits('Psalm'), ['Psalm', '']);
    expect(splitTrailingDigits('  123 '), ['', '123']);
    expect(splitTrailingDigits('Rev 1:2'), ['Rev 1:', '2']);
  });

  test('roundTo rounds to fixed precision', () {
    expect(roundTo(1.2345, 2), 1.23);
    expect(roundTo(1.235, 2), 1.24);
    expect(roundTo(-2.555, 2), -2.56);
    expect(roundTo(12.6, 0), 13);
  });

  test('createNonZeroRect enforces minimum size', () {
    final rect = createNonZeroRect(const Offset(0, 0), const Offset(0, 0));

    expect(rect.width, 1);
    expect(rect.height, 1);
  });

  test('createNonZeroRect normalizes bounds', () {
    final rect = createNonZeroRect(const Offset(5, 1), const Offset(2, 3));

    expect(rect.left, 2);
    expect(rect.top, 1);
    expect(rect.right, 5);
    expect(rect.bottom, 3);
  });

  test('createNonZeroRect grows only missing axis when one side is zero', () {
    final rect = createNonZeroRect(const Offset(7, 2), const Offset(7, 6));

    expect(rect.width, 1);
    expect(rect.height, 4);
    expect(rect.left, 7);
    expect(rect.top, 2);
  });

  test('launchLink opens regular url and returns true', () async {
    final launched = await launchLink('https://example.com/path');

    expect(launched, isTrue);
    expect(
      fakeUrlLauncherPlatform.launchedUrls,
      contains('https://example.com/path'),
    );
  });

  test('launchLink opens mailto url and returns true', () async {
    final launched = await launchLink('mailto:test@example.com');

    expect(launched, isTrue);
    expect(
      fakeUrlLauncherPlatform.launchedUrls,
      contains('mailto:test@example.com'),
    );
  });

  test('launchLink returns false when platform launcher rejects url', () async {
    fakeUrlLauncherPlatform.nextResult = false;

    final launched = await launchLink('https://example.com/rejected');

    expect(launched, isFalse);
    expect(
      fakeUrlLauncherPlatform.launchedUrls,
      contains('https://example.com/rejected'),
    );
  });

  test('launchLink returns false when url parsing fails', () async {
    final launched = await launchLink('http://[::1');

    expect(launched, isFalse);
  });
}

class _FakeUrlLauncherPlatform extends UrlLauncherPlatform {
  @override
  LinkDelegate? get linkDelegate => null;

  final List<String> launchedUrls = <String>[];
  bool nextResult = true;

  @override
  Future<bool> canLaunch(String url) async => true;

  @override
  Future<void> closeWebView() async {}

  @override
  Future<bool> launch(
    String url, {
    required bool useSafariVC,
    required bool useWebView,
    required bool enableJavaScript,
    required bool enableDomStorage,
    required bool universalLinksOnly,
    required Map<String, String> headers,
    String? webOnlyWindowName,
  }) async {
    launchedUrls.add(url);
    return nextResult;
  }

  void clear() {
    launchedUrls.clear();
    nextResult = true;
  }
}

class _FakeAudioplayersPlatform extends AudioplayersPlatformInterface {
  @override
  Future<void> create(String playerId) async {}

  @override
  Future<void> dispose(String playerId) async {}

  @override
  Future<int?> getCurrentPosition(String playerId) async => null;

  @override
  Future<int?> getDuration(String playerId) async => null;

  @override
  Stream<AudioEvent> getEventStream(String playerId) => const Stream.empty();

  @override
  Future<void> pause(String playerId) async {}

  @override
  Future<void> release(String playerId) async {}

  @override
  Future<void> resume(String playerId) async {}

  @override
  Future<void> seek(String playerId, Duration position) async {}

  @override
  Future<void> setAudioContext(
    String playerId,
    AudioContext audioContext,
  ) async {}

  @override
  Future<void> setBalance(String playerId, double balance) async {}

  @override
  Future<void> setPlaybackRate(String playerId, double playbackRate) async {}

  @override
  Future<void> setPlayerMode(String playerId, PlayerMode playerMode) async {}

  @override
  Future<void> setReleaseMode(String playerId, ReleaseMode releaseMode) async {}

  @override
  Future<void> setSourceBytes(
    String playerId,
    Uint8List bytes, {
    String? mimeType,
  }) async {}

  @override
  Future<void> setSourceUrl(
    String playerId,
    String url, {
    bool? isLocal,
    String? mimeType,
  }) async {}

  @override
  Future<void> setVolume(String playerId, double volume) async {}

  @override
  Future<void> stop(String playerId) async {}

  @override
  Future<void> emitError(String playerId, String code, String message) async {}

  @override
  Future<void> emitLog(String playerId, String message) async {}
}

class _FakeGlobalAudioplayersPlatform
    implements GlobalAudioplayersPlatformInterface {
  final StreamController<GlobalAudioEvent> _controller =
      StreamController<GlobalAudioEvent>.broadcast();

  @override
  Stream<GlobalAudioEvent> getGlobalEventStream() => _controller.stream;

  @override
  Future<void> init() async {}

  @override
  Future<void> setGlobalAudioContext(AudioContext ctx) async {}

  @override
  Future<void> emitGlobalError(String code, String message) async {}

  @override
  Future<void> emitGlobalLog(String message) async {}

  Future<void> dispose() async {
    await _controller.close();
  }
}

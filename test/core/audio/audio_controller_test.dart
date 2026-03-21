import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:audioplayers_platform_interface/audioplayers_platform_interface.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:talker_flutter/talker_flutter.dart';

class _FakeAudioplayersPlatform extends AudioplayersPlatformInterface {
  final Map<String, StreamController<AudioEvent>> _controllers = {};

  int createCalls = 0;
  int setAudioContextCalls = 0;
  int setSourceUrlCalls = 0;
  int resumeCalls = 0;
  int stopCalls = 0;

  void resetCounts() {
    createCalls = 0;
    setAudioContextCalls = 0;
    setSourceUrlCalls = 0;
    resumeCalls = 0;
    stopCalls = 0;
  }

  @override
  Future<void> create(String playerId) async {
    createCalls += 1;
    _controllers[playerId] = StreamController<AudioEvent>.broadcast();
  }

  @override
  Stream<AudioEvent> getEventStream(String playerId) {
    return _controllers[playerId]?.stream ?? const Stream.empty();
  }

  @override
  Future<void> dispose(String playerId) async {
    await _controllers.remove(playerId)?.close();
  }

  @override
  Future<void> pause(String playerId) async {}

  @override
  Future<void> stop(String playerId) async {
    stopCalls += 1;
  }

  @override
  Future<void> resume(String playerId) async {
    resumeCalls += 1;
  }

  @override
  Future<void> release(String playerId) async {}

  @override
  Future<void> seek(String playerId, Duration position) async {
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.seekComplete),
    );
  }

  @override
  Future<void> setBalance(String playerId, double balance) async {}

  @override
  Future<void> setVolume(String playerId, double volume) async {}

  @override
  Future<void> setReleaseMode(String playerId, ReleaseMode releaseMode) async {}

  @override
  Future<void> setPlaybackRate(String playerId, double playbackRate) async {}

  @override
  Future<void> setSourceUrl(
    String playerId,
    String url, {
    bool? isLocal,
    String? mimeType,
  }) async {
    setSourceUrlCalls += 1;
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.prepared, isPrepared: true),
    );
  }

  @override
  Future<void> setSourceBytes(
    String playerId,
    Uint8List bytes, {
    String? mimeType,
  }) async {
    _controllers[playerId]?.add(
      const AudioEvent(eventType: AudioEventType.prepared, isPrepared: true),
    );
  }

  @override
  Future<void> setAudioContext(
    String playerId,
    AudioContext audioContext,
  ) async {
    setAudioContextCalls += 1;
  }

  @override
  Future<void> setPlayerMode(String playerId, PlayerMode playerMode) async {}

  @override
  Future<int?> getDuration(String playerId) async => null;

  @override
  Future<int?> getCurrentPosition(String playerId) async => null;

  @override
  Future<void> emitLog(String playerId, String message) async {
    _controllers[playerId]?.add(
      AudioEvent(eventType: AudioEventType.log, logMessage: message),
    );
  }

  @override
  Future<void> emitError(String playerId, String code, String message) async {}
}

class _FakeGlobalAudioplayersPlatform
    implements GlobalAudioplayersPlatformInterface {
  final StreamController<GlobalAudioEvent> _controller =
      StreamController<GlobalAudioEvent>.broadcast();

  int initCalls = 0;

  @override
  Stream<GlobalAudioEvent> getGlobalEventStream() => _controller.stream;

  @override
  Future<void> init() async {
    initCalls += 1;
  }

  @override
  Future<void> setGlobalAudioContext(AudioContext ctx) async {}

  @override
  Future<void> emitGlobalLog(String message) async {
    _controller.add(
      GlobalAudioEvent(
        eventType: GlobalAudioEventType.log,
        logMessage: message,
      ),
    );
  }

  @override
  Future<void> emitGlobalError(String code, String message) async {
    _controller.add(
      GlobalAudioEvent(
        eventType: GlobalAudioEventType.log,
        logMessage: '$code:$message',
      ),
    );
  }

  Future<void> dispose() async {
    await _controller.close();
  }
}

class _FakePathProviderPlatform extends PathProviderPlatform {
  _FakePathProviderPlatform(this.tempPath) : super();

  final String tempPath;

  @override
  Future<String?> getTemporaryPath() async => tempPath;

  @override
  Future<String?> getDownloadsPath() async => tempPath;

  @override
  Future<String?> getApplicationDocumentsPath() async => tempPath;

  @override
  Future<String?> getApplicationSupportPath() async => null;

  @override
  Future<String?> getLibraryPath() async => null;

  @override
  Future<String?> getApplicationCachePath() async => null;

  @override
  Future<String?> getExternalStoragePath() async => null;

  @override
  Future<List<String>?> getExternalCachePaths() async => null;

  @override
  Future<List<String>?> getExternalStoragePaths({
    StorageDirectory? type,
  }) async => null;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late _FakeAudioplayersPlatform fakePlatform;
  late _FakeGlobalAudioplayersPlatform fakeGlobalPlatform;
  late AudioplayersPlatformInterface originalPlatform;
  late GlobalAudioplayersPlatformInterface originalGlobalPlatform;
  late PathProviderPlatform originalPathProvider;
  late Directory tempDir;

  final assetBytes = <String, Uint8List>{
    'assets/sounds/page.mp3': Uint8List.fromList([0, 1, 2]),
    'assets/sounds/stone.mp3': Uint8List.fromList([3, 4, 5]),
    'assets/sounds/click.mp3': Uint8List.fromList([6, 7, 8]),
  };

  setUpAll(() async {
    originalPlatform = AudioplayersPlatformInterface.instance;
    originalGlobalPlatform = GlobalAudioplayersPlatformInterface.instance;
    originalPathProvider = PathProviderPlatform.instance;

    fakePlatform = _FakeAudioplayersPlatform();
    fakeGlobalPlatform = _FakeGlobalAudioplayersPlatform();
    AudioplayersPlatformInterface.instance = fakePlatform;
    GlobalAudioplayersPlatformInterface.instance = fakeGlobalPlatform;

    tempDir = await Directory.systemTemp.createTemp('audio-cache-');
    PathProviderPlatform.instance = _FakePathProviderPlatform(tempDir.path);

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', (message) async {
          if (message == null) {
            return null;
          }
          final key = utf8.decode(message.buffer.asUint8List());
          final data = assetBytes[key];
          if (data == null) {
            return null;
          }
          return ByteData.sublistView(data);
        });
  });

  tearDownAll(() async {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMessageHandler('flutter/assets', null);
    PathProviderPlatform.instance = originalPathProvider;
    AudioplayersPlatformInterface.instance = originalPlatform;
    GlobalAudioplayersPlatformInterface.instance = originalGlobalPlatform;
    await tempDir.delete(recursive: true);
    await fakeGlobalPlatform.dispose();
  });

  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
    fakePlatform.resetCounts();
    AudioController.setInstanceForTest(AudioController.forTest());
  });

  tearDown(() async {
    AudioController.resetForTest();
    await GetIt.I.reset();
  });

  test('init configures audio context', () async {
    await AudioController().init(isSoundEnabled: () => true);

    expect(fakePlatform.setAudioContextCalls, 1);
  });

  test('playSound plays when enabled and source exists', () async {
    await AudioController().init(isSoundEnabled: () => true);
    fakePlatform.resetCounts();

    AudioController().playSound('click');
    await _waitForCondition(() => fakePlatform.setSourceUrlCalls == 1);
    await _waitForCondition(() => fakePlatform.resumeCalls == 1);

    expect(fakePlatform.setSourceUrlCalls, 1);
    expect(fakePlatform.resumeCalls, 1);
  });

  test('playSound is a no-op when sound is disabled', () async {
    await AudioController().init(isSoundEnabled: () => false);
    fakePlatform.resetCounts();

    AudioController().playSound('click');
    await Future<void>.delayed(const Duration(milliseconds: 20));

    expect(fakePlatform.setSourceUrlCalls, 0);
    expect(fakePlatform.resumeCalls, 0);
  });

  test('playSound ignores unknown sources', () async {
    await AudioController().init(isSoundEnabled: () => true);
    fakePlatform.resetCounts();

    AudioController().playSound('missing');
    await Future<void>.delayed(const Duration(milliseconds: 20));

    expect(fakePlatform.setSourceUrlCalls, 0);
    expect(fakePlatform.resumeCalls, 0);
  });

  test('stopSound forwards to platform stop', () async {
    await AudioController().init(isSoundEnabled: () => true);
    fakePlatform.resetCounts();

    await AudioController().stopSound();

    expect(fakePlatform.stopCalls, 1);
  });
}

Future<void> _waitForCondition(
  bool Function() condition, {
  Duration timeout = const Duration(seconds: 1),
}) async {
  final start = DateTime.now();
  while (!condition()) {
    if (DateTime.now().difference(start) > timeout) {
      break;
    }
    await Future<void>.delayed(const Duration(milliseconds: 5));
  }
}

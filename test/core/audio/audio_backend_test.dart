import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:audioplayers_platform_interface/audioplayers_platform_interface.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path_provider_platform_interface/path_provider_platform_interface.dart';
import 'package:revelation/core/audio/audio_backend.dart';

class _FakeAudioplayersPlatform extends AudioplayersPlatformInterface {
  final Map<String, StreamController<AudioEvent>> _controllers =
      <String, StreamController<AudioEvent>>{};

  int setAudioContextCalls = 0;
  int setSourceUrlCalls = 0;
  int resumeCalls = 0;
  int stopCalls = 0;

  void resetCounts() {
    setAudioContextCalls = 0;
    setSourceUrlCalls = 0;
    resumeCalls = 0;
    stopCalls = 0;
  }

  @override
  Future<void> create(String playerId) async {
    _controllers[playerId] = StreamController<AudioEvent>.broadcast();
  }

  @override
  Stream<AudioEvent> getEventStream(String playerId) {
    return _controllers[playerId]?.stream ?? const Stream<AudioEvent>.empty();
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

  @override
  Stream<GlobalAudioEvent> getGlobalEventStream() => _controller.stream;

  @override
  Future<void> init() async {}

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

  tearDown(() {
    debugDefaultTargetPlatformOverride = null;
  });

  group('AudioplayersSoundBackend', () {
    late _FakeAudioplayersPlatform fakePlatform;
    late _FakeGlobalAudioplayersPlatform fakeGlobalPlatform;
    late AudioplayersPlatformInterface originalPlatform;
    late GlobalAudioplayersPlatformInterface originalGlobalPlatform;
    late PathProviderPlatform originalPathProvider;
    late Directory tempDir;
    late AudioplayersSoundBackend backend;

    final Map<String, Uint8List> assetBytes = <String, Uint8List>{
      'assets/sounds/page.mp3': Uint8List.fromList(<int>[0, 1, 2]),
      'assets/sounds/stone.mp3': Uint8List.fromList(<int>[3, 4, 5]),
      'assets/sounds/click.mp3': Uint8List.fromList(<int>[6, 7, 8]),
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
          .setMockMessageHandler('flutter/assets', (ByteData? message) async {
            if (message == null) {
              return null;
            }
            final String key = utf8.decode(message.buffer.asUint8List());
            final Uint8List? data = assetBytes[key];
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

    setUp(() {
      fakePlatform.resetCounts();
      backend = AudioplayersSoundBackend();
    });

    test('init configures audio context', () async {
      await backend.init(<String, String>{'click': 'assets/sounds/click.mp3'});

      expect(fakePlatform.setAudioContextCalls, 1);
    });

    test('play loads and resumes configured asset', () async {
      await backend.init(<String, String>{'click': 'assets/sounds/click.mp3'});
      fakePlatform.resetCounts();

      await backend.play('click');
      await _waitForCondition(() => fakePlatform.setSourceUrlCalls == 1);
      await _waitForCondition(() => fakePlatform.resumeCalls == 1);

      expect(fakePlatform.setSourceUrlCalls, 1);
      expect(fakePlatform.resumeCalls, 1);
    });

    test('stop forwards to platform stop', () async {
      await backend.init(<String, String>{'click': 'assets/sounds/click.mp3'});
      fakePlatform.resetCounts();

      await backend.stop();

      expect(fakePlatform.stopCalls, 1);
    });
  });

  group('WindowsMethodChannelSoundBackend', () {
    const MethodChannel channel = MethodChannel('revelation/audio');
    final List<MethodCall> methodCalls = <MethodCall>[];
    late WindowsMethodChannelSoundBackend backend;

    setUp(() {
      methodCalls.clear();
      backend = WindowsMethodChannelSoundBackend(channel: channel);
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
            methodCalls.add(methodCall);
            return null;
          });
    });

    tearDown(() {
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(channel, null);
    });

    test('default backend uses method channel on Windows', () {
      debugDefaultTargetPlatformOverride = TargetPlatform.windows;

      final backend = createDefaultSoundBackend();

      expect(backend, isA<WindowsMethodChannelSoundBackend>());
    });

    test('init sends the asset map over the platform channel', () async {
      await backend.init(<String, String>{'click': 'assets/sounds/click.mp3'});

      expect(methodCalls, hasLength(1));
      expect(methodCalls.single.method, 'prepareAssets');
      expect(methodCalls.single.arguments, <String, Object>{
        'assets': <String, String>{'click': 'assets/sounds/click.mp3'},
      });
    });

    test('play sends the sound name over the platform channel', () async {
      await backend.init(<String, String>{'click': 'assets/sounds/click.mp3'});
      methodCalls.clear();

      await backend.play('click');

      expect(methodCalls, hasLength(1));
      expect(methodCalls.single.method, 'play');
      expect(methodCalls.single.arguments, <String, String>{
        'soundName': 'click',
      });
    });

    test('stop sends the stop command over the platform channel', () async {
      await backend.init(const <String, String>{});
      methodCalls.clear();

      await backend.stop();

      expect(methodCalls, hasLength(1));
      expect(methodCalls.single.method, 'stop');
    });
  });
}

Future<void> _waitForCondition(
  bool Function() condition, {
  Duration timeout = const Duration(seconds: 1),
}) async {
  final DateTime start = DateTime.now();
  while (!condition()) {
    if (DateTime.now().difference(start) > timeout) {
      break;
    }
    await Future<void>.delayed(const Duration(milliseconds: 5));
  }
}

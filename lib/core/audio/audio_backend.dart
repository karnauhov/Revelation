import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

abstract interface class AppSoundBackend {
  Future<void> init(Map<String, String> soundAssets);
  Future<void> play(String sourceName);
  Future<void> stop();
}

AppSoundBackend createDefaultSoundBackend({AudioPlayer? soundPlayer}) {
  if (!kIsWeb && defaultTargetPlatform == TargetPlatform.windows) {
    return WindowsMethodChannelSoundBackend();
  }

  return AudioplayersSoundBackend(soundPlayer: soundPlayer);
}

class AudioplayersSoundBackend implements AppSoundBackend {
  AudioplayersSoundBackend({AudioPlayer? soundPlayer})
    : _soundPlayer = soundPlayer ?? AudioPlayer();

  final AudioPlayer _soundPlayer;
  final Map<String, Source> _sources = <String, Source>{};

  @override
  Future<void> init(Map<String, String> soundAssets) async {
    _soundPlayer.audioCache = AudioCache(prefix: "");

    await _soundPlayer.setAudioContext(
      AudioContext(
        android: AudioContextAndroid(
          isSpeakerphoneOn: true,
          stayAwake: false,
          contentType: AndroidContentType.sonification,
          usageType: AndroidUsageType.assistanceSonification,
          audioFocus: AndroidAudioFocus.none,
        ),
        iOS: AudioContextIOS(
          category: AVAudioSessionCategory.playback,
          options: {AVAudioSessionOptions.mixWithOthers},
        ),
      ),
    );

    _sources
      ..clear()
      ..addAll(<String, Source>{
        for (final MapEntry<String, String> entry in soundAssets.entries)
          entry.key: AssetSource(entry.value, mimeType: 'audio/mpeg'),
      });
  }

  @override
  Future<void> play(String sourceName) async {
    final Source? source = _sources[sourceName];
    if (source == null) {
      return;
    }

    await _soundPlayer.play(source);
  }

  @override
  Future<void> stop() => _soundPlayer.stop();
}

class WindowsMethodChannelSoundBackend implements AppSoundBackend {
  WindowsMethodChannelSoundBackend({MethodChannel? channel})
    : _channel = channel ?? _defaultChannel;

  static const MethodChannel _defaultChannel = MethodChannel(
    'revelation/audio',
  );

  final MethodChannel _channel;
  Map<String, String> _soundAssets = const <String, String>{};

  @override
  Future<void> init(Map<String, String> soundAssets) async {
    _soundAssets = Map<String, String>.unmodifiable(soundAssets);
  }

  @override
  Future<void> play(String sourceName) async {
    final String? assetKey = _soundAssets[sourceName];
    if (assetKey == null) {
      return;
    }

    await _channel.invokeMethod<void>('playAsset', <String, String>{
      'assetKey': assetKey,
    });
  }

  @override
  Future<void> stop() => _channel.invokeMethod<void>('stop');
}

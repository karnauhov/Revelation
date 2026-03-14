import 'dart:async';
import 'package:audioplayers/audioplayers.dart';
import 'package:revelation/core/logging/common_logger.dart';

class AudioController {
  static final AudioController _instance = AudioController._internal();
  AudioController._internal();
  factory AudioController() => _instance;

  final AudioPlayer _soundPlayer = AudioPlayer();
  final _sources = <String, Source>{};
  bool Function() _isSoundEnabled = _soundDisabledByDefault;

  static bool _soundDisabledByDefault() => false;

  Future<void> init({required bool Function() isSoundEnabled}) async {
    _soundPlayer.audioCache = AudioCache(prefix: "");
    _isSoundEnabled = isSoundEnabled;

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

    _sources["page"] = AssetSource(
      'assets/sounds/page.mp3',
      mimeType: "audio/mpeg",
    );
    _sources["stone"] = AssetSource(
      'assets/sounds/stone.mp3',
      mimeType: "audio/mpeg",
    );
    _sources["click"] = AssetSource(
      'assets/sounds/click.mp3',
      mimeType: "audio/mpeg",
    );
  }

  void playSound(String sourceName) {
    try {
      if (_sources.containsKey(sourceName) && _isSoundEnabled()) {
        _soundPlayer.play(_sources[sourceName]!);
      }
    } catch (e) {
      log.error(e);
    }
  }

  Future<void> stopSound() async {
    try {
      await _soundPlayer.stop();
    } catch (_) {}
  }
}

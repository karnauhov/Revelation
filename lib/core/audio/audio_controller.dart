import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:revelation/core/audio/audio_backend.dart';
import 'package:revelation/core/logging/common_logger.dart';

class AudioController {
  static const Map<String, String> _soundAssets = <String, String>{
    'page': 'assets/sounds/page.mp3',
    'stone': 'assets/sounds/stone.mp3',
    'click': 'assets/sounds/click.mp3',
  };

  static AudioController _instance = AudioController._internal();

  AudioController._internal({AppSoundBackend? soundBackend})
    : _soundBackend = soundBackend ?? createDefaultSoundBackend();

  factory AudioController() => _instance;

  @visibleForTesting
  AudioController.forTest({AppSoundBackend? soundBackend})
    : _soundBackend = soundBackend ?? createDefaultSoundBackend();

  @visibleForTesting
  static void setInstanceForTest(AudioController controller) {
    _instance = controller;
  }

  @visibleForTesting
  static void resetForTest() {
    _instance = AudioController._internal();
  }

  final AppSoundBackend _soundBackend;
  bool Function() _isSoundEnabled = _soundDisabledByDefault;

  static bool _soundDisabledByDefault() => false;

  Future<void> init({required bool Function() isSoundEnabled}) async {
    _isSoundEnabled = isSoundEnabled;
    await _soundBackend.init(_soundAssets);
  }

  void playSound(String sourceName) {
    unawaited(_playSound(sourceName));
  }

  Future<void> _playSound(String sourceName) async {
    try {
      if (_soundAssets.containsKey(sourceName) && _isSoundEnabled()) {
        await _soundBackend.play(sourceName);
      }
    } catch (e) {
      log.error(e);
    }
  }

  Future<void> stopSound() async {
    try {
      await _soundBackend.stop();
    } catch (_) {}
  }
}

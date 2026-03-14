import 'dart:async';
import 'package:audioplayers/audioplayers.dart';
import 'package:revelation/features/settings/settings.dart' show SettingsCubit;
import 'package:revelation/shared/utils/common.dart';

class AudioController {
  static final AudioController _instance = AudioController._internal();
  AudioController._internal();
  factory AudioController() => _instance;

  final AudioPlayer _soundPlayer = AudioPlayer();
  final _sources = <String, Source>{};
  late SettingsCubit _settingsCubit;

  Future<void> init(SettingsCubit settingsCubit) async {
    _soundPlayer.audioCache = AudioCache(prefix: "");
    _settingsCubit = settingsCubit;

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
      if (_sources.containsKey(sourceName) &&
          _settingsCubit.state.settings.soundEnabled) {
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

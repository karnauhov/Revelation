import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/audio/audio_backend.dart';
import 'package:revelation/core/audio/audio_controller.dart';

class _FakeSoundBackend implements AppSoundBackend {
  Map<String, String>? initializedAssets;
  final List<String> playedSources = <String>[];
  int stopCalls = 0;

  @override
  Future<void> init(Map<String, String> soundAssets) async {
    initializedAssets = Map<String, String>.from(soundAssets);
  }

  @override
  Future<void> play(String sourceName) async {
    playedSources.add(sourceName);
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }
}

void main() {
  late _FakeSoundBackend fakeBackend;
  late AudioController controller;

  setUp(() {
    fakeBackend = _FakeSoundBackend();
    controller = AudioController.forTest(soundBackend: fakeBackend);
  });

  test('init passes configured sound assets to backend', () async {
    await controller.init(isSoundEnabled: () => true);

    expect(fakeBackend.initializedAssets, <String, String>{
      'page': 'assets/sounds/page.mp3',
      'stone': 'assets/sounds/stone.mp3',
      'click': 'assets/sounds/click.mp3',
    });
  });

  test('playSound plays known sounds when enabled', () async {
    await controller.init(isSoundEnabled: () => true);

    controller.playSound('click');
    await _settleSoundCall();

    expect(fakeBackend.playedSources, <String>['click']);
  });

  test('playSound is a no-op when sound is disabled', () async {
    await controller.init(isSoundEnabled: () => false);

    controller.playSound('click');
    await _settleSoundCall();

    expect(fakeBackend.playedSources, isEmpty);
  });

  test('playSound ignores unknown sources', () async {
    await controller.init(isSoundEnabled: () => true);

    controller.playSound('missing');
    await _settleSoundCall();

    expect(fakeBackend.playedSources, isEmpty);
  });

  test('stopSound forwards to backend', () async {
    await controller.init(isSoundEnabled: () => true);

    await controller.stopSound();

    expect(fakeBackend.stopCalls, 1);
  });
}

Future<void> _settleSoundCall() async {
  await Future<void>.delayed(Duration.zero);
}

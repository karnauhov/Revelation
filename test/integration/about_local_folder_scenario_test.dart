@Tags(['widget'])
library;

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/audio/audio_backend.dart';
import 'package:revelation/core/audio/audio_controller.dart';

import '../../integration_test/smoke/smoke_test_harness.dart';
import '../../integration_test/support/about_local_folder_native.dart'
    as scenario;

void main() {
  setUp(() {
    AudioController.setInstanceForTest(
      AudioController.forTest(soundBackend: _NoSoundBackend()),
    );
  });

  scenario.registerAboutLocalFolderScenarios(
    variant: const TargetPlatformVariant({
      TargetPlatform.android,
      TargetPlatform.windows,
    }),
  );
  testWidgets('global settling fails while the About tools are already ready', (
    tester,
  ) async {
    await expectLater(
      () => scenario.runAboutLocalFolderScenario(
        tester,
        language: 'en',
        waitForReady: (tester, {required isReady, required reason}) async {
          await tester.pump();
          expect(isReady(), isTrue);
          await pumpAndSettleSmoke(
            tester,
            timeout: const Duration(milliseconds: 96),
          );
        },
      ),
      throwsA(
        isA<FlutterError>().having(
          (error) => error.message,
          'message',
          contains('pumpAndSettle timed out'),
        ),
      ),
    );
  });
}

class _NoSoundBackend implements AppSoundBackend {
  @override
  Future<void> init(Map<String, String> soundAssets) async {}

  @override
  Future<void> play(String sourceName) async {
    fail('The folder scenario has sound disabled.');
  }

  @override
  Future<void> stop() async {}
}

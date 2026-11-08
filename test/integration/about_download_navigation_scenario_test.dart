@Tags(['widget'])
library;

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/features/about/presentation/bloc/about_cubit.dart';
import 'package:revelation/core/audio/audio_backend.dart';
import 'package:revelation/core/audio/audio_controller.dart';

import '../../integration_test/smoke/smoke_test_harness.dart';
import '../test_harness/about_download_navigation_scenarios.dart';

void main() {
  setUp(() {
    AudioController.setInstanceForTest(
      AudioController.forTest(soundBackend: _SoundBackend()),
    );
  });
  registerAboutDownloadNavigationScenarios(
    aboutCubitBuilder: _hostAbout,
    variant: const TargetPlatformVariant({
      TargetPlatform.android,
      TargetPlatform.windows,
    }),
  );
  testWidgets('global settle fails after the About metadata is ready', (
    tester,
  ) async {
    await expectLater(
      () => exerciseAboutShell(
        tester,
        aboutCubitBuilder: _hostAbout,
        waitForReady: (tester, {required isReady, required reason}) async {
          await pumpUntilSmoke(tester, isReady: isReady, reason: reason);
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

class _SoundBackend implements AppSoundBackend {
  @override
  Future<void> init(Map<String, String> soundAssets) async {}
  @override
  Future<void> play(String sourceName) async {}
  @override
  Future<void> stop() async {}
}

AboutCubit _hostAbout(String language) => AboutCubit(
  initialLanguageCode: language,
  packageInfoLoader: () async => PackageInfo(
    appName: 'Revelation',
    packageName: 'revelation',
    version: '1.0.0-test',
    buildNumber: '999',
  ),
  changelogLoader: () async => '',
  appBuildTimestampLoader: () async => null,
  dbVersionInfoLoader: (_) async => null,
);

@Tags(['widget'])
import 'dart:async';
import 'dart:ui' show ViewFocusDirection, ViewFocusEvent, ViewFocusState;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/main.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../test_harness/test_harness.dart';

void main() {
  testWidgets('cold startup preserves app focus during semantic view entry', (
    tester,
  ) async {
    await GetIt.I.reset();
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    PackageInfo.setMockInitialValues(
      appName: 'Revelation',
      packageName: 'revelation',
      version: '1.0.8',
      buildNumber: '174',
      buildSignature: '',
    );
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(SystemChannels.platform, (_) async => null);
    addTearDown(() {
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(SystemChannels.platform, null);
    });
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = '/settings';
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);
    final semantics = tester.ensureSemantics();
    final settings = SettingsCubit(
      FakeSettingsRepository(
        initialSettings: AppSettings(
          selectedLanguage: 'en',
          selectedTheme: 'manuscript',
          selectedFontSize: 'medium',
          soundEnabled: false,
        ),
      ),
    );
    await settings.loadSettings();
    final startup = Completer<SettingsCubit>();
    Widget? root;
    await startApp(
      talker,
      initializeSettingsCubit: (_) => startup.future,
      runAppCallback: (widget) => root = widget,
    );
    await tester.pumpWidget(root!);
    await tester.pump();
    expect(find.byType(AppStartupScreen), findsOneWidget);
    final appState = tester.state(find.byType(MaterialApp));
    final owner = tester.binding.renderViews.single.owner!.semanticsOwner!;
    var focusEvents = 0;
    var ready = false;
    void focusDuringSemantics() {
      if (!ready) return;
      focusEvents++;
      tester.binding.handleViewFocusChanged(
        ViewFocusEvent(
          viewId: tester.view.viewId,
          state: ViewFocusState.focused,
          direction: ViewFocusDirection.forward,
        ),
      );
    }

    owner.addListener(focusDuringSemantics);
    try {
      ready = true;
      startup.complete(settings);
      for (var i = 0; i < 20; i++) {
        await tester.pump(const Duration(milliseconds: 16));
        expect(tester.takeException(), isNull, reason: 'startup frame $i');
      }
      expect(focusEvents, greaterThan(0));
      expect(tester.state(find.byType(MaterialApp)), same(appState));
      expect(find.byType(RevelationApp), findsOneWidget);
    } finally {
      owner.removeListener(focusDuringSemantics);
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      semantics.dispose();
      await GetIt.I.reset();
    }
  });
}

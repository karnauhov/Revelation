import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/features/topics/presentation/screens/topic_screen.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/main.dart' as app;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

import 'smoke_test_harness.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    AppDi.registerCore(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });
  tearDownAll(() async {
    await DBManager().close();
    await GetIt.I.reset();
  });

  testWidgets('Web build serves the English documents as standalone HTML', (
    tester,
  ) async {
    await tester.runAsync(() async {
      for (final (file, title, heading) in [
        ('privacy-policy.html', 'Privacy Policy', '<h2>Introduction</h2>'),
        ('license.html', 'License', '<h1>Apache License</h1>'),
      ]) {
        final response = await http.get(Uri.base.resolve(file));
        expect(response.statusCode, 200, reason: file);
        expect(response.body, contains('<html lang="en">'));
        expect(response.body, contains('<title>$title | Revelation</title>'));
        expect(response.body, contains(heading));
        expect(response.body, isNot(contains('<script')));
      }
    });
  }, skip: !kIsWeb);

  testWidgets('Web startup preserves the legal link and loads each document', (
    tester,
  ) async {
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = '/privacy-policy';
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);

    SharedPreferences.setMockInitialValues({});
    final settingsCubit = SettingsCubit(SettingsRepository());
    await settingsCubit.loadSettings();
    await settingsCubit.changeLanguage('uk');

    final startup = Completer<SettingsCubit>();
    await app.startApp(
      GetIt.I<Talker>(),
      initializeSettingsCubit: (_) => startup.future,
    );
    await tester.pump();
    expect(find.byType(AppStartupScreen), findsOneWidget);
    expect(find.byType(Navigator), findsNothing);

    startup.complete(settingsCubit);
    await pumpAndSettleSmoke(tester, timeout: const Duration(seconds: 20));
    expect(find.byType(TopicScreen), findsOneWidget);
    expect(find.text('Політика конфіденційності'), findsOneWidget);
    expect(find.text('Вступ', findRichText: true), findsWidgets);

    AppRouter().router.go('/license');
    await pumpAndSettleSmoke(tester, timeout: const Duration(seconds: 20));
    expect(find.text('Ліцензія'), findsOneWidget);
    expect(find.text('Ліцензія Apache', findRichText: true), findsWidgets);

    await tester.pumpWidget(const SizedBox.shrink());
  }, skip: !kIsWeb);
}

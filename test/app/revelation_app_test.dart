@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/features/settings/presentation/bloc/settings_cubit.dart';
import 'package:revelation/main.dart';
import 'package:revelation/shared/models/app_settings.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../test_harness/test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    AppDi.registerCore(
      talker: Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    AppRouter().router.go('/');
    await GetIt.I.reset();
  });

  testWidgets('RevelationApp renders app shell in test environment', (
    tester,
  ) async {
    final settingsCubit = SettingsCubit(
      FakeSettingsRepository(initialSettings: _testSettings),
    );
    addTearDown(settingsCubit.close);
    await settingsCubit.loadSettings();

    AppRouter().router.go('/revelation-shell-smoke');

    await tester.pumpWidget(
      BlocProvider<SettingsCubit>.value(
        value: settingsCubit,
        child: const RevelationApp(),
      ),
    );
    await pumpAndSettleSafe(tester);

    expect(find.byType(RevelationApp), findsOneWidget);
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.textContaining('/revelation-shell-smoke'), findsOneWidget);
  });
}

final _testSettings = AppSettings(
  selectedLanguage: 'en',
  selectedTheme: 'manuscript',
  selectedFontSize: 'medium',
  soundEnabled: false,
);

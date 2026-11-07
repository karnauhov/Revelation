import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/app/router/app_router.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/main.dart' as app;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Cold Bible link survives startup and opens installed OH1988', (
    tester,
  ) async {
    const location =
        '/bible?book=66&chapter=1&verse=3&module=bible_ohienko_1988.sqlite';
    final dispatcher = tester.binding.platformDispatcher;
    dispatcher.defaultRouteNameTestValue = location;
    addTearDown(dispatcher.clearDefaultRouteNameTestValue);
    await GetIt.I.reset();
    final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
    AppDi.registerCore(talker: talker);
    SharedPreferences.setMockInitialValues({});
    final settings = SettingsCubit(SettingsRepository());
    await settings.loadSettings();
    await settings.changeLanguage('uk');
    final startup = Completer<SettingsCubit>();
    try {
      await app.startApp(
        talker,
        initializeSettingsCubit: (_) => startup.future,
      );
      await tester.pump();
      expect(find.byType(AppStartupScreen), findsOneWidget);
      expect(find.byType(Navigator), findsNothing);
      startup.complete(settings);
      for (var i = 0; i < 600; i++) {
        await tester.pump(const Duration(milliseconds: 100));
        await tester.runAsync(
          () => Future<void>.delayed(const Duration(milliseconds: 20)),
        );
        if (find.textContaining('Блаженний, хто читає').evaluate().isNotEmpty) {
          break;
        }
      }
      expect(find.byType(BibleScreen), findsOneWidget);
      final context = tester.element(
        find.byKey(const Key('bible_reader_pane_primary')),
      );
      final workspace = context.read<BibleWorkspaceCubit>();
      final state = workspace.readerCubitFor('primary').state;
      expect(state.selectedModule?.fileName, 'bible_ohienko_1988.sqlite');
      expect(state.selectedModule?.schemaVersion, 4);
      expect(state.selectedModule?.dataVersion, 2);
      expect(state.selectedReference?.bookId, 66);
      expect(state.selectedReference?.chapter, 1);
      expect(state.selectedReference?.verse, 3);
      expect(
        state.verses.firstWhere((verse) => verse.reference.verse == 3).text,
        contains('час бо близьки́й!'),
      );
      expect(find.textContaining('Блаженний, хто читає'), findsOneWidget);
      expect(
        AppRouter().router.routeInformationProvider.value.uri.toString(),
        location,
      );
      expect(tester.takeException(), isNull);
      binding.reportData = {
        'coldLocation': location,
        'actualLocation': AppRouter().router.routeInformationProvider.value.uri
            .toString(),
        'module': state.selectedModule!.fileName,
        'schemaVersion': state.selectedModule!.schemaVersion,
        'dataVersion': state.selectedModule!.dataVersion,
        'completeRev1_3': true,
        'uiLanguage': 'uk',
        'settingsStorage': 'isolated',
      };
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump();
      await DBManager().close();
      await GetIt.I.reset();
    }
  });
}

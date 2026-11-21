import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/bible/domain/services/bible_text_search.dart';
import 'package:revelation/app/di/app_di.dart';
import 'package:revelation/features/allusion_search/presentation/bloc/allusion_search_cubit.dart';
import 'package:revelation/features/settings/settings.dart';
import 'package:revelation/infra/db/runtime/db_manager.dart';
import 'package:revelation/main.dart' as app;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'first allusion search accepts input and shows a real translated result',
    (tester) async {
      final dispatcher = tester.binding.platformDispatcher;
      dispatcher.defaultRouteNameTestValue = '/allusion_search';
      addTearDown(dispatcher.clearDefaultRouteNameTestValue);
      await GetIt.I.reset();
      final talker = Talker(settings: TalkerSettings(useConsoleLogs: false));
      AppDi.registerCore(talker: talker);
      SharedPreferences.setMockInitialValues({});
      final settings = SettingsCubit(SettingsRepository());
      await settings.loadSettings();
      await settings.changeLanguage('en');
      Future<void> until(bool Function() condition) async {
        final timeout = Stopwatch()..start();
        while (!condition() && timeout.elapsed < const Duration(seconds: 45)) {
          await tester.pump(const Duration(milliseconds: 16));
          await tester.runAsync(
            () => Future<void>.delayed(const Duration(milliseconds: 10)),
          );
        }
        expect(condition(), isTrue);
      }

      try {
        final clock = Stopwatch()..start();
        await app.startApp(
          talker,
          initializeSettingsCubit: (_) async => settings,
        );
        final findSearch = find.byKey(const Key('allusion_search'));
        await until(() => findSearch.evaluate().isNotEmpty);
        final formMs = clock.elapsedMilliseconds;
        expect(find.byKey(const Key('allusion_verse')), findsOneWidget);
        await tester.tap(findSearch);
        final cubit = AppDi.allusionSearchCubit;
        await until(
          () =>
              cubit.state.results != null &&
              cubit.state.status == AllusionStatus.ready,
        );
        final first = cubit.state.visible.first.reference;
        expect((first.bookId, first.chapter, first.verse), (66, 22, 6));
        expect(cubit.state.module?.code, 'KJV');
        final text = plainBibleText(cubit.state.texts[first.verseKey]!);
        expect(text.toLowerCase(), contains('faithful and true'));
        await until(
          () => find.text(text, findRichText: true).evaluate().isNotEmpty,
        );
        final resultMs = clock.elapsedMilliseconds;
        expect(tester.takeException(), isNull);
        binding.reportData = {
          'formReadyMs': formMs,
          'translatedResultMs': resultMs,
          'module': cubit.state.module!.code,
          'target': first.verseKey,
          'verseMatches': cubit.state.matches.length,
        };
        debugPrint('Allusion timings: ${binding.reportData}');
      } finally {
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
        await DBManager().close();
        await GetIt.I.reset();
      }
    },
  );
}

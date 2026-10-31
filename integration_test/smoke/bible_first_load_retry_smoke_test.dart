import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_workspace_cubit.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:talker_flutter/talker_flutter.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  binding.reportData = {};
  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets(
      'Web first load retries and renders actual local Bible ($language)',
      (tester) async {
        await GetIt.I.reset();
        GetIt.I.registerSingleton<Talker>(
          Talker(settings: TalkerSettings(useConsoleLogs: false)),
        );
        SharedPreferences.setMockInitialValues({});
        final source = _FailOnce();
        try {
          await tester.pumpWidget(
            MaterialApp(
              locale: Locale(language),
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: BibleScreen(
                initialBookId: 1,
                bibleRepository: BibleRepository(moduleDataSource: source),
              ),
            ),
          );
          await _until(tester, find.byKey(const Key('bible_retry_button')));
          expect(source.listCalls, 1);
          final stopwatch = Stopwatch()..start();
          await tester.tap(find.byKey(const Key('bible_retry_button')));
          await _until(tester, find.byKey(const Key('bible_verse_1')));
          stopwatch.stop();
          final context = tester.element(
            find.byKey(const Key('bible_reader_pane_primary')),
          );
          final workspace = context.read<BibleWorkspaceCubit>();
          final state = workspace.readerCubitFor('primary').state;
          expect(state.verses.first.text.trim(), isNotEmpty);
          expect(state.selectedModule!.code, 'LXX_TR');
          expect(state.selectedModule!.language, 'grc');
          expect(find.byKey(const Key('bible_retry_button')), findsNothing);
          // One failed primary attempt, then one initial load per reader.
          // A successful retry also opens the available default translation.
          expect(source.listCalls, 1 + workspace.state.paneIds.length);
          expect(tester.takeException(), isNull);
          binding.reportData![language] = {
            'actualModule': state.selectedModule!.fileName,
            'visibleVerse': true,
            'recoveryToVisibleVerseMs': stopwatch.elapsedMilliseconds,
            'failureBoundary': 'module discovery',
            'readerPanes': workspace.state.paneIds.length,
            'moduleDiscoveryCalls': source.listCalls,
          };
          debugPrint(
            'REV210_WEB_RESULT $language ${jsonEncode(binding.reportData![language])}',
          );
        } finally {
          await tester.pumpWidget(const SizedBox.shrink());
          await tester.pumpAndSettle();
          await GetIt.I.reset();
        }
      },
      skip: !kIsWeb,
    );
  }
}

Future<void> _until(WidgetTester tester, Finder finder) async {
  for (var i = 0; i < 300 && finder.evaluate().isEmpty; i++) {
    await tester.pump(const Duration(milliseconds: 100));
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 20)),
    );
  }
  expect(finder, findsOneWidget);
  await tester.pumpAndSettle();
}

class _FailOnce implements BibleModuleDataSource {
  int listCalls = 0;
  final local = const LocalBibleModuleDataSource();
  @override
  Future<List<String>> listModuleFiles({required String defaultModuleFile}) {
    if (++listCalls == 1) throw const BibleModulesUnavailableException();
    return local.listModuleFiles(defaultModuleFile: defaultModuleFile);
  }

  @override
  BibleModuleDB openModule(String moduleFile) => local.openModule(moduleFile);
}

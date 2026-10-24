import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:intl/intl.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'support/installed_bible_stub.dart'
    if (dart.library.io) 'support/installed_bible_native.dart'
    if (dart.library.js_interop) 'support/installed_bible_web.dart'
    as platform;

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  binding.reportData = {};
  for (final language in ['en', 'es', 'uk', 'ru']) {
    testWidgets('installed module information in $language', (tester) async {
      SharedPreferences.setMockInitialValues({});
      for (final file in [
        'bible_lxx_tr.sqlite',
        'bible_kjv.sqlite',
        'bible_ohienko_1988.sqlite',
      ]) {
        late DatabaseVersionInfo version;
        late String title;
        late String source;
        late String moduleLanguage;
        late String code;
        late String moduleId;
        await tester.runAsync(() async {
          final db = BibleModuleDB(platform.openInstalledModule(file));
          try {
            await db.customStatement('PRAGMA query_only=ON');
            version = (await db.readVersionInfo())!;
            final info = await db.readInfo(file);
            title = info.title;
            source = info.sourceSummary;
            moduleLanguage = info.language;
            code = info.code;
            moduleId = info.moduleId;
          } finally {
            await db.close();
          }
        });
        await tester.pumpWidget(
          MaterialApp(
            key: ValueKey('$language/$file'),
            locale: Locale(language),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: BibleScreen(
              initialBookId: 1,
              bibleRepository: _InstalledRepository(file),
            ),
          ),
        );
        await _pumpUntil(tester, find.byKey(const Key('bible_verse_1')));
        final l10n = AppLocalizations.of(
          tester.element(find.byType(BibleScreen)),
        )!;
        final button = find.byKey(const Key('bible_module_info_button'));
        if (button.evaluate().isNotEmpty) {
          await tester.tap(button);
        } else {
          await tester.tap(find.byIcon(Icons.more_vert).first);
          await tester.pumpAndSettle();
          await tester.tap(
            find.widgetWithText(PopupMenuItem<String>, l10n.bible_module_info),
          );
        }
        await tester.pumpAndSettle();
        expect(
          find.byKey(const Key('bible_module_info_dialog')),
          findsOneWidget,
        );
        String value(String id) =>
            tester.widget<Text>(find.byKey(Key('bible_module_info_$id'))).data!;
        expect(find.text(title), findsOneWidget);
        const languageNames = {
          'en': {'en': 'English', 'grc': 'Ancient Greek', 'uk': 'Ukrainian'},
          'es': {'en': 'Inglés', 'grc': 'Griego antiguo', 'uk': 'Ucraniano'},
          'uk': {
            'en': 'Англійська',
            'grc': 'Давньогрецька',
            'uk': 'Українська',
          },
          'ru': {
            'en': 'Английский',
            'grc': 'Древнегреческий',
            'uk': 'Украинский',
          },
        };
        final languageName = value('language');
        expect(languageName, languageNames[language]![moduleLanguage]);
        final dialog = find.byKey(const Key('bible_module_info_dialog'));
        final material = find
            .descendant(
              of: dialog,
              matching: find.byWidgetPredicate(
                (widget) =>
                    widget is Material && widget.type == MaterialType.card,
              ),
            )
            .first;
        final dialogWidth = tester.getSize(material).width;
        final screenWidth = MediaQuery.sizeOf(tester.element(dialog)).width;
        expect(dialogWidth, closeTo((screenWidth - 48).clamp(0.0, 560.0), 0.1));
        expect(value('schema_version'), version.schemaVersion.toString());
        expect(value('data_version'), version.dataVersion.toString());
        expect(value('date'), DateFormat.yMMMd(language).format(version.date));
        expect(find.text('protestant_66'), findsNothing);
        expect(find.text('kjv_protestant'), findsNothing);
        expect(find.text(source, findRichText: true), findsNothing);
        final details = find.byKey(const Key('bible_module_info_details'));
        await tester.ensureVisible(details);
        await tester.tap(details);
        await tester.pumpAndSettle();
        expect(tester.getSize(material).width, dialogWidth);
        for (final technicalValue in [code, moduleId]) {
          expect(
            find.descendant(
              of: details,
              matching: find.text(technicalValue, findRichText: true),
            ),
            findsNothing,
          );
        }
        expect(find.text(source, findRichText: true), findsOneWidget);
        await tester.tap(find.text(l10n.close));
        await tester.pumpAndSettle();
        expect(find.byKey(const Key('bible_module_info_dialog')), findsNothing);
        expect(tester.takeException(), isNull);
        binding.reportData!['$language/$file'] = {
          'schema': version.schemaVersion,
          'data': version.dataVersion,
          'date': version.date.toIso8601String(),
          'detailsPreserved': true,
          'language': languageName,
          'dialogWidth': dialogWidth,
          'technicalIdsHidden': true,
        };
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pumpAndSettle();
      }
    });
  }
}

Future<void> _pumpUntil(WidgetTester tester, Finder finder) async {
  for (var attempt = 0; attempt < 150 && finder.evaluate().isEmpty; attempt++) {
    await tester.pump(const Duration(milliseconds: 100));
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 30)),
    );
  }
  expect(finder, findsOneWidget);
}

class _InstalledRepository extends BibleRepository {
  _InstalledRepository(this.file)
    : super(moduleDataSource: _InstalledModules());
  final String file;

  @override
  Future<List<String>> loadLastModuleFiles() async => [file];
}

class _InstalledModules implements BibleModuleDataSource {
  @override
  Future<List<String>> listModuleFiles({
    required String defaultModuleFile,
  }) async => [
    'bible_lxx_tr.sqlite',
    'bible_kjv.sqlite',
    'bible_ohienko_1988.sqlite',
  ];

  @override
  BibleModuleDB openModule(String moduleFile) =>
      BibleModuleDB(platform.openInstalledModule(moduleFile));
}

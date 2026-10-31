import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:revelation/features/bible/bible.dart';
import 'package:revelation/features/bible/data/repositories/bible_module_data_source.dart';
import 'package:revelation/infra/db/bible/bible_module_db.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'support/installed_bible_stub.dart'
    if (dart.library.io) 'support/installed_bible_native.dart'
    if (dart.library.js_interop) 'support/installed_bible_web.dart'
    as platform;

const _textModule = 'bible_ohienko_1988.sqlite';
const _restoredVerses = [
  (
    book: 66,
    chapter: 1,
    verse: 3,
    text:
        'Блаженний, хто читає, і ті, хто слухає слова пророцтва та '
        'доде́ржує написане в ньому, — час бо близьки́й!',
  ),
  (
    book: 5,
    chapter: 34,
    verse: 8,
    text:
        'І оплакували Мойсея Ізраїлеві сини в моавських степа́х '
        'тридцять день, та й покінчи́лися дні опла́кування жало́би за Мойсеєм.',
  ),
];

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  binding.reportData = {};

  testWidgets('installed OH1988 text, footnotes and legacy modules', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final repository = BibleRepository(moduleDataSource: _InstalledModules());
    late int verseWithoutComment;
    await tester.runAsync(() async {
      final db = BibleModuleDB(platform.openInstalledModule(_textModule));
      try {
        await db.customStatement('PRAGMA query_only=ON');
        expect((await db.readInfo(_textModule)).code, 'OH1988');
        expect((await db.readVersionInfo())?.schemaVersion, 4);
        expect((await db.readVersionInfo())?.dataVersion, 2);
        final verses = await db.readAllVerses();
        expect(verses, hasLength(31102));
        expect(verses.where((v) => v.comment.isNotEmpty), hasLength(1222));
        expect(
          verses.any((v) => RegExp(r'\b[GH]\d+\b').hasMatch(v.text)),
          isFalse,
        );
        expect(verses.first.comment, contains('šamajim'));
        expect(
          verses.last.text,
          'Благода́ть Господа нашого Ісуса Христа зо всіма́ вами! Амі́нь.',
        );
        binding.reportData!['verifiedVerseRows'] = verses.length;
        binding.reportData!['nonemptyComments'] = 1222;
      } finally {
        await db.close();
      }
      for (final name in ['bible_kjv.sqlite', 'bible_lxx_tr.sqlite']) {
        final legacy = BibleModuleDB(platform.openInstalledModule(name));
        try {
          await legacy.customStatement('PRAGMA query_only=ON');
          final verses = await legacy.readVersesByKeys(['001']);
          expect(verses.single.comment, '');
          final version = await legacy
              .customSelect('PRAGMA user_version')
              .getSingle();
          expect(version.read<int>('user_version'), 3);
        } finally {
          await legacy.close();
        }
      }
      final matches = await repository.searchModule(
        moduleFile: _textModule,
        query: 'šamajim',
      );
      expect(
        matches,
        isEmpty,
        reason: 'Footnote text must not enter Bible text search',
      );
      final chapter = await repository.loadChapter(
        moduleFile: _textModule,
        bookId: 1,
        chapter: 1,
        verse: 1,
      );
      expect(chapter.verses.first.comment, contains('šamajim'));
      verseWithoutComment = chapter.verses
          .firstWhere((v) => v.comment.isEmpty)
          .reference
          .verse;
    });

    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('uk'),
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: BibleScreen(
          initialBookId: 1,
          initialChapter: 1,
          initialVerse: 1,
          initialModuleFile: _textModule,
          bibleRepository: repository,
        ),
      ),
    );
    await _pumpUntil(tester, find.byKey(const Key('bible_verse_comment_1')));
    await tester.pumpAndSettle();
    expect(
      find.byKey(Key('bible_verse_comment_$verseWithoutComment')),
      findsNothing,
    );
    await tester.tap(find.byKey(const Key('bible_verse_comment_1')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('bible_verse_comment_dialog')), findsOneWidget);
    expect(find.textContaining('šamajim'), findsOneWidget);
    await tester.tap(find.text('Закрити'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('bible_verse_comment_dialog')), findsNothing);
    binding.reportData!['installedModuleReaderAndFootnote'] = true;
  });

  for (final restored in _restoredVerses) {
    testWidgets(
      'complete OH1988 ${restored.book}:${restored.chapter}:${restored.verse}',
      (tester) async {
        SharedPreferences.setMockInitialValues({});
        final repository = BibleRepository(
          moduleDataSource: _InstalledModules(),
        );
        await tester.runAsync(() async {
          final chapter = await repository.loadChapter(
            moduleFile: _textModule,
            bookId: restored.book,
            chapter: restored.chapter,
            verse: restored.verse,
          );
          expect(
            chapter.verses
                .singleWhere((v) => v.reference.verse == restored.verse)
                .text,
            restored.text,
          );
        });
        await tester.pumpWidget(
          MaterialApp(
            locale: const Locale('uk'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: BibleScreen(
              initialBookId: restored.book,
              initialChapter: restored.chapter,
              initialVerse: restored.verse,
              initialModuleFile: _textModule,
              bibleRepository: repository,
            ),
          ),
        );
        await _pumpUntil(
          tester,
          find.byKey(Key('bible_verse_${restored.verse}')),
        );
        await tester.pumpAndSettle();
        expect(
          find.textContaining(restored.text, findRichText: true),
          findsOneWidget,
        );
        binding.reportData!['restored_${restored.book}_${restored.chapter}_${restored.verse}'] =
            true;
      },
    );
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

class _InstalledModules implements BibleModuleDataSource {
  @override
  Future<List<String>> listModuleFiles({
    required String defaultModuleFile,
  }) async => [_textModule, 'bible_kjv.sqlite', 'bible_lxx_tr.sqlite'];

  @override
  BibleModuleDB openModule(String moduleFile) =>
      BibleModuleDB(platform.openInstalledModule(moduleFile));
}

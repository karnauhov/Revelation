import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:revelation/features/bible/presentation/bloc/bible_passage_preview_cubit.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_passage_dialog.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/services/bible_verse_map.dart';

import '../../../../test_harness/fakes/fake_allusion_repositories.dart';

void main() {
  for (final width in [320.0, 900.0]) {
    testWidgets(
      'parallel passage, export, copy and range navigation at width $width',
      (tester) async {
        await tester.binding.setSurfaceSize(Size(width, 620));
        addTearDown(() => tester.binding.setSurfaceSize(null));
        final map = (await tester.runAsync(BibleVerseMap.loadFromAssets))!;
        String? copied, exported, docTitle;
        final router = GoRouter(
          routes: [
            GoRoute(
              path: '/',
              builder: (context, state) => Scaffold(
                body: TextButton(
                  onPressed: () => showBiblePassageDialog(
                    context,
                    references: [
                      map.referenceForKey('001')!,
                      map.referenceForKey('002')!,
                    ],
                    verseMap: map,
                    moduleFile: FakeBibleLibrary.ukrainian.fileName,
                    previewCubit: BiblePassagePreviewCubit(FakeBibleLibrary()),
                    matchedNumbers: [10],
                    onCopyRequested: (text) async {
                      copied = text;
                    },
                    onExportPdfRequested:
                        ({required markdown, required documentTitle}) async {
                          exported = markdown;
                          docTitle = documentTitle;
                          return null;
                        },
                  ),
                  child: const Text('Preview'),
                ),
              ),
            ),
            GoRoute(
              path: '/bible',
              builder: (_, state) => Scaffold(body: Text(state.uri.toString())),
            ),
          ],
        );
        addTearDown(router.dispose);
        await tester.pumpWidget(
          MaterialApp.router(
            routerConfig: router,
            locale: const Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
          ),
        );
        await tester.tap(find.text('Preview'));
        await tester.pumpAndSettle();
        final firstTranslation = find.textContaining('Український текст 001');
        final greekWord = find
            .byKey(const ValueKey('bible_passage_word_G10'))
            .first;
        expect(firstTranslation, findsOneWidget);
        expect(greekWord, findsOneWidget);
        expect(
          find.byKey(const ValueKey('bible_passage_word_G20')),
          findsNWidgets(2),
        );
        final translationRect = tester.getRect(firstTranslation);
        final originalRect = tester.getRect(greekWord);
        if (width == 320) {
          expect(originalRect.top, greaterThan(translationRect.bottom));
        } else {
          expect(originalRect.left, greaterThan(translationRect.right));
        }
        await tester.tap(
          find.byKey(const Key('description_markdown_copy_button')),
        );
        await tester.pump();
        expect(copied, contains('Genesis 1:1-2'));
        expect(copied, contains('Український текст 002'));
        expect(copied, contains('λόγος θεός ποιέω'));
        expect(copied, isNot(contains('G10')));
        await tester.tap(
          find.byKey(const Key('description_markdown_export_pdf_button')),
        );
        await tester.pump();
        expect(docTitle, 'Genesis 1:1-2');
        expect(exported, contains('## OH1988'));
        expect(exported, contains(r'## LXX\_TR'));
        expect(exported, contains('λόγος θεός ποιέω'));
        await tester.tap(find.byKey(const Key('bible_passage_next')));
        await tester.pumpAndSettle();
        expect(find.text('Genesis 1:2-3'), findsOneWidget);
        await tester.tap(find.byKey(const Key('bible_passage_open_reader')));
        await tester.pumpAndSettle();
        expect(
          find.text(
            '/bible?book=1&chapter=1&verse=2&module=bible_ohienko_1988.sqlite&length=2',
          ),
          findsOneWidget,
        );
        expect(tester.takeException(), isNull);
      },
    );
  }
}

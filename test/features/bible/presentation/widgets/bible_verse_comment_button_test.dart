import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/bible/domain/models/bible_chapter_verse.dart';
import 'package:revelation/features/bible/presentation/widgets/bible_verse_comment_button.dart';
import 'package:revelation/shared/models/bible_verse_reference.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  const reference = BibleVerseReference(
    verseKey: '001',
    bookId: 1,
    chapter: 1,
    verse: 1,
  );

  for (final comment in ['', '   ']) {
    testWidgets('empty comment creates no action: "$comment"', (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: BibleVerseCommentButton(
            verse: BibleChapterVerse(
              reference: reference,
              text: 'Text',
              comment: comment,
            ),
          ),
        ),
      );
      expect(find.byType(IconButton), findsNothing);
      expect(find.byType(AlertDialog), findsNothing);
    });
  }

  testWidgets('footnote action is labelled and keyboard accessible', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const BibleVerseCommentButton(
          verse: BibleChapterVerse(
            reference: reference,
            text: 'Canonical text',
            comment: '1 Separate footnote.\n\n2 Second note.',
          ),
        ),
      ),
    );
    expect(find.byTooltip('Show footnotes for verse 1'), findsOneWidget);
    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await tester.sendKeyEvent(LogicalKeyboardKey.enter);
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('bible_verse_comment_dialog')), findsOneWidget);
    expect(find.text('1 Separate footnote.\n\n2 Second note.'), findsOneWidget);
    expect(find.text('Canonical text'), findsNothing);
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsNothing);
    semantics.dispose();
  });
}

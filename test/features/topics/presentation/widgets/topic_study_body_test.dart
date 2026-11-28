import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/topics/presentation/widgets/topic_study_body.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
  testWidgets('italic Strong link keeps the link color and underline', (
    tester,
  ) async {
    final theme = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
    );
    String? destination;
    await tester.pumpWidget(
      MaterialApp(
        theme: theme,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: TopicStudyBody(
            markdown: 'Перше грецьке слово, *[апокаліпсис](strong:G602)*.',
            onTapLink: (_, href, _) => destination = href,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final link = linkedTextFor(tester, 'апокаліпсис');
    expect(link.style?.fontStyle, FontStyle.italic);
    expect(link.style?.color, theme.colorScheme.primary);
    expect(link.style?.decoration, TextDecoration.underline);
    (link.recognizer as TapGestureRecognizer).onTap!();
    expect(destination, 'strong:G602');
  });

  testWidgets('a citation scrolls to its exact numbered reference', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 430));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    final controller = ScrollController();
    addTearDown(controller.dispose);
    final reachedLinks = <String?>[];
    final paragraphs = List.filled(
      35,
      'Another paragraph in the study.',
    ).join('\n\n');
    final notes = List.generate(
      15,
      (index) =>
          '${index + 1}. Source ${index + 1} with [original](https://example.org/$index)',
    ).join('\n');
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            controller: controller,
            child: TopicStudyBody(
              markdown:
                  'An observation¹⁰. [Read the verse](bible:Rev1:3).\n\n'
                  '$paragraphs\n\n$studyReferencesMarker\n\n---\n\n$notes',
              onTapLink: (_, href, _) => reachedLinks.add(href),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    recognizerFor(tester, 'Read the verse').onTap!();
    expect(reachedLinks, ['bible:Rev1:3']);
    recognizerFor(tester, '¹⁰').onTap!();
    await tester.pumpAndSettle();

    expect(controller.offset, greaterThan(0));
    expect(
      find.textContaining('10. Source 10', findRichText: true).hitTestable(),
      findsOneWidget,
    );
    expect(
      find.textContaining('1. Source 1 with', findRichText: true).hitTestable(),
      findsNothing,
    );
    expect(reachedLinks, ['bible:Rev1:3']);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}

TapGestureRecognizer recognizerFor(WidgetTester tester, String label) {
  return linkedTextFor(tester, label).recognizer as TapGestureRecognizer;
}

TextSpan linkedTextFor(WidgetTester tester, String label) {
  for (final richText in tester.widgetList<RichText>(find.byType(RichText))) {
    TextSpan? link;
    richText.text.visitChildren((span) {
      if (span is TextSpan &&
          span.text == label &&
          span.recognizer is TapGestureRecognizer) {
        link = span;
      }
      return link == null;
    });
    if (link != null) return link!;
  }
  throw StateError('Link not found: $label');
}

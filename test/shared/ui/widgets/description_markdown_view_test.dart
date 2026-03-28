@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:get_it/get_it.dart';
import 'package:talker_flutter/talker_flutter.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';

import '../../../test_harness/widget_test_harness.dart';

void main() {
  setUp(() async {
    await GetIt.I.reset();
    GetIt.I.registerSingleton<Talker>(
      Talker(settings: TalkerSettings(useConsoleLogs: false)),
    );
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets('DescriptionMarkdownView uses Markdown when scrollable', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(data: 'Hello **world**'),
      ),
    );

    final markdown = tester.widget<Markdown>(find.byType(Markdown));
    expect(markdown.data, contains('Hello'));
  });

  testWidgets('DescriptionMarkdownView uses MarkdownBody when static', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: 'Static text',
          scrollable: false,
        ),
      ),
    );

    final markdownBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
    expect(markdownBody.data, contains('Static text'));
  });

  testWidgets('DescriptionMarkdownView forwards strong link taps to callback', (
    tester,
  ) async {
    int? capturedStrongNumber;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: '[Strong](strong:G321)',
          onGreekStrongTap: (strongNumber, _) {
            capturedStrongNumber = strongNumber;
          },
        ),
      ),
    );

    await tester.tap(find.text('Strong'));
    await tester.pump();

    expect(capturedStrongNumber, 321);
  });

  testWidgets('DescriptionMarkdownView forwards word link taps to callback', (
    tester,
  ) async {
    String? sourceId;
    String? pageName;
    int? wordIndex;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: '[Word](word:source-1:page-4:7)',
          scrollable: false,
          onWordTap:
              (capturedSourceId, capturedPageName, capturedWordIndex, _) {
                sourceId = capturedSourceId;
                pageName = capturedPageName;
                wordIndex = capturedWordIndex;
              },
        ),
      ),
    );

    await tester.tap(find.text('Word'));
    await tester.pump();

    expect(sourceId, 'source-1');
    expect(pageName, 'page-4');
    expect(wordIndex, 7);
  });

  testWidgets(
    'DescriptionMarkdownView forwards strong picker taps to callback',
    (tester) async {
      int? capturedStrongNumber;

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: DescriptionMarkdownView(
            data: '[Picker](strong_picker:G145)',
            onGreekStrongPickerTap: (strongNumber, _) {
              capturedStrongNumber = strongNumber;
            },
          ),
        ),
      );

      await tester.tap(find.text('Picker'));
      await tester.pump();

      expect(capturedStrongNumber, 145);
    },
  );

  testWidgets('DescriptionMarkdownView applies custom padding in static mode', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: 'content',
          scrollable: false,
          padding: EdgeInsets.only(left: 11, top: 7),
        ),
      ),
    );

    final padding = tester.widget<Padding>(find.byType(Padding).first);
    expect(padding.padding, const EdgeInsets.only(left: 11, top: 7));
  });
}

@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/shared/ui/widgets/description_markdown_view.dart';
import 'package:revelation/shared/utils/description_markdown_tokens.dart';
import 'package:talker_flutter/talker_flutter.dart';

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

  testWidgets(
    'DescriptionMarkdownView wraps shared markdown body in scroll view when scrollable',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: const DescriptionMarkdownView(data: 'Hello **world**'),
        ),
      );

      expect(find.byType(SingleChildScrollView), findsOneWidget);
      final markdownBody = tester.widget<MarkdownBody>(
        find.byType(MarkdownBody),
      );
      expect(markdownBody.data, contains('Hello'));
    },
  );

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

  testWidgets('DescriptionMarkdownView can override h2 font weight', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: '## ΑⲂΜ',
          scrollable: false,
          h2FontWeight: FontWeight.normal,
        ),
      ),
    );

    final markdownBody = tester.widget<MarkdownBody>(find.byType(MarkdownBody));
    expect(markdownBody.styleSheet!.h2!.fontWeight, FontWeight.normal);
  });

  testWidgets(
    'DescriptionMarkdownView renders strong origin info marker as tooltip icon',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: const DescriptionMarkdownView(
            data: 'Word analysis: $strongOriginInfoMarkdownMarker **Alpha**',
            scrollable: false,
            showExportPdfButton: false,
          ),
        ),
      );

      const tooltip =
          'Word analysis may include the following elements: derivatives, '
          'comparative words, phrases, and related words.';

      expect(find.text(strongOriginInfoMarkdownMarker), findsNothing);
      expect(
        find.byKey(const Key('description_markdown_strong_origin_info_button')),
        findsOneWidget,
      );
      expect(find.byTooltip(tooltip), findsOneWidget);

      await tester.tap(
        find.byKey(const Key('description_markdown_strong_origin_info_button')),
      );
      await tester.pump();

      expect(find.text(tooltip), findsOneWidget);
    },
  );

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
          showExportPdfButton: false,
          padding: EdgeInsets.only(left: 11, top: 7),
        ),
      ),
    );

    final padding = tester.widget<Padding>(find.byType(Padding).first);
    expect(padding.padding, const EdgeInsets.only(left: 11, top: 7));
  });

  testWidgets('DescriptionMarkdownView shows PDF export button by default', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(data: 'Printable content'),
      ),
    );

    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('description_markdown_copy_button')),
      findsOneWidget,
    );
  });

  testWidgets('DescriptionMarkdownView can delegate PDF export action', (
    tester,
  ) async {
    String? capturedMarkdown;
    String? capturedDocumentTitle;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Printable content',
          onExportPdfRequested:
              ({required markdown, required documentTitle}) async {
                capturedMarkdown = markdown;
                capturedDocumentTitle = documentTitle;
                return 'Revelation.pdf';
              },
        ),
      ),
    );

    await tester.tap(
      find.byKey(const Key('description_markdown_export_pdf_button')),
    );
    await tester.pump();

    expect(capturedMarkdown, 'Printable content');
    expect(capturedDocumentTitle, 'Revelation');
  });

  testWidgets(
    'DescriptionMarkdownView strips presentation markers for export',
    (tester) async {
      String? capturedMarkdown;

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: DescriptionMarkdownView(
            data: 'Word analysis: $strongOriginInfoMarkdownMarker **Alpha**',
            onExportPdfRequested:
                ({required markdown, required documentTitle}) async {
                  capturedMarkdown = markdown;
                  return 'Revelation.pdf';
                },
          ),
        ),
      );

      await tester.tap(
        find.byKey(const Key('description_markdown_export_pdf_button')),
      );
      await tester.pump();

      expect(capturedMarkdown, 'Word analysis: **Alpha**');
    },
  );

  testWidgets('DescriptionMarkdownView can use custom PDF document title', (
    tester,
  ) async {
    String? capturedDocumentTitle;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Strong content',
          exportPdfDocumentTitle: 'G25',
          onExportPdfRequested:
              ({required markdown, required documentTitle}) async {
                capturedDocumentTitle = documentTitle;
                return 'G25.pdf';
              },
        ),
      ),
    );

    await tester.tap(
      find.byKey(const Key('description_markdown_export_pdf_button')),
    );
    await tester.pump();

    expect(capturedDocumentTitle, 'G25');
  });

  testWidgets('DescriptionMarkdownView can disable PDF export and copy', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Disabled content',
          exportPdfEnabled: false,
          copyEnabled: false,
          onExportPdfRequested:
              ({required markdown, required documentTitle}) async {
                fail('PDF export should stay disabled.');
              },
          onCopyRequested: (_) async {
            fail('Copy should stay disabled.');
          },
        ),
      ),
    );

    final exportIgnorePointerFinder = find.ancestor(
      of: find.byKey(const Key('description_markdown_export_pdf_button')),
      matching: find.byType(IgnorePointer),
    );
    final copyIgnorePointerFinder = find.ancestor(
      of: find.byKey(const Key('description_markdown_copy_button')),
      matching: find.byType(IgnorePointer),
    );

    expect(
      tester.widget<IgnorePointer>(exportIgnorePointerFinder.first).ignoring,
      isTrue,
    );
    expect(
      tester.widget<IgnorePointer>(copyIgnorePointerFinder.first).ignoring,
      isTrue,
    );
  });

  testWidgets('DescriptionMarkdownView can delegate copy action', (
    tester,
  ) async {
    String? capturedMarkdown;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Printable content',
          onCopyRequested: (markdown) async {
            capturedMarkdown = markdown;
          },
        ),
      ),
    );

    await tester.tap(find.byKey(const Key('description_markdown_copy_button')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(capturedMarkdown, 'Printable content');
    expect(find.byType(SnackBar), findsOneWidget);
    expect(find.text('Content copied to the clipboard.'), findsOneWidget);
  });

  testWidgets('DescriptionMarkdownView strips presentation markers for copy', (
    tester,
  ) async {
    String? capturedMarkdown;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Word analysis: $strongOriginInfoMarkdownMarker **Alpha**',
          onCopyRequested: (markdown) async {
            capturedMarkdown = markdown;
          },
        ),
      ),
    );

    await tester.tap(find.byKey(const Key('description_markdown_copy_button')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(capturedMarkdown, 'Word analysis: **Alpha**');
  });

  testWidgets(
    'DescriptionMarkdownView shows toolbar actions after PDF export',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: DescriptionMarkdownView(
            data: 'Printable content',
            toolbarActions: [
              DescriptionMarkdownToolbarButton(
                buttonKey: const Key('custom_toolbar_action'),
                tooltip: 'Next',
                icon: Icons.arrow_forward,
                onPressed: () {},
              ),
            ],
          ),
        ),
      );

      final exportButtonLeft = tester.getTopLeft(
        find.byKey(const Key('description_markdown_export_pdf_button')),
      );
      final copyButtonLeft = tester.getTopLeft(
        find.byKey(const Key('description_markdown_copy_button')),
      );
      final customActionLeft = tester.getTopLeft(
        find.byKey(const Key('custom_toolbar_action')),
      );

      expect(copyButtonLeft.dx, greaterThan(exportButtonLeft.dx));
      expect(customActionLeft.dx, greaterThan(copyButtonLeft.dx));
    },
  );

  testWidgets(
    'DescriptionMarkdownView can show toolbar actions without PDF export',
    (tester) async {
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: DescriptionMarkdownView(
            data: 'Printable content',
            showExportPdfButton: false,
            toolbarActions: [
              DescriptionMarkdownToolbarButton(
                buttonKey: const Key('custom_toolbar_action'),
                tooltip: 'Next',
                icon: Icons.arrow_forward,
                onPressed: () {},
              ),
            ],
          ),
        ),
      );

      expect(
        find.byKey(const Key('description_markdown_export_pdf_button')),
        findsNothing,
      );
      expect(
        find.byKey(const Key('description_markdown_copy_button')),
        findsNothing,
      );
      expect(find.byKey(const Key('custom_toolbar_action')), findsOneWidget);
    },
  );

  testWidgets('DescriptionMarkdownView hides toolbar when it has no actions', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: 'Printable content',
          showExportPdfButton: false,
        ),
      ),
    );

    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsNothing,
    );
    expect(
      find.byKey(const Key('description_markdown_copy_button')),
      findsNothing,
    );
    expect(find.byType(DescriptionMarkdownToolbarButton), findsNothing);
  });

  testWidgets('DescriptionMarkdownView can hide PDF export button', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: const DescriptionMarkdownView(
          data: 'Printable content',
          showExportPdfButton: false,
        ),
      ),
    );

    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsNothing,
    );
    expect(
      find.byKey(const Key('description_markdown_copy_button')),
      findsNothing,
    );
  });

  testWidgets('DescriptionMarkdownView shows snackbar when PDF export fails', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Printable content',
          onExportPdfRequested:
              ({required markdown, required documentTitle}) async {
                throw StateError('boom');
              },
        ),
      ),
    );

    await tester.tap(
      find.byKey(const Key('description_markdown_export_pdf_button')),
    );
    await tester.pump();

    await tester.pumpAndSettle();

    expect(find.byType(SnackBar), findsOneWidget);
    expect(find.text("Couldn't export the PDF."), findsOneWidget);
  });

  testWidgets('DescriptionMarkdownView shows snackbar when copy fails', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: DescriptionMarkdownView(
          data: 'Printable content',
          onCopyRequested: (markdown) async {
            throw StateError('boom');
          },
        ),
      ),
    );

    await tester.tap(find.byKey(const Key('description_markdown_copy_button')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(find.byType(SnackBar), findsOneWidget);
    expect(find.text("Couldn't copy the content."), findsOneWidget);
  });
}

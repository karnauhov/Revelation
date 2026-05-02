@Tags(['widget'])
import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:revelation/features/primary_sources/application/services/primary_source_word_image_service.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_word_images_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_words_dialog.dart';
import 'package:revelation/shared/models/primary_source_word_link_target.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'showPrimarySourceWordsDialog normalizes title and renders sections',
    (tester) async {
      const availableTarget = PrimarySourceWordLinkTarget(
        sourceId: 'U001',
        pageName: '325v',
        wordIndex: 2,
      );
      const unavailableTarget = PrimarySourceWordLinkTarget(
        sourceId: 'U002',
        pageName: '150r',
        wordIndex: 5,
      );
      const sourceOnlyTarget = PrimarySourceWordLinkTarget(sourceId: 'U003');
      final cubit = PrimarySourceWordImagesCubit(
        targets: const [availableTarget, unavailableTarget, sourceOnlyTarget],
        isWeb: false,
        isMobileWeb: false,
        localizations: lookupAppLocalizations(const Locale('en')),
        imageService: _FakeWordImageService([
          PrimarySourceWordImageResult(
            target: availableTarget,
            sourceTitle: 'Source <sup>One</sup>',
            imageBytes: _png(),
            displayWordText: 'A~~PO~~KALYPSIS',
            unavailableReason: PrimarySourceWordImageUnavailableReason.none,
          ),
          PrimarySourceWordImageResult.unavailable(
            target: unavailableTarget,
            sourceTitle: 'Source Two',
            displayWordText: 'APOKALYPSIS',
            reason: PrimarySourceWordImageUnavailableReason.wordUnavailable,
          ),
          PrimarySourceWordImageResult.unavailable(
            target: sourceOnlyTarget,
            sourceTitle: 'Source Three',
            displayWordText: 'LOGOS',
            reason: PrimarySourceWordImageUnavailableReason.pageUnavailable,
          ),
        ]),
        autoLoad: false,
      );
      addTearDown(cubit.close);
      await cubit.load();

      final context = await pumpLocalizedContext(tester);
      final l10n = AppLocalizations.of(context)!;

      unawaited(
        showPrimarySourceWordsDialog(context, const [
          availableTarget,
          unavailableTarget,
          sourceOnlyTarget,
        ], cubit: cubit),
      );
      await tester.pumpAndSettle();

      expect(find.byType(PrimarySourceWordsDialog), findsOneWidget);
      expect(find.text('APOKALYPSIS, LOGOS'), findsOneWidget);
      expect(find.text('U001'), findsOneWidget);
      expect(find.text('U002'), findsOneWidget);
      expect(find.text('U003'), findsOneWidget);
      expect(find.text('Source One'), findsNothing);
      expect(find.text('Source Two'), findsNothing);
      expect(find.text('Source Three'), findsNothing);
      expect(find.byType(RotatedBox), findsNWidgets(3));
      expect(
        find.byKey(const Key('description_markdown_export_pdf_button')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('description_markdown_copy_button')),
        findsNothing,
      );
      expect(find.byType(Image), findsOneWidget);
      expect(find.text(l10n.primary_source_words_image_hint), findsOneWidget);
      expect(_richTextContaining('602'), findsWidgets);
      expect(_richTextContaining('apokalupsis'), findsWidgets);
      expect(_richTextContaining('revelation'), findsWidgets);
      expect(
        find.text(l10n.primary_source_word_word_unavailable),
        findsOneWidget,
      );
      expect(
        find.text(l10n.primary_source_word_page_unavailable),
        findsOneWidget,
      );

      final titleText = tester.widget<Text>(find.text('APOKALYPSIS, LOGOS'));
      expect(titleText.style?.fontWeight, FontWeight.normal);
      final rotatedBoxes = tester.widgetList<RotatedBox>(
        find.byType(RotatedBox),
      );
      expect(rotatedBoxes.every((widget) => widget.quarterTurns == 3), isTrue);
      final tooltips = tester
          .widgetList<Tooltip>(find.byType(Tooltip))
          .where((widget) => widget.triggerMode == TooltipTriggerMode.tap)
          .toList();
      expect(tooltips.map((widget) => widget.message), [
        'Source One',
        'Source Two',
        'Source Three',
      ]);
      expect(
        tooltips.every(
          (widget) => widget.triggerMode == TooltipTriggerMode.tap,
        ),
        isTrue,
      );

      await tester.tap(find.text(l10n.close));
      await tester.pumpAndSettle();
      expect(find.byType(PrimarySourceWordsDialog), findsNothing);
    },
  );

  testWidgets('export uses plain markdown and sanitized link title', (
    tester,
  ) async {
    const availableTarget = PrimarySourceWordLinkTarget(
      sourceId: 'U001',
      pageName: '325v',
      wordIndex: 2,
    );
    const unavailableTarget = PrimarySourceWordLinkTarget(
      sourceId: 'U002',
      pageName: '150r',
      wordIndex: 5,
    );
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [availableTarget, unavailableTarget],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: _FakeWordImageService([
        PrimarySourceWordImageResult(
          target: availableTarget,
          sourceTitle: 'Source One',
          imageBytes: _png(),
          displayWordText: 'APOKALYPSIS',
          unavailableReason: PrimarySourceWordImageUnavailableReason.none,
        ),
        PrimarySourceWordImageResult.unavailable(
          target: unavailableTarget,
          sourceTitle: 'Source Two',
          displayWordText: 'APOKALYPSIS',
          reason: PrimarySourceWordImageUnavailableReason.wordUnavailable,
        ),
      ]),
      autoLoad: false,
    );
    addTearDown(cubit.close);
    await cubit.load();

    String? exportedMarkdown;
    String? exportedDocumentTitle;
    late BuildContext context;
    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: Builder(
          builder: (buildContext) {
            context = buildContext;
            return const SizedBox.shrink();
          },
        ),
      ),
    );
    await tester.pump();
    final l10n = AppLocalizations.of(context)!;

    unawaited(
      showPrimarySourceWordsDialog(
        context,
        const [availableTarget, unavailableTarget],
        cubit: cubit,
        onExportPdfRequested:
            ({required markdown, required documentTitle}) async {
              exportedMarkdown = markdown;
              exportedDocumentTitle = documentTitle;
              return null;
            },
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(
      find.byKey(const Key('description_markdown_export_pdf_button')),
    );
    await tester.pump();

    expect(exportedDocumentTitle, 'U001.325v.2_U002.150r.5');
    expect(exportedMarkdown, contains('# APOKALYPSIS'));
    expect(exportedMarkdown, contains('**Source One**'));
    expect(
      exportedMarkdown,
      contains('src: https://revelation.local/primary-source-words/0.png'),
    );
    expect(exportedMarkdown, contains('**Source Two**'));
    expect(exportedMarkdown, contains('Word unavailable'));
    expect(exportedMarkdown, isNot(contains('<h1')));
    expect(exportedMarkdown, isNot(contains('<p')));
    expect(exportedMarkdown, isNot(contains('align="center"')));
    expect(exportedMarkdown, isNot(contains('align: center')));
    expect(
      exportedMarkdown,
      isNot(contains(l10n.primary_source_words_image_hint)),
    );
    expect(exportedMarkdown, contains('---'));
    expect(exportedMarkdown, contains('Strong Number'));
  });

  testWidgets('dialog shows row loading indicators until snippets are ready', (
    tester,
  ) async {
    const target = PrimarySourceWordLinkTarget(
      sourceId: 'U001',
      pageName: '325v',
      wordIndex: 2,
    );
    final completer = Completer<void>();
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: true,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: _StreamingWordImageService(
        loadingItems: [
          PrimarySourceWordImageResult.loading(
            target: target,
            sourceTitle: 'Source One',
            displayWordText: 'APOKALYPSIS',
          ),
        ],
        finalItems: [
          PrimarySourceWordImageResult(
            target: target,
            sourceTitle: 'Source One',
            imageBytes: _png(),
            displayWordText: 'APOKALYPSIS',
            unavailableReason: PrimarySourceWordImageUnavailableReason.none,
          ),
        ],
        completeAfter: completer.future,
      ),
    );
    addTearDown(cubit.close);

    final context = await pumpLocalizedContext(tester);
    unawaited(
      showPrimarySourceWordsDialog(context, const [target], cubit: cubit),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('APOKALYPSIS'), findsOneWidget);
    expect(find.text('U001'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsWidgets);
    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsNothing,
    );

    completer.complete();
    await tester.pumpAndSettle();

    expect(find.byType(Image), findsOneWidget);
    expect(
      find.byKey(const Key('description_markdown_export_pdf_button')),
      findsOneWidget,
    );
  });

  testWidgets('tapping word image opens the corresponding word link', (
    tester,
  ) async {
    const target = PrimarySourceWordLinkTarget(
      sourceId: 'U001',
      pageName: '325v',
      wordIndex: 2,
    );
    final cubit = PrimarySourceWordImagesCubit(
      targets: const [target],
      isWeb: false,
      isMobileWeb: false,
      localizations: lookupAppLocalizations(const Locale('en')),
      imageService: _FakeWordImageService([
        PrimarySourceWordImageResult(
          target: target,
          sourceTitle: 'Source One',
          imageBytes: _png(),
          displayWordText: 'APOKALYPSIS',
          unavailableReason: PrimarySourceWordImageUnavailableReason.none,
        ),
      ]),
      autoLoad: false,
    );
    addTearDown(cubit.close);
    await cubit.load();

    String? capturedSourceId;
    String? capturedPageName;
    int? capturedWordIndex;
    final context = await pumpLocalizedContext(tester);

    unawaited(
      showPrimarySourceWordsDialog(
        context,
        const [target],
        cubit: cubit,
        onWordTap: (sourceId, pageName, wordIndex, _) {
          capturedSourceId = sourceId;
          capturedPageName = pageName;
          capturedWordIndex = wordIndex;
        },
      ),
    );
    await tester.pumpAndSettle();

    final imageInkWell = tester.widget<InkWell>(
      find.byKey(const ValueKey('primary-source-word-image-U001:325v:2')),
    );
    imageInkWell.onTap?.call();
    await tester.pumpAndSettle();

    expect(find.byType(PrimarySourceWordsDialog), findsNothing);
    expect(capturedSourceId, 'U001');
    expect(capturedPageName, '325v');
    expect(capturedWordIndex, 2);
  });
}

class _FakeWordImageService extends PrimarySourceWordImageService {
  _FakeWordImageService(this.items);

  final List<PrimarySourceWordImageResult> items;

  @override
  Stream<PrimarySourceWordsDialogData> loadDialogDataStream({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) async* {
    yield await loadDialogData(
      targets: targets,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      localizations: localizations,
    );
  }

  @override
  Future<PrimarySourceWordsDialogData> loadDialogData({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) async {
    return PrimarySourceWordsDialogData(
      items: items,
      sharedWordDetailsMarkdown:
          'Strong Number: **[602](strong:G602)**\n\r'
          'Pronunciation: **apokalupsis**\n\r'
          '\n\r'
          '*** \nrevelation\n ***',
    );
  }
}

class _StreamingWordImageService extends PrimarySourceWordImageService {
  _StreamingWordImageService({
    required this.loadingItems,
    required this.finalItems,
    required this.completeAfter,
  });

  final List<PrimarySourceWordImageResult> loadingItems;
  final List<PrimarySourceWordImageResult> finalItems;
  final Future<void> completeAfter;

  @override
  Stream<PrimarySourceWordsDialogData> loadDialogDataStream({
    required List<PrimarySourceWordLinkTarget> targets,
    required bool isWeb,
    required bool isMobileWeb,
    required AppLocalizations localizations,
  }) async* {
    yield PrimarySourceWordsDialogData(items: loadingItems);
    await completeAfter;
    yield PrimarySourceWordsDialogData(items: finalItems);
  }
}

Uint8List _png() {
  final image = img.Image(width: 120, height: 36);
  img.fill(image, color: img.ColorRgb8(255, 255, 255));
  return Uint8List.fromList(img.encodePng(image));
}

Finder _richTextContaining(String value) {
  return find.byWidgetPredicate(
    (widget) => widget is RichText && widget.text.toPlainText().contains(value),
    description: 'RichText containing "$value"',
  );
}

@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/audio/audio_controller.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar_overflow_menu.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets(
    'menu selection dispatches reset callback and tracks open state',
    (tester) async {
      addTearDown(_suppressOverflowErrors());
      final source = _buildSource(permissionsReceived: true);
      final selectedPage = source.pages.first;
      final imageController = ImagePreviewController(4)
        ..setImageSize(const Size(800, 600), 800, 600);
      addTearDown(imageController.dispose);

      final menuStates = <bool>[];
      var resetCalls = 0;

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: MediaQuery(
            data: const MediaQueryData(textScaler: TextScaler.linear(0.7)),
            child: PrimarySourceToolbarOverflowMenuButton(
              primarySource: source,
              selectedPage: selectedPage,
              localPageLoaded: <String, bool?>{selectedPage.image: true},
              refreshError: false,
              isNegative: false,
              isMonochrome: false,
              brightness: 0,
              contrast: 100,
              selectedArea: null,
              tolerance: 0,
              showWordSeparators: false,
              showStrongNumbers: false,
              showVerseNumbers: true,
              zoomStatusNotifier: ValueNotifier(
                const ZoomStatus(
                  canZoomIn: true,
                  canZoomOut: false,
                  canReset: false,
                ),
              ),
              imageController: imageController,
              onSetMenuOpen: menuStates.add,
              onReloadImage: () async {},
              onToggleNegative: () {},
              onToggleMonochrome: () {},
              onToggleShowWordSeparators: () {},
              onToggleShowStrongNumbers: () {},
              onToggleShowVerseNumbers: () {},
              onRemovePageSettings: () {
                resetCalls++;
              },
              onOpenBrightnessContrastDialog: () {},
              onOpenReplaceColorDialog: () {},
              audioController: AudioController(),
              numButtons: 11,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final context = tester.element(
        find.byType(PrimarySourceToolbarOverflowMenuButton),
      );
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text(l10n.page_settings_reset));
      await tester.pumpAndSettle();

      expect(resetCalls, 1);
      expect(menuStates, <bool>[true, false]);
    },
  );

  testWidgets('reset action stays disabled without selected page permissions', (
    tester,
  ) async {
    addTearDown(_suppressOverflowErrors());
    final source = _buildSource(permissionsReceived: false);
    final imageController = ImagePreviewController(4);
    addTearDown(imageController.dispose);

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(0.7)),
          child: PrimarySourceToolbarOverflowMenuButton(
            primarySource: source,
            selectedPage: source.pages.first,
            localPageLoaded: const <String, bool?>{},
            refreshError: false,
            isNegative: false,
            isMonochrome: false,
            brightness: 0,
            contrast: 100,
            selectedArea: null,
            tolerance: 0,
            showWordSeparators: false,
            showStrongNumbers: false,
            showVerseNumbers: true,
            zoomStatusNotifier: ValueNotifier(
              const ZoomStatus(
                canZoomIn: false,
                canZoomOut: false,
                canReset: false,
              ),
            ),
            imageController: imageController,
            onSetMenuOpen: (_) {},
            onReloadImage: () async {},
            onToggleNegative: () {},
            onToggleMonochrome: () {},
            onToggleShowWordSeparators: () {},
            onToggleShowStrongNumbers: () {},
            onToggleShowVerseNumbers: () {},
            onRemovePageSettings: () {},
            onOpenBrightnessContrastDialog: () {},
            onOpenReplaceColorDialog: () {},
            audioController: AudioController(),
            numButtons: 11,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(
      find.byType(PrimarySourceToolbarOverflowMenuButton),
    );
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byIcon(Icons.more_vert));
    await tester.pumpAndSettle();

    final resetItem = tester.widget<PopupMenuItem<String>>(
      find.widgetWithText(PopupMenuItem<String>, l10n.page_settings_reset),
    );
    expect(resetItem.enabled, isFalse);
  });

  testWidgets('overflow menu dispatches all enabled actions', (tester) async {
    addTearDown(_suppressOverflowErrors());
    final source = _buildSource(permissionsReceived: true);
    final selectedPage = source.pages.first;
    final imageController = ImagePreviewController(4)
      ..setImageSize(const Size(800, 600), 800, 600);
    addTearDown(imageController.dispose);
    final zoom = ValueNotifier(
      const ZoomStatus(canZoomIn: true, canZoomOut: true, canReset: true),
    );
    addTearDown(zoom.dispose);

    final menuStates = <bool>[];
    var reloadCalls = 0;
    var negativeCalls = 0;
    var monochromeCalls = 0;
    var wordSeparatorsCalls = 0;
    var strongNumbersCalls = 0;
    var verseNumbersCalls = 0;
    var resetPageCalls = 0;
    var openBrightnessCalls = 0;
    var openReplaceCalls = 0;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(0.7)),
          child: PrimarySourceToolbarOverflowMenuButton(
            primarySource: source,
            selectedPage: selectedPage,
            localPageLoaded: <String, bool?>{selectedPage.image: true},
            refreshError: true,
            isNegative: true,
            isMonochrome: false,
            brightness: 15,
            contrast: 105,
            selectedArea: const Rect.fromLTWH(1, 1, 3, 3),
            tolerance: 20,
            showWordSeparators: true,
            showStrongNumbers: true,
            showVerseNumbers: true,
            zoomStatusNotifier: zoom,
            imageController: imageController,
            onSetMenuOpen: menuStates.add,
            onReloadImage: () async {
              reloadCalls++;
            },
            onToggleNegative: () {
              negativeCalls++;
            },
            onToggleMonochrome: () {
              monochromeCalls++;
            },
            onToggleShowWordSeparators: () {
              wordSeparatorsCalls++;
            },
            onToggleShowStrongNumbers: () {
              strongNumbersCalls++;
            },
            onToggleShowVerseNumbers: () {
              verseNumbersCalls++;
            },
            onRemovePageSettings: () {
              resetPageCalls++;
            },
            onOpenBrightnessContrastDialog: () {
              openBrightnessCalls++;
            },
            onOpenReplaceColorDialog: () {
              openReplaceCalls++;
            },
            audioController: AudioController(),
            numButtons: 0,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(
      find.byType(PrimarySourceToolbarOverflowMenuButton),
    );
    final l10n = AppLocalizations.of(context)!;

    Future<void> choose(String label) async {
      await tester.tap(find.byIcon(Icons.more_vert));
      await tester.pumpAndSettle();
      await tester.tap(find.text(label).last);
      await tester.pumpAndSettle();
    }

    final initialScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    await choose(l10n.zoom_in);
    final zoomedInScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(zoomedInScale, greaterThan(initialScale));

    await choose(l10n.zoom_out);
    final zoomedOutScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(zoomedOutScale, lessThanOrEqualTo(zoomedInScale));

    await choose(l10n.restore_original_scale);
    final resetScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(resetScale, closeTo(imageController.minScale, 0.001));

    await choose(l10n.reload_image);
    await choose(l10n.toggle_negative);
    await choose(l10n.toggle_monochrome);
    await choose(l10n.brightness_contrast);
    await choose(l10n.color_replacement);
    await choose(l10n.toggle_show_word_separators);
    await choose(l10n.toggle_show_strong_numbers);
    await choose(l10n.toggle_show_verse_numbers);
    await choose(l10n.page_settings_reset);

    expect(reloadCalls, 1);
    expect(negativeCalls, 1);
    expect(monochromeCalls, 1);
    expect(openBrightnessCalls, 1);
    expect(openReplaceCalls, 1);
    expect(wordSeparatorsCalls, 1);
    expect(strongNumbersCalls, 1);
    expect(verseNumbersCalls, 1);
    expect(resetPageCalls, 1);
    expect(menuStates.where((value) => value).length, greaterThan(0));
    expect(menuStates.where((value) => !value).length, greaterThan(0));
  });

  testWidgets('monochrome toggle action is disabled for monochrome sources', (
    tester,
  ) async {
    addTearDown(_suppressOverflowErrors());
    final source = _buildSource(permissionsReceived: true, isMonochrome: true);
    final imageController = ImagePreviewController(4)
      ..setImageSize(const Size(800, 600), 800, 600);
    addTearDown(imageController.dispose);
    final zoom = ValueNotifier(
      const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
    );
    addTearDown(zoom.dispose);

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(0.7)),
          child: PrimarySourceToolbarOverflowMenuButton(
            primarySource: source,
            selectedPage: source.pages.first,
            localPageLoaded: <String, bool?>{source.pages.first.image: true},
            refreshError: false,
            isNegative: false,
            isMonochrome: true,
            brightness: 0,
            contrast: 100,
            selectedArea: null,
            tolerance: 0,
            showWordSeparators: false,
            showStrongNumbers: false,
            showVerseNumbers: false,
            zoomStatusNotifier: zoom,
            imageController: imageController,
            onSetMenuOpen: (_) {},
            onReloadImage: () async {},
            onToggleNegative: () {},
            onToggleMonochrome: () {},
            onToggleShowWordSeparators: () {},
            onToggleShowStrongNumbers: () {},
            onToggleShowVerseNumbers: () {},
            onRemovePageSettings: () {},
            onOpenBrightnessContrastDialog: () {},
            onOpenReplaceColorDialog: () {},
            audioController: AudioController(),
            numButtons: 0,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(
      find.byType(PrimarySourceToolbarOverflowMenuButton),
    );
    final l10n = AppLocalizations.of(context)!;

    await tester.tap(find.byIcon(Icons.more_vert));
    await tester.pumpAndSettle();

    final monochromeItem = tester.widget<PopupMenuItem<String>>(
      find.widgetWithText(PopupMenuItem<String>, l10n.toggle_monochrome),
    );
    expect(monochromeItem.enabled, isFalse);
  });
}

VoidCallback _suppressOverflowErrors() {
  final originalHandler = FlutterError.onError;
  FlutterError.onError = (details) {
    final message = details.exceptionAsString();
    if (message.contains('A RenderFlex overflowed by')) {
      return;
    }
    if (originalHandler != null) {
      originalHandler(details);
    }
  };

  return () {
    FlutterError.onError = originalHandler;
  };
}

PrimarySource _buildSource({
  required bool permissionsReceived,
  bool isMonochrome = false,
}) {
  return PrimarySource(
    id: 'source-1',
    title: 'Source',
    date: '',
    content: '',
    quantity: 0,
    material: '',
    textStyle: '',
    found: '',
    classification: '',
    currentLocation: '',
    preview: '',
    maxScale: 3,
    isMonochrome: isMonochrome,
    pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
    attributes: const [],
    permissionsReceived: permissionsReceived,
  );
}

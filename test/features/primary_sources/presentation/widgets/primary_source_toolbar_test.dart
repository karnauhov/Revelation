@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/image_preview_controller.dart';
import 'package:revelation/features/primary_sources/presentation/widgets/primary_source_toolbar.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:revelation/shared/models/zoom_status.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  testWidgets('dropdown change and action buttons invoke provided callbacks', (
    tester,
  ) async {
    final source = _buildSource(permissionsReceived: true);
    final selectedPage = source.pages.first;
    final imageController = ImagePreviewController(6)
      ..setImageSize(const Size(800, 600), 800, 600);
    addTearDown(imageController.dispose);
    final zoom = ValueNotifier(
      const ZoomStatus(canZoomIn: true, canZoomOut: true, canReset: true),
    );
    addTearDown(zoom.dispose);

    model.Page? changedPage;
    var showInfoCalls = 0;
    var reloadCalls = 0;
    var negativeCalls = 0;

    await tester.pumpWidget(
      buildLocalizedTestApp(
        child: PrimarySourceToolbar(
          primarySource: source,
          selectedPage: selectedPage,
          localPageLoaded: {selectedPage.image: true},
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
          zoomStatusNotifier: zoom,
          imageController: imageController,
          isBottom: false,
          dropdownWidth: 200,
          onChangeSelectedPage: (newPage) async {
            changedPage = newPage;
          },
          onShowCommonInfo: () {
            showInfoCalls++;
          },
          onReloadImage: () async {
            reloadCalls++;
          },
          onToggleNegative: () {
            negativeCalls++;
          },
          onToggleMonochrome: () {},
          onToggleShowWordSeparators: () {},
          onToggleShowStrongNumbers: () {},
          onToggleShowVerseNumbers: () {},
          onRemovePageSettings: () {},
          onOpenBrightnessContrastDialog: () {},
          onOpenReplaceColorDialog: () {},
          onSetMenuOpen: (_) {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    final context = tester.element(find.byType(PrimarySourceToolbar));
    final l10n = AppLocalizations.of(context)!;

    final initialScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    await tester.tap(find.byTooltip(l10n.zoom_in));
    await tester.pump();
    final zoomedInScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(zoomedInScale, greaterThan(initialScale));

    await tester.tap(find.byTooltip(l10n.zoom_out));
    await tester.pump();
    final zoomedOutScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(zoomedOutScale, lessThanOrEqualTo(zoomedInScale));

    await tester.tap(find.byTooltip(l10n.restore_original_scale));
    await tester.pump();
    final resetScale = imageController.transformationController.value
        .getMaxScaleOnAxis();
    expect(resetScale, closeTo(imageController.minScale, 0.001));

    await tester.tap(find.byTooltip(l10n.reload_image));
    await tester.pump();
    await tester.tap(find.byTooltip(l10n.toggle_negative));
    await tester.pump();

    await tester.tap(find.byType(DropdownButton<model.Page>));
    await tester.pumpAndSettle();
    await tester.tap(find.textContaining('P2', findRichText: true).last);
    await tester.pumpAndSettle();

    expect(reloadCalls, 1);
    expect(negativeCalls, 1);
    expect(changedPage?.name, 'P2');
    expect(showInfoCalls, 1);
  });

  testWidgets(
    'filter toggles stay disabled when selected page image is not ready',
    (tester) async {
      final source = _buildSource(permissionsReceived: true);
      final selectedPage = source.pages.first;
      final imageController = ImagePreviewController(6);
      addTearDown(imageController.dispose);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceToolbar(
            primarySource: source,
            selectedPage: selectedPage,
            localPageLoaded: {selectedPage.image: false},
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
            isBottom: false,
            dropdownWidth: 200,
            onChangeSelectedPage: (_) async {},
            onShowCommonInfo: () {},
            onReloadImage: () async {},
            onToggleNegative: () {},
            onToggleMonochrome: () {},
            onToggleShowWordSeparators: () {},
            onToggleShowStrongNumbers: () {},
            onToggleShowVerseNumbers: () {},
            onRemovePageSettings: () {},
            onOpenBrightnessContrastDialog: () {},
            onOpenReplaceColorDialog: () {},
            onSetMenuOpen: (_) {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final negativeButton = tester.widget<IconButton>(
        find.widgetWithIcon(IconButton, Icons.invert_colors),
      );
      final replaceColorButton = tester.widget<IconButton>(
        find.widgetWithIcon(IconButton, Icons.format_paint),
      );

      expect(negativeButton.onPressed, isNull);
      expect(replaceColorButton.onPressed, isNull);
    },
  );

  testWidgets(
    'bottom adaptive toolbar renders overflow actions when constrained',
    (tester) async {
      final source = _buildSource(permissionsReceived: true);
      final selectedPage = source.pages.first;
      final imageController = ImagePreviewController(6)
        ..setImageSize(const Size(800, 600), 800, 600);
      addTearDown(imageController.dispose);
      final zoom = ValueNotifier(
        const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
      );
      addTearDown(zoom.dispose);

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: SizedBox(
            width: 320,
            child: PrimarySourceToolbar(
              primarySource: source,
              selectedPage: selectedPage,
              localPageLoaded: {selectedPage.image: true},
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
              zoomStatusNotifier: zoom,
              imageController: imageController,
              isBottom: true,
              dropdownWidth: 220,
              onChangeSelectedPage: (_) async {},
              onShowCommonInfo: () {},
              onReloadImage: () async {},
              onToggleNegative: () {},
              onToggleMonochrome: () {},
              onToggleShowWordSeparators: () {},
              onToggleShowStrongNumbers: () {},
              onToggleShowVerseNumbers: () {},
              onRemovePageSettings: () {},
              onOpenBrightnessContrastDialog: () {},
              onOpenReplaceColorDialog: () {},
              onSetMenuOpen: (_) {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.more_vert), findsOneWidget);
    },
  );

  testWidgets(
    'ready image enables all rendering actions and dispatches callbacks',
    (tester) async {
      final source = _buildSource(permissionsReceived: true);
      final selectedPage = source.pages.first;
      final imageController = ImagePreviewController(6)
        ..setImageSize(const Size(800, 600), 800, 600);
      addTearDown(imageController.dispose);
      final zoom = ValueNotifier(
        const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
      );
      addTearDown(zoom.dispose);

      var monochromeCalls = 0;
      var brightnessCalls = 0;
      var replaceColorCalls = 0;
      var wordSepCalls = 0;
      var strongCalls = 0;
      var verseCalls = 0;
      var resetCalls = 0;

      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceToolbar(
            primarySource: source,
            selectedPage: selectedPage,
            localPageLoaded: {selectedPage.image: true},
            refreshError: false,
            isNegative: true,
            isMonochrome: true,
            brightness: 10,
            contrast: 110,
            selectedArea: const Rect.fromLTWH(1, 1, 2, 2),
            tolerance: 15,
            showWordSeparators: true,
            showStrongNumbers: true,
            showVerseNumbers: true,
            zoomStatusNotifier: zoom,
            imageController: imageController,
            isBottom: false,
            dropdownWidth: 220,
            onChangeSelectedPage: (_) async {},
            onShowCommonInfo: () {},
            onReloadImage: () async {},
            onToggleNegative: () {},
            onToggleMonochrome: () {
              monochromeCalls++;
            },
            onToggleShowWordSeparators: () {
              wordSepCalls++;
            },
            onToggleShowStrongNumbers: () {
              strongCalls++;
            },
            onToggleShowVerseNumbers: () {
              verseCalls++;
            },
            onRemovePageSettings: () {
              resetCalls++;
            },
            onOpenBrightnessContrastDialog: () {
              brightnessCalls++;
            },
            onOpenReplaceColorDialog: () {
              replaceColorCalls++;
            },
            onSetMenuOpen: (_) {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final context = tester.element(find.byType(PrimarySourceToolbar));
      final l10n = AppLocalizations.of(context)!;

      await tester.tap(find.byTooltip(l10n.toggle_monochrome));
      await tester.tap(find.byTooltip(l10n.brightness_contrast));
      await tester.tap(find.byTooltip(l10n.color_replacement));
      await tester.tap(find.byTooltip(l10n.toggle_show_word_separators));
      await tester.tap(find.byTooltip(l10n.toggle_show_strong_numbers));
      await tester.tap(find.byTooltip(l10n.toggle_show_verse_numbers));
      await tester.tap(find.byTooltip(l10n.page_settings_reset));
      await tester.pump();

      expect(monochromeCalls, 1);
      expect(brightnessCalls, 1);
      expect(replaceColorCalls, 1);
      expect(wordSepCalls, 1);
      expect(strongCalls, 1);
      expect(verseCalls, 1);
      expect(resetCalls, 1);
    },
  );

  testWidgets(
    'dropdown selection does not trigger source change when permissions are absent',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1600, 900));
      addTearDown(() {
        tester.binding.setSurfaceSize(null);
      });
      final source = _buildSource(permissionsReceived: false);
      final imageController = ImagePreviewController(6);
      addTearDown(imageController.dispose);
      final zoom = ValueNotifier(
        const ZoomStatus(canZoomIn: false, canZoomOut: false, canReset: false),
      );
      addTearDown(zoom.dispose);

      model.Page? changedPage;
      var showInfoCalls = 0;
      await tester.pumpWidget(
        buildLocalizedTestApp(
          child: PrimarySourceToolbar(
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
            showVerseNumbers: false,
            zoomStatusNotifier: zoom,
            imageController: imageController,
            isBottom: false,
            dropdownWidth: 200,
            onChangeSelectedPage: (newPage) async {
              changedPage = newPage;
            },
            onShowCommonInfo: () {
              showInfoCalls++;
            },
            onReloadImage: () async {},
            onToggleNegative: () {},
            onToggleMonochrome: () {},
            onToggleShowWordSeparators: () {},
            onToggleShowStrongNumbers: () {},
            onToggleShowVerseNumbers: () {},
            onRemovePageSettings: () {},
            onOpenBrightnessContrastDialog: () {},
            onOpenReplaceColorDialog: () {},
            onSetMenuOpen: (_) {},
          ),
        ),
      );
      await tester.pumpAndSettle();

      final dropdown = tester.widget<DropdownButton<model.Page>>(
        find.byType(DropdownButton<model.Page>),
      );
      dropdown.onChanged?.call(source.pages.last);
      await tester.pump();

      expect(changedPage, isNull);
      expect(showInfoCalls, 0);
    },
  );
}

PrimarySource _buildSource({required bool permissionsReceived}) {
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
    isMonochrome: false,
    pages: [
      model.Page(name: 'P1', content: 'C1', image: 'p1.png'),
      model.Page(name: 'P2', content: 'C2', image: 'p2.png'),
    ],
    attributes: const [],
    permissionsReceived: permissionsReceived,
  );
}

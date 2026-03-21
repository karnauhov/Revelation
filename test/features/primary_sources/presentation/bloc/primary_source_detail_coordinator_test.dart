import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_coordinator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/description_kind.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

import '../../../../test_harness/test_harness.dart';

void main() {
  test('select area callback is invoked only while mode is active', () {
    final bundle = _createBundle();
    addTearDown(bundle.dispose);

    Rect? callbackRect;
    bundle.coordinator.startSelectAreaMode((rect) {
      callbackRect = rect;
    });
    expect(bundle.coordinator.selectAreaMode, isTrue);

    final selectedRect = const Rect.fromLTWH(1, 2, 3, 4);
    bundle.coordinator.finishSelectAreaMode(selectedRect);

    expect(callbackRect, selectedRect);
    expect(bundle.coordinator.selectAreaMode, isFalse);

    callbackRect = null;
    bundle.coordinator.finishSelectAreaMode(const Rect.fromLTWH(4, 5, 6, 7));
    expect(callbackRect, isNull);
  });

  test('pipette callback is invoked only while mode is active', () {
    final bundle = _createBundle();
    addTearDown(bundle.dispose);

    Color? callbackColor;
    bundle.coordinator.startPipetteMode((color) {
      callbackColor = color;
    }, true);
    expect(bundle.coordinator.pipetteMode, isTrue);

    bundle.coordinator.finishPipetteMode(const Color(0xFFABCDEF));
    expect(callbackColor, const Color(0xFFABCDEF));
    expect(bundle.coordinator.pipetteMode, isFalse);

    callbackColor = null;
    bundle.coordinator.finishPipetteMode(const Color(0xFF010101));
    expect(callbackColor, isNull);
  });

  test(
    'changeSelectedPage delegates orchestration and updates selected page',
    () async {
      final bundle = _createBundle();
      addTearDown(bundle.dispose);

      final nextPage = bundle.source.pages[1];
      await bundle.coordinator.changeSelectedPage(nextPage);

      expect(bundle.coordinator.selectedPage, nextPage);
      expect(
        bundle.coordinator.imageName,
        '${bundle.source.hashCode}_${nextPage.image}',
      );
    },
  );

  test('dispose does not close injected cubits', () async {
    final bundle = _createBundle();

    bundle.coordinator.dispose();
    await Future<void>.delayed(Duration.zero);

    expect(bundle.imageCubit.isClosed, isFalse);
    expect(bundle.pageSettingsCubit.isClosed, isFalse);
    expect(bundle.descriptionCubit.isClosed, isFalse);
    expect(bundle.viewportCubit.isClosed, isFalse);
    expect(bundle.sessionCubit.isClosed, isFalse);

    await bundle.imageCubit.close();
    await bundle.pageSettingsCubit.close();
    await bundle.descriptionCubit.close();
    await bundle.viewportCubit.close();
    await bundle.sessionCubit.close();
  });

  testWidgets('coordinator exposes delegated state/actions as contracts', (
    tester,
  ) async {
    final context = await pumpLocalizedContext(tester);
    final l10n = AppLocalizations.of(context)!;
    final bundle = _createBundle();
    addTearDown(bundle.dispose);

    final page = bundle.source.pages.first;
    await bundle.coordinator.loadImage(page.image);

    expect(bundle.coordinator.primarySource, same(bundle.source));
    expect(bundle.coordinator.selectedPage, page);
    expect(bundle.coordinator.imageData, isNotNull);
    expect(bundle.coordinator.isLoading, isFalse);
    expect(bundle.coordinator.refreshError, isFalse);
    expect(bundle.coordinator.localPageLoaded[page.image], isTrue);
    expect(bundle.coordinator.maxTextureSize, greaterThanOrEqualTo(0));

    bundle.coordinator.toggleNegative();
    expect(bundle.coordinator.isNegative, isTrue);
    bundle.coordinator.toggleMonochrome();
    expect(bundle.coordinator.isMonochrome, isTrue);
    bundle.coordinator.applyBrightnessContrast(20, 120);
    expect(bundle.coordinator.brightness, 20);
    expect(bundle.coordinator.contrast, 120);
    bundle.coordinator.resetBrightnessContrast();
    expect(bundle.coordinator.brightness, 0);
    expect(bundle.coordinator.contrast, 100);

    bundle.coordinator.toggleShowWordSeparators();
    bundle.coordinator.toggleShowStrongNumbers();
    bundle.coordinator.toggleShowVerseNumbers();
    expect(bundle.coordinator.showWordSeparators, isTrue);
    expect(bundle.coordinator.showStrongNumbers, isTrue);
    expect(bundle.coordinator.showVerseNumbers, isFalse);

    bundle.coordinator.applyColorReplacement(
      const Rect.fromLTWH(1, 2, 3, 4),
      const Color(0xFF010203),
      const Color(0xFF040506),
      44,
    );
    expect(bundle.coordinator.selectedArea, const Rect.fromLTWH(1, 2, 3, 4));
    expect(bundle.coordinator.colorToReplace, const Color(0xFF010203));
    expect(bundle.coordinator.newColor, const Color(0xFF040506));
    expect(bundle.coordinator.tolerance, 44);
    bundle.coordinator.resetColorReplacement();
    expect(bundle.coordinator.selectedArea, isNull);
    expect(bundle.coordinator.tolerance, 0);

    bundle.coordinator.setMenuOpen(true);
    expect(bundle.coordinator.isMenuOpen, isTrue);
    bundle.coordinator.setMenuOpen(false);
    expect(bundle.coordinator.isMenuOpen, isFalse);

    bundle.coordinator.updateDescriptionContent(
      'custom',
      DescriptionKind.word,
      0,
    );
    expect(bundle.coordinator.descriptionContent, 'custom');
    expect(bundle.coordinator.currentDescriptionType, DescriptionKind.word);
    expect(bundle.coordinator.currentDescriptionNumber, 0);

    bundle.coordinator.showCommonInfo(l10n);
    expect(bundle.coordinator.currentDescriptionType, DescriptionKind.info);
    expect(bundle.coordinator.descriptionContent, l10n.click_for_info);

    expect(
      bundle.coordinator.navigateDescriptionSelection(l10n, forward: true),
      isFalse,
    );
    expect(bundle.coordinator.getGreekStrongPickerEntries(), isA<List>());
    bundle.coordinator.showInfoForStrongNumber(1, l10n);
    bundle.coordinator.showInfoForWord(0, l10n);
    bundle.coordinator.showInfoForVerse(0, l10n);

    bundle.coordinator.savePageSettings();
    bundle.coordinator.removePageSettings();

    expect(bundle.coordinator.scaleAndPositionRestored, isA<bool>());
    expect(bundle.coordinator.dx, isA<double>());
    expect(bundle.coordinator.dy, isA<double>());
    expect(bundle.coordinator.scale, isA<double>());
    expect(bundle.coordinator.savedX, isA<double>());
    expect(bundle.coordinator.savedY, isA<double>());
    expect(bundle.coordinator.savedScale, isA<double>());
    expect(bundle.coordinator.pageSettings, isA<String>());
  });

  test('dispose safely handles internally owned cubits', () async {
    final source = _buildSourceWithoutPages();
    final coordinator = PrimarySourceDetailCoordinator(
      PagesRepository(),
      primarySource: source,
    );

    coordinator.dispose();
    await Future<void>.delayed(Duration.zero);
  });
}

class _CoordinatorBundle {
  _CoordinatorBundle({
    required this.source,
    required this.coordinator,
    required this.imageCubit,
    required this.pageSettingsCubit,
    required this.descriptionCubit,
    required this.viewportCubit,
    required this.sessionCubit,
  });

  final PrimarySource source;
  final PrimarySourceDetailCoordinator coordinator;
  final PrimarySourceImageCubit imageCubit;
  final PrimarySourcePageSettingsCubit pageSettingsCubit;
  final PrimarySourceDescriptionCubit descriptionCubit;
  final PrimarySourceViewportCubit viewportCubit;
  final PrimarySourceSessionCubit sessionCubit;

  Future<void> dispose() async {
    coordinator.dispose();
    await Future<void>.delayed(Duration.zero);
    if (!imageCubit.isClosed) {
      await imageCubit.close();
    }
    if (!pageSettingsCubit.isClosed) {
      await pageSettingsCubit.close();
    }
    if (!descriptionCubit.isClosed) {
      await descriptionCubit.close();
    }
    if (!viewportCubit.isClosed) {
      await viewportCubit.close();
    }
    if (!sessionCubit.isClosed) {
      await sessionCubit.close();
    }
  }
}

_CoordinatorBundle _createBundle() {
  final source = _buildSource();
  final imageCubit = PrimarySourceImageCubit(
    source: source,
    isWeb: false,
    isMobileWeb: false,
    imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
      detectLocalPageAvailabilityImpl:
          ({required pages, required isWeb}) async => {
            'p1.png': true,
            'p2.png': true,
          },
      loadPageImageImpl:
          ({
            required page,
            required sourceHashCode,
            required isWeb,
            required isMobileWeb,
            required isReload,
            previousPageLoaded,
          }) async => PageImageLoadResult(
            contentAction: ImageContentAction.replace,
            imageData: Uint8List.fromList([1, 2, 3]),
            imageName: '${sourceHashCode}_$page',
            pageLoaded: true,
            refreshError: false,
          ),
    ),
    autoInitialize: false,
  );
  final pageSettingsCubit = PrimarySourcePageSettingsCubit(
    _FakePageSettingsOrchestrator(),
  );
  final descriptionCubit = PrimarySourceDescriptionCubit();
  final viewportCubit = PrimarySourceViewportCubit();
  final sessionCubit = PrimarySourceSessionCubit(source: source);
  final coordinator = PrimarySourceDetailCoordinator(
    PagesRepository(),
    primarySource: source,
    imageCubit: imageCubit,
    pageSettingsCubit: pageSettingsCubit,
    descriptionCubit: descriptionCubit,
    viewportCubit: viewportCubit,
    sessionCubit: sessionCubit,
  );

  return _CoordinatorBundle(
    source: source,
    coordinator: coordinator,
    imageCubit: imageCubit,
    pageSettingsCubit: pageSettingsCubit,
    descriptionCubit: descriptionCubit,
    viewportCubit: viewportCubit,
    sessionCubit: sessionCubit,
  );
}

class _FakeImageLoadingOrchestrator
    extends PrimarySourceImageLoadingOrchestrator {
  _FakeImageLoadingOrchestrator({
    required this.detectLocalPageAvailabilityImpl,
    required this.loadPageImageImpl,
  });

  final Future<Map<String, bool?>> Function({
    required List<model.Page> pages,
    required bool isWeb,
  })
  detectLocalPageAvailabilityImpl;

  final Future<PageImageLoadResult> Function({
    required String page,
    required int sourceHashCode,
    required bool isWeb,
    required bool isMobileWeb,
    required bool isReload,
    bool? previousPageLoaded,
  })
  loadPageImageImpl;

  @override
  Future<Map<String, bool?>> detectLocalPageAvailability({
    required List<model.Page> pages,
    required bool isWeb,
  }) {
    return detectLocalPageAvailabilityImpl(pages: pages, isWeb: isWeb);
  }

  @override
  Future<PageImageLoadResult> loadPageImage({
    required String page,
    required int sourceHashCode,
    required bool isWeb,
    required bool isMobileWeb,
    required bool isReload,
    bool? previousPageLoaded,
  }) {
    return loadPageImageImpl(
      page: page,
      sourceHashCode: sourceHashCode,
      isWeb: isWeb,
      isMobileWeb: isMobileWeb,
      isReload: isReload,
      previousPageLoaded: previousPageLoaded,
    );
  }
}

class _FakePageSettingsOrchestrator
    extends PrimarySourcePageSettingsOrchestrator {
  _FakePageSettingsOrchestrator() : super(PagesRepository());

  @override
  Future<PageSettingsState> loadSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
  }) async {
    return const PageSettingsState(
      rawSettings: '',
      posX: 0,
      posY: 0,
      scale: 1,
      isNegative: false,
      isMonochrome: false,
      brightness: 0,
      contrast: 100,
      showWordSeparators: false,
      showStrongNumbers: false,
      showVerseNumbers: true,
    );
  }
}

PrimarySource _buildSource() {
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
    permissionsReceived: true,
  );
}

PrimarySource _buildSourceWithoutPages() {
  return PrimarySource(
    id: 'source-empty',
    title: 'Source empty',
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
    pages: const [],
    attributes: const [],
    permissionsReceived: false,
  );
}

import 'dart:async';
import 'dart:typed_data';

import 'package:fake_async/fake_async.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';
import 'package:talker_flutter/talker_flutter.dart';

import '../../../../test_harness/test_harness.dart';

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

  test('loadImage updates image/session through orchestration cubit', () async {
    final source = _buildSource();
    final page = source.pages.first;
    final imageBytes = Uint8List.fromList([1, 2, 3]);

    final imageCubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
        detectLocalPageAvailabilityImpl:
            ({required pages, required isWeb}) async => <String, bool?>{
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
              imageData: imageBytes,
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
    final sessionCubit = PrimarySourceSessionCubit(source: source);
    final viewportCubit = PrimarySourceViewportCubit();
    final cubit = PrimarySourceDetailOrchestrationCubit(
      source: source,
      imageCubit: imageCubit,
      pageSettingsCubit: pageSettingsCubit,
      descriptionCubit: descriptionCubit,
      sessionCubit: sessionCubit,
      viewportCubit: viewportCubit,
    );
    addTearDown(cubit.close);
    addTearDown(imageCubit.close);
    addTearDown(pageSettingsCubit.close);
    addTearDown(descriptionCubit.close);
    addTearDown(sessionCubit.close);
    addTearDown(viewportCubit.close);

    sessionCubit.setSelectedPage(page);
    await cubit.loadImage(page.image);

    expect(imageCubit.state.imageData, imageBytes);
    expect(sessionCubit.state.imageName, '${source.hashCode}_${page.image}');
  });

  test(
    'changeSelectedPage(null) resets session/viewport/page-settings',
    () async {
      final source = _buildSource();
      final imageCubit = PrimarySourceImageCubit(
        source: source,
        isWeb: false,
        isMobileWeb: false,
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
          detectLocalPageAvailabilityImpl:
              ({required pages, required isWeb}) async => <String, bool?>{
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
              }) async => const PageImageLoadResult(
                contentAction: ImageContentAction.keep,
                imageData: null,
                imageName: '',
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
      final sessionCubit = PrimarySourceSessionCubit(source: source);
      final viewportCubit = PrimarySourceViewportCubit();
      final cubit = PrimarySourceDetailOrchestrationCubit(
        source: source,
        imageCubit: imageCubit,
        pageSettingsCubit: pageSettingsCubit,
        descriptionCubit: descriptionCubit,
        sessionCubit: sessionCubit,
        viewportCubit: viewportCubit,
      );
      addTearDown(cubit.close);
      addTearDown(imageCubit.close);
      addTearDown(pageSettingsCubit.close);
      addTearDown(descriptionCubit.close);
      addTearDown(sessionCubit.close);
      addTearDown(viewportCubit.close);

      sessionCubit.setSelectedPage(source.pages.first);
      viewportCubit.applyColorReplacement(
        selectedArea: const Rect.fromLTWH(1, 2, 3, 4),
        colorToReplace: const Color(0xFF000000),
        newColor: const Color(0xFFFFFFFF),
        tolerance: 25,
      );
      pageSettingsCubit.toggleNegative();

      await cubit.changeSelectedPage(null);

      expect(sessionCubit.state.selectedPage, isNull);
      expect(viewportCubit.state.selectedArea, isNull);
      expect(viewportCubit.state.scaleAndPositionRestored, isTrue);
      expect(pageSettingsCubit.state.isNegative, isFalse);
      expect(pageSettingsCubit.state.brightness, 0);
      expect(pageSettingsCubit.state.contrast, 100);
    },
  );

  test('restorePositionAndScale applies saved transform after debounce', () {
    final source = _buildSource();
    final imageCubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
        detectLocalPageAvailabilityImpl:
            ({required pages, required isWeb}) async => <String, bool?>{
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
            }) async => const PageImageLoadResult(
              contentAction: ImageContentAction.keep,
              imageData: null,
              imageName: '',
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
    final sessionCubit = PrimarySourceSessionCubit(source: source);
    final viewportCubit = PrimarySourceViewportCubit();
    final cubit = PrimarySourceDetailOrchestrationCubit(
      source: source,
      imageCubit: imageCubit,
      pageSettingsCubit: pageSettingsCubit,
      descriptionCubit: descriptionCubit,
      sessionCubit: sessionCubit,
      viewportCubit: viewportCubit,
    );
    addTearDown(cubit.close);
    addTearDown(imageCubit.close);
    addTearDown(pageSettingsCubit.close);
    addTearDown(descriptionCubit.close);
    addTearDown(sessionCubit.close);
    addTearDown(viewportCubit.close);

    viewportCubit.applyViewportSettings(
      const PageSettingsState(
        rawSettings: 'raw',
        posX: 17,
        posY: 23,
        scale: 1.4,
        isNegative: false,
        isMonochrome: false,
        brightness: 0,
        contrast: 100,
        showWordSeparators: false,
        showStrongNumbers: false,
        showVerseNumbers: true,
      ),
    );
    viewportCubit.setScaleAndPositionRestored(false);

    fakeAsync((async) {
      cubit.restorePositionAndScale();
      async.elapse(const Duration(milliseconds: 999));
      expect(viewportCubit.state.scaleAndPositionRestored, isFalse);
      async.elapse(const Duration(milliseconds: 1));
    });

    final matrix = cubit.imageController.transformationController.value;
    expect(viewportCubit.state.scaleAndPositionRestored, isTrue);
    expect(matrix.storage[12], closeTo(17, 0.001));
    expect(matrix.storage[13], closeTo(23, 0.001));
  });

  test(
    'rapid transform updates trigger one debounced save side effect',
    () async {
      final source = _buildSource();
      final page = source.pages.first;
      final imageBytes = Uint8List.fromList([5, 6, 7]);

      final imageCubit = PrimarySourceImageCubit(
        source: source,
        isWeb: false,
        isMobileWeb: false,
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
          detectLocalPageAvailabilityImpl:
              ({required pages, required isWeb}) async => <String, bool?>{
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
                imageData: imageBytes,
                imageName: '${sourceHashCode}_$page',
                pageLoaded: true,
                refreshError: false,
              ),
        ),
        autoInitialize: false,
      );
      final pageSettingsOrchestrator = _FakePageSettingsOrchestrator();
      final pageSettingsCubit = PrimarySourcePageSettingsCubit(
        pageSettingsOrchestrator,
      );
      final descriptionCubit = PrimarySourceDescriptionCubit();
      final sessionCubit = PrimarySourceSessionCubit(source: source);
      final viewportCubit = PrimarySourceViewportCubit();
      final cubit = PrimarySourceDetailOrchestrationCubit(
        source: source,
        imageCubit: imageCubit,
        pageSettingsCubit: pageSettingsCubit,
        descriptionCubit: descriptionCubit,
        sessionCubit: sessionCubit,
        viewportCubit: viewportCubit,
      );
      addTearDown(cubit.close);
      addTearDown(imageCubit.close);
      addTearDown(pageSettingsCubit.close);
      addTearDown(descriptionCubit.close);
      addTearDown(sessionCubit.close);
      addTearDown(viewportCubit.close);

      sessionCubit.setSelectedPage(page);
      await cubit.loadImage(page.image);
      viewportCubit.setScaleAndPositionRestored(true);

      fakeAsync((async) {
        cubit.imageController.transformationController.value =
            Matrix4.identity()..setTranslationRaw(10.0, 0.0, 0.0);
        async.elapse(const Duration(milliseconds: 300));
        cubit.imageController.transformationController.value =
            Matrix4.identity()..setTranslationRaw(20.0, 0.0, 0.0);
        async.elapse(const Duration(milliseconds: 300));
        cubit.imageController.transformationController.value =
            Matrix4.identity()..setTranslationRaw(30.0, 0.0, 0.0);

        expect(pageSettingsOrchestrator.saveCallCount, 0);
        async.elapse(const Duration(milliseconds: 999));
        expect(pageSettingsOrchestrator.saveCallCount, 0);
        async.elapse(const Duration(milliseconds: 1));
        expect(pageSettingsOrchestrator.saveCallCount, 1);
      });
    },
  );

  test(
    'latest image load request wins when requests complete out of order',
    () async {
      final source = _buildSource();
      final page = source.pages.first;
      var callIndex = 0;
      final imageCubit = PrimarySourceImageCubit(
        source: source,
        isWeb: false,
        isMobileWeb: false,
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
          detectLocalPageAvailabilityImpl:
              ({required pages, required isWeb}) async => <String, bool?>{
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
              }) async {
                callIndex++;
                if (callIndex == 1) {
                  await Future<void>.delayed(const Duration(milliseconds: 60));
                  return PageImageLoadResult(
                    contentAction: ImageContentAction.replace,
                    imageData: Uint8List.fromList([1, 1, 1]),
                    imageName: '${sourceHashCode}_$page',
                    pageLoaded: true,
                    refreshError: false,
                  );
                }
                return PageImageLoadResult(
                  contentAction: ImageContentAction.replace,
                  imageData: Uint8List.fromList([2, 2, 2]),
                  imageName: '${sourceHashCode}_$page',
                  pageLoaded: true,
                  refreshError: false,
                );
              },
        ),
        autoInitialize: false,
      );
      final pageSettingsCubit = PrimarySourcePageSettingsCubit(
        _FakePageSettingsOrchestrator(),
      );
      final descriptionCubit = PrimarySourceDescriptionCubit();
      final sessionCubit = PrimarySourceSessionCubit(source: source);
      final viewportCubit = PrimarySourceViewportCubit();
      final cubit = PrimarySourceDetailOrchestrationCubit(
        source: source,
        imageCubit: imageCubit,
        pageSettingsCubit: pageSettingsCubit,
        descriptionCubit: descriptionCubit,
        sessionCubit: sessionCubit,
        viewportCubit: viewportCubit,
      );
      addTearDown(cubit.close);
      addTearDown(imageCubit.close);
      addTearDown(pageSettingsCubit.close);
      addTearDown(descriptionCubit.close);
      addTearDown(sessionCubit.close);
      addTearDown(viewportCubit.close);

      sessionCubit.setSelectedPage(page);

      unawaited(cubit.loadImage(page.image));
      await Future<void>.delayed(const Duration(milliseconds: 1));
      final secondFuture = cubit.loadImage(page.image, isReload: true);
      await secondFuture;
      await Future<void>.delayed(const Duration(milliseconds: 120));

      expect(imageCubit.state.imageData, equals(<int>[2, 2, 2]));
      expect(sessionCubit.state.imageName, '${source.hashCode}_${page.image}');
    },
  );

  test(
    'loadImage keeps session image name empty when loading throws',
    () async {
      final source = _buildSource();
      final page = source.pages.first;
      final imageCubit = PrimarySourceImageCubit(
        source: source,
        isWeb: false,
        isMobileWeb: false,
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
          detectLocalPageAvailabilityImpl:
              ({required pages, required isWeb}) async => <String, bool?>{
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
              }) async {
                throw StateError('forced');
              },
        ),
        autoInitialize: false,
      );
      final pageSettingsCubit = PrimarySourcePageSettingsCubit(
        _FakePageSettingsOrchestrator(),
      );
      final descriptionCubit = PrimarySourceDescriptionCubit();
      final sessionCubit = PrimarySourceSessionCubit(source: source);
      final viewportCubit = PrimarySourceViewportCubit();
      final cubit = PrimarySourceDetailOrchestrationCubit(
        source: source,
        imageCubit: imageCubit,
        pageSettingsCubit: pageSettingsCubit,
        descriptionCubit: descriptionCubit,
        sessionCubit: sessionCubit,
        viewportCubit: viewportCubit,
      );
      addTearDown(cubit.close);
      addTearDown(imageCubit.close);
      addTearDown(pageSettingsCubit.close);
      addTearDown(descriptionCubit.close);
      addTearDown(sessionCubit.close);
      addTearDown(viewportCubit.close);

      sessionCubit.setSelectedPage(page);
      await cubit.loadImage(page.image);

      expect(sessionCubit.state.imageName, isEmpty);
    },
  );

  test('removePageSettings resets viewport controls and transform', () async {
    final source = _buildSource();
    final imageCubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
        detectLocalPageAvailabilityImpl:
            ({required pages, required isWeb}) async => <String, bool?>{
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
            }) async => const PageImageLoadResult(
              contentAction: ImageContentAction.keep,
              imageData: null,
              imageName: '',
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
    final sessionCubit = PrimarySourceSessionCubit(source: source);
    final viewportCubit = PrimarySourceViewportCubit();
    final cubit = PrimarySourceDetailOrchestrationCubit(
      source: source,
      imageCubit: imageCubit,
      pageSettingsCubit: pageSettingsCubit,
      descriptionCubit: descriptionCubit,
      sessionCubit: sessionCubit,
      viewportCubit: viewportCubit,
    );
    addTearDown(cubit.close);
    addTearDown(imageCubit.close);
    addTearDown(pageSettingsCubit.close);
    addTearDown(descriptionCubit.close);
    addTearDown(sessionCubit.close);
    addTearDown(viewportCubit.close);

    viewportCubit.applyColorReplacement(
      selectedArea: const Rect.fromLTWH(1, 1, 4, 4),
      colorToReplace: const Color(0xFF000000),
      newColor: const Color(0xFF00FF00),
      tolerance: 44,
    );
    cubit.imageController.setImageSize(const Size(100, 100), 300, 300);
    cubit.imageController.setTransformParams(10, 20, 2);

    cubit.removePageSettings();

    expect(viewportCubit.state.selectedArea, isNull);
    expect(viewportCubit.state.tolerance, 0);
    final matrix = cubit.imageController.transformationController.value;
    expect(
      matrix.getMaxScaleOnAxis(),
      closeTo(cubit.imageController.minScale, 0.001),
    );
  });

  test('setMenuOpen delegates to session cubit', () {
    final source = _buildSource();
    final imageCubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
        detectLocalPageAvailabilityImpl:
            ({required pages, required isWeb}) async => <String, bool?>{},
        loadPageImageImpl:
            ({
              required page,
              required sourceHashCode,
              required isWeb,
              required isMobileWeb,
              required isReload,
              previousPageLoaded,
            }) async => const PageImageLoadResult(
              contentAction: ImageContentAction.keep,
              imageData: null,
              imageName: '',
              pageLoaded: false,
              refreshError: false,
            ),
      ),
      autoInitialize: false,
    );
    final pageSettingsCubit = PrimarySourcePageSettingsCubit(
      _FakePageSettingsOrchestrator(),
    );
    final descriptionCubit = PrimarySourceDescriptionCubit();
    final sessionCubit = PrimarySourceSessionCubit(source: source);
    final viewportCubit = PrimarySourceViewportCubit();
    final cubit = PrimarySourceDetailOrchestrationCubit(
      source: source,
      imageCubit: imageCubit,
      pageSettingsCubit: pageSettingsCubit,
      descriptionCubit: descriptionCubit,
      sessionCubit: sessionCubit,
      viewportCubit: viewportCubit,
    );
    addTearDown(cubit.close);
    addTearDown(imageCubit.close);
    addTearDown(pageSettingsCubit.close);
    addTearDown(descriptionCubit.close);
    addTearDown(sessionCubit.close);
    addTearDown(viewportCubit.close);

    cubit.setMenuOpen(true);
    expect(sessionCubit.state.isMenuOpen, isTrue);
    cubit.setMenuOpen(false);
    expect(sessionCubit.state.isMenuOpen, isFalse);
  });

  testWidgets(
    'settings, viewport and description delegates preserve contract',
    (tester) async {
      final context = await pumpLocalizedContext(tester);
      final l10n = AppLocalizations.of(context)!;
      final source = _buildSource();
      final imageCubit = PrimarySourceImageCubit(
        source: source,
        isWeb: false,
        isMobileWeb: false,
        imageLoadingOrchestrator: _FakeImageLoadingOrchestrator(
          detectLocalPageAvailabilityImpl:
              ({required pages, required isWeb}) async => <String, bool?>{
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
              }) async => const PageImageLoadResult(
                contentAction: ImageContentAction.keep,
                imageData: null,
                imageName: '',
                pageLoaded: true,
                refreshError: false,
              ),
        ),
        autoInitialize: false,
      );
      final pageSettingsOrchestrator = _FakePageSettingsOrchestrator();
      final pageSettingsCubit = PrimarySourcePageSettingsCubit(
        pageSettingsOrchestrator,
      );
      final descriptionCubit = PrimarySourceDescriptionCubit();
      final sessionCubit = PrimarySourceSessionCubit(source: source);
      final viewportCubit = PrimarySourceViewportCubit();
      final cubit = PrimarySourceDetailOrchestrationCubit(
        source: source,
        imageCubit: imageCubit,
        pageSettingsCubit: pageSettingsCubit,
        descriptionCubit: descriptionCubit,
        sessionCubit: sessionCubit,
        viewportCubit: viewportCubit,
      );
      addTearDown(cubit.close);
      addTearDown(imageCubit.close);
      addTearDown(pageSettingsCubit.close);
      addTearDown(descriptionCubit.close);
      addTearDown(sessionCubit.close);
      addTearDown(viewportCubit.close);

      sessionCubit.setSelectedPage(source.pages.first);

      cubit.toggleNegative();
      cubit.toggleMonochrome();
      cubit.applyBrightnessContrast(15, 120);
      cubit.resetBrightnessContrast();
      cubit.toggleShowWordSeparators();
      cubit.toggleShowStrongNumbers();
      cubit.toggleShowVerseNumbers();
      expect(pageSettingsOrchestrator.saveCallCount, greaterThan(0));

      cubit.startSelectAreaMode();
      expect(viewportCubit.state.selectAreaMode, isTrue);
      cubit.finishSelectAreaMode(const Rect.fromLTWH(1, 2, 3, 4));
      expect(viewportCubit.state.selectAreaMode, isFalse);
      expect(viewportCubit.state.selectedArea, const Rect.fromLTWH(1, 2, 3, 4));

      cubit.startPipetteMode(isColorToReplace: true);
      expect(viewportCubit.state.pipetteMode, isTrue);
      cubit.finishPipetteMode(const Color(0xFF123456));
      expect(viewportCubit.state.pipetteMode, isFalse);
      expect(viewportCubit.state.colorToReplace, const Color(0xFF123456));

      cubit.applyColorReplacement(
        selectedArea: const Rect.fromLTWH(3, 4, 5, 6),
        colorToReplace: const Color(0xFF010203),
        newColor: const Color(0xFF040506),
        tolerance: 77,
      );
      expect(viewportCubit.state.selectedArea, const Rect.fromLTWH(3, 4, 5, 6));
      expect(viewportCubit.state.newColor, const Color(0xFF040506));
      cubit.resetColorReplacement();
      expect(viewportCubit.state.selectedArea, isNull);
      expect(viewportCubit.state.tolerance, 0);

      cubit.setMenuOpen(true);
      expect(sessionCubit.state.isMenuOpen, isTrue);
      cubit.setMenuOpen(false);
      expect(sessionCubit.state.isMenuOpen, isFalse);

      cubit.updateDescriptionContent(
        content: 'desc',
        type: descriptionCubit.state.currentType,
        number: 0,
      );
      expect(descriptionCubit.state.content, 'desc');
      cubit.showCommonInfo(l10n);
      expect(descriptionCubit.state.content, l10n.click_for_info);
      expect(cubit.navigateDescriptionSelection(l10n, forward: true), isFalse);
      expect(cubit.getGreekStrongPickerEntries(), isA<List>());
      expect(
        cubit.showInfoForStrongNumber(strongNumber: 1, localizations: l10n),
        isA<bool>(),
      );
      expect(cubit.showInfoForWord(wordIndex: 0, localizations: l10n), isFalse);
      expect(
        cubit.showInfoForVerse(verseIndex: 0, localizations: l10n),
        isFalse,
      );

      cubit.savePageSettings();
      expect(pageSettingsOrchestrator.saveCallCount, greaterThan(1));
    },
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

  int saveCallCount = 0;

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

  @override
  String saveSettingsForPage({
    required PrimarySource source,
    required model.Page? selectedPage,
    required bool scaleAndPositionRestored,
    required double posX,
    required double posY,
    required double scale,
    required bool isNegative,
    required bool isMonochrome,
    required double brightness,
    required double contrast,
    required bool showWordSeparators,
    required bool showStrongNumbers,
    required bool showVerseNumbers,
  }) {
    saveCallCount++;
    return 'saved-raw';
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
    permissionsReceived: false,
  );
}

import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/page_settings_orchestrator.dart';
import 'package:revelation/features/primary_sources/data/repositories/pages_repository.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_description_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_detail_orchestration_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_page_settings_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_session_cubit.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_viewport_cubit.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

void main() {
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

  test(
    'restorePositionAndScale applies saved transform after debounce',
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

      cubit.restorePositionAndScale();
      await Future<void>.delayed(const Duration(milliseconds: 1100));

      final matrix = cubit.imageController.transformationController.value;
      expect(viewportCubit.state.scaleAndPositionRestored, isTrue);
      expect(matrix.storage[12], closeTo(17, 0.001));
      expect(matrix.storage[13], closeTo(23, 0.001));
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
    link1Title: '',
    link1Url: '',
    link2Title: '',
    link2Url: '',
    link3Title: '',
    link3Url: '',
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

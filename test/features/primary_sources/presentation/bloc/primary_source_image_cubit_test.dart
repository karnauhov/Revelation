import 'dart:async';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/features/primary_sources/application/orchestrators/image_loading_orchestrator.dart';
import 'package:revelation/features/primary_sources/presentation/bloc/primary_source_image_cubit.dart';
import 'package:revelation/shared/models/page.dart' as model;
import 'package:revelation/shared/models/primary_source.dart';

void main() {
  test('refreshLocalPageAvailability updates local page map', () async {
    final source = _buildSource(
      pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
      permissionsReceived: true,
    );
    final orchestrator = _FakeImageLoadingOrchestrator(
      detectLocalPageAvailabilityImpl:
          ({required pages, required isWeb}) async {
            return {'p1.png': true};
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
            return const PageImageLoadResult(
              contentAction: ImageContentAction.keep,
              imageData: null,
              imageName: '',
              pageLoaded: true,
              refreshError: false,
            );
          },
    );

    final cubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: orchestrator,
      autoInitialize: false,
    );
    addTearDown(cubit.close);

    await cubit.refreshLocalPageAvailability();

    expect(cubit.state.localPageLoaded['p1.png'], isTrue);
  });

  test('loadImage replaces image data and updates loading flags', () async {
    final bytes = Uint8List.fromList([1, 2, 3, 4]);
    final source = _buildSource(
      pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
      permissionsReceived: true,
    );
    final orchestrator = _FakeImageLoadingOrchestrator(
      detectLocalPageAvailabilityImpl:
          ({required pages, required isWeb}) async {
            return {'p1.png': false};
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
            return PageImageLoadResult(
              contentAction: ImageContentAction.replace,
              imageData: bytes,
              imageName: '${sourceHashCode}_$page',
              pageLoaded: true,
              refreshError: false,
            );
          },
    );

    final cubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: orchestrator,
      autoInitialize: false,
    );
    addTearDown(cubit.close);

    await cubit.loadImage(page: 'p1.png', sourceHashCode: 77);

    expect(cubit.state.isLoading, isFalse);
    expect(cubit.state.refreshError, isFalse);
    expect(cubit.state.localPageLoaded['p1.png'], isTrue);
    expect(cubit.state.imageData, bytes);
  });

  test('loadImage keep action preserves existing image data', () async {
    final firstBytes = Uint8List.fromList([9, 8, 7]);
    final source = _buildSource(
      pages: [model.Page(name: 'P1', content: 'C1', image: 'p1.png')],
      permissionsReceived: true,
    );
    final completer = Completer<PageImageLoadResult>();
    var callCount = 0;
    final orchestrator = _FakeImageLoadingOrchestrator(
      detectLocalPageAvailabilityImpl:
          ({required pages, required isWeb}) async {
            return {'p1.png': true};
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
            callCount++;
            if (callCount == 1) {
              return PageImageLoadResult(
                contentAction: ImageContentAction.replace,
                imageData: firstBytes,
                imageName: '${sourceHashCode}_$page',
                pageLoaded: true,
                refreshError: false,
              );
            }
            return completer.future;
          },
    );

    final cubit = PrimarySourceImageCubit(
      source: source,
      isWeb: false,
      isMobileWeb: false,
      imageLoadingOrchestrator: orchestrator,
      autoInitialize: false,
    );
    addTearDown(cubit.close);

    await cubit.loadImage(page: 'p1.png', sourceHashCode: 11);
    final firstLoadedBytes = cubit.state.imageData;

    unawaited(
      cubit.loadImage(page: 'p1.png', sourceHashCode: 11, isReload: true),
    );
    completer.complete(
      const PageImageLoadResult(
        contentAction: ImageContentAction.keep,
        imageData: null,
        imageName: '',
        pageLoaded: true,
        refreshError: true,
      ),
    );
    await Future<void>.delayed(Duration.zero);
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.imageData, firstLoadedBytes);
    expect(cubit.state.refreshError, isTrue);
  });
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

PrimarySource _buildSource({
  required List<model.Page> pages,
  required bool permissionsReceived,
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
    maxScale: 1,
    isMonochrome: false,
    pages: pages,
    attributes: const [],
    permissionsReceived: permissionsReceived,
  );
}

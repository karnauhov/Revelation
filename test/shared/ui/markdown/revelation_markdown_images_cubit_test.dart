import 'dart:async';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_images_cubit.dart';

void main() {
  test('preloads markdown images and updates completion counters', () async {
    final loader = _FakeMarkdownImageLoader(
      resultsByCacheKey: <String, MarkdownImageLoadResult>{
        'databaseResource:seal': MarkdownImageLoadResult.success(
          bytes: Uint8List.fromList(<int>[1, 2, 3]),
          mimeType: 'image/png',
        ),
        'network:https://example.com/two.png':
            const MarkdownImageLoadResult.failure(),
      },
    );
    final cubit = RevelationMarkdownImagesCubit(imageLoader: loader);
    addTearDown(cubit.close);

    await cubit.setMarkdown(
      '![One](dbres:seal)\n'
      '![Two](https://example.com/two.png)',
    );

    expect(cubit.state.totalCount, 2);
    expect(cubit.state.completedCount, 2);
    expect(cubit.state.failedCount, 1);
    expect(cubit.state.hasPreload, isTrue);
    expect(cubit.state.isPreloadActive, isFalse);
  });

  test('ignores stale image completion from older markdown load', () async {
    final loader = _ControllableMarkdownImageLoader();
    final cubit = RevelationMarkdownImagesCubit(imageLoader: loader);
    addTearDown(cubit.close);

    final firstLoad = cubit.setMarkdown('![EN](dbres:en-image)');
    await _flushAsync();
    final secondLoad = cubit.setMarkdown('![RU](dbres:ru-image)');
    await _flushAsync();

    loader.complete(
      'databaseResource:ru-image',
      MarkdownImageLoadResult.success(
        bytes: Uint8List.fromList(<int>[7]),
        mimeType: 'image/png',
      ),
    );
    await secondLoad;
    await _flushAsync();

    loader.complete(
      'databaseResource:en-image',
      MarkdownImageLoadResult.success(
        bytes: Uint8List.fromList(<int>[9]),
        mimeType: 'image/png',
      ),
    );
    await firstLoad;
    await _flushAsync();

    expect(cubit.state.images.keys, contains('databaseResource:ru-image'));
    expect(
      cubit.state.images.keys,
      isNot(contains('databaseResource:en-image')),
    );
  });

  test('ignores image completion after cubit is closed', () async {
    final loader = _ControllableMarkdownImageLoader();
    final cubit = RevelationMarkdownImagesCubit(imageLoader: loader);

    final loadFuture = cubit.setMarkdown('![Late](dbres:late-image)');
    await _flushAsync();
    expect(cubit.state.totalCount, 1);

    await cubit.close();
    loader.complete(
      'databaseResource:late-image',
      MarkdownImageLoadResult.success(
        bytes: Uint8List.fromList(<int>[5]),
        mimeType: 'image/png',
      ),
    );
    await loadFuture;

    expect(cubit.isClosed, isTrue);
  });
}

Future<void> _flushAsync() async {
  await Future<void>.delayed(Duration.zero);
  await Future<void>.delayed(Duration.zero);
}

class _FakeMarkdownImageLoader implements MarkdownImageLoader {
  _FakeMarkdownImageLoader({
    this.resultsByCacheKey = const <String, MarkdownImageLoadResult>{},
  });

  final Map<String, MarkdownImageLoadResult> resultsByCacheKey;

  @override
  Future<MarkdownImageLoadResult> loadImage(
    MarkdownImageRequest request,
  ) async {
    return resultsByCacheKey[request.cacheKey] ??
        const MarkdownImageLoadResult.failure();
  }
}

class _ControllableMarkdownImageLoader implements MarkdownImageLoader {
  final Map<String, Completer<MarkdownImageLoadResult>> _requests =
      <String, Completer<MarkdownImageLoadResult>>{};

  @override
  Future<MarkdownImageLoadResult> loadImage(MarkdownImageRequest request) {
    return _requests
        .putIfAbsent(
          request.cacheKey,
          () => Completer<MarkdownImageLoadResult>(),
        )
        .future;
  }

  void complete(String cacheKey, MarkdownImageLoadResult result) {
    final completer = _requests.putIfAbsent(
      cacheKey,
      () => Completer<MarkdownImageLoadResult>(),
    );
    if (!completer.isCompleted) {
      completer.complete(result);
    }
  }
}

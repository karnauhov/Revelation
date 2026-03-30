import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/topics/application/orchestrators/topic_markdown_image_orchestrator.dart';
import 'package:revelation/features/topics/data/models/topic_info.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/infra/db/common/db_common.dart';
import 'package:revelation/infra/db/data_sources/topics_data_source.dart';
import 'package:revelation/infra/db/localized/db_localized.dart';
import 'package:revelation/infra/remote/image/external_image_download_client.dart';
import 'package:revelation/infra/storage/markdown_image_local_store.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';

void main() {
  test('collectAsyncImages keeps unique async sources and ignores assets', () {
    final orchestrator = TopicMarkdownImageOrchestrator(
      topicsRepository: _FakeTopicsRepository(),
      localStore: _FakeMarkdownImageLocalStore(),
      externalImageDownloadClient: _FakeExternalImageDownloadClient(),
      supabaseObjectDownloader: (_, __) async => null,
    );

    const markdown = '''
![One](dbres:seal)
![One duplicate](dbres:seal)
![Two](https://example.com/dragon.png)
![Three](supabase:media/visions/lamp.svg)
![Asset](resource:assets/images/lamb.png)
''';

    final images = orchestrator.collectAsyncImages(markdown);

    expect(images.map((image) => image.cacheKey), <String>[
      RevelationMarkdownImageSource.parse('dbres:seal').cacheKey,
      RevelationMarkdownImageSource.parse(
        'https://example.com/dragon.png',
      ).cacheKey,
      RevelationMarkdownImageSource.parse(
        'supabase:media/visions/lamp.svg',
      ).cacheKey,
    ]);
  });

  test(
    'loadImage caches downloaded network images in the local store',
    () async {
      final store = _FakeMarkdownImageLocalStore();
      final client = _FakeExternalImageDownloadClient(
        bytesByUri: <String, Uint8List>{
          'https://example.com/image.png': Uint8List.fromList(<int>[1, 2, 3]),
        },
      );
      final orchestrator = TopicMarkdownImageOrchestrator(
        topicsRepository: _FakeTopicsRepository(),
        localStore: store,
        externalImageDownloadClient: client,
        supabaseObjectDownloader: (_, __) async => null,
      );
      final image = RevelationMarkdownImageData(
        source: RevelationMarkdownImageSource.parse(
          'https://example.com/image.png',
        ),
        alt: 'Example',
        alignment: RevelationMarkdownImageAlignment.center,
        isBlockImage: false,
      );

      final first = await orchestrator.loadImage(image);
      final second = await orchestrator.loadImage(image);

      expect(first.isSuccess, isTrue);
      expect(second.isSuccess, isTrue);
      expect(client.requestedUris, <String>['https://example.com/image.png']);
      expect(
        store.bytesByRelativePath['external/example.com/image.png'],
        orderedEquals(Uint8List.fromList(<int>[1, 2, 3])),
      );
    },
  );

  test(
    'loadImage stores Supabase images as readable files under images',
    () async {
      final store = _FakeMarkdownImageLocalStore();
      final orchestrator = TopicMarkdownImageOrchestrator(
        topicsRepository: _FakeTopicsRepository(),
        localStore: store,
        externalImageDownloadClient: _FakeExternalImageDownloadClient(),
        supabaseObjectDownloader: (_, __) async =>
            Uint8List.fromList(<int>[4, 5, 6]),
      );
      final image = RevelationMarkdownImageData(
        source: RevelationMarkdownImageSource.parse('images/map.jpg'),
        alt: 'Map',
        alignment: RevelationMarkdownImageAlignment.center,
        isBlockImage: true,
      );

      final result = await orchestrator.loadImage(image);

      expect(result.isSuccess, isTrue);
      expect(
        store.bytesByRelativePath['map.jpg'],
        orderedEquals(<int>[4, 5, 6]),
      );
    },
  );

  test('loadImage resolves database resources with their mime type', () async {
    final orchestrator = TopicMarkdownImageOrchestrator(
      topicsRepository: _FakeTopicsRepository(
        resourceByKey: <String, AppResult<TopicResource?>>{
          'seal': AppSuccess<TopicResource?>(
            TopicResource(
              fileName: 'seal.svg',
              mimeType: 'image/svg+xml',
              data: Uint8List.fromList('<svg></svg>'.codeUnits),
            ),
          ),
        },
      ),
      localStore: _FakeMarkdownImageLocalStore(),
      externalImageDownloadClient: _FakeExternalImageDownloadClient(),
      supabaseObjectDownloader: (_, __) async => null,
    );
    final image = RevelationMarkdownImageData(
      source: RevelationMarkdownImageSource.parse('dbres:seal'),
      alt: 'Seal',
      alignment: RevelationMarkdownImageAlignment.center,
      isBlockImage: false,
    );

    final result = await orchestrator.loadImage(image);

    expect(result.isSuccess, isTrue);
    expect(result.mimeType, 'image/svg+xml');
    expect(result.bytes, isNotNull);
  });
}

class _FakeTopicsRepository extends TopicsRepository {
  _FakeTopicsRepository({
    this.resourceByKey = const <String, AppResult<TopicResource?>>{},
  }) : super(dataSource: _NoopTopicsDataSource());

  final Map<String, AppResult<TopicResource?>> resourceByKey;

  @override
  Future<AppResult<String>> getArticleMarkdown({
    required String route,
    required String language,
  }) async {
    return const AppFailureResult<String>(
      AppFailure.notFound('Unused in orchestrator test.'),
    );
  }

  @override
  Future<AppResult<TopicInfo?>> getTopicByRoute({
    required String route,
    required String language,
  }) async {
    return const AppSuccess<TopicInfo?>(null);
  }

  @override
  Future<AppResult<TopicResource?>> getCommonResource(String key) async {
    return resourceByKey[key] ??
        const AppFailureResult<TopicResource?>(
          AppFailure.notFound('Missing fake resource.'),
        );
  }
}

class _FakeMarkdownImageLocalStore implements MarkdownImageLocalStore {
  final Map<String, Uint8List> bytesByRelativePath = <String, Uint8List>{};

  @override
  Future<MarkdownImageLocalStoreEntry?> read(String relativePath) async {
    final bytes = bytesByRelativePath[relativePath];
    if (bytes == null) {
      return null;
    }
    return MarkdownImageLocalStoreEntry(
      bytes: bytes,
      filePath: 'C:/fake/$relativePath',
    );
  }

  @override
  Future<String?> write(String relativePath, Uint8List bytes) async {
    bytesByRelativePath[relativePath] = Uint8List.fromList(bytes);
    return 'C:/fake/$relativePath';
  }
}

class _FakeExternalImageDownloadClient implements ExternalImageDownloadClient {
  _FakeExternalImageDownloadClient({
    this.bytesByUri = const <String, Uint8List>{},
  });

  final Map<String, Uint8List> bytesByUri;
  final List<String> requestedUris = <String>[];

  @override
  Future<Uint8List?> download(Uri uri) async {
    requestedUris.add(uri.toString());
    return bytesByUri[uri.toString()];
  }
}

class _NoopTopicsDataSource implements TopicsDataSource {
  @override
  Future<void> updateLanguage(String language) async {}

  @override
  Future<List<Article>> fetchArticles({bool onlyVisible = true}) async =>
      const <Article>[];

  @override
  Future<String> fetchArticleMarkdown(String route) async => '';

  @override
  Future<Article?> fetchArticleByRoute(String route) async => null;

  @override
  Future<CommonResource?> fetchCommonResource(String key) async => null;
}

import 'dart:typed_data';

import 'package:drift/drift.dart' show GeneratedDatabase;
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/infra/content/markdown_images/default_markdown_image_loader.dart';
import 'package:revelation/infra/db/common/db_common.dart' as common_db;
import 'package:revelation/infra/db/localized/db_localized.dart'
    as localized_db;
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';
import 'package:revelation/infra/remote/image/external_image_download_client.dart';
import 'package:revelation/infra/remote/image/supabase_storage_download_client.dart';
import 'package:revelation/infra/storage/markdown_image_local_store.dart';

void main() {
  test(
    'loads cached network images without repeated remote requests',
    () async {
      final store = _FakeMarkdownImageLocalStore();
      final client = _FakeExternalImageDownloadClient(
        bytesByUri: <String, Uint8List>{
          'https://example.com/image.png': Uint8List.fromList(<int>[1, 2, 3]),
        },
      );
      final loader = DefaultMarkdownImageLoader(
        articlesDatabaseGateway: _FakeArticlesDatabaseGateway(),
        localStore: store,
        externalImageDownloadClient: client,
        supabaseStorageDownloadClient: _FakeSupabaseStorageDownloadClient(),
      );
      final request = MarkdownImageRequest(
        kind: MarkdownImageRequestKind.network,
        cacheKey: 'network:https://example.com/image.png',
        networkUri: Uri.parse('https://example.com/image.png'),
        localRelativePath: 'external/example.com/image.png',
        guessedMimeType: 'image/png',
      );

      final first = await loader.loadImage(request);
      final second = await loader.loadImage(request);

      expect(first.isSuccess, isTrue);
      expect(second.isSuccess, isTrue);
      expect(client.requestedUris, <String>['https://example.com/image.png']);
      expect(
        store.bytesByRelativePath['external/example.com/image.png'],
        orderedEquals(Uint8List.fromList(<int>[1, 2, 3])),
      );
    },
  );

  test('stores Supabase images as readable files under images', () async {
    final store = _FakeMarkdownImageLocalStore();
    final loader = DefaultMarkdownImageLoader(
      articlesDatabaseGateway: _FakeArticlesDatabaseGateway(),
      localStore: store,
      externalImageDownloadClient: _FakeExternalImageDownloadClient(),
      supabaseStorageDownloadClient: _FakeSupabaseStorageDownloadClient(
        bytesByObject: <String, Uint8List>{
          'images/map.jpg': Uint8List.fromList(<int>[4, 5, 6]),
        },
      ),
    );
    const request = MarkdownImageRequest(
      kind: MarkdownImageRequestKind.supabaseStorage,
      cacheKey: 'supabase:images/map.jpg',
      supabaseBucket: 'images',
      supabasePath: 'map.jpg',
      localRelativePath: 'map.jpg',
      guessedMimeType: 'image/jpeg',
    );

    final result = await loader.loadImage(request);

    expect(result.isSuccess, isTrue);
    expect(store.bytesByRelativePath['map.jpg'], orderedEquals(<int>[4, 5, 6]));
  });

  test('loads database resources with their mime type', () async {
    final loader = DefaultMarkdownImageLoader(
      articlesDatabaseGateway: _FakeArticlesDatabaseGateway(
        resourcesByKey: <String, common_db.CommonResource>{
          'seal': common_db.CommonResource(
            key: 'seal',
            fileName: 'seal.svg',
            mimeType: 'image/svg+xml',
            data: Uint8List.fromList('<svg></svg>'.codeUnits),
          ),
        },
      ),
      localStore: _FakeMarkdownImageLocalStore(),
      externalImageDownloadClient: _FakeExternalImageDownloadClient(),
      supabaseStorageDownloadClient: _FakeSupabaseStorageDownloadClient(),
    );
    const request = MarkdownImageRequest(
      kind: MarkdownImageRequestKind.databaseResource,
      cacheKey: 'databaseResource:seal',
      databaseResourceKey: 'seal',
    );

    final result = await loader.loadImage(request);

    expect(result.isSuccess, isTrue);
    expect(result.mimeType, 'image/svg+xml');
    expect(result.bytes, isNotNull);
  });
}

class _FakeArticlesDatabaseGateway implements ArticlesDatabaseGateway {
  _FakeArticlesDatabaseGateway({
    this.resourcesByKey = const <String, common_db.CommonResource>{},
  });

  final Map<String, common_db.CommonResource> resourcesByKey;

  @override
  bool get isInitialized => true;

  @override
  String get languageCode => 'en';

  @override
  GeneratedDatabase? getActiveDatabase(String dbFile) => null;

  @override
  Future<List<localized_db.Article>> getArticles({
    bool onlyVisible = true,
  }) async {
    return const <localized_db.Article>[];
  }

  @override
  Future<localized_db.Article?> getArticleByRoute(String route) async => null;

  @override
  Future<String> getArticleMarkdown(String route) async => '';

  @override
  Future<common_db.CommonResource?> getCommonResource(String key) async {
    return resourcesByKey[key];
  }

  @override
  Future<void> initialize(String language) async {}

  @override
  Future<void> updateLanguage(String language) async {}
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

class _FakeSupabaseStorageDownloadClient
    implements SupabaseStorageDownloadClient {
  _FakeSupabaseStorageDownloadClient({
    this.bytesByObject = const <String, Uint8List>{},
  });

  final Map<String, Uint8List> bytesByObject;

  @override
  Future<Uint8List?> downloadObject({
    required String bucket,
    required String path,
  }) async {
    return bytesByObject['$bucket/$path'];
  }
}

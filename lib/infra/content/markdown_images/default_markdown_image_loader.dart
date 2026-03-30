import 'dart:async';
import 'dart:typed_data';

import 'package:revelation/core/content/markdown_images/markdown_image_load_result.dart';
import 'package:revelation/core/content/markdown_images/markdown_image_loader.dart';
import 'package:revelation/infra/db/runtime/gateways/articles_database_gateway.dart';
import 'package:revelation/infra/remote/image/external_image_download_client.dart';
import 'package:revelation/infra/remote/image/supabase_storage_download_client.dart';
import 'package:revelation/infra/storage/markdown_image_local_store.dart';

class DefaultMarkdownImageLoader implements MarkdownImageLoader {
  static const Duration _remoteDownloadTimeout = Duration(seconds: 30);

  DefaultMarkdownImageLoader({
    ArticlesDatabaseGateway? articlesDatabaseGateway,
    MarkdownImageLocalStore? localStore,
    ExternalImageDownloadClient? externalImageDownloadClient,
    SupabaseStorageDownloadClient? supabaseStorageDownloadClient,
  }) : _articlesDatabaseGateway =
           articlesDatabaseGateway ?? DbManagerArticlesDatabaseGateway(),
       _localStore = localStore ?? createMarkdownImageLocalStore(),
       _externalImageDownloadClient =
           externalImageDownloadClient ?? createExternalImageDownloadClient(),
       _supabaseStorageDownloadClient =
           supabaseStorageDownloadClient ??
           ServerManagerSupabaseStorageDownloadClient();

  final ArticlesDatabaseGateway _articlesDatabaseGateway;
  final MarkdownImageLocalStore _localStore;
  final ExternalImageDownloadClient _externalImageDownloadClient;
  final SupabaseStorageDownloadClient _supabaseStorageDownloadClient;
  final Map<String, Future<MarkdownImageLoadResult>> _inFlightRequests =
      <String, Future<MarkdownImageLoadResult>>{};

  @override
  Future<MarkdownImageLoadResult> loadImage(MarkdownImageRequest request) {
    final activeRequest = _inFlightRequests[request.cacheKey];
    if (activeRequest != null) {
      return activeRequest;
    }

    final loadRequest = _loadImageInternal(request).whenComplete(() {
      _inFlightRequests.remove(request.cacheKey);
    });
    _inFlightRequests[request.cacheKey] = loadRequest;
    return loadRequest;
  }

  Future<MarkdownImageLoadResult> _loadImageInternal(
    MarkdownImageRequest request,
  ) async {
    switch (request.kind) {
      case MarkdownImageRequestKind.databaseResource:
        return _loadDatabaseResource(request);
      case MarkdownImageRequestKind.supabaseStorage:
        return _loadSupabaseImage(request);
      case MarkdownImageRequestKind.network:
        return _loadExternalImage(request);
    }
  }

  Future<MarkdownImageLoadResult> _loadDatabaseResource(
    MarkdownImageRequest request,
  ) async {
    final key = request.databaseResourceKey;
    if (key == null || key.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }

    final resource = await _articlesDatabaseGateway.getCommonResource(key);
    if (resource == null || resource.data.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }

    return MarkdownImageLoadResult.success(
      bytes: resource.data,
      mimeType: _resolveMimeType(
        explicitMimeType: resource.mimeType,
        guessedMimeType: request.guessedMimeType,
        bytes: resource.data,
      ),
    );
  }

  Future<MarkdownImageLoadResult> _loadSupabaseImage(
    MarkdownImageRequest request,
  ) async {
    final cachedEntry = await _readRemoteCachedEntry(request);
    if (cachedEntry != null) {
      return MarkdownImageLoadResult.success(
        bytes: cachedEntry.bytes,
        mimeType: _resolveMimeType(
          guessedMimeType: request.guessedMimeType,
          bytes: cachedEntry.bytes,
        ),
      );
    }

    final bucket = request.supabaseBucket;
    final path = request.supabasePath;
    if (bucket == null || bucket.isEmpty || path == null || path.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }

    final bytes = await _awaitRemoteBytes(
      _supabaseStorageDownloadClient.downloadObject(bucket: bucket, path: path),
    );
    if (bytes == null || bytes.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }

    final mimeType = _resolveMimeType(
      guessedMimeType: request.guessedMimeType,
      bytes: bytes,
    );
    final relativePath = request.localRelativePath;
    if (relativePath != null && relativePath.isNotEmpty) {
      await _localStore.write(relativePath, bytes);
    }
    return MarkdownImageLoadResult.success(bytes: bytes, mimeType: mimeType);
  }

  Future<MarkdownImageLoadResult> _loadExternalImage(
    MarkdownImageRequest request,
  ) async {
    final cachedEntry = await _readRemoteCachedEntry(request);
    if (cachedEntry != null) {
      return MarkdownImageLoadResult.success(
        bytes: cachedEntry.bytes,
        mimeType: _resolveMimeType(
          guessedMimeType: request.guessedMimeType,
          bytes: cachedEntry.bytes,
        ),
      );
    }

    final uri = request.networkUri;
    if (uri == null) {
      return const MarkdownImageLoadResult.failure();
    }

    final bytes = await _awaitRemoteBytes(
      _externalImageDownloadClient.download(uri),
    );
    if (bytes == null || bytes.isEmpty) {
      return const MarkdownImageLoadResult.failure();
    }

    final mimeType = _resolveMimeType(
      guessedMimeType: request.guessedMimeType,
      bytes: bytes,
    );
    final relativePath = request.localRelativePath;
    if (relativePath != null && relativePath.isNotEmpty) {
      await _localStore.write(relativePath, bytes);
    }
    return MarkdownImageLoadResult.success(bytes: bytes, mimeType: mimeType);
  }

  Future<MarkdownImageLocalStoreEntry?> _readRemoteCachedEntry(
    MarkdownImageRequest request,
  ) async {
    final relativePath = request.localRelativePath;
    if (relativePath == null || relativePath.isEmpty) {
      return null;
    }
    return _localStore.read(relativePath);
  }

  String? _resolveMimeType({
    String? explicitMimeType,
    String? guessedMimeType,
    required Uint8List bytes,
  }) {
    final normalizedExplicitMimeType = explicitMimeType?.trim();
    if (normalizedExplicitMimeType != null &&
        normalizedExplicitMimeType.isNotEmpty) {
      return normalizedExplicitMimeType;
    }

    final normalizedGuessedMimeType = guessedMimeType?.trim();
    if (normalizedGuessedMimeType != null &&
        normalizedGuessedMimeType.isNotEmpty) {
      return normalizedGuessedMimeType;
    }

    if (_looksLikeSvg(bytes)) {
      return 'image/svg+xml';
    }

    return null;
  }

  bool _looksLikeSvg(Uint8List bytes) {
    final previewBytes = bytes.length > 256 ? bytes.sublist(0, 256) : bytes;
    final textPreview = String.fromCharCodes(
      previewBytes,
    ).trimLeft().toLowerCase();
    return textPreview.startsWith('<svg') || textPreview.contains('<svg');
  }

  Future<Uint8List?> _awaitRemoteBytes(Future<Uint8List?> future) async {
    try {
      return await future.timeout(_remoteDownloadTimeout);
    } on TimeoutException {
      return null;
    }
  }
}

import 'dart:async';
import 'dart:typed_data';

import 'package:revelation/core/errors/app_result.dart';
import 'package:revelation/features/topics/data/models/topic_resource.dart';
import 'package:revelation/features/topics/data/repositories/topics_repository.dart';
import 'package:revelation/infra/remote/image/external_image_download_client.dart';
import 'package:revelation/infra/storage/markdown_image_local_store.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_data.dart';
import 'package:revelation/shared/ui/markdown/revelation_markdown_image_extractor.dart';

typedef SupabaseObjectDownloader =
    Future<Uint8List?> Function(String bucket, String path);

class TopicMarkdownImageLoadResult {
  const TopicMarkdownImageLoadResult._({
    required this.isSuccess,
    this.bytes,
    this.mimeType,
  });

  const TopicMarkdownImageLoadResult.success({
    required Uint8List bytes,
    String? mimeType,
  }) : this._(isSuccess: true, bytes: bytes, mimeType: mimeType);

  const TopicMarkdownImageLoadResult.failure()
    : this._(isSuccess: false, bytes: null, mimeType: null);

  final bool isSuccess;
  final Uint8List? bytes;
  final String? mimeType;
}

class TopicMarkdownImageOrchestrator {
  static const Duration _remoteDownloadTimeout = Duration(seconds: 30);

  TopicMarkdownImageOrchestrator({
    required TopicsRepository topicsRepository,
    MarkdownImageLocalStore? localStore,
    ExternalImageDownloadClient? externalImageDownloadClient,
    SupabaseObjectDownloader? supabaseObjectDownloader,
  }) : _topicsRepository = topicsRepository,
       _localStore = localStore ?? createMarkdownImageLocalStore(),
       _externalImageDownloadClient =
           externalImageDownloadClient ?? createExternalImageDownloadClient(),
       _supabaseObjectDownloader =
           supabaseObjectDownloader ?? _unsupportedSupabaseDownload;

  final TopicsRepository _topicsRepository;
  final MarkdownImageLocalStore _localStore;
  final ExternalImageDownloadClient _externalImageDownloadClient;
  final SupabaseObjectDownloader _supabaseObjectDownloader;
  final Map<String, Future<TopicMarkdownImageLoadResult>> _inFlightRequests =
      <String, Future<TopicMarkdownImageLoadResult>>{};

  List<RevelationMarkdownImageData> collectAsyncImages(String markdown) {
    final seenCacheKeys = <String>{};
    final images = <RevelationMarkdownImageData>[];

    for (final image in extractRevelationMarkdownImages(markdown)) {
      final sourceKind = image.source.kind;
      if (sourceKind != RevelationMarkdownImageSourceKind.databaseResource &&
          sourceKind != RevelationMarkdownImageSourceKind.supabaseStorage &&
          sourceKind != RevelationMarkdownImageSourceKind.network) {
        continue;
      }
      if (seenCacheKeys.add(image.cacheKey)) {
        images.add(image);
      }
    }

    return images;
  }

  Future<TopicMarkdownImageLoadResult> loadImage(
    RevelationMarkdownImageData image,
  ) {
    final cacheKey = image.cacheKey;
    final activeRequest = _inFlightRequests[cacheKey];
    if (activeRequest != null) {
      return activeRequest;
    }

    final request = _loadImageInternal(image).whenComplete(() {
      _inFlightRequests.remove(cacheKey);
    });
    _inFlightRequests[cacheKey] = request;
    return request;
  }

  Future<TopicMarkdownImageLoadResult> _loadImageInternal(
    RevelationMarkdownImageData image,
  ) async {
    switch (image.source.kind) {
      case RevelationMarkdownImageSourceKind.databaseResource:
        return _loadDatabaseResource(image);
      case RevelationMarkdownImageSourceKind.supabaseStorage:
        return _loadSupabaseImage(image);
      case RevelationMarkdownImageSourceKind.network:
        return _loadExternalImage(image);
      case RevelationMarkdownImageSourceKind.asset:
      case RevelationMarkdownImageSourceKind.unsupported:
        return const TopicMarkdownImageLoadResult.failure();
    }
  }

  Future<TopicMarkdownImageLoadResult> _loadDatabaseResource(
    RevelationMarkdownImageData image,
  ) async {
    final key = image.source.databaseResourceKey;
    if (key == null || key.isEmpty) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final result = await _topicsRepository.getCommonResource(key);
    if (result is! AppSuccess<TopicResource?>) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final resource = result.data;
    if (resource == null || resource.data.isEmpty) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    return TopicMarkdownImageLoadResult.success(
      bytes: resource.data,
      mimeType: _resolveMimeType(
        explicitMimeType: resource.mimeType,
        source: image.source,
        bytes: resource.data,
      ),
    );
  }

  Future<TopicMarkdownImageLoadResult> _loadSupabaseImage(
    RevelationMarkdownImageData image,
  ) async {
    final cachedEntry = await _readRemoteCachedEntry(image);
    if (cachedEntry != null) {
      return TopicMarkdownImageLoadResult.success(
        bytes: cachedEntry.bytes,
        mimeType: _resolveMimeType(
          source: image.source,
          bytes: cachedEntry.bytes,
        ),
      );
    }

    final bucket = image.source.supabaseBucket;
    final path = image.source.supabasePath;
    if (bucket == null || bucket.isEmpty || path == null || path.isEmpty) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final bytes = await _awaitRemoteBytes(
      _supabaseObjectDownloader(bucket, path),
    );
    if (bytes == null || bytes.isEmpty) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final mimeType = _resolveMimeType(source: image.source, bytes: bytes);
    final relativePath = image.source.buildLocalRelativePath(
      mimeType: mimeType,
    );
    if (relativePath != null) {
      await _localStore.write(relativePath, bytes);
    }
    return TopicMarkdownImageLoadResult.success(
      bytes: bytes,
      mimeType: mimeType,
    );
  }

  Future<TopicMarkdownImageLoadResult> _loadExternalImage(
    RevelationMarkdownImageData image,
  ) async {
    final cachedEntry = await _readRemoteCachedEntry(image);
    if (cachedEntry != null) {
      return TopicMarkdownImageLoadResult.success(
        bytes: cachedEntry.bytes,
        mimeType: _resolveMimeType(
          source: image.source,
          bytes: cachedEntry.bytes,
        ),
      );
    }

    final uri = image.source.networkUri;
    if (uri == null) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final bytes = await _awaitRemoteBytes(
      _externalImageDownloadClient.download(uri),
    );
    if (bytes == null || bytes.isEmpty) {
      return const TopicMarkdownImageLoadResult.failure();
    }

    final mimeType = _resolveMimeType(source: image.source, bytes: bytes);
    final relativePath = image.source.buildLocalRelativePath(
      mimeType: mimeType,
    );
    if (relativePath != null) {
      await _localStore.write(relativePath, bytes);
    }
    return TopicMarkdownImageLoadResult.success(
      bytes: bytes,
      mimeType: mimeType,
    );
  }

  Future<MarkdownImageLocalStoreEntry?> _readRemoteCachedEntry(
    RevelationMarkdownImageData image,
  ) async {
    final sourceKind = image.source.kind;
    if (sourceKind != RevelationMarkdownImageSourceKind.supabaseStorage &&
        sourceKind != RevelationMarkdownImageSourceKind.network) {
      return null;
    }
    final relativePath = image.source.buildLocalRelativePath();
    if (relativePath == null || relativePath.isEmpty) {
      return null;
    }
    return _localStore.read(relativePath);
  }

  String? _resolveMimeType({
    String? explicitMimeType,
    required RevelationMarkdownImageSource source,
    required Uint8List bytes,
  }) {
    final normalizedMimeType = explicitMimeType?.trim();
    if (normalizedMimeType != null && normalizedMimeType.isNotEmpty) {
      return normalizedMimeType;
    }

    final guessedMimeType = source.guessedMimeType;
    if (guessedMimeType != null && guessedMimeType.isNotEmpty) {
      return guessedMimeType;
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

  static Future<Uint8List?> _unsupportedSupabaseDownload(
    String bucket,
    String path,
  ) async {
    return null;
  }
}

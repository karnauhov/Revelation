import 'package:markdown/markdown.dart' as md;
import 'package:path/path.dart' as p;
import 'package:revelation/shared/config/supabase_storage_paths.dart';

enum RevelationMarkdownImageAlignment { left, center, right }

enum RevelationMarkdownImageSourceKind {
  asset,
  databaseResource,
  supabaseStorage,
  network,
  unsupported,
}

class RevelationMarkdownImageSource {
  const RevelationMarkdownImageSource._({
    required this.kind,
    required this.original,
    required this.locator,
  });

  static const String assetScheme = 'resource:';
  static const String databaseResourceScheme = 'dbres:';
  static const String supabaseScheme = 'supabase:';
  static const Set<String> shorthandSupabaseBuckets = <String>{'images'};

  final RevelationMarkdownImageSourceKind kind;
  final String original;
  final String locator;

  bool get isCacheable =>
      kind == RevelationMarkdownImageSourceKind.databaseResource ||
      kind == RevelationMarkdownImageSourceKind.supabaseStorage ||
      kind == RevelationMarkdownImageSourceKind.network;

  String get cacheKey => '${kind.name}:$locator';

  String? get assetPath =>
      kind == RevelationMarkdownImageSourceKind.asset ? locator : null;

  String? get databaseResourceKey =>
      kind == RevelationMarkdownImageSourceKind.databaseResource
      ? locator
      : null;

  Uri? get networkUri => kind == RevelationMarkdownImageSourceKind.network
      ? Uri.tryParse(locator)
      : null;

  String? get supabaseBucket {
    if (kind != RevelationMarkdownImageSourceKind.supabaseStorage) {
      return null;
    }
    final separatorIndex = locator.indexOf('/');
    if (separatorIndex <= 0) {
      return null;
    }
    return locator.substring(0, separatorIndex);
  }

  String? get supabasePath {
    if (kind != RevelationMarkdownImageSourceKind.supabaseStorage) {
      return null;
    }
    final separatorIndex = locator.indexOf('/');
    if (separatorIndex <= 0 || separatorIndex == locator.length - 1) {
      return null;
    }
    return locator.substring(separatorIndex + 1);
  }

  String? get guessedMimeType {
    final extension = _extension.toLowerCase();
    switch (extension) {
      case '.svg':
        return 'image/svg+xml';
      case '.png':
        return 'image/png';
      case '.jpg':
      case '.jpeg':
        return 'image/jpeg';
      case '.gif':
        return 'image/gif';
      case '.webp':
        return 'image/webp';
      case '.bmp':
        return 'image/bmp';
      default:
        return null;
    }
  }

  bool get isSvg => guessedMimeType == 'image/svg+xml';

  Uri? get supabasePublicUri {
    final originalUri = Uri.tryParse(original);
    if (originalUri != null &&
        (originalUri.scheme == 'http' || originalUri.scheme == 'https') &&
        parseSupabasePublicStorageUri(originalUri) != null &&
        isConfiguredSupabasePublicStorageUri(originalUri)) {
      return originalUri;
    }

    final bucket = supabaseBucket;
    final path = supabasePath;
    if (bucket == null || path == null) {
      return null;
    }
    return buildSupabasePublicStorageUri(bucket: bucket, objectPath: path);
  }

  String? buildLocalRelativePath({String? mimeType}) {
    switch (kind) {
      case RevelationMarkdownImageSourceKind.supabaseStorage:
        final bucket = supabaseBucket;
        final path = supabasePath;
        if (bucket == null || path == null) {
          return null;
        }
        final normalizedPath = _sanitizeRelativePath(path);
        if (normalizedPath.isEmpty) {
          return null;
        }
        if (bucket.toLowerCase() == 'images') {
          return normalizedPath;
        }
        return _joinPath(<String>[bucket, normalizedPath]);
      case RevelationMarkdownImageSourceKind.network:
        final uri = networkUri;
        if (uri == null) {
          return null;
        }
        final segments = <String>[
          'external',
          _sanitizePathSegment(uri.host.isEmpty ? 'unknown-host' : uri.host),
        ];
        final normalizedSegments = uri.pathSegments
            .map(_sanitizePathSegment)
            .where((segment) => segment.isNotEmpty)
            .toList(growable: true);
        if (normalizedSegments.isNotEmpty) {
          segments.addAll(normalizedSegments);
        } else {
          segments.add(_fallbackExternalFileName(uri: uri, mimeType: mimeType));
        }
        if (uri.hasQuery) {
          segments[segments.length - 1] = _appendSuffixBeforeExtension(
            segments.last,
            _stableHexHash(uri.query),
          );
        }
        return _joinPath(segments);
      case RevelationMarkdownImageSourceKind.asset:
      case RevelationMarkdownImageSourceKind.databaseResource:
      case RevelationMarkdownImageSourceKind.unsupported:
        return null;
    }
  }

  String get _extension {
    switch (kind) {
      case RevelationMarkdownImageSourceKind.asset:
      case RevelationMarkdownImageSourceKind.databaseResource:
      case RevelationMarkdownImageSourceKind.supabaseStorage:
        return p.extension(locator);
      case RevelationMarkdownImageSourceKind.network:
        final uri = Uri.tryParse(locator);
        return p.extension(uri?.path ?? locator);
      case RevelationMarkdownImageSourceKind.unsupported:
        return p.extension(locator);
    }
  }

  static RevelationMarkdownImageSource parse(
    String rawSource, {
    String? ownedSupabaseBaseUrl,
  }) {
    final normalizedSource = rawSource.trim();
    if (normalizedSource.isEmpty) {
      return const RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.unsupported,
        original: '',
        locator: '',
      );
    }

    final lowercase = normalizedSource.toLowerCase();
    if (lowercase.startsWith(assetScheme)) {
      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.asset,
        original: normalizedSource,
        locator: normalizedSource.substring(assetScheme.length).trim(),
      );
    }

    if (lowercase.startsWith(databaseResourceScheme)) {
      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.databaseResource,
        original: normalizedSource,
        locator: normalizedSource
            .substring(databaseResourceScheme.length)
            .trim(),
      );
    }

    if (lowercase.startsWith(supabaseScheme)) {
      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.supabaseStorage,
        original: normalizedSource,
        locator: normalizedSource.substring(supabaseScheme.length).trim(),
      );
    }

    if (lowercase.startsWith('assets/')) {
      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.asset,
        original: normalizedSource,
        locator: normalizedSource,
      );
    }

    if (_looksLikeShorthandSupabasePath(normalizedSource)) {
      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.supabaseStorage,
        original: normalizedSource,
        locator: normalizedSource.replaceAll('\\', '/'),
      );
    }

    final uri = Uri.tryParse(normalizedSource);
    if (uri != null && (uri.scheme == 'http' || uri.scheme == 'https')) {
      final supabaseRef = parseSupabasePublicStorageUri(uri);
      if (supabaseRef != null &&
          isConfiguredSupabasePublicStorageUri(
            uri,
            baseUrl: ownedSupabaseBaseUrl,
          )) {
        return RevelationMarkdownImageSource._(
          kind: RevelationMarkdownImageSourceKind.supabaseStorage,
          original: normalizedSource,
          locator: supabaseRef.locator,
        );
      }

      return RevelationMarkdownImageSource._(
        kind: RevelationMarkdownImageSourceKind.network,
        original: normalizedSource,
        locator: uri.toString(),
      );
    }

    return RevelationMarkdownImageSource._(
      kind: RevelationMarkdownImageSourceKind.unsupported,
      original: normalizedSource,
      locator: normalizedSource,
    );
  }

  static bool _looksLikeShorthandSupabasePath(String source) {
    final normalized = source
        .replaceAll('\\', '/')
        .trim()
        .replaceFirst(RegExp(r'^/+'), '');
    final separatorIndex = normalized.indexOf('/');
    if (separatorIndex <= 0 || separatorIndex == normalized.length - 1) {
      return false;
    }
    final bucket = normalized.substring(0, separatorIndex).toLowerCase();
    if (!shorthandSupabaseBuckets.contains(bucket)) {
      return false;
    }
    return p.extension(normalized).isNotEmpty;
  }

  static String _sanitizeRelativePath(String path) {
    final segments = path
        .replaceAll('\\', '/')
        .split('/')
        .map(_sanitizePathSegment)
        .where((segment) => segment.isNotEmpty)
        .toList(growable: false);
    return _joinPath(segments);
  }

  static String _sanitizePathSegment(String segment) {
    final trimmed = segment.trim();
    if (trimmed.isEmpty || trimmed == '.' || trimmed == '..') {
      return '';
    }
    return trimmed.replaceAll(RegExp(r'[<>:"\\|?*]'), '_');
  }

  static String _fallbackExternalFileName({
    required Uri uri,
    String? mimeType,
  }) {
    final extension = _extensionForMimeType(mimeType) ?? '.bin';
    return 'download$extension';
  }

  static String _joinPath(List<String> segments) {
    return segments.where((segment) => segment.isNotEmpty).join('/');
  }

  static String _appendSuffixBeforeExtension(String fileName, String suffix) {
    final extension = p.extension(fileName);
    if (extension.isEmpty) {
      return '${fileName}_$suffix';
    }
    final baseName = fileName.substring(0, fileName.length - extension.length);
    return '${baseName}_$suffix$extension';
  }

  static String? _extensionForMimeType(String? mimeType) {
    switch (mimeType?.trim().toLowerCase()) {
      case 'image/svg+xml':
        return '.svg';
      case 'image/png':
        return '.png';
      case 'image/jpeg':
        return '.jpg';
      case 'image/gif':
        return '.gif';
      case 'image/webp':
        return '.webp';
      case 'image/bmp':
        return '.bmp';
      default:
        return null;
    }
  }

  static String _stableHexHash(String value) {
    const int offsetBasis = 0xcbf29ce484222325;
    const int prime = 0x100000001b3;
    var hash = offsetBasis;
    for (final unit in value.codeUnits) {
      hash ^= unit;
      hash = (hash * prime) & 0xffffffffffffffff;
    }
    return hash.toRadixString(16).padLeft(16, '0');
  }
}

class RevelationMarkdownImageData {
  const RevelationMarkdownImageData({
    required this.source,
    required this.alt,
    required this.alignment,
    required this.isBlockImage,
    this.title,
    this.caption,
    this.width,
    this.height,
  });

  final RevelationMarkdownImageSource source;
  final String alt;
  final String? title;
  final String? caption;
  final double? width;
  final double? height;
  final RevelationMarkdownImageAlignment alignment;
  final bool isBlockImage;

  String get cacheKey => source.cacheKey;

  bool get hasExplicitSize => width != null || height != null;

  static RevelationMarkdownImageData? fromMarkdownElement(md.Element element) {
    final rawSource = element.attributes['src']?.trim() ?? '';
    if (rawSource.isEmpty) {
      return null;
    }

    final sourceWithDimensions = _extractDimensionsFromSource(rawSource);
    final width =
        _parseDimension(element.attributes['width']) ??
        sourceWithDimensions.width;
    final height =
        _parseDimension(element.attributes['height']) ??
        sourceWithDimensions.height;

    return RevelationMarkdownImageData(
      source: RevelationMarkdownImageSource.parse(sourceWithDimensions.source),
      alt: (element.attributes['alt'] ?? '').trim(),
      title: _nullIfEmpty(element.attributes['title']),
      caption: _nullIfEmpty(element.attributes['caption']),
      width: width,
      height: height,
      alignment: _parseAlignment(
        element.attributes['align'] ?? element.attributes['alignment'],
      ),
      isBlockImage: element.tag != 'img',
    );
  }

  static _SourceWithDimensions _extractDimensionsFromSource(String source) {
    final fragmentIndex = source.lastIndexOf('#');
    if (fragmentIndex == -1 || fragmentIndex == source.length - 1) {
      return _SourceWithDimensions(source: source);
    }

    final fragment = source.substring(fragmentIndex + 1);
    final match = RegExp(
      r'^([0-9]+(?:\.[0-9]+)?)x([0-9]+(?:\.[0-9]+)?)$',
    ).firstMatch(fragment);
    if (match == null) {
      return _SourceWithDimensions(source: source);
    }

    return _SourceWithDimensions(
      source: source.substring(0, fragmentIndex),
      width: double.tryParse(match.group(1)!),
      height: double.tryParse(match.group(2)!),
    );
  }

  static double? _parseDimension(String? rawValue) {
    final normalized = _nullIfEmpty(rawValue);
    if (normalized == null) {
      return null;
    }
    return double.tryParse(normalized);
  }

  static RevelationMarkdownImageAlignment _parseAlignment(String? rawValue) {
    switch (_nullIfEmpty(rawValue)?.toLowerCase()) {
      case 'left':
        return RevelationMarkdownImageAlignment.left;
      case 'right':
        return RevelationMarkdownImageAlignment.right;
      default:
        return RevelationMarkdownImageAlignment.center;
    }
  }

  static String? _nullIfEmpty(String? rawValue) {
    final normalized = rawValue?.trim();
    if (normalized == null || normalized.isEmpty) {
      return null;
    }
    return normalized;
  }
}

class _SourceWithDimensions {
  const _SourceWithDimensions({required this.source, this.width, this.height});

  final String source;
  final double? width;
  final double? height;
}

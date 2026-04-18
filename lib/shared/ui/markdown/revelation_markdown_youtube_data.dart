import 'package:markdown/markdown.dart' as md;

class RevelationMarkdownYoutubeData {
  const RevelationMarkdownYoutubeData({
    required this.rawSource,
    required this.videoId,
    required this.startAtSeconds,
    required this.aspectRatio,
    this.title,
    this.caption,
    this.width,
    this.height,
  });

  static const String tag = 'revelation-youtube';
  static const double _defaultAspectRatio = 16 / 9;

  final String rawSource;
  final String videoId;
  final int startAtSeconds;
  final double aspectRatio;
  final String? title;
  final String? caption;
  final double? width;
  final double? height;

  bool get isValid => videoId.isNotEmpty;

  Uri? get embedUri {
    if (!isValid) {
      return null;
    }
    return Uri.https('www.youtube.com', '/embed/$videoId', <String, String>{
      'playsinline': '1',
      'fs': '1',
      'rel': '0',
      'loop': '1',
      'playlist': videoId,
      if (startAtSeconds > 0) 'start': '$startAtSeconds',
    });
  }

  Uri? get originalVideoUri {
    if (isValid) {
      return Uri.https('www.youtube.com', '/watch', <String, String>{
        'v': videoId,
        if (startAtSeconds > 0) 't': '${startAtSeconds}s',
      });
    }

    final rawUri = Uri.tryParse(rawSource);
    if (rawUri == null ||
        !(rawUri.scheme == 'http' || rawUri.scheme == 'https')) {
      return null;
    }
    return rawUri;
  }

  double get resolvedAspectRatio {
    if (width != null && width! > 0 && height != null && height! > 0) {
      return width! / height!;
    }
    if (aspectRatio > 0) {
      return aspectRatio;
    }
    return _defaultAspectRatio;
  }

  double? get maxWidth => width != null && width! > 0 ? width : null;

  String get viewTypeKey {
    final buffer = StringBuffer()
      ..write(videoId)
      ..write('|')
      ..write(startAtSeconds)
      ..write('|')
      ..write(title ?? '')
      ..write('|')
      ..write(width ?? '')
      ..write('|')
      ..write(height ?? '');
    return _stableHexHash(buffer.toString());
  }

  static RevelationMarkdownYoutubeData? fromMarkdownElement(
    md.Element element,
  ) {
    final rawSource = _nullIfEmpty(
      element.attributes['url'] ??
          element.attributes['id'] ??
          element.attributes['video_id'] ??
          element.attributes['video-id'],
    );
    if (rawSource == null) {
      return null;
    }

    final parsedUrl = Uri.tryParse(rawSource);
    final videoId = _resolveVideoId(rawSource: rawSource, uri: parsedUrl);
    final startAtSeconds =
        _parseStartSeconds(element.attributes['start']) ??
        _parseStartSeconds(
          element.attributes['start_at'] ?? element.attributes['start-at'],
        ) ??
        _parseStartSecondsFromUri(parsedUrl) ??
        0;

    final width = _parsePositiveDouble(element.attributes['width']);
    final height = _parsePositiveDouble(element.attributes['height']);
    final aspectRatio =
        _parseAspectRatio(
          element.attributes['aspect_ratio'] ??
              element.attributes['aspect-ratio'],
        ) ??
        _resolveAspectRatioFromSize(width: width, height: height) ??
        _defaultAspectRatio;

    return RevelationMarkdownYoutubeData(
      rawSource: rawSource,
      videoId: videoId,
      startAtSeconds: startAtSeconds,
      aspectRatio: aspectRatio,
      title: _nullIfEmpty(element.attributes['title']),
      caption: _nullIfEmpty(element.attributes['caption']),
      width: width,
      height: height,
    );
  }

  static String _resolveVideoId({required String rawSource, Uri? uri}) {
    final directId = _nullIfEmpty(rawSource);
    if (directId != null && !_looksLikeUrl(directId)) {
      return directId;
    }

    if (uri == null) {
      return '';
    }

    final host = uri.host.toLowerCase();
    if (host == 'youtu.be') {
      return _firstNonEmptySegment(uri.pathSegments);
    }
    if (host.endsWith('youtube.com') || host.endsWith('youtube-nocookie.com')) {
      if (uri.path == '/watch') {
        return _nullIfEmpty(uri.queryParameters['v']) ?? '';
      }
      if (uri.pathSegments.isEmpty) {
        return '';
      }
      final first = uri.pathSegments.first.toLowerCase();
      if (first == 'embed' || first == 'shorts' || first == 'live') {
        return uri.pathSegments.length >= 2 ? uri.pathSegments[1].trim() : '';
      }
    }
    return '';
  }

  static int? _parseStartSecondsFromUri(Uri? uri) {
    if (uri == null) {
      return null;
    }

    return _parseStartSeconds(uri.queryParameters['t']) ??
        _parseStartSeconds(uri.queryParameters['start']) ??
        _parseStartSeconds(uri.fragment);
  }

  static int? _parseStartSeconds(String? rawValue) {
    final normalized = _nullIfEmpty(rawValue)?.toLowerCase();
    if (normalized == null) {
      return null;
    }

    final stripped = normalized.replaceFirst(RegExp(r'^#?t='), '');
    final direct = int.tryParse(stripped);
    if (direct != null && direct >= 0) {
      return direct;
    }

    final match = RegExp(
      r'^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$',
    ).firstMatch(stripped);
    if (match == null) {
      return null;
    }

    final hours = int.tryParse(match.group(1) ?? '') ?? 0;
    final minutes = int.tryParse(match.group(2) ?? '') ?? 0;
    final seconds = int.tryParse(match.group(3) ?? '') ?? 0;
    if (hours == 0 && minutes == 0 && seconds == 0) {
      return null;
    }
    return (hours * 3600) + (minutes * 60) + seconds;
  }

  static double? _parseAspectRatio(String? rawValue) {
    final normalized = _nullIfEmpty(rawValue);
    if (normalized == null) {
      return null;
    }

    final numeric = double.tryParse(normalized);
    if (numeric != null && numeric > 0) {
      return numeric;
    }

    final ratioMatch = RegExp(
      r'^([0-9]+(?:\.[0-9]+)?)\s*[:/]\s*([0-9]+(?:\.[0-9]+)?)$',
    ).firstMatch(normalized);
    if (ratioMatch == null) {
      return null;
    }

    final width = double.tryParse(ratioMatch.group(1)!);
    final height = double.tryParse(ratioMatch.group(2)!);
    if (width == null || height == null || width <= 0 || height <= 0) {
      return null;
    }
    return width / height;
  }

  static double? _resolveAspectRatioFromSize({
    required double? width,
    required double? height,
  }) {
    if (width == null || height == null || width <= 0 || height <= 0) {
      return null;
    }
    return width / height;
  }

  static double? _parsePositiveDouble(String? rawValue) {
    final normalized = _nullIfEmpty(rawValue);
    if (normalized == null) {
      return null;
    }
    final value = double.tryParse(normalized);
    if (value == null || value <= 0) {
      return null;
    }
    return value;
  }

  static String _firstNonEmptySegment(List<String> segments) {
    for (final segment in segments) {
      final normalized = segment.trim();
      if (normalized.isNotEmpty) {
        return normalized;
      }
    }
    return '';
  }

  static bool _looksLikeUrl(String value) {
    final uri = Uri.tryParse(value);
    return uri != null && (uri.scheme == 'http' || uri.scheme == 'https');
  }

  static String? _nullIfEmpty(String? rawValue) {
    final normalized = rawValue?.trim();
    if (normalized == null || normalized.isEmpty) {
      return null;
    }
    return normalized;
  }

  static String _stableHexHash(String value) {
    const int offsetBasis = 0x811c9dc5;
    const int prime = 0x01000193;
    var hash = offsetBasis;
    for (final unit in value.codeUnits) {
      hash ^= unit;
      hash = (hash * prime) & 0xffffffff;
    }
    return hash.toUnsigned(32).toRadixString(16).padLeft(8, '0');
  }
}

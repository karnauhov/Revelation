class SupabasePublicStorageObjectRef {
  const SupabasePublicStorageObjectRef({
    required this.bucket,
    required this.objectPath,
  });

  final String bucket;
  final String objectPath;

  String get locator => '$bucket/$objectPath';

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        other is SupabasePublicStorageObjectRef &&
            bucket == other.bucket &&
            objectPath == other.objectPath;
  }

  @override
  int get hashCode => Object.hash(bucket, objectPath);
}

const String _publicStoragePathPrefix = '/storage/v1/object/public/';

String getConfiguredSupabaseBaseUrl() {
  final baseUrl = const String.fromEnvironment('SUPABASE_URL').trim();
  if (baseUrl.isEmpty) {
    return '';
  }
  return baseUrl.endsWith('/')
      ? baseUrl.substring(0, baseUrl.length - 1)
      : baseUrl;
}

String buildSupabasePublicStoragePath({
  required String bucket,
  required String objectPath,
}) {
  final normalizedBucket = bucket.trim().replaceAll(RegExp(r'^/+|/+$'), '');
  final normalizedObjectPath = objectPath
      .replaceAll('\\', '/')
      .trim()
      .replaceAll(RegExp(r'^/+'), '');
  final encodedSegments = normalizedObjectPath
      .split('/')
      .where((segment) => segment.isNotEmpty)
      .map(Uri.encodeComponent)
      .join('/');
  return '$_publicStoragePathPrefix$normalizedBucket/$encodedSegments';
}

Uri? buildSupabasePublicStorageUri({
  required String bucket,
  required String objectPath,
  String? baseUrl,
}) {
  final normalizedBaseUrl = (baseUrl ?? getConfiguredSupabaseBaseUrl()).trim();
  if (normalizedBaseUrl.isEmpty) {
    return null;
  }
  return Uri.parse(
    '$normalizedBaseUrl${buildSupabasePublicStoragePath(bucket: bucket, objectPath: objectPath)}',
  );
}

bool isConfiguredSupabasePublicStorageUri(Uri uri, {String? baseUrl}) {
  final configuredBaseUrl = (baseUrl ?? getConfiguredSupabaseBaseUrl()).trim();
  if (configuredBaseUrl.isEmpty) {
    return true;
  }

  final configuredUri = Uri.tryParse(configuredBaseUrl);
  if (configuredUri == null) {
    return false;
  }

  final normalizedConfiguredPort = configuredUri.hasPort
      ? configuredUri.port
      : null;
  final normalizedUriPort = uri.hasPort ? uri.port : null;

  return uri.scheme == configuredUri.scheme &&
      uri.host.toLowerCase() == configuredUri.host.toLowerCase() &&
      normalizedUriPort == normalizedConfiguredPort;
}

SupabasePublicStorageObjectRef? parseSupabasePublicStorageUri(Uri uri) {
  if (uri.scheme != 'http' && uri.scheme != 'https') {
    return null;
  }

  final segments = uri.pathSegments;
  if (segments.length < 5 ||
      segments[0] != 'storage' ||
      segments[1] != 'v1' ||
      segments[2] != 'object' ||
      segments[3] != 'public') {
    return null;
  }

  final bucket = segments[4].trim();
  final objectPath = segments.skip(5).join('/').trim();
  if (bucket.isEmpty || objectPath.isEmpty) {
    return null;
  }

  return SupabasePublicStorageObjectRef(bucket: bucket, objectPath: objectPath);
}

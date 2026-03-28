Uri buildWebDbUri(
  String dbFile, {
  Uri? baseUri,
  String? versionToken,
  bool forceNoCache = false,
}) {
  return _buildWebAssetUri(
    'db/$dbFile',
    baseUri: baseUri,
    versionToken: versionToken,
    forceNoCache: forceNoCache,
  );
}

Uri buildWebDbManifestUri({Uri? baseUri, bool forceNoCache = false}) {
  return _buildWebAssetUri(
    'db/manifest.json',
    baseUri: baseUri,
    forceNoCache: forceNoCache,
  );
}

Uri _buildWebAssetUri(
  String path, {
  Uri? baseUri,
  String? versionToken,
  bool forceNoCache = false,
}) {
  final query = <String, String>{};
  if (versionToken != null && versionToken.isNotEmpty) {
    query['rev'] = versionToken;
  }
  if (forceNoCache) {
    query['ts'] = DateTime.now().millisecondsSinceEpoch.toString();
  }

  final resolvedBaseUri = baseUri ?? Uri.base;
  final relativeUri = Uri(
    path: path,
    queryParameters: query.isEmpty ? null : query,
  );

  return resolvedBaseUri.resolveUri(relativeUri);
}

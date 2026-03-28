import 'dart:convert';

String buildWebDbManifestVersionToken({
  required int schemaVersion,
  required int dataVersion,
  required String date,
  int? fileSizeBytes,
}) {
  final parts = <String>[
    'schema:$schemaVersion',
    'data:$dataVersion',
    'date:$date',
  ];
  if (fileSizeBytes != null) {
    parts.add('size:$fileSizeBytes');
  }
  return 'manifest:${parts.join('|')}';
}

Map<String, String> parseWebDbManifestVersionTokens(String manifestBody) {
  try {
    final decoded = jsonDecode(manifestBody);
    if (decoded is! Map<Object?, Object?>) {
      return const {};
    }

    final rawDatabases = decoded['databases'];
    if (rawDatabases is! Map<Object?, Object?>) {
      return const {};
    }

    final tokens = <String, String>{};
    for (final entry in rawDatabases.entries) {
      final dbFile = entry.key;
      final value = entry.value;
      if (dbFile is! String || value is! Map<Object?, Object?>) {
        continue;
      }

      final token = _parseManifestEntryVersionToken(value);
      if (token != null) {
        tokens[dbFile] = token;
      }
    }

    return tokens;
  } catch (_) {
    return const {};
  }
}

String? _parseManifestEntryVersionToken(Map<Object?, Object?> entry) {
  final explicitToken = _asNonEmptyString(entry['versionToken']);
  if (explicitToken != null) {
    return explicitToken;
  }

  final schemaVersion = _asInt(entry['schemaVersion']);
  final dataVersion = _asInt(entry['dataVersion']);
  final date = _asNonEmptyString(entry['date']);
  if (schemaVersion == null || dataVersion == null || date == null) {
    return null;
  }

  return buildWebDbManifestVersionToken(
    schemaVersion: schemaVersion,
    dataVersion: dataVersion,
    date: date,
    fileSizeBytes: _asInt(entry['fileSizeBytes']),
  );
}

String? _asNonEmptyString(Object? value) {
  if (value is String && value.isNotEmpty) {
    return value;
  }
  return null;
}

int? _asInt(Object? value) {
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.toInt();
  }
  if (value is String) {
    return int.tryParse(value);
  }
  return null;
}

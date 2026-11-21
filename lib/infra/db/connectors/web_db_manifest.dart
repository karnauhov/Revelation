import 'dart:convert';

import 'package:revelation/infra/db/connectors/database_version_info.dart';

class WebDbManifestEntry {
  const WebDbManifestEntry({
    required this.versionToken,
    required this.versionInfo,
    this.fileSizeBytes,
    this.bible,
  });

  final String versionToken;
  final DatabaseVersionInfo versionInfo;
  final int? fileSizeBytes;
  final Map<String, String>? bible;

  /// Include the release metadata even when a publisher reuses an opaque token.
  String get snapshotIdentity {
    final release = buildWebDbManifestVersionToken(
      schemaVersion: versionInfo.schemaVersion,
      dataVersion: versionInfo.dataVersion,
      date: versionInfo.date.toUtc().toIso8601String(),
      fileSizeBytes: fileSizeBytes,
    );
    return '$versionToken|$release';
  }
}

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

Map<String, WebDbManifestEntry> parseWebDbManifestEntries(String manifestBody) {
  try {
    final decoded = jsonDecode(manifestBody);
    if (decoded is! Map<Object?, Object?>) {
      return const {};
    }

    final rawDatabases = decoded['databases'];
    if (rawDatabases is! Map<Object?, Object?>) {
      return const {};
    }

    final entries = <String, WebDbManifestEntry>{};
    for (final entry in rawDatabases.entries) {
      final dbFile = entry.key;
      final value = entry.value;
      if (dbFile is! String || value is! Map<Object?, Object?>) {
        continue;
      }

      final parsedEntry = _parseManifestEntry(value);
      if (parsedEntry != null) {
        entries[dbFile] = parsedEntry;
      }
    }

    return entries;
  } catch (_) {
    return const {};
  }
}

WebDbManifestEntry? _parseManifestEntry(Map<Object?, Object?> entry) {
  final explicitToken = _asNonEmptyString(entry['versionToken']);
  final schemaVersion = _asInt(entry['schemaVersion']);
  final dataVersion = _asInt(entry['dataVersion']);
  final date = _asNonEmptyString(entry['date']);
  if (schemaVersion == null || dataVersion == null || date == null) {
    return null;
  }

  final parsedDate = DateTime.tryParse(date);
  if (parsedDate == null) {
    return null;
  }

  final fileSizeBytes = _asInt(entry['fileSizeBytes']);
  final rawBible = entry['bible'];
  final bible = rawBible is Map
      ? <String, String>{
          for (final MapEntry(:key, :value) in rawBible.entries)
            if (key is String && value is String) key: value,
        }
      : null;
  return WebDbManifestEntry(
    versionToken:
        explicitToken ??
        buildWebDbManifestVersionToken(
          schemaVersion: schemaVersion,
          dataVersion: dataVersion,
          date: date,
          fileSizeBytes: fileSizeBytes,
        ),
    versionInfo: DatabaseVersionInfo(
      schemaVersion: schemaVersion,
      dataVersion: dataVersion,
      date: parsedDate,
    ),
    fileSizeBytes: fileSizeBytes,
    bible: bible == null ? null : Map.unmodifiable(bible),
  );
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

import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';
import 'package:revelation/infra/db/connectors/web_db_manifest.dart';
import 'package:revelation/infra/db/connectors/web_db_uri.dart';

void main() {
  test('buildWebDbManifestUri respects non-root base href', () {
    final uri = buildWebDbManifestUri(
      baseUri: Uri.parse('https://example.com/revelation/'),
      forceNoCache: true,
    );

    expect(uri.origin, 'https://example.com');
    expect(uri.path, '/revelation/db/manifest.json');
    expect(uri.queryParameters.containsKey('ts'), isTrue);
  });

  test('parseWebDbManifestVersionTokens reads explicit manifest tokens', () {
    const manifest = '''
{
  "databases": {
    "revelation.sqlite": {
      "versionToken": "manifest:schema:4|data:2|date:2026-03-21T06:09:24Z|size:1630208"
    },
    "revelation_ru.sqlite": {
      "versionToken": "manifest:schema:6|data:2|date:2026-03-21T06:09:14Z|size:675840"
    }
  }
}
''';

    final tokens = parseWebDbManifestVersionTokens(manifest);

    expect(
      tokens['revelation.sqlite'],
      'manifest:schema:4|data:2|date:2026-03-21T06:09:24Z|size:1630208',
    );
    expect(
      tokens['revelation_ru.sqlite'],
      'manifest:schema:6|data:2|date:2026-03-21T06:09:14Z|size:675840',
    );
  });

  test('parseWebDbManifestEntries reads version info and file sizes', () {
    const manifest = '''
{
  "databases": {
    "revelation.sqlite": {
      "versionToken": "manifest:schema:4|data:2|date:2026-03-21T06:09:24Z|size:1630208",
      "schemaVersion": 4,
      "dataVersion": 2,
      "date": "2026-03-21T06:09:24Z",
      "fileSizeBytes": 1630208
    }
  }
}
''';

    final entries = parseWebDbManifestEntries(manifest);

    expect(entries['revelation.sqlite'], isNotNull);
    expect(
      entries['revelation.sqlite']!.versionInfo,
      DatabaseVersionInfo(
        schemaVersion: 4,
        dataVersion: 2,
        date: DateTime.parse('2026-03-21T06:09:24Z'),
      ),
    );
    expect(entries['revelation.sqlite']!.fileSizeBytes, 1630208);
    expect(
      entries['revelation.sqlite']!.versionToken,
      'manifest:schema:4|data:2|date:2026-03-21T06:09:24Z|size:1630208',
    );
  });

  test(
    'parseWebDbManifestVersionTokens synthesizes a token from metadata fields',
    () {
      const manifest = '''
{
  "databases": {
    "revelation.sqlite": {
      "schemaVersion": "4",
      "dataVersion": 2,
      "date": "2026-03-21T06:09:24Z",
      "fileSizeBytes": 1630208
    }
  }
}
''';

      final tokens = parseWebDbManifestVersionTokens(manifest);

      expect(
        tokens['revelation.sqlite'],
        buildWebDbManifestVersionToken(
          schemaVersion: 4,
          dataVersion: 2,
          date: '2026-03-21T06:09:24Z',
          fileSizeBytes: 1630208,
        ),
      );
    },
  );

  test(
    'parseWebDbManifestVersionTokens returns empty map for invalid input',
    () {
      expect(parseWebDbManifestVersionTokens('[]'), isEmpty);
      expect(parseWebDbManifestVersionTokens('{invalid json'), isEmpty);
      expect(
        parseWebDbManifestVersionTokens(
          '{"databases":{"revelation.sqlite":{}}}',
        ),
        isEmpty,
      );
    },
  );

  test('parseWebDbManifestEntries ignores entries with invalid dates', () {
    const manifest = '''
{
  "databases": {
    "revelation.sqlite": {
      "schemaVersion": 4,
      "dataVersion": 2,
      "date": "not-a-date",
      "fileSizeBytes": 1630208
    }
  }
}
''';

    expect(parseWebDbManifestEntries(manifest), isEmpty);
  });
}

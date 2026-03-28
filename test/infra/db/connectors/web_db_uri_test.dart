import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/web_db_uri.dart';

void main() {
  test('buildWebDbUri resolves db files from the site root base', () {
    final uri = buildWebDbUri(
      'revelation.sqlite',
      baseUri: Uri.parse('https://example.com/'),
    );

    expect(uri.toString(), 'https://example.com/db/revelation.sqlite');
  });

  test('buildWebDbUri respects non-root base href and query parameters', () {
    final uri = buildWebDbUri(
      'revelation_ru.sqlite',
      baseUri: Uri.parse('https://example.com/revelation/'),
      versionToken: 'etag-123',
      forceNoCache: true,
    );

    expect(uri.origin, 'https://example.com');
    expect(uri.path, '/revelation/db/revelation_ru.sqlite');
    expect(uri.queryParameters['rev'], 'etag-123');
    expect(uri.queryParameters.containsKey('ts'), isTrue);
  });
}

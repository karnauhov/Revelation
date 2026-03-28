import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/web_db_version_probe_policy.dart';

void main() {
  test('HEAD probe is skipped on localhost web origins', () {
    final shouldUseHead = shouldUseHeadForWebDbVersionProbe(
      uri: Uri.parse('http://localhost:61108/db/revelation.sqlite'),
    );

    expect(shouldUseHead, isFalse);
  });

  test('HEAD probe is skipped on loopback web origins', () {
    final shouldUseHead = shouldUseHeadForWebDbVersionProbe(
      uri: Uri.parse('http://127.0.0.1:8080/db/revelation_ru.sqlite'),
    );

    expect(shouldUseHead, isFalse);
  });

  test('HEAD probe is kept for non-local web origins', () {
    final shouldUseHead = shouldUseHeadForWebDbVersionProbe(
      uri: Uri.parse('https://example.com/revelation/db/revelation.sqlite'),
    );

    expect(shouldUseHead, isTrue);
  });
}

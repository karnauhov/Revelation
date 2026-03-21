import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/primary_source_file_info.dart';

void main() {
  test('PrimarySourceFileInfo stores success metadata', () {
    const info = PrimarySourceFileInfo(
      relativePath: 'primary_sources/en/source/page.png',
      sizeBytes: 4096,
    );

    expect(info.relativePath, 'primary_sources/en/source/page.png');
    expect(info.sizeBytes, 4096);
    expect(info.error, isNull);
  });

  test('PrimarySourceFileInfo stores failure metadata', () {
    const info = PrimarySourceFileInfo(
      relativePath: 'primary_sources/en/source',
      error: 'list failed',
    );

    expect(info.relativePath, 'primary_sources/en/source');
    expect(info.sizeBytes, isNull);
    expect(info.error, 'list failed');
  });
}

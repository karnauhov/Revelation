import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/db/connectors/database_version_info.dart';

void main() {
  test('DatabaseVersionInfo equality compares all fields', () {
    final date = DateTime.utc(2026, 3, 21, 12, 0, 0);
    final left = DatabaseVersionInfo(
      schemaVersion: 4,
      dataVersion: 11,
      date: date,
    );
    final same = DatabaseVersionInfo(
      schemaVersion: 4,
      dataVersion: 11,
      date: date,
    );
    final differentSchema = DatabaseVersionInfo(
      schemaVersion: 5,
      dataVersion: 11,
      date: date,
    );
    final differentData = DatabaseVersionInfo(
      schemaVersion: 4,
      dataVersion: 12,
      date: date,
    );
    final differentDate = DatabaseVersionInfo(
      schemaVersion: 4,
      dataVersion: 11,
      date: date.add(const Duration(seconds: 1)),
    );

    expect(left, same);
    expect(left.hashCode, same.hashCode);
    expect(left == differentSchema, isFalse);
    expect(left == differentData, isFalse);
    expect(left == differentDate, isFalse);
  });
}

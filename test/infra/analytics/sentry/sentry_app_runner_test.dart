import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/infra/analytics/sentry/sentry_app_runner.dart';

void main() {
  group('parseSentrySampleRate', () {
    test('accepts values in Sentry sample-rate range', () {
      expect(parseSentrySampleRate('0', fallback: 1), 0);
      expect(parseSentrySampleRate('0.25', fallback: 1), 0.25);
      expect(parseSentrySampleRate('1', fallback: 0), 1);
    });

    test('falls back for invalid values', () {
      expect(parseSentrySampleRate('', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('nope', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('-0.1', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('1.1', fallback: 0.5), 0.5);
      expect(parseSentrySampleRate('NaN', fallback: 0.5), 0.5);
    });
  });
}

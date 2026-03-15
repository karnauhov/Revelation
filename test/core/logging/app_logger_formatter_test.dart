import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/core/logging/app_logger_formatter.dart';
import 'package:talker_logger/talker_logger.dart';

void main() {
  group('AppLoggerFormatter', () {
    test('formats multiline message without borders or colors', () {
      final formatter = AppLoggerFormatter();
      final details = LogDetails(
        message: 'first\nsecond',
        level: LogLevel.debug,
        pen: AnsiPen(),
      );
      final settings = TalkerLoggerSettings(enableColors: false);

      final result = formatter.fmt(details, settings);

      const prefix = '\u2502 ';
      expect(result, '${prefix}first\n${prefix}second');
    });

    test('uses pen formatting when colors are enabled', () {
      final formatter = AppLoggerFormatter();
      final details = LogDetails(
        message: 'colored',
        level: LogLevel.info,
        pen: AnsiPen()..red(),
      );
      final settings = TalkerLoggerSettings(enableColors: true);

      final result = formatter.fmt(details, settings);

      const prefix = '\u2502 ';
      final expected = details.pen.write('${prefix}colored');
      expect(result, expected);
    });
  });
}

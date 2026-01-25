import 'package:talker_flutter/talker_flutter.dart';

class AppLoggerFormatter extends ExtendedLoggerFormatter {
  AppLoggerFormatter() {}

  @override
  String fmt(LogDetails details, TalkerLoggerSettings settings) {
    final msg = details.message?.toString() ?? '';
    final msgBorderedLines = msg.split('\n').map((e) => '│ $e');
    if (!settings.enableColors) {
      return '${msgBorderedLines.join('\n')}';
    }
    var lines = [...msgBorderedLines];
    lines = lines.map((e) => details.pen.write(e)).toList();
    final coloredMsg = lines.join('\n');
    return coloredMsg;
  }
}

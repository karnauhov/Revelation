import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/shared/utils/bug_report_utils.dart';
import 'package:talker_flutter/talker_flutter.dart';

Future<void> reportStartupFailure(
  BuildContext context,
  AppStartupState state, {
  BugReportDependencies dependencies = const BugReportDependencies(),
  String Function()? logsLoader,
}) {
  return submitBugReport(
    context: context,
    dependencies: dependencies,
    diagnosticsBuilder: () async {
      final buffer = StringBuffer();
      buffer.write('=======TIMESTAMP=======\r\n');
      buffer.write('${DateTime.now().toIso8601String()}\r\n\r\n');
      buffer.write('=======LOGS=======\r\n');
      buffer.write((logsLoader ?? _defaultStartupLogsLoader).call());
      buffer.write('\r\n');
      buffer.write(
        await dependencies.collectSystemAndAppInfo(context: context),
      );
      buffer.write('\r\n=======STARTUP=======\r\n');
      buffer.writeln('step: ${state.step.name}');
      buffer.writeln('stepNumber: ${state.stepNumber}');
      buffer.writeln('progressValue: ${state.progressValue}');
      buffer.writeln('localeCode: ${state.localeCode}');
      buffer.writeln('appVersion: ${state.appVersion}');
      buffer.writeln('buildNumber: ${state.buildNumber}');
      buffer.writeln('isLoading: ${state.isLoading}');
      buffer.writeln('isReady: ${state.isReady}');

      final failure = state.failure;
      if (failure != null) {
        buffer.writeln('failure.type: ${failure.type.name}');
        buffer.writeln('failure.message: ${failure.message}');
        if (failure.cause != null) {
          buffer.writeln('failure.cause: ${failure.cause}');
        }
        if (failure.stackTrace != null) {
          buffer.writeln('failure.stackTrace: ${failure.stackTrace}');
        }
      }

      return buffer.toString();
    },
  );
}

String _defaultStartupLogsLoader() {
  if (!GetIt.I.isRegistered<Talker>()) {
    return 'Talker is not registered.\r\n';
  }
  return GetIt.I<Talker>().history.text();
}

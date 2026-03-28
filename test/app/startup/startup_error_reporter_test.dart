@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/app/startup/startup_error_reporter.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/utils/bug_report_utils.dart';

void main() {
  testWidgets(
    'reportStartupFailure copies startup diagnostics and opens bug report email',
    (tester) async {
      String? clipboardText;
      String? launchedUrl;
      final state = AppStartupState.initial(localeCode: 'en').copyWith(
        step: AppBootstrapStep.ready,
        appVersion: '1.0.5',
        buildNumber: '141',
        isLoading: false,
        failure: const AppFailure.dataSource('Unable to initialize the app.'),
      );

      await tester.pumpWidget(
        _buildHarness((context) async {
          await reportStartupFailure(
            context,
            state,
            dependencies: BugReportDependencies(
              launchLink: (url) async {
                launchedUrl = url;
                return true;
              },
              collectSystemAndAppInfo: ({context, dbFilesSection}) async {
                return 'SYSTEM INFO';
              },
              writeClipboardText: (text) async {
                clipboardText = text;
              },
            ),
            logsLoader: () => 'talker-history',
          );
        }),
      );

      await tester.tap(find.text('report'));
      await tester.pump();

      expect(launchedUrl, isNotNull);
      expect(launchedUrl, contains('mailto:'));
      expect(clipboardText, isNotNull);
      expect(clipboardText, contains('=======STARTUP======='));
      expect(clipboardText, contains('step: ready'));
      expect(clipboardText, contains('stepNumber: 5'));
      expect(clipboardText, contains('appVersion: 1.0.5'));
      expect(clipboardText, contains('buildNumber: 141'));
      expect(
        clipboardText,
        contains('failure.message: Unable to initialize the app.'),
      );
      expect(clipboardText, contains('talker-history'));
      expect(clipboardText, contains('SYSTEM INFO'));
    },
  );
}

Widget _buildHarness(Future<void> Function(BuildContext context) onPressed) {
  return MaterialApp(
    locale: const Locale('en'),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: Scaffold(
      body: Builder(
        builder: (context) {
          return Center(
            child: TextButton(
              onPressed: () async {
                await onPressed(context);
              },
              child: const Text('report'),
            ),
          );
        },
      ),
    ),
  );
}

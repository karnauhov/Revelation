@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/utils/bug_report_utils.dart';

void main() {
  testWidgets('submitBugReport copies diagnostics and opens bug report email', (
    tester,
  ) async {
    String? clipboardText;
    String? launchedUrl;

    await tester.pumpWidget(
      _buildHarness((context) async {
        await submitBugReport(
          context: context,
          dependencies: BugReportDependencies(
            launchLink: (url) async {
              launchedUrl = url;
              return true;
            },
            writeClipboardText: (text) async {
              clipboardText = text;
            },
          ),
          diagnosticsBuilder: () async => 'DIAGNOSTICS',
        );
      }),
    );

    await tester.tap(find.text('send'));
    await tester.pump();

    final l10n = AppLocalizations.of(tester.element(find.text('send')))!;
    expect(clipboardText, 'DIAGNOSTICS');
    expect(launchedUrl, isNotNull);
    expect(launchedUrl, contains('mailto:'));
    expect(launchedUrl, contains('Revelation%20Bug%20Report'));
    expect(Uri.decodeFull(launchedUrl!), contains(l10n.bug_report_wish));
    expect(find.byType(SnackBar), findsNothing);
  });

  testWidgets(
    'submitBugReport shows fallback message when mail app is absent',
    (tester) async {
      String? clipboardText;

      await tester.pumpWidget(
        _buildHarness((context) async {
          await submitBugReport(
            context: context,
            dependencies: BugReportDependencies(
              launchLink: (_) async => false,
              writeClipboardText: (text) async {
                clipboardText = text;
              },
            ),
            diagnosticsBuilder: () async => 'DIAGNOSTICS',
          );
        }),
      );

      await tester.tap(find.text('send'));
      await tester.pump();

      final l10n = AppLocalizations.of(tester.element(find.text('send')))!;
      expect(clipboardText, 'DIAGNOSTICS');
      expect(find.textContaining(l10n.log_copied_message), findsOneWidget);
    },
  );

  testWidgets(
    'submitBugReport shows fallback message when diagnostics builder fails',
    (tester) async {
      var launchCalls = 0;
      String? clipboardText;

      await tester.pumpWidget(
        _buildHarness((context) async {
          await submitBugReport(
            context: context,
            dependencies: BugReportDependencies(
              launchLink: (_) async {
                launchCalls++;
                return true;
              },
              writeClipboardText: (text) async {
                clipboardText = text;
              },
            ),
            diagnosticsBuilder: () async {
              throw StateError('forced diagnostics failure');
            },
          );
        }),
      );

      await tester.tap(find.text('send'));
      await tester.pump();

      final l10n = AppLocalizations.of(tester.element(find.text('send')))!;
      expect(launchCalls, 0);
      expect(clipboardText, isNull);
      expect(find.textContaining(l10n.log_copied_message), findsOneWidget);
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
              child: const Text('send'),
            ),
          );
        },
      ),
    ),
  );
}

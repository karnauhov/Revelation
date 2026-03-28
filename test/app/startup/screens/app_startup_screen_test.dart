@Tags(['widget'])
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/app/startup/screens/app_startup_screen.dart';
import 'package:revelation/core/errors/app_failure.dart';
import 'package:revelation/l10n/app_localizations.dart';

void main() {
  testWidgets('renders full-screen splash progress and version info', (
    tester,
  ) async {
    await tester.pumpWidget(
      _buildHarness(
        AppStartupState.initial(localeCode: 'en').copyWith(
          step: AppBootstrapStep.initializingDatabases,
          appVersion: '1.0.5',
          buildNumber: '141',
        ),
      ),
    );
    await tester.pump();

    final image = tester.widget<Image>(find.byType(Image).first);
    final progress = tester.widget<LinearProgressIndicator>(
      find.byKey(const ValueKey<String>('startup-progress-indicator')),
    );
    final l10n = AppLocalizations.of(
      tester.element(find.byType(AppStartupScreen)),
    )!;

    expect(image.fit, BoxFit.cover);
    expect(find.text(l10n.startup_title), findsOneWidget);
    expect(find.text(l10n.startup_step_initializing_databases), findsOneWidget);
    expect(find.text('Step 4 of 5'), findsOneWidget);
    expect(find.text('Version 1.0.5 (141)'), findsOneWidget);
    expect(progress.value, 0.74);
  });

  testWidgets('shows retry action when startup failed', (tester) async {
    var retryCalls = 0;
    var reportCalls = 0;

    await tester.pumpWidget(
      _buildHarness(
        AppStartupState.initial(localeCode: 'en').copyWith(
          step: AppBootstrapStep.loadingSettings,
          failure: const AppFailure.dataSource('forced startup failure'),
        ),
        onRetry: () {
          retryCalls++;
        },
        onReportError: (_) async {
          reportCalls++;
        },
      ),
    );
    await tester.pump();

    final l10n = AppLocalizations.of(
      tester.element(find.byType(AppStartupScreen)),
    )!;

    expect(find.text(l10n.startup_error), findsOneWidget);
    expect(find.text(l10n.startup_retry), findsOneWidget);
    expect(find.text(l10n.bug_report), findsOneWidget);

    await tester.tap(find.text('Try again'));
    await tester.pump();
    await tester.tap(
      find.byKey(const ValueKey<String>('startup-report-error')),
    );
    await tester.pump();

    expect(retryCalls, 1);
    expect(reportCalls, 1);
  });

  testWidgets('adapts splash layout for wide screens', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 720));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      _buildHarness(
        AppStartupState.initial(
          localeCode: 'en',
        ).copyWith(step: AppBootstrapStep.configuringLinks),
      ),
    );
    await tester.pump();

    final decoratedBox = tester.widget<DecoratedBox>(
      find.byKey(const ValueKey<String>('startup-panel')),
    );
    final decoration = decoratedBox.decoration as BoxDecoration;
    final l10n = AppLocalizations.of(
      tester.element(find.byType(AppStartupScreen)),
    )!;

    expect(decoration.borderRadius, BorderRadius.circular(28));
    expect(find.text(l10n.startup_step_configuring_links), findsOneWidget);
  });
}

Widget _buildHarness(
  AppStartupState state, {
  VoidCallback? onRetry,
  Future<void> Function(BuildContext context)? onReportError,
}) {
  return MaterialApp(
    locale: const Locale('en'),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(useMaterial3: true),
    home: AppStartupScreen(
      state: state,
      onRetry: onRetry,
      onReportError: onReportError,
    ),
  );
}

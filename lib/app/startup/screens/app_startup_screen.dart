import 'package:flutter/material.dart';
import 'package:revelation/app/bootstrap/app_bootstrap.dart';
import 'package:revelation/app/startup/bloc/app_startup_state.dart';
import 'package:revelation/l10n/app_localizations.dart';

class AppStartupScreen extends StatelessWidget {
  const AppStartupScreen({
    super.key,
    required this.state,
    this.onRetry,
    this.onReportError,
  });

  static const String backgroundAssetPath =
      'assets/images/UI/startup_splash_banner.jpg';

  final AppStartupState state;
  final VoidCallback? onRetry;
  final Future<void> Function(BuildContext context)? onReportError;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      body: LayoutBuilder(
        builder: (context, constraints) {
          final width = constraints.maxWidth;
          final isExpanded = width >= 840;
          final horizontalPadding = isExpanded ? 48.0 : 24.0;
          final verticalPadding = isExpanded ? 40.0 : 24.0;
          final panelMaxWidth = isExpanded ? 560.0 : 460.0;
          final panelPadding = isExpanded ? 28.0 : 22.0;
          final crossAxisAlignment = isExpanded
              ? CrossAxisAlignment.start
              : CrossAxisAlignment.center;

          return Stack(
            fit: StackFit.expand,
            children: [
              Image.asset(
                backgroundAssetPath,
                fit: BoxFit.cover,
                alignment: Alignment.center,
                filterQuality: FilterQuality.medium,
              ),
              const DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: <Color>[
                      Color(0x66000000),
                      Color(0x88110C09),
                      Color(0xD9110C09),
                    ],
                  ),
                ),
              ),
              SafeArea(
                child: Padding(
                  padding: EdgeInsets.fromLTRB(
                    horizontalPadding,
                    verticalPadding,
                    horizontalPadding,
                    verticalPadding,
                  ),
                  child: Align(
                    alignment: isExpanded
                        ? Alignment.bottomLeft
                        : Alignment.bottomCenter,
                    child: ConstrainedBox(
                      constraints: BoxConstraints(maxWidth: panelMaxWidth),
                      child: DecoratedBox(
                        key: const ValueKey<String>('startup-panel'),
                        decoration: BoxDecoration(
                          color: const Color(0xA617120E),
                          borderRadius: BorderRadius.circular(
                            isExpanded ? 28 : 24,
                          ),
                          border: Border.all(color: const Color(0x40FFFFFF)),
                          boxShadow: const <BoxShadow>[
                            BoxShadow(
                              color: Color(0x33000000),
                              blurRadius: 24,
                              offset: Offset(0, 12),
                            ),
                          ],
                        ),
                        child: Padding(
                          padding: EdgeInsets.all(panelPadding),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: crossAxisAlignment,
                            children: [
                              Text(
                                l10n.app_name,
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineMedium
                                    ?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.w700,
                                    ),
                                textAlign: isExpanded
                                    ? TextAlign.start
                                    : TextAlign.center,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                l10n.startup_title,
                                style: Theme.of(context).textTheme.titleMedium
                                    ?.copyWith(
                                      color: const Color(0xFFE8DDD4),
                                      fontWeight: FontWeight.w500,
                                    ),
                                textAlign: isExpanded
                                    ? TextAlign.start
                                    : TextAlign.center,
                              ),
                              const SizedBox(height: 18),
                              Text(
                                _statusText(l10n),
                                key: const ValueKey<String>('startup-status'),
                                style: Theme.of(context).textTheme.bodyLarge
                                    ?.copyWith(
                                      color: Colors.white,
                                      fontWeight: FontWeight.w600,
                                    ),
                                textAlign: isExpanded
                                    ? TextAlign.start
                                    : TextAlign.center,
                              ),
                              const SizedBox(height: 14),
                              ClipRRect(
                                borderRadius: BorderRadius.circular(999),
                                child: LinearProgressIndicator(
                                  key: const ValueKey<String>(
                                    'startup-progress-indicator',
                                  ),
                                  value: state.progressValue,
                                  minHeight: 8,
                                  backgroundColor: const Color(0x33FFFFFF),
                                  valueColor:
                                      const AlwaysStoppedAnimation<Color>(
                                        Color(0xFFF2C48E),
                                      ),
                                ),
                              ),
                              const SizedBox(height: 10),
                              Text(
                                l10n.startup_progress(
                                  state.stepNumber,
                                  appBootstrapVisibleStepCount,
                                ),
                                style: Theme.of(context).textTheme.bodySmall
                                    ?.copyWith(color: const Color(0xFFD5C4B7)),
                                textAlign: isExpanded
                                    ? TextAlign.start
                                    : TextAlign.center,
                              ),
                              if (state.failure != null) ...[
                                const SizedBox(height: 18),
                                Text(
                                  l10n.startup_error,
                                  style: Theme.of(context).textTheme.bodyMedium
                                      ?.copyWith(color: Colors.white),
                                  textAlign: isExpanded
                                      ? TextAlign.start
                                      : TextAlign.center,
                                ),
                                const SizedBox(height: 14),
                                Wrap(
                                  alignment: isExpanded
                                      ? WrapAlignment.start
                                      : WrapAlignment.center,
                                  crossAxisAlignment: WrapCrossAlignment.center,
                                  spacing: 12,
                                  runSpacing: 8,
                                  children: [
                                    if (onRetry != null)
                                      FilledButton.tonal(
                                        onPressed: onRetry,
                                        child: Text(l10n.startup_retry),
                                      ),
                                    if (onReportError != null)
                                      TextButton(
                                        key: const ValueKey<String>(
                                          'startup-report-error',
                                        ),
                                        onPressed: () async {
                                          await onReportError!(context);
                                        },
                                        style: TextButton.styleFrom(
                                          foregroundColor: const Color(
                                            0xFFF2C48E,
                                          ),
                                          textStyle: Theme.of(context)
                                              .textTheme
                                              .bodyMedium
                                              ?.copyWith(
                                                fontWeight: FontWeight.w600,
                                                decoration:
                                                    TextDecoration.underline,
                                              ),
                                        ),
                                        child: Text(l10n.bug_report),
                                      ),
                                  ],
                                ),
                              ],
                              if (state.appVersion.isNotEmpty &&
                                  state.buildNumber.isNotEmpty) ...[
                                const SizedBox(height: 18),
                                Text(
                                  l10n.startup_version_build(
                                    state.appVersion,
                                    state.buildNumber,
                                  ),
                                  key: const ValueKey<String>(
                                    'startup-version',
                                  ),
                                  style: Theme.of(context).textTheme.bodySmall
                                      ?.copyWith(
                                        color: const Color(0xFFE8DDD4),
                                      ),
                                  textAlign: isExpanded
                                      ? TextAlign.start
                                      : TextAlign.center,
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  String _statusText(AppLocalizations l10n) {
    switch (state.step) {
      case AppBootstrapStep.preparing:
        return l10n.startup_step_preparing;
      case AppBootstrapStep.loadingSettings:
        return l10n.startup_step_loading_settings;
      case AppBootstrapStep.initializingServer:
        return l10n.startup_step_initializing_server;
      case AppBootstrapStep.initializingDatabases:
        return l10n.startup_step_initializing_databases;
      case AppBootstrapStep.configuringLinks:
      case AppBootstrapStep.ready:
        return l10n.startup_step_configuring_links;
    }
  }
}

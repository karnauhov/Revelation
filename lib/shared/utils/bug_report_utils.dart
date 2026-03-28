import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:revelation/core/diagnostics/diagnostics_utils.dart';
import 'package:revelation/core/logging/common_logger.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/utils/links_utils.dart';

typedef BugReportLinkLauncher = Future<bool> Function(String url);
typedef BugReportSystemInfoCollector =
    Future<String> Function({BuildContext? context, String? dbFilesSection});
typedef BugReportClipboardWriter = Future<void> Function(String text);

Future<void> defaultBugReportClipboardWriter(String text) {
  return Clipboard.setData(ClipboardData(text: text));
}

Future<bool> defaultBugReportLinkLauncher(String url) {
  return launchLink(url);
}

Future<String> defaultBugReportSystemInfoCollector({
  BuildContext? context,
  String? dbFilesSection,
}) {
  return collectSystemAndAppInfo(
    context: context,
    dbFilesSection: dbFilesSection,
  );
}

@immutable
class BugReportDependencies {
  const BugReportDependencies({
    this.launchLink = defaultBugReportLinkLauncher,
    this.collectSystemAndAppInfo = defaultBugReportSystemInfoCollector,
    this.writeClipboardText = defaultBugReportClipboardWriter,
  });

  final BugReportLinkLauncher launchLink;
  final BugReportSystemInfoCollector collectSystemAndAppInfo;
  final BugReportClipboardWriter writeClipboardText;
}

Future<void> submitBugReport({
  required BuildContext context,
  required Future<String> Function() diagnosticsBuilder,
  BugReportDependencies dependencies = const BugReportDependencies(),
  String? emailBodyText,
}) async {
  final l10n = AppLocalizations.of(context)!;
  final resolvedEmailBody = emailBodyText ?? '${l10n.bug_report_wish}\r\n\r\n';

  try {
    final diagnostics = await diagnosticsBuilder();
    if (!context.mounted) {
      return;
    }

    await dependencies.writeClipboardText(diagnostics);
    final openEmailResult = await dependencies.launchLink(
      buildBugReportMailtoUrl(emailBodyText: resolvedEmailBody),
    );
    if (!context.mounted) {
      return;
    }
    if (!openEmailResult) {
      showBugReportFallbackMessage(context);
    }
  } catch (error, stackTrace) {
    try {
      log.handle(error, stackTrace);
    } catch (_) {}
    if (!context.mounted) {
      return;
    }
    showBugReportFallbackMessage(context);
  }
}

String buildBugReportMailtoUrl({required String emailBodyText}) {
  final encodedBody = Uri.encodeFull(emailBodyText);
  return 'mailto:${AppConstants.supportEmail}?subject=Revelation%20Bug%20Report&body=$encodedBody';
}

void showBugReportFallbackMessage(BuildContext context) {
  final l10n = AppLocalizations.of(context)!;
  final messenger = ScaffoldMessenger.maybeOf(context);
  if (messenger == null) {
    return;
  }

  messenger.showSnackBar(
    SnackBar(
      content: Text('${l10n.log_copied_message} ${AppConstants.supportEmail}'),
      duration: const Duration(seconds: 10),
    ),
  );
}

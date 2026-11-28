import 'package:flutter/material.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/shared/config/app_constants.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';
import 'package:revelation/shared/ui/dialogs/study_text_dialog.dart';
import 'package:revelation/shared/utils/links_utils.dart';

Future<void> showHebrewStrongDialog(
  BuildContext context,
  int number, {
  String? word,
}) {
  return showDialog<void>(
    context: context,
    routeSettings: const RouteSettings(name: 'hebrew_strong_dialog'),
    builder: (dialog) {
      final l10n = AppLocalizations.of(dialog)!;
      return StudyTextDialog(
        title: 'H$number',
        subtitle: l10n.bible_module_info_hebrew,
        content: Padding(
          padding: const EdgeInsets.all(12),
          child: Text(word ?? 'Bible Hub'),
        ),
        secondaryActions: [
          RevelationDialogAction(
            label: l10n.close,
            onPressed: () => Navigator.pop(dialog),
          ),
        ],
        primaryAction: RevelationDialogAction(
          key: const Key('hebrew_strong_open_dictionary'),
          icon: Icons.open_in_new,
          label: l10n.strong_open_dictionary,
          onPressed: () => launchLink(
            AppConstants.hebrewUrl.replaceFirst('@index', '$number'),
          ),
        ),
      );
    },
  );
}

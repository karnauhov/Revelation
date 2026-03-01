import 'package:flutter/material.dart';
import 'package:revelation/common_widgets/description_markdown_view.dart';
import 'package:revelation/l10n/app_localizations.dart';
import 'package:revelation/screens/primary_source/strong_number_picker_dialog.dart';
import 'package:revelation/services/description_content_service.dart';

Future<void> showStrongDictionaryDialog(
  BuildContext context,
  int initialStrongNumber,
) {
  return showDialog<void>(
    context: context,
    routeSettings: const RouteSettings(name: 'strong_dictionary_dialog'),
    builder: (_) =>
        StrongDictionaryDialog(initialStrongNumber: initialStrongNumber),
  );
}

class StrongDictionaryDialog extends StatefulWidget {
  final int initialStrongNumber;

  const StrongDictionaryDialog({required this.initialStrongNumber, super.key});

  @override
  State<StrongDictionaryDialog> createState() => _StrongDictionaryDialogState();
}

class _StrongDictionaryDialogState extends State<StrongDictionaryDialog> {
  final DescriptionContentService _descriptionService =
      DescriptionContentService();

  late int _strongNumber;

  @override
  void initState() {
    super.initState();
    _strongNumber = widget.initialStrongNumber;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final mediaSize = MediaQuery.sizeOf(context);

    final dialogWidth = (mediaSize.width - 20).clamp(320.0, 800.0).toDouble();
    final dialogHeight = (mediaSize.height - 36).clamp(220.0, 600.0).toDouble();

    final content = _descriptionService.buildStrongContent(
      context,
      _strongNumber,
    );

    return AlertDialog(
      insetPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      backgroundColor: colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      titlePadding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      contentPadding: const EdgeInsets.fromLTRB(10, 0, 10, 0),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
      title: Center(
        child: Text(
          l10n.strongsConcordance,
          textAlign: TextAlign.center,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      content: SizedBox(
        width: dialogWidth,
        height: dialogHeight,
        child: DescriptionMarkdownView(
          data: content?.markdown ?? '-',
          padding: const EdgeInsets.fromLTRB(6, 0, 6, 6),
          onGreekStrongTap: (strongNumber, _) {
            setState(() {
              _strongNumber = strongNumber;
            });
          },
          onGreekStrongPickerTap: (strongNumber, linkContext) {
            _openStrongNumberPicker(linkContext, strongNumber);
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.close),
        ),
      ],
    );
  }

  Future<void> _openStrongNumberPicker(
    BuildContext dialogContext,
    int initialStrongNumber,
  ) async {
    final pickedStrongNumber = await showDialog<int>(
      context: dialogContext,
      routeSettings: const RouteSettings(name: 'strong_number_picker_dialog'),
      builder: (context) => StrongNumberPickerDialog(
        entries: _descriptionService.getGreekStrongPickerEntries(),
        initialStrongNumber: initialStrongNumber,
      ),
    );

    if (!mounted || pickedStrongNumber == null) {
      return;
    }

    setState(() {
      _strongNumber = pickedStrongNumber;
    });
  }
}

import 'package:flutter/material.dart';

/// The compact reading surface shared by passages and dictionary entries.
class StudyTextDialog extends StatelessWidget {
  const StudyTextDialog({
    required this.title,
    this.subtitle,
    required this.content,
    required this.actions,
    this.titleInfo,
    this.maxWidth = 660,
    super.key,
  });

  final String title;
  final String? subtitle;
  final Widget content;
  final List<Widget> actions;
  final Widget? titleInfo;
  final double maxWidth;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      constraints: BoxConstraints(maxWidth: maxWidth),
      insetPadding: const EdgeInsets.all(10),
      backgroundColor: theme.colorScheme.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: theme.colorScheme.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      titlePadding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      contentPadding: const EdgeInsets.symmetric(horizontal: 10),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
      title: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Flexible(
                child: Text(
                  title,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (titleInfo != null)
                Transform.translate(
                  offset: const Offset(4, -5),
                  child: titleInfo,
                ),
            ],
          ),
          if (subtitle != null)
            Text(
              subtitle!,
              style: theme.textTheme.labelSmall,
              textAlign: TextAlign.center,
            ),
        ],
      ),
      content: content,
      actions: actions,
    );
  }
}

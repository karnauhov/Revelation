import 'package:flutter/material.dart';

import 'revelation_dialog.dart';

/// The compact reading surface shared by passages and dictionary entries.
class StudyTextDialog extends StatelessWidget {
  const StudyTextDialog({
    required this.title,
    this.subtitle,
    required this.content,
    this.secondaryActions = const [],
    this.primaryAction,
    this.titleInfo,
    this.maxWidth = 660,
    super.key,
  });

  final String title;
  final String? subtitle;
  final Widget content;
  final List<RevelationDialogAction> secondaryActions;
  final RevelationDialogAction? primaryAction;
  final Widget? titleInfo;
  final double maxWidth;
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final heading = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Flexible(child: Text(title, textAlign: TextAlign.center)),
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
    );

    return RevelationDialog(
      constraints: BoxConstraints(minWidth: 280, maxWidth: maxWidth),
      title: heading,
      content: content,
      secondaryActions: secondaryActions,
      primaryAction: primaryAction,
    );
  }
}

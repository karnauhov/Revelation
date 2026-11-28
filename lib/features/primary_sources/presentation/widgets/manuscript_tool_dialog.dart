import 'package:flutter/material.dart';
import 'package:revelation/shared/ui/dialogs/revelation_dialog.dart';

class ManuscriptToolDialog extends StatelessWidget {
  const ManuscriptToolDialog({
    required this.content,
    this.secondaryActions = const [],
    this.primaryAction,
    required this.title,
    super.key,
  });
  final Widget content;
  final List<RevelationDialogAction> secondaryActions;
  final RevelationDialogAction? primaryAction;
  final Widget title;

  @override
  Widget build(BuildContext context) {
    final height = MediaQuery.sizeOf(context).height;
    return RevelationDialog(
      title: title,
      initialAlignment: Alignment.topRight,
      insetPadding: EdgeInsets.fromLTRB(8, height > 620 ? 64 : 8, 8, 8),
      constraints: const BoxConstraints(maxWidth: 400),
      scrollContent: true,
      content: SizedBox(width: 400, child: content),
      secondaryActions: secondaryActions,
      primaryAction: primaryAction,
    );
  }
}

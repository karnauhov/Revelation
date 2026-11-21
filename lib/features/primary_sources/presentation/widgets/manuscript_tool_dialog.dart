import 'package:flutter/material.dart';

class ManuscriptToolDialog extends StatelessWidget {
  const ManuscriptToolDialog({
    required this.content,
    required this.actions,
    this.title,
    super.key,
  });
  final Widget content;
  final List<Widget> actions;
  final Widget? title;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final height = MediaQuery.sizeOf(context).height;
    return AlertDialog(
      title: title,
      alignment: Alignment.topRight,
      insetPadding: EdgeInsets.fromLTRB(8, height > 620 ? 64 : 8, 8, 8),
      constraints: const BoxConstraints(maxWidth: 400),
      contentPadding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      actionsPadding: const EdgeInsets.fromLTRB(8, 0, 8, 4),
      backgroundColor: colors.surface,
      shape: RoundedRectangleBorder(
        side: BorderSide(color: colors.primary),
        borderRadius: BorderRadius.circular(8),
      ),
      scrollable: true,
      content: SizedBox(width: 400, child: content),
      actions: actions,
    );
  }
}

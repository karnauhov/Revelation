import 'package:flutter/material.dart';

class PrimarySourceSplitView extends StatelessWidget {
  final Widget imagePreview;
  final Widget descriptionPanel;
  final Widget footer;
  final Color dividerColor;

  const PrimarySourceSplitView({
    required this.imagePreview,
    required this.descriptionPanel,
    this.footer = const SizedBox.shrink(),
    required this.dividerColor,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    if (MediaQuery.orientationOf(context) == Orientation.landscape) {
      return Row(
        key: const Key('primary_source_split_view_row'),
        children: [
          Expanded(
            flex: 2,
            child: Column(
              children: [
                Expanded(child: imagePreview),
                footer,
              ],
            ),
          ),
          VerticalDivider(width: 1, thickness: 1, color: dividerColor),
          Expanded(child: descriptionPanel),
        ],
      );
    }
    return Column(
      key: const Key('primary_source_split_view_column'),
      children: [
        Expanded(flex: 2, child: imagePreview),
        footer,
        Divider(height: 1, thickness: 1, color: dividerColor),
        Expanded(child: descriptionPanel),
      ],
    );
  }
}

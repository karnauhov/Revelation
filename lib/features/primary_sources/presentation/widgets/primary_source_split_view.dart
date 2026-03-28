import 'package:flutter/material.dart';

class PrimarySourceSplitView extends StatelessWidget {
  final Widget imagePreview;
  final Widget descriptionPanel;
  final Color dividerColor;

  const PrimarySourceSplitView({
    required this.imagePreview,
    required this.descriptionPanel,
    required this.dividerColor,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final totalWidth = constraints.maxWidth;
        final totalHeight = constraints.maxHeight;
        final isLandscape =
            MediaQuery.of(context).orientation == Orientation.landscape;

        if (isLandscape) {
          final previewWidth = totalWidth * 2 / 3;
          final descriptionWidth = totalWidth * 1 / 3 - 10;
          return Row(
            key: const Key('primary_source_split_view_row'),
            children: [
              SizedBox(width: previewWidth, child: imagePreview),
              Container(width: 1, color: dividerColor),
              SizedBox(width: descriptionWidth, child: descriptionPanel),
            ],
          );
        }

        final previewHeight = totalHeight * 2 / 3;
        final descriptionHeight = totalHeight * 1 / 3 - 10;
        return Column(
          key: const Key('primary_source_split_view_column'),
          children: [
            SizedBox(height: previewHeight, child: imagePreview),
            Container(height: 1, color: dividerColor),
            SizedBox(height: descriptionHeight, child: descriptionPanel),
          ],
        );
      },
    );
  }
}

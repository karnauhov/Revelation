import 'package:flutter/material.dart';
import 'package:revelation/common_widgets/new_icon_button.dart';
import 'package:revelation/utils/common.dart';

class IconUrl extends StatelessWidget {
  final String iconPath;
  final String url;
  final String tooltip;

  const IconUrl({
    super.key,
    required this.iconPath,
    required this.url,
    required this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    return NewIconButton(
        assetPath: iconPath,
        tooltip: tooltip,
        size: 32,
        onPressed: () => launchLink(url));
  }
}

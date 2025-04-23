import 'package:flutter/material.dart';
import 'package:revelation/common_widgets/svg_icon_button.dart';
import 'package:revelation/utils/common.dart';

class IconUrl extends StatelessWidget {
  final String iconPath;
  final String url;

  const IconUrl({
    super.key,
    required this.iconPath,
    required this.url,
  });

  @override
  Widget build(BuildContext context) {
    return SvgIconButton(
        assetPath: iconPath,
        tooltip: "",
        size: 32,
        onPressed: () => launchLink(url));
  }
}

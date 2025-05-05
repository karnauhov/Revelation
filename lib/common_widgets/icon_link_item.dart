import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class IconLinkItem extends StatelessWidget {
  final String iconPath;
  final String text;
  final VoidCallback onTap;
  final double leftMargin;

  const IconLinkItem({
    super.key,
    required this.iconPath,
    required this.text,
    required this.onTap,
    this.leftMargin = 0,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.fromLTRB(leftMargin, 0, 0, 0),
      visualDensity: VisualDensity.compact,
      minTileHeight: 0,
      leading: SvgPicture.asset(
        iconPath,
        width: 24,
        height: 24,
      ),
      title: Text(
        text,
        style: TextStyle(color: Theme.of(context).colorScheme.primary),
      ),
      onTap: onTap,
    );
  }
}

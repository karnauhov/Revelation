import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class NewIconButton extends StatelessWidget {
  final String assetPath;
  final String tooltip;
  final double size;
  final VoidCallback onPressed;

  const NewIconButton({
    super.key,
    required this.assetPath,
    required this.tooltip,
    required this.size,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    Widget iconWidget;
    if (assetPath.toLowerCase().endsWith('.svg')) {
      iconWidget = SvgPicture.asset(
        assetPath,
        width: size,
        height: size,
        colorFilter: ColorFilter.mode(colorScheme.primary, BlendMode.srcIn),
      );
    } else {
      iconWidget = Image.asset(
        assetPath,
        width: size,
        height: size,
        color: colorScheme.primary,
      );
    }

    return Material(
      color: Colors.transparent,
      shape: const CircleBorder(),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(size * 1.2),
        customBorder: const CircleBorder(),
        hoverColor: colorScheme.primary.withValues(alpha: 0.08),
        splashColor: colorScheme.primary.withValues(alpha: 0.12),
        highlightColor: Colors.transparent,
        child: Tooltip(
          message: tooltip,
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: iconWidget,
          ),
        ),
      ),
    );
  }
}

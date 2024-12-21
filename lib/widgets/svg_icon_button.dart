import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class SvgIconButton extends StatelessWidget {
  final String assetPath;
  final String tooltip;
  final double size;
  final VoidCallback onPressed;

  const SvgIconButton({
    super.key,
    required this.assetPath,
    required this.tooltip,
    required this.size,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      shape: const CircleBorder(),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(size * 1.2),
        customBorder: const CircleBorder(),
        hoverColor: Colors.grey.withValues(alpha: 0.25),
        splashColor: Colors.transparent,
        highlightColor: Colors.transparent,
        child: Tooltip(
          message: tooltip,
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: SvgPicture.asset(
              assetPath,
              width: size,
              height: size,
            ),
          ),
        ),
      ),
    );
  }
}

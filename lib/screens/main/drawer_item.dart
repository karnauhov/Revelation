import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class DrawerItem extends StatelessWidget {
  final String assetPath;
  final String text;
  final VoidCallback onClick;

  const DrawerItem({
    super.key,
    required this.assetPath,
    required this.text,
    required this.onClick,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final backgroundColor = colorScheme.primary.withValues(alpha: 0.25);
    final contentColor = colorScheme.onSurface;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
      child: InkWell(
        onTap: onClick,
        borderRadius: BorderRadius.circular(8.0),
        splashColor: colorScheme.primary.withValues(alpha: 0.12),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(8.0),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(8.0),
          ),
          child: Row(
            children: [
              SvgPicture.asset(
                assetPath,
                width: 24.0,
                height: 24.0,
              ),
              const SizedBox(width: 16.0),
              Text(
                text,
                style: Theme.of(context)
                    .textTheme
                    .bodyLarge
                    ?.copyWith(color: contentColor),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

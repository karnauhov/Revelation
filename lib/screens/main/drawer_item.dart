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
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
      child: InkWell(
        onTap: onClick,
        borderRadius: BorderRadius.circular(8.0),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(8.0),
          decoration: BoxDecoration(
            color:
                Theme.of(context).colorScheme.primary.withValues(alpha: 0.25),
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
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

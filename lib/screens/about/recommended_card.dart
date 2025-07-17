import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:revelation/models/recommended_info.dart';
import '../../utils/common.dart';

class RecommendedCard extends StatelessWidget {
  final RecommendedInfo recommended;

  const RecommendedCard({super.key, required this.recommended});

  @override
  Widget build(BuildContext context) {
    const iconWidth = 24.0;
    const iconHeight = 24.0;

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      color: colorScheme.surfaceContainer,
      child: ListTile(
        visualDensity: VisualDensity.compact,
        minTileHeight: 0,
        onTap: () => launchLink(recommended.officialSite),
        leading: _buildIcon(
          recommended.idIcon,
          iconWidth,
          iconHeight,
          colorScheme.primary,
        ),
        title: Text(
          recommended.name,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: colorScheme.primary,
          ),
        ),
      ),
    );
  }

  Widget _buildIcon(
    String idIcon,
    double iconWidth,
    double iconHeight,
    Color color,
  ) {
    final iconPath = "assets/images/UI/${recommended.idIcon}";

    if (idIcon.isNotEmpty && idIcon.toLowerCase().endsWith('.svg')) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: SvgPicture.asset(
          iconPath,
          width: iconWidth,
          height: iconHeight,
          placeholderBuilder: (BuildContext context) =>
              const CircularProgressIndicator(),
        ),
      );
    } else if (idIcon.isNotEmpty) {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: Image.asset(
          iconPath,
          width: iconWidth,
          height: iconHeight,
          fit: BoxFit.contain,
        ),
      );
    } else {
      return SizedBox(
        width: iconWidth,
        height: iconHeight,
        child: SvgPicture.asset(
          "assets/images/UI/like.svg",
          width: iconWidth,
          height: iconHeight,
          placeholderBuilder: (BuildContext context) =>
              const CircularProgressIndicator(),
          colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
        ),
      );
    }
  }
}
